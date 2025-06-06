###############
### Authors ###
###############

# Sarit Moses 211772900
# Itamar Nini 207047150

###############
### Imports ###
###############

from typing import List, Dict
import argparse
import random
import copy
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


#################
### Functions ###
#################

def change_quasispecies(population: Dict[str, List[float]], q: float):
    """
    Args:
        q = mutation rate
        population = dictionary of sequenes (keys) and their relative fitness and frequencies (values)
    returns:
        population with new frequency values for all sequences, based on the quasispecies equation
    """
    avg_f = average_fitness(population)
    temp_new_population = copy.deepcopy(
        population)  # deepcopy to make sure I do not change the values while iterating on them
    for seq_i, values_i in population.items():
        # current frequency, multiplied by current fitness minus the average fitness
        population_fragment_i = values_i[0]
        fitness_i = values_i[1]

        a = population_fragment_i * (fitness_i - avg_f)

        # chance of other species to mutate into this seq
        b = 0
        for seq_j, values_j in population.items():
            population_fragment_j = values_j[0]
            fitness_j = values_j[1]
            if seq_j == seq_i:
                continue  # do not calculate for same sequence
            d = get_distance(seq_i, seq_j)  # get edit distance between the two sequences
            bij = (q ** d) * (1 - q) ** (len(seq_i) - d)
            b += bij * population_fragment_j

        # chance of this species to turn into other species (by mutations)
        c = population_fragment_i * (1 - (1 - q) ** len(seq_i))

        temp_new_population[seq_i][0] += (a + b - c)  # assign new value to frequency of this quasispecies

    new_population = temp_new_population
    return new_population


def get_distance(seq1, seq2):
    """
    Args: two sequences of the same lengths
    Returns: the edit distance between them
    """
    d = 0
    for i in range(len(seq1)):
        if seq1[i] != seq2[i]:
            d += 1
    return d


def average_fitness(population: Dict[str, List[float]]) -> float:
    """
    receives population
    calculates and returns the average fitness of the population
    """
    f = 0.0
    for _, values in population.items():
        f += values[0] * values[1]  # multiply fitness of sequence by its relative frequency

    return f


def init_population(L: int, N: int) -> Dict[str, List[float]]:
    """
    receives length of sequence.
    generates all possible sequences of this length, and assigns 100% frequency to only one of them and a fitness to all of them.
    the 1st value of the list is the frequency and the 2nd one is the fitness.
    """
    sequences = []
    population = dict()
    for i in range(2 ** L):
        binary_string = bin(i)[2:].zfill(L)  # Convert to binary, remove "0b", pad with zeros
        sequences.append(binary_string)

    for seq in sequences:
        population[seq] = [0.0, generate_fitness(seq)]

    founder_seq = random.choice(sequences)

    population[founder_seq][0] = 1.0  # assign the entire population to be a single random sequence out of the possibilities.

    print(population)

    return population


def generate_fitness(sequence: str) -> float:
    """
    Assigns fitness to a sequence, based on sequence properties but with some redomness.
    """
    fitness = random.uniform(0, 2)
    return fitness


def main():
    # create initial population
    population = init_population(args.sequence_length, args.population_size)
    avg_fitness = [average_fitness(population)]  # initiate list with average fitness at t=0
    # run simulation fot stated number of generations
    population_history = pd.DataFrame(columns=population.keys())
    for generation in range(args.generations):
        f = average_fitness(population)
        avg_fitness.append(f)
        pop_fraction_dist = np.array([v[0] for v in population.values()])
        population_history.loc[generation] = pop_fraction_dist / sum(pop_fraction_dist)
        population = change_quasispecies(population, args.mutation_rate)

    # plot the average fitness of the quasispecies over time
    plt.plot(range(args.generations + 1), avg_fitness)
    plt.xlabel("Generation")
    plt.ylabel("Average Fitness")
    plt.title(
        f"Average Population Fitness Over Time for mutation rate = {args.mutation_rate} and sequence length = {args.sequence_length}")
    plt.show()  # show the plot
    fitnesses = [v[1] for v in population.values()]
    # plot the frequency of the different populations
    for species in population_history:
        plt.plot(population_history[species],
                 label=f"{str(species)} (fitness: {round(population.get(species)[1], 2)})")  # Add label for legend
    plt.xlabel("Generation")
    plt.ylabel("Frequency")
    plt.title("Frequency of Different Populations Over Time")
    plt.legend(title="Population", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()  # Adjust layout so labels/legend don't get cut off
    plt.show()

    fitnesses = [population[key][1] for key in population.keys()]
    print(f"max fitness possible: {max(fitnesses)}")

def main_until_convergence(q, seq_length, max_generations=10000, threshold=1e-4):
    # Initialize population
    population = init_population(seq_length, args.population_size)
    avg_fitness = [average_fitness(population)]  # Store average fitness over time
    population_history = pd.DataFrame(columns=population.keys())

    prev_dist = np.array([v[0] for v in population.values()])
    counter = 0

    while counter < max_generations:
        # Record current distribution
        population_history.loc[counter] = prev_dist

        # Update population
        population = change_quasispecies(population, q)

        # Get new distribution
        new_dist = np.array([v[0] for v in population.values()])
        avg_fitness.append(average_fitness(population))

        # Check for convergence (based on distribution change)
        if np.linalg.norm(new_dist - prev_dist) < threshold:
            break

        prev_dist = new_dist
        counter += 1
    return counter


def convergence_figure():
    lengths = [1, 2, 3, 4, 5]
    counter_history = []
    mutation_rates = np.linspace(0.001, 0.5, 100)
    for l in lengths:
        l_time_to_converge = []
        for mutation_rate in mutation_rates:
            counter_until_convergence = main_until_convergence(mutation_rate, seq_length=l)
            l_time_to_converge.append(counter_until_convergence)
        counter_history.append(l_time_to_converge)
    plt.figure(figsize=(8, 5))
    for i, l_time_to_converge in enumerate(counter_history):
        plt.plot(mutation_rates, l_time_to_converge, label=f"Length {lengths[i]}")
    plt.title("Effect of Mutation Rate on Time to Equilibrium")
    plt.xlabel("Mutation Rate")
    plt.ylabel("Generations Until Convergence")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


###########
### Run ###
###########



if __name__ == "__main__":

    # get arguments from command line
    parser = argparse.ArgumentParser(description="Run a simple population genetics simulation.")
    parser.add_argument("-N", "--population_size", type=int, required=False, default=100,
                        help="Population size (positive integer)")
    parser.add_argument("-L", "--sequence_length", type=int, required=False, default=3,
                        help="Length of the sequence (positive integer)")
    parser.add_argument("-q", "--mutation_rate", type=float, required=False, default=0,
                        help="Mutation rate (float between 0 and 1)")
    parser.add_argument("-t", "--generations", type=int, required=False, default=1000,
                        help="Number of generatons i(positive integer)")
    args = parser.parse_args()


    main()

    # convergence_figure()