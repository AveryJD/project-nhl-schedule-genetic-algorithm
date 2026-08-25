
# Imports
import json
import os
import random
import time
import utils


# ====================HYPERPARAMETERS====================
HYPERPARAMETERS = {
    'POPULATION_SIZE': 500, # Must be even (due to crossover)
    'GENERATIONS': 10_000,
    'STAGNANT_GENERATIONS': 1_000,

    'TOURNAMENT_SIZE': 5,
    'CROSSOVER_RATE': 0.40,
    'MUTATION_RATE': 0.20,
    'ELITISM': True,
}

# The frequency of generations to print progress updates
UPDATE_FREQUENCY = 100


# ====================THE GENETIC ALGORITHM====================
def nhl_schedule_ga(hyperparameters: dict = HYPERPARAMETERS, update_frequency: int = UPDATE_FREQUENCY, hyperparameter_testing: bool = False):
    """
    A genetic algorithm to create an optimal NHL schedule.
    The chromosome representation is a list of lists of integers, where each inner list represents a day in the season and the integers represent the game IDs scheduled for that day.
    The fitness function is a multi-objective function that aims to optimize rest/game day balance, home/away balance, and minimal travel distance.
    The genetic algorithm uses tournament selection, order crossover, several mutations, and elitism, and terminates when one of two termination criteria are met.

    :param hyperparameters: a dictionary of hyperparameter values to use in the genetic algorithm
    :param update_frequency: an integer indicating at what interval of generations to print an update statement
    :param hyperparameter_testing: a boolean indicating if hyperparameters are being tested (do not save results if so)
    :return best_fitness: a float of the best fitness found
    :return best_schedule: a list of list of ints representing the best schedule found
    """
    # GA start time (to track runtime)
    start_time = time.time()

    # ====================UNPACK HYPERPARAMETERS====================
    population_size = hyperparameters['POPULATION_SIZE']
    generations = hyperparameters['GENERATIONS']
    stagnant_generations = hyperparameters['STAGNANT_GENERATIONS']

    tournament_size = hyperparameters['TOURNAMENT_SIZE']
    crossover_rate = hyperparameters['CROSSOVER_RATE']
    mutation_rate = hyperparameters['MUTATION_RATE']
    elitism = hyperparameters['ELITISM']


    # ====================INITIALIZATION====================
    # Make distance matrix of all possible NHL travel
    distance_matrix = utils.make_distance_matrix()

    # Create the first population
    population = []
    for _ in range(population_size):
        schedule_chromosome = utils.generate_initial_schedule()
        population.append(schedule_chromosome)


    # ====================FIRST FITNESS EVALUATION====================
    # First population's fitness and best schedule
    population_fitnesses = utils.evaluate_population(population, distance_matrix)
    best_fitness = min(population_fitnesses)
    best_idx = population_fitnesses.index(best_fitness)
    best_schedule = population[best_idx]
    _, team_fitnesses = utils.total_schedule_fitness(best_schedule, distance_matrix)

    previous_best_fitness = float('inf')


    # ====================INITIALIZE BOOKKEEPING====================
    # Track best fitness, generation, and stagnation
    generation = 0
    stagnant_generation = 0
    first_stagnation_generation = 0

    generation_best_fitnesses = [best_fitness]
    generation_average_fitnesses = [sum(population_fitnesses)/len(population_fitnesses)]

    global_best_fitness = best_fitness
    global_best_schedule = best_schedule


    # ====================GENETIC ALGORITHM LOOP====================
    while generation < generations and stagnant_generation < stagnant_generations:

        # ====================STAGNATION CHECK====================
        # Check if the fitness value has improved
        if best_fitness < previous_best_fitness:
            previous_best_fitness = best_fitness
            # If the fitness has improved, set the stagnant generation counter back to 0 and keep track of the generation of last improvement
            stagnant_generation = 0
            first_stagnation_generation = generation
        # If the fitness has not improved, increment the stagnant generation counter
        else:
            stagnant_generation += 1

        # Keep the normal crossover and mutation rates if the fitness is improving
        current_crossover_rate = crossover_rate
        current_mutation_rate = mutation_rate
        no_day_inversion = False
        # If the fitness has not improved in a while, decrease the crossover rate, increase the mutation rate, and remove day inversion mutations
        if stagnant_generation / stagnant_generations >= 0.90:
            current_crossover_rate = current_crossover_rate / 2
            current_mutation_rate = min(1.00, current_mutation_rate * 1.5)
            no_day_inversion = True


        # ====================TOURNAMENT SELECTION====================
        # Create the mating pool with tournament selection
        mating_pool = utils.tournament_selection(population, population_fitnesses, tournament_size)


        # ====================CROSSOVER====================
        # Apply order crossover on pairs of chromosomes in the mating pool
        for i in range(0, population_size, 2):
            if random.random() < current_crossover_rate:
                parent_one, parent_two = mating_pool[i], mating_pool[i+1]
                mating_pool[i] = utils.apply_order_crossover(parent_one, parent_two)
                mating_pool[i+1] = utils.apply_order_crossover(parent_two, parent_one)


        # ====================MUTATION===================
        # Apply mutation to chromosomes in the mating pool
        for i in range(population_size):
            if random.random() < current_mutation_rate:
                mating_pool[i] = utils.apply_mutation(mating_pool[i], no_day_inversion)


        # ====================ELITISM====================
        # Apply elitism if the hyperparameter is set to true and update the mating pool to the next population
        if elitism:
            mating_pool_fitnesses = utils.evaluate_population(mating_pool, distance_matrix)
            population = utils.apply_elitism(mating_pool, mating_pool_fitnesses, global_best_schedule)
        else:
            population = mating_pool


        # ====================FITNESS EVALUATION====================
        # Evaluate each chromosome's fitness in the population
        population_fitnesses = utils.evaluate_population(population, distance_matrix)

        current_best_fitness = min(population_fitnesses)
        current_best_idx = population_fitnesses.index(current_best_fitness)
        current_best_schedule = population[current_best_idx]
        _, team_fitnesses = utils.total_schedule_fitness(current_best_schedule, distance_matrix)

        if current_best_fitness < global_best_fitness:
            global_best_fitness = current_best_fitness
            global_best_schedule = current_best_schedule


        # ====================BOOK KEEPING====================
        best_schedule = global_best_schedule
        best_fitness = global_best_fitness

        generation_best_fitnesses.append(global_best_fitness)
        generation_average_fitnesses.append(sum(population_fitnesses)/len(population_fitnesses))

        generation += 1


        # ====================PRINT GENERATION PROGRESS====================
        if update_frequency != 0:
            if generation % update_frequency == 0 or generation == 1:
                # Calculate current runtime
                elapsed = time.time() - start_time
                print(f'Generation: {generation}\nBest fitness = {best_fitness:.2f}\nRuntime = {elapsed:.2f}s\n')


    # ====================END EVALUATION====================
    # Calculate total runtime
    total_runtime = time.time() - start_time

    # Ending print statement
    print(f'Stopping after {generation} generations'
          f'\nBest fitness: {best_fitness:.2f}, found at generation {first_stagnation_generation}'
          f'\nTotal runtime = {total_runtime:.2f}s ({(total_runtime/60):.2f}m)\n')

    # Only save results if not testing hyperparameters
    if not hyperparameter_testing:
        os.makedirs('genetic_algorithm_results', exist_ok=True)

        # Save the best_schedule to a JSON file
        with open('genetic_algorithm_results/best_schedule.json', 'w') as f:
            json.dump(best_schedule, f, indent=2)

        # Save the fitness values to a JSON file
        results = {
            'total_runtime': total_runtime,
            'best_fitness': best_fitness,
            'generation_best_fitnesses': generation_best_fitnesses,
            'generation_average_fitnesses': generation_average_fitnesses
        }
        with open('genetic_algorithm_results/fitness_results.json', 'w') as f:
            json.dump(results, f, indent=2)

        # Save each team's fitness values from the best schedule to a JSON file
        sorted_team_fitnesses = sorted(team_fitnesses.items(), key=lambda item: item[1])
        sorted_team_fitnesses_dict = dict(sorted_team_fitnesses)
        with open('genetic_algorithm_results/team_fitnesses.json', 'w') as f:
            json.dump(sorted_team_fitnesses_dict, f, indent=2)

    return best_fitness, best_schedule


# ====================RUN THE GENETIC ALGORITHM====================
if __name__ == '__main__':
    best_fitness, best_schedule = nhl_schedule_ga(HYPERPARAMETERS)
