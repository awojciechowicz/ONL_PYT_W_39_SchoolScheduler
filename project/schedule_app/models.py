from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
DAYS = (
    (1, 'Monday'),
    (2, 'Tuesday'),
    (3, 'Wednesday'),
    (4, 'Thursday'),
    (5, 'Friday'),
    (6, 'Saturday'),
    (7, 'Sunday'),
)

class Subject(models.Model):
    name = models.CharField(max_length=200, unique=True)
    def __str__(self):
        return self.name

class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

class Weekday(models.Model):
    day = models.IntegerField(choices=DAYS)
    time_slots = models.ManyToManyField(TimeSlot, through='ScheduleSlot')
    def __str__(self):
        return self.get_day_display()

class ScheduleSlot(models.Model):
    weekday = models.ForeignKey(Weekday, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)

class TeacherAvailability(models.Model):
    availability = models.ForeignKey(ScheduleSlot, on_delete=models.CASCADE)
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('teacher', 'availability')

class Teacher(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(
        max_length=100,
        unique=True
    )
    available = models.ManyToManyField(ScheduleSlot, blank=True, through='TeacherAvailability')
    subjects = models.ManyToManyField(Subject, blank=True, through='TeacherSubject', related_name='teachers')
    def __str__(self):
        return self.first_name + " " + self.last_name

class TeacherSubject(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('teacher', 'subject')
    def __str__(self):
        return f"{self.subject} with {self.teacher}"

class SchoolClass(models.Model):
    name = models.CharField(max_length=10, unique=True)
    required = models.ManyToManyField(TeacherSubject, through='Requirements')
    def __str__(self):
        return self.name

class Requirements(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    teacher_subject = models.ForeignKey(TeacherSubject, on_delete=models.CASCADE)
    lessons_required = models.IntegerField()
    class Meta:
        unique_together = ('school_class', 'teacher_subject')

class Lessons(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, default=1)
    teacher_subject = models.ForeignKey(TeacherSubject, on_delete=models.CASCADE, default=1)
    lessons_time = models.ForeignKey(ScheduleSlot, on_delete=models.CASCADE, default=1)

    class Meta:
        unique_together = ('school_class', 'teacher_subject', 'lessons_time')


class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False)