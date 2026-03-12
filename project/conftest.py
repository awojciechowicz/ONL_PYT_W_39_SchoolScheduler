import pytest

from schedule_app.models import Subject, Teacher


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