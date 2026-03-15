from django.core.management.base import BaseCommand
from faker import Faker
from schedule_app.models import Teacher, Subject, TimeSlot

fake = Faker("en_GB")

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Generating teachers"))
        for _ in range(15):
            Teacher.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
            )
        self.stdout.write(self.style.SUCCESS("Generating subjects"))
        subjects = ["Mathematics",
                    "English Language",
                    "English Literature",
                    "Biology",
                    "Chemistry",
                    "Physics",
                    "History",
                    "Geography",
                    "Computer Science",
                    "Physical Education"]
        # for subject in subjects:
        #     Subject.objects.create(
        #         name=subject,
        #     )
        # self.stdout.write(self.style.SUCCESS("Generating timeslots"))
        timeslots = [
            {"start": "8:00", "end": "8:55"},
            {"start": "8:55", "end": "9:40"},
            {"start": "9:50", "end": "10:35"},
            {"start": "10:45", "end": "11:30"},
            {"start": "11:40", "end": "12:25"},
            {"start": "12:55", "end": "13:40"},
            {"start": "13:50", "end": "14:35"},
            {"start": "14:45", "end": "15:30"},
        ]
        for timeslot in timeslots:
            TimeSlot.objects.create(
                start_time=timeslot["start"],
                end_time=timeslot["end"],
            )
        self.stdout.write(self.style.SUCCESS("Database seeded"))