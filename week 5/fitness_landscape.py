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

        # print(f"a={a}, b={b}, c={c}")

        temp_new_population[seq_i][0] += (a + b - c)  # assign new value to frequency of this quasispecies
        # print("new frewuency")
        # print(new_population[seq][0])

    # new_population = normalize_new_population(temp_new_population)
    new_population = temp_new_population
    return new_population


# def normalize_new_population(temp_new_population):
#     fitness = np.array([v[1] for v in temp_new_population.values()])
#     freq = np.array([v[0] for v in temp_new_population.values()])
#
#     freq += abs(min(freq))
#     freq /= freq.sum()
#
#     updated_values = [list(x) for x in zip(freq, fitness)]
#     return dict(zip(temp_new_population.keys(), updated_values))

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
        # print(f"single species: {values[0] * values[1]}")
    #  print(f)

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

    # for seq in sequences:
    # population[seq] = [0.0, generate_fitness(seq)]
    # population[seq] = [1/len(sequences), generate_fitness(seq)]
    # founder_seq = random.choice(sequences)
    # population[founder_seq][0] = 1.0 # assign the entire population to be a single random sequence out of the possibilities.

    raw_fitness = {seq: generate_fitness(seq) for seq in sequences}
    total_fitness = sum(raw_fitness.values())

    # Normalize fitness
    population = {
        seq: [0, raw_fitness[seq] / total_fitness]
        for seq in sequences
    }
    founder_seq = random.choice(sequences)
    # founder_seq = '1111'
    population[founder_seq][
        0] = 1.0  # assign the entire population to be a single random sequence out of the possibilities.
    return population


def generate_fitness(sequence: str) -> float:
    """
    Assigns fitness to a sequence, based on sequence properties but with some redomness.
    """
    num_ones = sequence.count('1')
    # sequence_length = len(sequence)
    # base_fitness = num_ones / sequence_length  # Calculate proportion of '1's
    base_fitness = np.log(num_ones*100)
    noise = random.uniform(-0.1, 0.1)  # Add a small amount of random noise
    # noise = num_ones%2
    fitness = (base_fitness + noise) # Scale to range between 0 and 2

    # Ensure fitness stays within the bounds [0, 2]
    fitness = max(0, fitness)
    return fitness


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
    parser.add_argument("-q", "--mutation_rate", type=float, required=False, default=0.001,
                        help="Mutation rate (float between 0 and 1)")
    parser.add_argument("-t", "--generations", type=int, required=False, default=1000,
                        help="Number of generatons i(positive integer)")
    args = parser.parse_args()

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

        # print(sum(pop_fraction_dist))
        # print(f)

    # print(args.generations)

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
                 label=f"{str(species)} (fitness: {round(population.get(species)[1], 2)}")  # Add label for legend

    plt.xlabel("Generation")
    plt.ylabel("Frequency")
    plt.title("Frequency of Different Populations Over Time")
    plt.legend(title="Population")
    plt.show()  # Show the second plot