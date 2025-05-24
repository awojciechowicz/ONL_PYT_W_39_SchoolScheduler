from deap import creator, base, tools, algorithms
import random



creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

def evalSchedule(individual):
    new_individual = []
    for i in range(len(individual)):
        if i == 4:
            new_individual.append(4 * individual[i])
        else:
            new_individual.append(individual[i])
    print(individual, ": ", sum(new_individual))
    return (sum(new_individual),)

toolbox = base.Toolbox()
toolbox.register("attr_bool", random.randint, 0, 9)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, 10)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
toolbox.register("evaluate", evalSchedule)
toolbox.register("select", tools.selTournament, tournsize=10)

population = toolbox.population(n=60)
print(population)
algorithms.eaSimple(population, toolbox, cxpb=0.5, mutpb=0.2, ngen=10)
best_individual = tools.selBest(population, k=1)[0]
print(best_individual)