import uuid
from django.db import models

class Student(models.Model):
    FOOD_CHOICES = [('Veg', 'Veg'), ('Non-Veg', 'Non-Veg')]

    name       = models.CharField(max_length=200)
    usn        = models.CharField(max_length=20, unique=True)
    section    = models.CharField(max_length=10)
    food_type  = models.CharField(max_length=10, choices=FOOD_CHOICES)
    email      = models.EmailField()
    qr_id      = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    is_used    = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.usn})"  

