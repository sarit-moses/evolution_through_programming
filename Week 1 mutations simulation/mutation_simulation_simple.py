###############
### Authors ###
###############

# Sarit Moses 211772900
# Itamar

###############
### Imports ###
###############

import random
import math
import argparse
from typing import Tuple, List
import matplotlib.pyplot as plt
import numpy as np

########################
### Class definition ###
########################

class Bacterium:
    """
    A bacterium in the population
    """

    def __init__(self, rep_time=20, mutation=False, children=None, live_state=True):
        self.rep_time = rep_time
        self.mutation = mutation
        self.children = children # initialize as None
        self.live_state = live_state

    def replicate(self, p: float, mut_mode: str):
        """ replicates the bacterium which will generate two daughter cells and kill the original one """
        if self.live_state: # only replicate if alive
            child1 = Bacterium(mutation = mutate(p, self.mutation, mut_mode))
            child2 = Bacterium(mutation = mutate(p, self.mutation, mut_mode))
            self.children = [child1, child2]
            self.die()

    def mutate_bacterium(self, p: float, mut_mode: str):
        """ mutates bacteria on demand by posing external stress """
        self.mutation = mutate(p, self.mutation, mut_mode)

    def die(self):
        """ changes the live state to False (dead) """
        self.live_state = False


#################
### functions ###
#################

def mutate(p: float, parent_mutation: bool, mut_mode: str) -> bool:
    """ determine if mutation should occur, considering the parent's mutation """
    rand_val: float = random.random()
    if mut_mode == "random":
        if rand_val <= p: 
            return not parent_mutation # flip the mutation state
        else:
            return parent_mutation
    else: # mutations occur on demand
        return parent_mutation
    

def simulation(p: float, t: int, rep_time: int, mut_mode: str) -> Tuple[int, float]:
    """
    Creates one simulation and reports number of live mutated cells at the end.
    Args:
        p = probability of mutation
        t = time passing in simulation
        rep_time = time for a bacterium to replicate
        mut_mode: string, "random" or "on demand"
    """
    initial_bacterium = Bacterium()
    generation_number = math.floor(t / rep_time)

    bacteria_list = [initial_bacterium] #list to hold all bacteria

    for gen in range(generation_number): #simulate each generation
        new_bacteria = [] #list to hold new bacteria
        for bacterium in bacteria_list:
            if bacterium.live_state:
                bacterium.replicate(p, mut_mode)
                if bacterium.children:
                    new_bacteria.extend(bacterium.children)
        bacteria_list.extend(new_bacteria)
        bacteria_list = [b for b in bacteria_list if b.live_state] #remove dead bacteria

    if mut_mode == "on demand":
        for b in bacteria_list:
            b.mutate_bacterium(p=p, mut_mode="random") # mutate all living cells at end of exponential growth.
    
    # Count mutations
    mutation_count = sum(1 for b in bacteria_list if b.mutation)
    total_bacteria = len(bacteria_list)
    mutation_percentage = mutation_count / total_bacteria

    return (mutation_count, mutation_percentage)

###########
### run ###
# #########    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bacterial simulation.")
    parser.add_argument("-p", type=float, default=0.1, help="Probability of mutation.")
    parser.add_argument("-t", type=int, default=200, help="Length of experiment (minutes).")
    parser.add_argument("-r", "--rep_time", type=int, default=20, help="Length of generation (minutes).")
    parser.add_argument("-n", "--num_simulations", type=int, default=100, help="Number of simulations to perform.")
    parser.add_argument("-m", "--mut_mode", type=str, default="random", choices=["random", "on demand"], help="Mutation node: 'random' or 'on demand'.")

    args = parser.parse_args()

    results: List[Tuple[int, float]] = []
    for _ in range(args.num_simulations):
        result = simulation(args.p, args.t, args.rep_time, args.mut_mode)
        results.append(result)

    # Print results
    print("Simulation Results:")

    mutation_counts = [mc for mc, _ in results]

    # Calculate mean and variance
    mean_mutation_count = np.mean(mutation_counts)
    variance_mutation_count = np.var(mutation_counts)

    print(f"\nMean Mutated Bacteria: {mean_mutation_count:.2f}")
    print(f"Variance Mutated Bacteria: {variance_mutation_count:.2f}")

    # Plot histogram
    plt.hist(mutation_counts, bins='auto')
    plt.title("Histogram of Mutated Bacteria Counts")
    plt.xlabel("Number of Mutated Bacteria")
    plt.ylabel("Frequency")
    plt.show()

