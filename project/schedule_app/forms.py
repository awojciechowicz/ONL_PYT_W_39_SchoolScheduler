from django import forms
from numpy.f2py.crackfortran import verbose

from schedule_app.models import DAYS, Requirements, Subject


class SubjectCreateForm(forms.Form):
    name = forms.CharField(max_length=200)

class SchoolClassCreateForm(forms.Form):
    name = forms.CharField(max_length=10)

class TeacherCreateForm(forms.Form):
    first_name = forms.CharField(max_length=64)
    last_name = forms.CharField(max_length=64)
    email = forms.EmailField()
    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), widget=forms.CheckboxSelectMultiple)
