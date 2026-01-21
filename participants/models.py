import uuid
from django.db import models

class Participant(models.Model):
    STATUS_CHOICES = [
        ('Registered', 'Registered'),
        ('Checked-in', 'Checked-in'),
        ('Cancelled', 'Cancelled'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=200, blank=True, null=True)
    agreement = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Registered')
    
    # QR token for secure check-in URL
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
