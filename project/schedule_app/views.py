import random
from calendar import weekday

import numpy as np
from deap import creator, base, tools, algorithms
import random
from django.shortcuts import render, redirect
from django.views import View

from .forms import (SubjectCreateForm,
                    SchoolClassCreateForm, TeacherCreateForm)
from .models import (Weekday,
                     TimeSlot,
                     ScheduleSlot,
                     Teacher,
                     TeacherAvailability,
                     Subject,
                     SchoolClass,
                     Requirements,
                     Lessons, TeacherSubject)




# Create your views here.
class TeachersView(View):
    def get(self, request, *args, **kwargs):
        teachers = Teacher.objects.all()
        context = {
            'teachers': teachers,
        }
        return render(
            request,
            'schedule_app/teachers.html',
            context
        )

class TeacherDetailsView(View):
    def get(self, request, *args, **kwargs):
        teacher = Teacher.objects.get(pk=kwargs['teacher_id'])
        available = teacher.available.all()
        weekdays = Weekday.objects.all()
        time_slots = TimeSlot.objects.all()
        schedule_slots = ScheduleSlot.objects.all().order_by('time_slot', 'weekday')
        availability = []
        for schedule_slot in schedule_slots:
            if available.filter(weekday=schedule_slot.weekday, time_slot=schedule_slot.time_slot).exists():
                availability.append({
                    'weekday': schedule_slot.weekday,
                    'time_slot': schedule_slot.time_slot,
                    'color': 'Lightgreen'
                })
            else:
                availability.append({
                    'weekday': schedule_slot.weekday,
                    'time_slot': schedule_slot.time_slot,
                    'color': 'Lightpink'
                })
        context = {
            'teacher': teacher,
            # 'available': available,
            'weekdays': weekdays,
            'time_slots': time_slots,
            # 'schedule_slots': schedule_slots,
            'availability': availability,
        }
        return render(
            request,
            'schedule_app/teacher_availability.html',
            context
        )

class TeachersAvailabilityView(View):
    def get(self, request, *args, **kwargs):
        teachers_availability = TeacherAvailability.objects.all()
        weekdays = Weekday.objects.all()
        time_slots = TimeSlot.objects.all()
        schedule_slots = ScheduleSlot.objects.all().order_by('time_slot', 'weekday')
        teach_avail = []
        for schedule_slot in schedule_slots:
            teach_avail.append({
                'weekday': schedule_slot.weekday,
                'time_slot': schedule_slot.time_slot,
                'teachers': [teach.teacher
                             for teach in teachers_availability.filter(availability=schedule_slot)]
            })
        context = {
            'teachers_availability': teach_avail,
            'weekdays': weekdays,
            'time_slots': time_slots,
        }
        return render(
            request,
            'schedule_app/teachers_available.html',
            context
        )

class SubjectsView(View):
    def get(self, request, *args, **kwargs):
        subjects = Subject.objects.all()
        context = {
            'subjects': subjects,
        }
        return render(
            request,
            'schedule_app/subjects.html',
            context
        )

class SchoolClassesView(View):
    def get(self, request, *args, **kwargs):
        school_classes = SchoolClass.objects.all()

        context = {
            'school_classes': school_classes,
        }
        return render(
            request,
            'schedule_app/school_classes.html',
            context
        )

class SchoolClassDetailView(View):
    def get(self, request, *args, **kwargs):
        school_class = SchoolClass.objects.get(pk=kwargs['school_class_id'])
        subjects = school_class.requirements_set.all()
        context = {
            'school_class': school_class,
            'subjects': subjects,
        }
        return render(
            request,
            'schedule_app/school_class_detail.html',
            context
        )

class GenerateScheduleView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'schedule_app/generate_schedule.html')
    def post(self, request, *args, **kwargs):
        requirements = Requirements.objects.all()
        schedule_slots = ScheduleSlot.objects.all().order_by('time_slot', 'weekday')
        teachers_availability = TeacherAvailability.objects.all()
        weekdays = Weekday.objects.all()
        time_slots = TimeSlot.objects.all()
        school_classes = SchoolClass.objects.all()
        teacher_subjects = TeacherSubject.objects.all()
        teachers = Teacher.objects.all()
        schedule_old = Lessons.objects.all().delete()


        # teachers_subject = []
        lessons = []
        for requirement in requirements:
            # teachers_subject.append(requirement.teacher_subject)
            for _ in range(requirement.lessons_required):
                lessons.append({
                    'school_class': requirement.school_class_id,
                    'teach': requirement.teacher_subject.teacher_id,
                    'subj': requirement.teacher_subject.subject_id,
                })
        temp = []
        for schedule_slot in schedule_slots:
            temp.append([teach_avail.teacher_id
                        for teach_avail
                        in teachers_availability.filter(availability=schedule_slot)])
        teach_avail = np.ndarray((time_slots.count(), weekdays.count()), dtype=list)
        for i in range(weekdays.count()):
            for j in range(time_slots.count()):
                teach_avail[j, i] = temp[i + weekdays.count() * j]



        def genetic_alg():
            creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0, 1.0,))
            creator.create("Individual", np.ndarray, fitness=creator.FitnessMulti)

            def random_individual():
                arr = np.ndarray((school_classes.count(),
                                  time_slots.count(),
                                  weekdays.count()),
                                 dtype=object)
                for i, school_class in enumerate(school_classes):
                    # print('start: ', school_class)
                    filtered_lessons = [lesson for lesson in lessons if lesson['school_class'] == school_class.id]
                    random.shuffle(filtered_lessons)
                    index = 0

                    for j, time_slot in enumerate(time_slots):
                        # print(time_slot)
                        for k, weekday in enumerate(weekdays):
                            # print(k, weekday)
                            if len(filtered_lessons) > k + (weekdays.count() * j):
                                # print(k, weekday)
                                arr[i, j, k] = {'school_class': str(filtered_lessons[index]['school_class']),
                                                'teach': str(filtered_lessons[index]['teach']),
                                                'subj': str(filtered_lessons[index]['subj'])}
                                # print('IND1: ', arr[i, j, k])
                            else:
                                arr[i, j, k] = None
                            index += 1
                individual = creator.Individual(arr)
                return individual

            def evalSchedule(individual):
                collision = 0
                # kolizja wewnatrz planu pomiedzy klasami:
                for i in range(individual.shape[0]):
                    for j in range(i + 1, individual.shape[0]):
                        for k in range(individual.shape[1]):
                            for l in range(individual.shape[2]):
                                if individual[i, k, l] is not None and individual[j, k, l] is not None:
                                    # print('IND1: ', individual[i, k, l]['teach'])
                                    if individual[i, k, l]['teach'] == individual[j, k, l]['teach']:
                                        # print(individual[i, k, l]['teach'], ' i ', individual[j, k, l]['teach'])
                                        collision -= 100
                # dostepnosc nauczycieli:
                availability = 0
                for i in range(individual.shape[0]):
                    for j in range(individual.shape[1]):
                        for k in range(individual.shape[2]):
                            if individual[i][j][k] is not None:
                                if int(individual[i, j, k]['teach']) in teach_avail[j, k]:
                                    # print(individual[i, j, k]['teach'], ' w ', teach_avail[j, k])
                                    # availability += 50
                                    availability += 0
                                else:
                                    # print('Avail: ', individual[i, j, k]['teach'], ' w ', teach_avail[j, k])
                                    # print(type(individual[i, j, k]['teach']))
                                    availability -= 10
                                    # availability -= 0

                # okienka:
                result = 0
                for i in range(individual.shape[0]):
                    for j in range(1, individual.shape[1] - 1):
                        for k in range(individual.shape[2]):
                            if individual[i, j, k] is None and (
                                    individual[i, j - 1, k] is not None or individual[i, j + 1, k] is not None):
                                result -= 3
                                # result -= 0

                # powtarzanie przedmiotów jednego dnia
                # result = 0
                for i in range(individual.shape[0]):
                    for j in range(individual.shape[1]):
                        for k in range(j + 1, individual.shape[1]):
                            for l in range(individual.shape[2]):
                                if individual[i, j, l] is not None and individual[i, k, l] is not None:
                                    if individual[i, j, l]['subj'] == individual[i, k, l]['subj']:
                                        result -= 1
                                        # result -= 0
                # print('Result: ', collision, availability, result)

                return (collision, availability, result,)

            def cxTwoPoint3D(ind1, ind2):
                x = ind1.shape[0]
                cxpoint = random.randint(0, x - 1)
                ind1_copy = creator.Individual(ind1.copy())
                ind2_copy = creator.Individual(ind2.copy())
                ind1_copy[cxpoint, :, :], ind2_copy[cxpoint, :, :] = \
                    ind2[cxpoint, :, :].copy(), ind1[cxpoint, :, :].copy()
                return ind1_copy, ind2_copy

            def mutShuffle2D(individual, indpb):
                for i in range(individual.shape[0]):
                    for row in range(individual.shape[1]):
                        if random.random() < indpb:
                            pos1 = random.randint(0, individual.shape[2] - 1)
                            pos2 = random.randint(0, individual.shape[2] - 1)
                            individual[i, row, pos1], individual[i, row, pos2] = \
                                individual[i, row, pos2], individual[i, row, pos1]
                    for col in range(individual.shape[2]):
                        if random.random() < indpb:
                            pos1 = random.randint(0, individual.shape[1] - 1)
                            # while individual[i, pos1, col] is None and individual[i, pos1 - 1, col] is None:
                            #     pos1 = random.randint(0, individual.shape[1] - 1)
                            #     print("POS1: ", pos1)
                            #     print(individual[i, pos1, col])
                            pos2 = random.randint(0, individual.shape[1] - 1)
                            # while individual[i, pos2, col] is None and individual[i, pos2 - 1, col] is None:
                            #     pos2 = random.randint(0, individual.shape[1] - 1)
                            #     print("POS2: ", pos2)
                            #     print(individual[i, pos2, col])
                            individual[i, pos1, col], individual[i, pos2, col] = \
                                individual[i, pos2, col], individual[i, pos1, col]
                return individual,

            toolbox = base.Toolbox()
            toolbox.register("individual", random_individual)
            toolbox.register("population", tools.initRepeat, list, toolbox.individual)
            toolbox.register("mate", cxTwoPoint3D)
            toolbox.register("mutate", mutShuffle2D, indpb=0.3)
            toolbox.register("evaluate", evalSchedule)
            toolbox.register("select", tools.selTournament, tournsize=10)
            # toolbox.register("select", tools.selNSGA2)

            population = toolbox.population(n=200)
            algorithms.eaSimple(population, toolbox, cxpb=0.2, mutpb=0.35, ngen=500)
            best_individual = tools.selBest(population, k=1)[0]
            fitness_values = best_individual.fitness.values
            print('Last fitness: ', fitness_values)
            return best_individual, fitness_values

        schedule, fitness = genetic_alg()

        for i in range(schedule.shape[0]):
            for j, schedule_slot in enumerate(schedule_slots):
                if schedule[i, j // weekdays.count(), j % weekdays.count()] is not None:
                    school_class_gen = schedule[i, j // weekdays.count(), j % weekdays.count()]['school_class']
                    teacher_gen = schedule[i, j // weekdays.count(), j % weekdays.count()]['teach']
                    subject_gen = schedule[i, j // weekdays.count(), j % weekdays.count()]['subj']
                    teacher_subject_gen = teacher_subjects.get(teacher_id=teacher_gen, subject_id=subject_gen)
                    schedule_slot_gen = schedule_slots.get(weekday=schedule_slot.weekday, time_slot=schedule_slot.time_slot)
                    Lessons.objects.create(
                        school_class_id=school_class_gen,
                        teacher_subject_id=teacher_subject_gen.id,
                        lessons_time_id=schedule_slot_gen.id,
                    )

        context = {
            'conflicts': int(abs(fitness[0]/100)),
            'availability': int(abs(fitness[1]/10)),
            'result': fitness[2],
            'school_classes': school_classes,
            'weekdays': weekdays,
            'teachers': teachers,
        }
        return render(request, 'schedule_app/schedule_generated.html', context)

class SubjectCreateView(View):
    def get(self, request, *args, **kwargs):
        form = SubjectCreateForm()
        context = {
            'form': form,
        }
        return render(
            request,
            'schedule_app/subject_create.html',
            context
        )

    def post(self, request, *args, **kwargs):
        form = SubjectCreateForm(request.POST)
        context = {
           'form': form,
        }
        if form.is_valid():
           name = form.cleaned_data['name']
           subject = Subject.objects.create(
               name=name,
           )
           return redirect('subjects')
        else:
           return render(
               request,
               'schedule_app/subject_create.html',
               context
           )

class SchoolClassCreateView(View):
    def get(self, request, *args, **kwargs):
        form = SchoolClassCreateForm()
        context = {
            'form': form,
        }
        return render(
            request,
            'schedule_app/school_class_create.html',
            context
        )
    def post(self, request, *args, **kwargs):
        form = SchoolClassCreateForm(request.POST)
        context = {
            'form': form,
        }
        if form.is_valid():
            name = form.cleaned_data['name']
            school_class = SchoolClass.objects.create(
                name=name,
            )
            return redirect('school_classes')
        else:
            return render(
                request,
                'schedule_app/school_class_create.html',
                context
            )

class RequirementsCreateView(View):
    def get(self, request, *args, **kwargs):
        school_class = SchoolClass.objects.get(pk=kwargs['school_class_id'])
        teacher_subjects = TeacherSubject.objects.all()
        requirements = Requirements.objects.filter(school_class=school_class)
        context = {
            'school_class': school_class,
            'teacher_subjects': teacher_subjects,
            'requirements': requirements,
        }
        return render(
            request,
            'schedule_app/requirements_create.html',
            context
        )
    def post(self, request, *args, **kwargs):
        school_class = SchoolClass.objects.get(pk=kwargs['school_class_id'])
        teacher_subject_ids = request.POST.getlist('teacher_subject_ids')
        for teach_subj_id in teacher_subject_ids:
            hours = request.POST.get(f"hours_{teach_subj_id}")
            teacher_subject = TeacherSubject.objects.get(id=teach_subj_id)
            if hours and int(hours) > 0:
                if Requirements.objects.filter(school_class=school_class, teacher_subject=teacher_subject).exists():
                    Requirements.objects.filter(school_class=school_class, teacher_subject=teacher_subject).update(
                        lessons_required=int(hours),
                    )
                else:
                    Requirements.objects.create(
                        school_class=school_class,
                        teacher_subject=teacher_subject,
                        lessons_required=int(hours),
                    )
            elif hours and int(hours) == 0:
                Requirements.objects.filter(school_class=school_class, teacher_subject=teacher_subject).delete()
        return redirect('school_class', school_class_id=school_class.id)

class TeacherCreateView(View):
    def get(self, request, *args, **kwargs):
        form = TeacherCreateForm()
        context = {
            'form': form,
        }
        return render(
            request,
            'schedule_app/teacher_create.html',
            context
        )
    def post(self, request, *args, **kwargs):
        form = TeacherCreateForm(request.POST)
        context = {
            'form': form,
        }
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            subjects = form.cleaned_data['subjects']

            teacher = Teacher.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            teacher.subjects.set(subjects)
            return redirect('teachers')
        else:
            return render(
                request,
                'schedule_app/teacher_create.html',
                context
            )

class TeacherAvailabilityEditView(View):
    def get(self, request, *args, **kwargs):
        teacher = Teacher.objects.get(pk=kwargs['teacher_id'])
        available = teacher.available.all()
        weekdays = Weekday.objects.all()
        time_slots = TimeSlot.objects.all()
        teacher_availabilities = TeacherAvailability.objects.filter(teacher=teacher)
        schedule_slots = ScheduleSlot.objects.all().order_by('time_slot', 'weekday')
        availability = []
        for schedule_slot in schedule_slots:
            if available.filter(weekday=schedule_slot.weekday, time_slot=schedule_slot.time_slot).exists():
                availability.append({
                    'weekday': schedule_slot.weekday,
                    'time_slot': schedule_slot.time_slot,
                    'color': 'Lightgreen'
                })
            else:
                availability.append({
                    'weekday': schedule_slot.weekday,
                    'time_slot': schedule_slot.time_slot,
                    'color': 'Lightpink'
                })
        context = {
            'teacher': teacher,
            'weekdays': weekdays,
            'time_slots': time_slots,
            'availability': availability,
        }
        return render(
            request,
            'schedule_app/teacher_availability_edit.html',
            context
        )
    def post(self, request, *args, **kwargs):
        teacher = Teacher.objects.get(pk=kwargs['teacher_id'])
        weekdays = Weekday.objects.all()
        time_slots = TimeSlot.objects.all()
        for weekday in weekdays:
            for time_slot in time_slots:
                schedule_slot = ScheduleSlot.objects.get(weekday=weekday, time_slot=time_slot)
                if request.POST.get(f"avail_{weekday}_{time_slot}") == 'on':
                    if not TeacherAvailability.objects.filter(teacher=teacher, availability=schedule_slot).exists():
                        TeacherAvailability.objects.create(teacher=teacher, availability=schedule_slot)
                else:
                    print(request.POST.get(f"avail_{weekday}_{time_slot}"))
                    if TeacherAvailability.objects.filter(teacher=teacher, availability=schedule_slot).exists():
                        TeacherAvailability.objects.get(teacher=teacher, availability=schedule_slot).delete()
        return redirect('teacher', teacher_id=teacher.id)

class ScheduleSchoolClassView(View):
    def get(self, request, *args, **kwargs):
        school_class = SchoolClass.objects.get(pk=kwargs['school_class_id'])
        school_classes = SchoolClass.objects.all()
        teachers = Teacher.objects.all()
        lessons = school_class.lessons_set.all()
        weekdays = Weekday.objects.all()
        time_slots = TimeSlot.objects.all()
        schedule_slots = ScheduleSlot.objects.all().order_by('time_slot', 'weekday')
        class_schedule = []
        for schedule_slot in schedule_slots:
            if lessons.filter(lessons_time=schedule_slot).exists():
                class_schedule.append({
                    'schedule_slot': schedule_slot,
                    'teacher_subject': lessons.filter(lessons_time=schedule_slot).get().teacher_subject,
                    'school_class': lessons.filter(lessons_time=schedule_slot).get().school_class,
                })
            else:
                class_schedule.append({
                    'schedule_slot': schedule_slot,
                    'teacher_subject': '',
                    'school_class': '',
                })

        context = {
            'school_class': school_class,
            'lessons': class_schedule,
            'weekdays': weekdays,
            'time_slots': time_slots,
            'school_classes': school_classes,
            'teachers': teachers,
        }
        return render(
            request,
            'schedule_app/school_class_schedule.html',
            context
        )

class ScheduleTeacherView(View):
    def get(self, request, *args, **kwargs):
        teacher = Teacher.objects.get(pk=kwargs['teacher_id'])
        teachers = Teacher.objects.all()
        school_classes = SchoolClass.objects.all()
        teacher_id = teacher.id
        available = teacher.available.all()
        lessons = Lessons.objects.filter(teacher_subject__teacher_id=teacher_id)
        weekdays = Weekday.objects.all()
        time_slots = TimeSlot.objects.all()
        schedule_slots = ScheduleSlot.objects.all().order_by('time_slot', 'weekday')

        # print(lessons)
        teacher_schedule = []
        for schedule_slot in schedule_slots:
            if lessons.filter(lessons_time=schedule_slot).exists():
                if available.filter(weekday=schedule_slot.weekday, time_slot=schedule_slot.time_slot).exists():
                    teacher_schedule.append({
                        'schedule_slot': schedule_slot,
                        'teacher_subject': lessons.filter(lessons_time=schedule_slot).get().teacher_subject,
                        'school_class': lessons.filter(lessons_time=schedule_slot).get().school_class,
                        'color': 'Lightgreen'
                    })
                else:
                    teacher_schedule.append({
                        'schedule_slot': schedule_slot,
                        'teacher_subject': lessons.filter(lessons_time=schedule_slot).get().teacher_subject,
                        'school_class': lessons.filter(lessons_time=schedule_slot).get().school_class,
                        'color': 'Lightpink'
                    })
            else:
                if available.filter(weekday=schedule_slot.weekday, time_slot=schedule_slot.time_slot).exists():
                    teacher_schedule.append({
                        'schedule_slot': schedule_slot,
                        'teacher_subject': '',
                        'school_class': '',
                        'color': 'Lightgreen'
                    })
                else:
                    teacher_schedule.append({
                        'schedule_slot': schedule_slot,
                        'teacher_subject': '',
                        'school_class': '',
                        'color': 'Lightpink'
                    })

        # print(teacher_schedule)
        context = {
            'teacher': teacher,
            'lessons': teacher_schedule,
            'weekdays': weekdays,
            'time_slots': time_slots,
            'teachers': teachers,
            'school_classes': school_classes,
        }
        return render(
            request,
            'schedule_app/teacher_schedule.html',
            context
        )

class ScheduleDaySchoolClassView(View):
    def get(self, request, *args, **kwargs):
        weekday = Weekday.objects.get(pk=kwargs['weekday_id'])
        weekdays = Weekday.objects.all()
        lessons = Lessons.objects.filter(lessons_time__weekday=weekday).order_by('lessons_time__time_slot', 'school_class')
        school_classes = SchoolClass.objects.all()
        teachers = Teacher.objects.all()
        time_slots = TimeSlot.objects.all()
        schedule_slots = ScheduleSlot.objects.all().order_by('time_slot', 'weekday')
        day_schedule = []
        # for schedule_slot in schedule_slots:
        for time_slot in time_slots:
            for school_class in school_classes:
                if lessons.filter(lessons_time__time_slot=time_slot, school_class=school_class).exists():
                    day_schedule.append({
                        'time_slot': time_slot,
                        'teacher_subject': lessons.filter(lessons_time__time_slot=time_slot,
                                                          school_class=school_class).get().teacher_subject,
                    })
                else:
                    day_schedule.append({
                        'time_slot': time_slot,
                        'teacher_subject': '',
                    })
        context = {
            'school_classes': school_classes,
            'weekday': weekday,
            'lessons': day_schedule,
            'time_slots': time_slots,
            'teachers': teachers,
            'weekdays': weekdays,
        }
        return render(
            request,
            'schedule_app/day_school_class_schedule.html',
            context
        )

class ScheduleDayTeacherView(View):
    def get(self, request, *args, **kwargs):
        weekday = Weekday.objects.get(pk=kwargs['weekday_id'])
        weekdays = Weekday.objects.all()
        lessons = Lessons.objects.filter(lessons_time__weekday=weekday).order_by('lessons_time__time_slot', 'teacher_subject__teacher_id')
        for lesson in lessons:
            print(lesson.teacher_subject.teacher, lesson.teacher_subject.subject, lesson.lessons_time.time_slot, lesson.lessons_time.weekday, lesson.school_class)
        teachers = Teacher.objects.all()
        school_classes = SchoolClass.objects.all()
        time_slots = TimeSlot.objects.all()
        day_schedule = []
        for time_slot in time_slots:
            for teacher in teachers:
                if lessons.filter(lessons_time__time_slot=time_slot, teacher_subject__teacher=teacher).exists():
                    day_schedule.append({
                        'time_slot': time_slot,
                        'teacher_subject': lessons.filter(lessons_time__time_slot=time_slot,
                                                          teacher_subject__teacher=teacher).get().teacher_subject,
                        'school_class': lessons.filter(lessons_time__time_slot=time_slot,
                                                       teacher_subject__teacher=teacher).get().school_class,
                    })
                else:
                    day_schedule.append({
                        'time_slot': time_slot,
                        'teacher_subject': '',
                        'school_class': '',
                    })
        context = {
            'teachers': teachers,
            'weekday': weekday,
            'lessons': day_schedule,
            'time_slots': time_slots,
            'school_classes': school_classes,
            'weekdays': weekdays,
        }
        return render(
            request,
            'schedule_app/day_teacher_schedule.html',
            context
        )

class SchedulesView(View):
    def get(self, request, *args, **kwargs):
        school_classes = SchoolClass.objects.all()
        teachers = Teacher.objects.all()
        weekdays = Weekday.objects.all()
        context = {
            'school_classes': school_classes,
            'teachers': teachers,
            'weekdays': weekdays,
        }
        return render(
            request,
            'schedule_app/schedules_template.html',
            context
        )