import uuid
from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Student(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


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

    course = models.ForeignKey(Course, related_name='calendar_slots', on_delete=models.CASCADE)
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


class StudentPick(models.Model):
    calendar_slot = models.ForeignKey(CalendarSlot, related_name='student_picks', on_delete=models.CASCADE)
    student = models.ForeignKey(Student, related_name='student_picks', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.name} ({self.calendar_slot.course})"

