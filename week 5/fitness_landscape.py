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
    f = average_fitness(population)
    new_population = copy.deepcopy(population) # deepcopy to make sure I do not change the values while iterating on them
    for seq, values in population.items():
        # current frequency, multiplied by current fitness minus the average fitness
        a = values[0] * (values[1] - f) 
        
        # chance of other species to mutate into this seq
        b = 0 
        for s, val in population.items():
            if s == seq:
                continue # do not calculate for same sequence
            d = get_distance(seq, s) # get edit distance between the two sequences
            bij = (q**d) * (1-q)**(len(seq)-d)
            b += bij * val[1]
        
        # chance of this species to turn into other species (by mutations)
        c = values[0] * (1 - (1-q)**len(seq))

        print(f"a={a}, b={b}, c={c}")

        new_population[seq][0] += (a + b - c) # assign new value to frequency of this quasispecies
        # print("new frewuency")
        # print(new_population[seq][0])
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
        f += values[0] * values[1] # multiply fitness of sequence by its relative frequency
        print(f"single species: {values[0] * values[1]}")
      #  print(f)
    
    return f


def init_population(L: int) -> Dict[str, List[float]]:
    """
    receives length of sequence. 
    generates all possible sequences of this length, and assigns 100% frequency to only one of them and a fitness to all of them.
    the 1st value of the list is the frequency and the 2nd one is the fitness. 
    """
    sequences = []
    population = dict()
    for i in range(2**L):
        binary_string = bin(i)[2:].zfill(L)  # Convert to binary, remove "0b", pad with zeros
        sequences.append(binary_string)

    for seq in sequences:
        population[seq] = [0.0, generate_fitness(seq)]

    founder_seq = random.choice(sequences)
    population[founder_seq][0] = 1.0 # assign the entire population to be a single random sequence out of the possibilities.        

    return population


def generate_fitness(sequence: str) -> float:
    """
    Assigns fitness to a sequence, based on sequence properties but with some redomness. 
    """
    num_ones = sequence.count('1')
    sequence_length = len(sequence)
    base_fitness = num_ones / sequence_length  # Calculate proportion of '1's
    noise = random.uniform(-0.1, 0.1)  # Add a small amount of random noise
    fitness = (base_fitness + noise) * 2  # Scale to range between 0 and 2

    # Ensure fitness stays within the bounds [0, 2]
    fitness = max(0, min(fitness, 2))
    return fitness


###########
### Run ###
###########

if __name__ == "__main__":

    # get arguments from command line
    parser = argparse.ArgumentParser(description="Run a simple population genetics simulation.")
    parser.add_argument("-N", "--population_size", type=int, required=False, default=100,
                        help="Population size (positive integer)")
    parser.add_argument("-L", "--sequence_length", type=int, required=False, default=10,
                        help="Length of the sequence (positive integer)")
    parser.add_argument("-q", "--mutation_rate", type=float, required=False, default=0.05,
                        help="Mutation rate (float between 0 and 1)")
    parser.add_argument("-t", "--generations", type=int, required=False, default=100,
                        help="Number of generations (positive integer)")
    args = parser.parse_args()

    # create initial population
    population = init_population(args.sequence_length)
    avg_fitness = [average_fitness(population)] # initiate list with average fitness at t=0

    # run simulation fot stated number of generations
    for generation in range(args.generations):
        population = change_quasispecies(population, args.mutation_rate)
        f = average_fitness(population)
        print(f)
        avg_fitness.append(f)

    print(args.generations)

    # plot the average fitness of the quasispecies over time
    plt.plot(range(args.generations + 1), avg_fitness)
    plt.xlabel("Generation")
    plt.ylabel("Average Fitness")
    plt.title(f"Average Population Fitness Over Time for mutation rate = {args.mutation_rate} and sequence length = {args.sequence_length}")
    plt.show() #show the plot

