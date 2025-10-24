
# Imports
import utils
import json
import random
import math



games_json = open('schedule_info/nhl_all_games.json')
ALL_GAMES = json.load(games_json)

locations_json = open('schedule_info/arena_locations.json')
ARENA_LOCATIONS = json.load(locations_json)

# ==================== HYPERPARAMETERS ====================
HYPERPARAMETERS = {
    'POPULATION_SIZE': 200,     # Must be even
    'GENERATIONS': 100000,
    'STAGNANT_GENERATIONS': 1000,

    'TOURNAMENT_SIZE': 2,
    'CROSSOVER_RATE': 0.50,
    'MUTATION_RATE': 0.30,
    'ELITISM': True,
}


def nhl_schedule_ga(games=ALL_GAMES, arena_locations=ARENA_LOCATIONS, hyperparameters=HYPERPARAMETERS):
    """
    
    """

    # Make distance matrix of all possible NHL travel
    distance_matrix = utils.make_distance_matrix(arena_locations)

    # ==================== UNPACK HYPERPARAMETERS ====================
    population_size = hyperparameters['POPULATION_SIZE']
    generations = hyperparameters['GENERATIONS']
    stagnant_generations = hyperparameters['STAGNANT_GENERATIONS']

    tournament_size = hyperparameters['TOURNAMENT_SIZE']
    crossover_rate = hyperparameters['CROSSOVER_RATE']
    mutation_rate = hyperparameters['MUTATION_RATE']
    elitism = hyperparameters['ELITISM']


    # ==================== INITIALIZATION ====================
    # Create the first population
    population = []
    for _ in range(population_size):
        schedule_chromosome = utils.generate_initial_schedule(games)
        population.append(schedule_chromosome)

    # First population's fitness and best schedule
    population_fitnesses = utils.evaluate_population(population, ALL_GAMES, ARENA_LOCATIONS, distance_matrix)
    best_fitness = min(population_fitnesses)
    best_idx = population_fitnesses.index(best_fitness)
    best_schedule = population[best_idx]

    previous_best_fitness = math.inf

    # ====================INITIALIZE BOOKKEEPING====================
    # Track best fitness, generation, and stagnation
    generation = 0
    stagnant_generation = 0
    first_stagnation_generation = 0

    generation_best_fitnesses = [best_fitness]
    generation_average_fitnesses = [sum(population_fitnesses)/len(population_fitnesses)]

    global_best_fitness = best_fitness
    global_best_schedule = best_schedule


    # The genetic algorithm loop
    while generation < generations and stagnant_generation < stagnant_generations:

        # ========================================STAGNATION CHECK========================================
        # Check if the fitness value has improved
        if best_fitness < previous_best_fitness:
            previous_best_fitness = best_fitness
            # If the fitness has improved, set the stagnnt generation counter back to 0 and keep track of the generation
            stagnant_generation = 0
            first_stagnation_generation = generation
        # If the fitness has not improved, increment the stagnnt generation counter
        else:
            stagnant_generation += 1


        # ========================================TOURNAMENT SELECTION========================================
        # Create the mating pool with tournament selection
        mating_pool = utils.tournament_selection(population, population_fitnesses, tournament_size)


        # ========================================ORDER CROSSOVER========================================
        # Perform order crossover on pairs of chromosomes in the mating pool
        for i in range(0, population_size, 2):
            if random.random() < crossover_rate:
                mating_pool[i] = utils.apply_order_crossover(mating_pool[i], mating_pool[i+1])
                mating_pool[i+1] = utils.apply_order_crossover(mating_pool[i+1], mating_pool[i])


        # ========================================MUTATION========================================
        current_mutation_rate = mutation_rate
        if stagnant_generation/stagnant_generations >= 0.90:
            current_mutation_rate = min(1.0, current_mutation_rate * 1.5)

        # If the fitness has not improved in a while, increase the mutation rate and make the mutation more likely to be a swap
        for i in range(population_size):
            mating_pool[i] = utils.apply_mutation(mating_pool[i], ALL_GAMES, current_mutation_rate)


        # ========================================ELITISM========================================
        if elitism:
            mating_pool_fitnesses = utils.evaluate_population(mating_pool, ALL_GAMES, ARENA_LOCATIONS, distance_matrix)
            population = utils.apply_elitism(mating_pool, mating_pool_fitnesses, global_best_schedule)
        else:
            population = mating_pool


        # Increment the generation number
        generation += 1


        # ========================================FITNESS EVALUATION========================================
        # Evaluate each chromosome's fitness in the population
        population_fitnesses = utils.evaluate_population(population, ALL_GAMES, ARENA_LOCATIONS, distance_matrix)

        current_best_fitness = min(population_fitnesses)
        current_best_idx = population_fitnesses.index(current_best_fitness)
        current_best_schedule = population[current_best_idx]

        if current_best_fitness < global_best_fitness:
            global_best_fitness = current_best_fitness
            global_best_schedule = current_best_schedule

        
        # ========================================BOOK KEEPING========================================
        best_schedule = global_best_schedule
        best_fitness = global_best_fitness

        generation_best_fitnesses.append(global_best_fitness)
        generation_average_fitnesses.append(sum(population_fitnesses)/len(population_fitnesses))


    # ========================================END EVALUATION========================================

    # Ending print statement
    print(f'Stopping after {generation} generations\tBest fitness: {best_fitness} found at generation {first_stagnation_generation}')


    # Save the best_schedule to a JSON file
    with open("schedule_info/best_schedule.json", "w") as f:
        json.dump(best_schedule, f, indent=2)

    # Save the fitness values to a JSON file
    results = {
        "best_fitness": best_fitness,
        "generation_best_fitnesses": generation_best_fitnesses,
        "generation_average_fitnesses": generation_average_fitnesses
    }

    with open("schedule_info/ga_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return best_schedule, best_fitness, generation_best_fitnesses, generation_average_fitnesses


best_schedule, best_fitness, generation_best_fitnesses, generation_average_fitnesses = nhl_schedule_ga(ALL_GAMES, ARENA_LOCATIONS, HYPERPARAMETERS)



