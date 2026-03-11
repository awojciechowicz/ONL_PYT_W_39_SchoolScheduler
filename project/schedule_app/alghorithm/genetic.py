import random

import numpy as np
from deap import creator, base, tools, algorithms


def genetic_alg(weekdays, time_slots, school_classes, lessons, teach_avail):
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", np.ndarray, fitness=creator.FitnessMax)

    def random_individual():

        arr = np.ndarray((school_classes.count(),
                          time_slots.count(),
                          weekdays.count()),
                         dtype=object)
        for i, school_class in enumerate(school_classes):
            # filtered_lessons = list(lessons.filter(school_class=school_class))
            filtered_lessons = [lesson for lesson in lessons if lesson['school_class'] == school_class]
            random.shuffle(filtered_lessons)
            index = 0
            # print('Pierwsza lista: ', filtered_lessons)
            for j, time_slot in enumerate(time_slots):
                for k, weekday in enumerate(weekdays):
                    # index = (j * weekdays.count() + k) % len(filtered_lessons)
                    # arr[i][j][k] = filtered_lessons[index]
                    if len(filtered_lessons) > k + (weekdays.count() * j):
                        # arr[i][j][k] = filtered_lessons[index]
                        arr[i][j][k] = filtered_lessons[index]['teach_subj']
                    else:
                        arr[i][j][k] = None
                    index += 1
            # print('Druga lista: ', arr[i])
        individual = creator.Individual(arr)
        # print(individual)
        return individual

    def evalSchedule(individual):
        result = 0
        # print('Pierwszy: ', individual)
        for i in range(individual.shape[0]):
            for j in range(i + 1, individual.shape[0]):
                for k in range(individual.shape[1]):
                    for l in range(individual.shape[2]):
                        ind1 = individual[i][k][l]
                        ind2 = individual[j][k][l]
                        # print('IND1: ', ind1, 'IND2: ', ind2)
                        if individual[i][k][l] and individual[i][k][l] == individual[j][k][l]:
                            result -= 100
        print('Result: ', result)
        for i in range(individual.shape[0]):
            for j in range(individual.shape[1]):
                for k in range(individual.shape[2]):
                    ind = str(individual[i][j][k])
                    print('IND: ', ind)
                    after_with = ind.split(' with ')
                    print('after_with: ', type(after_with[-1]))
                    print('teach: ', teach_avail[j][k])
                    if after_with in teach_avail[j][k]:
                        print('True')
                        result += 100
                    else:
                        print('False')
                        result -= 100
                    print('Result: ', result)
                    print('--------------------------------')
        return (result,)

    def cxTwoPoint3D(ind1, ind2):
        x = ind1.shape[0]
        cxpoint = random.randint(0, x - 1)
        ind1_copy = creator.Individual(ind1.copy())
        ind2_copy = creator.Individual(ind2.copy())
        ind1_copy[cxpoint, :, :], ind2_copy[cxpoint, :, :] = \
            ind2[cxpoint, :, :].copy(), ind1[cxpoint, :, :].copy()
        return ind1_copy, ind2_copy

    def mutShuffle2D(individual, indpb):
        for i in range(individual.shape[0]):  # dla każdej warstwy
            for row in range(individual.shape[2]):
                if random.random() < indpb:
                    pos1 = random.randint(0, individual.shape[2] - 1)
                    pos2 = random.randint(0, individual.shape[2] - 1)
                    # print('Row before: ', individual[i, row, :])
                    individual[i, row, pos1], individual[i, row, pos2] = \
                        individual[i, row, pos2], individual[i, row, pos1]
                    # print('Row after: ', individual[i, row, :])
            # for col in range(individual.shape[2]):
            #     if random.random() < indpb:
            #         pos1 = random.randint(0, individual.shape[1] - 1)
            #         pos2 = random.randint(0, individual.shape[2] - 1)
            #         individual[i, pos1, col], individual[i, pos2, col] = \
            #             individual[i, pos2, col], individual[i, pos1, col]
        return individual,

    toolbox = base.Toolbox()
    toolbox.register("individual", random_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("mate", cxTwoPoint3D)
    toolbox.register("mutate", mutShuffle2D, indpb=0.3)
    toolbox.register("evaluate", evalSchedule)
    toolbox.register("select", tools.selTournament, tournsize=1)

    population = toolbox.population(n=2)
    algorithms.eaSimple(population, toolbox, cxpb=0.2, mutpb=0.3, ngen=5)
    best_individual = tools.selBest(population, k=2)[0]
    # print(best_individual)
    fitness_values = best_individual.fitness.values[0]
    print('Last fitness: ', fitness_values)
    return best_individual

# weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
# time_slots = ['8:00', '8:55', '9:50', '10:45', '11:40', '12:35', '13:30', '14:25', '15:20', '16:15']
# school_classes = ['1a', '1b']
# lessons = [
#     {'teacher': 'Jodie Foster',
#      'subject': 'Matematyka',
#      'school_class': '1a'},
#     {'teacher': 'Jodie Foster',
#      'subject': 'Matematyka',
#      'school_class': '1a'},
#     {'teacher': 'Jodie Foster',
#      'subject': 'Matematyka',
#      'school_class': '1a'},
#     {'teacher': 'Leonardo DiCaprio',
#      'subject': 'Fizyka',
#      'school_class': '1a'},
#     {'teacher': 'Leonardo DiCaprio',
#      'subject': 'Fizyka',
#      'school_class': '1a'},
#     {'teacher': 'Leonardo DiCaprio',
#      'subject': 'Fizyka',
#      'school_class': '1a'},
#     {'teacher': 'Jodie Foster',
#      'subject': 'Matematyka',
#      'school_class': '1b'},
#     {'teacher': 'Jodie Foster',
#      'subject': 'Matematyka',
#      'school_class': '1b'},
#     {'teacher': 'Jodie Foster',
#      'subject': 'Matematyka',
#      'school_class': '1b'},
#     {'teacher': 'Leonardo DiCaprio',
#      'subject': 'Fizyka',
#      'school_class': '1b'},
#     {'teacher': 'Leonardo DiCaprio',
#      'subject': 'Fizyka',
#      'school_class': '1b'},
#     {'teacher': 'Leonardo DiCaprio',
#      'subject': 'Fizyka',
#      'school_class': '1b'},
# ]
# teach_avail = []
