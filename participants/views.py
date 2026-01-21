import qrcode
import io
import base64
import openpyxl
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Participant

def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        company = request.POST.get('company')
        agreement = request.POST.get('agreement')

        # Basic Validation
        errors = {}
        if not first_name: errors['first_name'] = "First name is required."
        if not last_name: errors['last_name'] = "Last name is required."
        if not email: errors['email'] = "Email is required."
        if not phone: errors['phone'] = "Phone is required."
        if not agreement: errors['agreement'] = "You must agree to the terms."

        # Duplicate Email Check
        if email and Participant.objects.filter(email=email).exists():
            errors['email'] = "This email is already registered."

        if not errors:
            participant = Participant.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                company=company,
                agreement=(agreement == "on")
            )
            return redirect('success', qr_token=participant.qr_token)
        
        return render(request, 'participants/register.html', {
            'errors': errors, 
            'data': request.POST
        })

    return render(request, 'participants/register.html')

def success_view(request, qr_token):
    participant = get_object_or_404(Participant, qr_token=qr_token)
    
    # Generate Absolute Check-in URL
    checkin_url = request.build_absolute_uri(reverse('checkin', args=[qr_token]))
    
    # Generate QR Code Image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(checkin_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'participants/success.html', {
        'participant': participant,
        'qr_image': qr_base64
    })

@require_POST
def cancel_view(request, qr_token):
    participant = get_object_or_404(Participant, qr_token=qr_token)
    
    if participant.status == 'Checked-in':
        return render(request, 'participants/cancel_result.html', {
            'participant': participant,
            'message': "Cannot cancel registration. You have already checked in.",
            'status_type': "danger"
        })
    
    participant.status = 'Cancelled'
    participant.save()
    
    return render(request, 'participants/cancel_result.html', {
        'participant': participant,
        'message': "Your registration has been successfully cancelled.",
        'status_type': "success"
    })

def checkin_view(request, qr_token):
    participant = get_object_or_404(Participant, qr_token=qr_token)
    status_message = ""
    status_type = "info" # bootstrap alert class (success, warning, danger, info)

    if participant.status == 'Registered':
        participant.status = 'Checked-in'
        participant.save()
        status_message = "Check-in Successful!"
        status_type = "success"
    elif participant.status == 'Checked-in':
        status_message = "Already Checked-in."
        status_type = "warning"
    elif participant.status == 'Cancelled':
        status_message = "Check-in Blocked: Registration Cancelled."
        status_type = "danger"

    return render(request, 'participants/checkin.html', {
        'participant': participant,
        'status_message': status_message,
        'status_type': status_type
    })

@staff_member_required
def dashboard_view(request):
    total_count = Participant.objects.count()
    registered_count = Participant.objects.filter(status='Registered').count()
    checked_in_count = Participant.objects.filter(status='Checked-in').count()
    cancelled_count = Participant.objects.filter(status='Cancelled').count()
    
    recent_participants = Participant.objects.all().order_by('-created_at')[:10]
    
    return render(request, 'participants/dashboard.html', {
        'total_count': total_count,
        'registered_count': registered_count,
        'checked_in_count': checked_in_count,
        'cancelled_count': cancelled_count,
        'recent_participants': recent_participants
    })

@staff_member_required
def export_participants(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Participants"

    # Headers
    columns = ['First Name', 'Last Name', 'Email', 'Phone', 'Company', 'Status', 'Created At']
    ws.append(columns)

    for p in Participant.objects.all():
        ws.append([
            p.first_name,
            p.last_name,
            p.email,
            p.phone,
            p.company or "",
            p.status,
            p.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=participants.xlsx'
    
    wb.save(response)
    return response