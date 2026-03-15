import datetime
import pytest

from schedule_app.models import Subject, Teacher, TimeSlot


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
def timeslot():
    return TimeSlot.objects.create(
        start_time=datetime.time(hour=8, minute=00),
        end_time=datetime.time(hour=8, minute=45),
    )