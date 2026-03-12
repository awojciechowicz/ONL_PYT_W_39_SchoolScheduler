import pytest

@pytest.mark.django_db
def test_subject_view(subject, client):
    response = client.get(f"/subjects/")
    assert response.status_code == 200
    name = response.context["subjects"].all().get(pk=subject.pk).name
    assert name == subject.name

@pytest.mark.django_db
def test_teacher_view(teacher, client):
    response = client.get(f"/teachers/{teacher.pk}/")
    assert response.status_code == 200
    first_name = response.context["teacher"].first_name
    last_name = response.context["teacher"].last_name
    email = response.context["teacher"].email
    assert first_name == teacher.first_name
    assert last_name == teacher.last_name
    assert email == teacher.email