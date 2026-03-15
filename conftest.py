import datetime
import pytest
from faker import Faker

from schedule_app.models import Subject, Teacher, TimeSlot

fake = Faker('en_GB')

@pytest.fixture
def subject():
    return Subject.objects.create(name="Test subject")

@pytest.fixture
def teacher():
    return Teacher.objects.create(
        first_name="Test teacher name",
        last_name="Test teacher surname",
        email="Test teacher email"
    )

@pytest.fixture
def teachers():
    teachers = []
    for _ in range(10):
        teacher=Teacher.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
        )
        teachers.append(teacher)
    return teachers

@pytest.fixture
def timeslot():
    return TimeSlot.objects.create(
        start_time=datetime.time(hour=8, minute=00),
        end_time=datetime.time(hour=8, minute=45),
    )