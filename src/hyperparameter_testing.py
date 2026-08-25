
# Imports
import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from schedule_ga import nhl_schedule_ga


# ========================================HYPERPARAMETERS========================================
# Default hyperparameters
DEFAULT_HYPERPARAMETERS = {
    'POPULATION_SIZE': 50,
    'GENERATIONS': 300,
    'STAGNANT_GENERATIONS': 1000,
    'TOURNAMENT_SIZE': 2,
    'CROSSOVER_RATE': 0.50,
    'MUTATION_RATE': 0.20,
    'ELITISM': True
}

# The testing hyperparameters and their values to test
TEST_HYPERPARAMETERS = {
    'TOURNAMENT_SIZE':[2, 3, 4, 5],
    'CROSSOVER_RATE': [0.40, 0.50, 0.60, 0.70],
    'MUTATION_RATE': [0.10, 0.20, 0.30, 0.40],
    'ELITISM': [True, False]
}

# Number of runs per hyperparameter value
STATISTICAL_RUNS = 50


# ========================================HELPER FUNCTIONS========================================
def run_multiple(hyperparameters: dict, n_runs: int = STATISTICAL_RUNS):
    """
    Run the NHL schedule GA multiple times and get each run's best fitness values.

    :param hyperparameters: a dictionary containing the values of the hyperparameters for the GA
    :param n_runs: an integer of the number of times to run the GA
    :return results: a list of the best fitness values from each run
    """
    results = []
    # Run the GA n times
    for i in range(n_runs):
        print(f'Run {i+1}/{n_runs}')
        # Get the best fitness value of the run and add it to the list
        best_fitness, _ = nhl_schedule_ga(hyperparameters, update_frequency=0, hyperparameter_testing=True)
        results.append(best_fitness)
    return results


# ========================================RUN THE HYPERPARAMETER TEST========================================
if __name__ == '__main__':
    os.makedirs('results_hyperparameters', exist_ok=True)

    all_results = {}

    # Run a test for each test hyperparameter
    for test_hyperparameter in TEST_HYPERPARAMETERS:
        # Test each value for the test hyperparameter
        values = TEST_HYPERPARAMETERS[test_hyperparameter]
        for value in values:
            print(f'\n====================Testing {test_hyperparameter} = {value}====================')
            # Copy the defaults so testing one hyperparameter doesn't permanently change the baseline for the others
            hyperparameters = DEFAULT_HYPERPARAMETERS.copy()
            hyperparameters[test_hyperparameter] = value

            results = run_multiple(hyperparameters, STATISTICAL_RUNS)
            all_results[value] = results


        # ========================================DISTRIBUTION PLOTTING========================================
        plt.figure()

        # Get the minimum and maximum values for the x axis
        x_min = float('inf')
        x_max = float('-inf')
        for result_list in all_results.values():
            current_min = min(result_list)
            current_max = max(result_list)

            if current_min < x_min:
                x_min = current_min
            if current_max > x_max:
                x_max = current_max

        x_values = np.linspace(x_min, x_max, 500)

        # Plot the gaussian KDE for each hyperparameter value
        for value, results in all_results.items():
            kde = stats.gaussian_kde(results)
            plt.plot(x_values, kde(x_values), label=f'{test_hyperparameter} = {value}')

        plt.title(f'Comparison of Best Fitness Distributions')
        plt.xlabel('Best Fitness')
        plt.ylabel('Density')
        plt.legend()
        plt.savefig(f'results_hyperparameters/{test_hyperparameter.lower()}_distribution.png')
        plt.close()

        # Clear results for the next hyperparameter test
        all_results.clear()
