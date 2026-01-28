from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=255)
    REQUIRED_FIELDS = []

    phone_validator = RegexValidator(
        regex=r'^0\d{10}$',
        message="Phone number must start with 0 and contain 11 digits."
    )

    # database field stays 'username' but label it as phone_number in forms/API
    username = models.CharField(
        max_length=11,
        unique=True,
        validators=[phone_validator],
        help_text="phone_number",
    )

    def __str__(self):
        return self.full_name or self.username


class Course(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class CalendarSlot(models.Model):
    DAYS_OF_WEEK = [
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday')
    ]

    TIME_SLOTS = [
        ('3-5', '3 PM - 5 PM'),
        ('5-7', '5 PM - 7 PM'),
        ('7-9', '7 PM - 9 PM'),
    ]
    
    DAY_ORDER_MAP = {
        'saturday': 0,
        'sunday': 1,
        'monday': 2,
        'tuesday': 3,
        'wednesday': 4,
        'thursday': 5,
    }

    course = models.ForeignKey(
        Course,
        related_name='calendar_slots',
        on_delete=models.CASCADE,
    )
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    time = models.CharField(max_length=5, choices=TIME_SLOTS)
    status = models.BooleanField(default=False)
    count = models.PositiveIntegerField(default=0)
    day_order = models.IntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('course', 'day', 'time')
        ordering = ['day_order', 'time']
    
    def save(self, *args, **kwargs):
        # Automatically set day_order based on the day
        self.day_order = self.DAY_ORDER_MAP.get(self.day.lower(), 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course.title} - {self.day} ({self.time})"




class UserPick(models.Model):
    calendar_slot = models.ForeignKey(
        CalendarSlot,
        related_name='user_picks',
        on_delete=models.CASCADE,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='user_picks',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_username()} ({self.calendar_slot.course})"