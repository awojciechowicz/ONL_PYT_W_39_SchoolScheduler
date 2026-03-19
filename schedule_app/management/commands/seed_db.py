from random import randint
from zoneinfo import available_timezones

from django.core.management.base import BaseCommand
from faker import Faker
from packaging.requirements import Requirement

from schedule_app.models import (Teacher, Subject, TimeSlot,
                                 Weekday, ScheduleSlot, TeacherAvailability,
                                 TeacherSubject, SchoolClass, Requirements)

fake = Faker("en_GB")

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Generating subjects"))
        Subject.objects.all().delete()
        subjects = ["Mathematics",
                    "English Language",
                    "English Literature",
                    "Biology",
                    "Chemistry",
                    "Physics",
                    "History",
                    "Geography",
                    # "Computer Science",
                    "Physical Education"]
        for subject in subjects:
            Subject.objects.create(
                name=subject,
            )
        self.stdout.write(self.style.SUCCESS("Generating timeslots"))
        timeslots = [
            {"start": "8:00", "end": "8:45"},
            {"start": "8:55", "end": "9:40"},
            {"start": "9:50", "end": "10:35"},
            # {"start": "10:45", "end": "11:30"},
            # {"start": "11:40", "end": "12:25"},
            # {"start": "12:55", "end": "13:40"},
            # {"start": "13:50", "end": "14:35"},
            # {"start": "14:45", "end": "15:30"},
            # {"start": "15:40", "end": "16:25"},
        ]
        TimeSlot.objects.all().delete()
        for timeslot in timeslots:
            TimeSlot.objects.create(
                start_time=timeslot["start"],
                end_time=timeslot["end"],
            )
        self.stdout.write(self.style.SUCCESS("Generating teachers"))
        Teacher.objects.all().delete()
        for _ in range(9):
            Teacher.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
            )
        self.stdout.write(self.style.SUCCESS("Generating weekdays"))
        Weekday.objects.all().delete()
        for i in range(1,6):
            Weekday.objects.create(
                day=i,
            )
        self.stdout.write(self.style.SUCCESS("Generating schedule slots"))
        ScheduleSlot.objects.all().delete()
        for weekday in Weekday.objects.all():
            for timeslot in TimeSlot.objects.all():
                ScheduleSlot.objects.create(
                    weekday=weekday,
                    time_slot=timeslot,
                )
        self.stdout.write(self.style.SUCCESS("Generating teachers availability"))
        TeacherAvailability.objects.all().delete()
        # for teacher in Teacher.objects.all():
        #     free_spots = randint(int(ScheduleSlot.objects.count() / 3), ScheduleSlot.objects.count()-1)
        #     for _ in range(free_spots):
        #         slot = ScheduleSlot.objects.all().order_by("?").first()
        #         while TeacherAvailability.objects.filter(teacher=teacher, availability=slot).exists():
        #             slot = ScheduleSlot.objects.all().order_by("?").first()
        #         TeacherAvailability.objects.create(
        #             availability=slot,
        #             teacher=teacher,
        #         )
        for teacher in Teacher.objects.all():
            for _ in range(3):
                slot = ScheduleSlot.objects.all().order_by("?").first()
                while (TeacherAvailability.objects.filter(teacher=teacher, availability=slot).exists()
                        or TeacherAvailability.objects.filter(availability=slot).count() > 2):
                    slot = ScheduleSlot.objects.all().order_by("?").first()
                TeacherAvailability.objects.create(
                    availability=slot,
                    teacher=teacher,
                )
        self.stdout.write(self.style.SUCCESS("Generating teachers subjects"))
        TeacherSubject.objects.all().delete()
        # for subject in Subject.objects.all():
        #     num_of_teachers = randint(1,2)
        #     for _ in range(1, num_of_teachers+1):
        #         teacher = Teacher.objects.all().order_by("?").first()
        #         while (TeacherSubject.objects.filter(teacher=teacher, subject=subject).exists()
        #                or TeacherSubject.objects.filter(teacher=teacher).count() > 2):
        #             teacher = Teacher.objects.all().order_by("?").first()
        #         TeacherSubject.objects.create(
        #             subject=subject,
        #             teacher=teacher,
        #         )
        for subject in Subject.objects.all():
            teacher = Teacher.objects.all().order_by("?").first()
            while (TeacherSubject.objects.filter(teacher=teacher).exists()):
                teacher = Teacher.objects.all().order_by("?").first()
            TeacherSubject.objects.create(
                subject=subject,
                teacher=teacher,
            )
        self.stdout.write(self.style.SUCCESS("Generating school classes"))
        schoolclasses = [
            "1a",
            "1b",
            "1c",
        ]
        SchoolClass.objects.all().delete()
        for schoolclass in schoolclasses:
            SchoolClass.objects.create(
                name=schoolclass,
            )
        self.stdout.write(self.style.SUCCESS("Generating requirements"))
        Requirements.objects.all().delete()
        for subject in Subject.objects.all():
            num_of_lessons = randint(1,1)
            for school_class in SchoolClass.objects.all():
                teacher = TeacherSubject.objects.filter(subject=subject).order_by("?").first()
                Requirements.objects.create(
                    school_class=school_class,
                    teacher_subject=teacher,
                    lessons_required=num_of_lessons,
                )

        self.stdout.write(self.style.SUCCESS("Database seeded"))