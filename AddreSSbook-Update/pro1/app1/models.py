from django.db import models
from django.core.exceptions import ValidationError


def validate_phone_length(value):
    for p in value.split(","):
        if len(p.strip()) != 10:
            raise ValidationError("Phone number must be exactly 10 digits")


class Contact(models.Model):
    company = models.CharField(max_length=200)
    owner = models.CharField(max_length=200)
    ceo = models.CharField(max_length=200, blank=True)
    manager = models.CharField(max_length=200, blank=True)

    email = models.TextField(blank=True)
    phone = models.TextField(blank=True, validators=[validate_phone_length])

    social_links = models.TextField(blank=True)

    front_image = models.ImageField(upload_to='cards/')
    back_image = models.ImageField(upload_to='cards/')
    qr_image = models.ImageField(upload_to='cards/', blank=True, null=True)  # ✅ IMPORTANT
    address = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company