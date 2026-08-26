
# Imports
import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from concurrent.futures import ProcessPoolExecutor, as_completed
from schedule_ga import nhl_schedule_ga
from constants import DEFAULT_HYPERPARAMETERS, TEST_HYPERPARAMETERS, STATISTICAL_RUNS


# ========================================HELPER FUNCTIONS========================================
def run_multiple(hyperparameters: dict, n_runs: int = STATISTICAL_RUNS):
    """
    Run the NHL schedule GA multiple times in parallel and get each run's best fitness values.
    Since each run is completely independent of the others, they're distributed across worker processes instead of run one after another.

    :param hyperparameters: a dictionary containing the values of the hyperparameters for the GA
    :param n_runs: an integer of the number of times to run the GA
    :return results: a list of the best fitness values from each run
    """

    # Number of GA runs to execute in parallel (defaults to all available CPU cores)
    max_workers = os.cpu_count()

    results = []
    # Run the GA n times, distributed across worker processes
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(nhl_schedule_ga, hyperparameters, 0, True) for _ in range(n_runs)]

        # Collect results as each run finishes (not necessarily in the order they were submitted)
        for i, future in enumerate(as_completed(futures)):
            best_fitness, _ = future.result()
            print(f'Run {i+1}/{n_runs} complete')
            results.append(best_fitness)

    return results


# ========================================RUN THE HYPERPARAMETER TEST========================================
if __name__ == '__main__':
    os.makedirs('hyperparameters_results', exist_ok=True)

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
        plt.savefig(f'hyperparameters_results/{test_hyperparameter.lower()}_distribution.png')
        plt.close()

        # Clear results for the next hyperparameter test
        all_results.clear()
