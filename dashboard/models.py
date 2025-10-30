from django.db import models
from django.contrib.auth.models import User


class School(models.Model):
    name = models.CharField(max_length=256)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    adopted_section = models.CharField(max_length=256)
    no_of_students = models.IntegerField(default=0)
    theme_color = models.CharField(max_length=7, default="#ffffff")
    coordinate1_lat = models.DecimalField(max_digits=9, decimal_places=6)
    coordinate1_lng = models.DecimalField(max_digits=9, decimal_places=6)
    coordinate2_lat = models.DecimalField(max_digits=9, decimal_places=6)
    coordinate2_lng = models.DecimalField(max_digits=9, decimal_places=6)
    coordinate3_lat = models.DecimalField(max_digits=9, decimal_places=6)
    coordinate3_lng = models.DecimalField(max_digits=9, decimal_places=6)
    coordinate4_lat = models.DecimalField(max_digits=9, decimal_places=6)
    coordinate4_lng = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    student = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.student.username


class Events(models.Model):
    EVENT_TYPE_CHOICES = [
        ("cleanup", "cleanup"),
        ("workshop", "workshop"),
        ("plantation", "plantation"),
        ("awareness", "awareness"),
        ("research", "research"),
        ("other", "other"),
    ]
    name = models.CharField(max_length=256)
    description = models.TextField(default="no description provided")
    requirements = models.TextField(default="no requirements")
    event_type = models.CharField(
        max_length=56, choices=EVENT_TYPE_CHOICES, default="cleanup"
    )
    location = models.CharField(max_length=256)
    date = models.DateField()
    time = models.TimeField()
    expected_participants = models.IntegerField()
    waste_collected = models.IntegerField(default=0)
    plastic_collected = models.IntegerField(default=0)
    paper_collected = models.IntegerField(default=0)
    glass_collected = models.IntegerField(default=0)
    miscellaneous_collected = models.IntegerField(default=0)
    organised_by = models.ForeignKey(School, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class EventParticipants(models.Model):
    student = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    event = models.ForeignKey(
        Events, on_delete=models.CASCADE, related_name="eventparticipants"
    )

    class Meta:
        unique_together = ("student", "event")

    def __str__(self):
        return f"{self.student.username} - {self.event.name}"
