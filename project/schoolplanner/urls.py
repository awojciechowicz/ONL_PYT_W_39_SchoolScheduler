"""
URL configuration for schoolplanner project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from schedule_app import views as sch_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('school_classes/', sch_views.SchoolClassesView.as_view(), name='school_classes'),
    path('school_classes/create/', sch_views.SchoolClassCreateView.as_view(), name='school-class-create'),
    path('school_classes/requirements/<int:school_class_id>/', sch_views.SchoolClassDetailView.as_view(), name='school_class'),
    path('school_classes/requirements/create/<int:school_class_id>/', sch_views.RequirementsCreateView.as_view(), name='requirements-create'),
    path('teachers/', sch_views.TeachersView.as_view(), name='teachers'),
    path('teachers/<int:teacher_id>/', sch_views.TeacherDetailsView.as_view(), name='teacher'),
    path('teachers/create/', sch_views.TeacherCreateView.as_view(), name='teacher-create'),
    path('teachers/edit/<int:teacher_id>/', sch_views.TeacherAvailabilityEditView.as_view(), name='teacher-availability_edit'),
    path('teachers/teach_avail/', sch_views.TeachersAvailabilityView.as_view(), name='teachers-avail'),
    path('subjects/', sch_views.SubjectsView.as_view(), name='subjects'),
    path('subjects/create/', sch_views.SubjectCreateView.as_view(), name='subject-create'),
    path('schedule/', sch_views.GenerateScheduleView.as_view(), name='schedule'),
    path('schedule/all/', sch_views.SchedulesView.as_view(), name='schedules'),
    path('schedule/school_classes/<int:school_class_id>/', sch_views.ScheduleSchoolClassView.as_view(), name='school-class-schedule'),
    path('schedule/teachers/<int:teacher_id>/', sch_views.ScheduleTeacherView.as_view(), name='teacher-schedule'),
    path('schedule/school_classes/day/<int:weekday_id>/', sch_views.ScheduleDaySchoolClassView.as_view(), name='day-school-class-schedule'),
    path('schedule/teachers/day/<int:weekday_id>/', sch_views.ScheduleDayTeacherView.as_view(), name='day-teacher-schedule'),





]
