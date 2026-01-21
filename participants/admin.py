from django.contrib import admin
from .models import Participant

@admin.action(description='Mark selected participants as Checked-in')
def make_checked_in(modeladmin, request, queryset):
    updated = queryset.update(status='Checked-in')
    modeladmin.message_user(request, f'{updated} user(s) successfully marked as Checked-in.')

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    actions = [make_checked_in]
    readonly_fields = ('qr_token', 'created_at')
