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
from enum import Enum

from select import select
import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-x))


class Dead(Enum):
    DEAD = 0
    ALIVE = 1

class Clade:
    def __init__(self, parent_fitness =1):
        noise = np.random.normal(loc=0, scale=0.01)
        self.fitness = parent_fitness + noise

    def draw_clade(self):
        return Clade(self.fitness)


class World:

    def __init__(self, prey_number, predator_number, grass_amount):
        self.grass = grass_amount
        prey_clade = Clade()
        prey_list = [Prey(prey_clade, self) for _ in range(prey_number)]
        self.prey_list = sorted(prey_list, key=lambda prey: prey.fitness, reverse=True)

        predator_clade = Clade()
        self.predator_list = [Predator(predator_clade, self) for _ in range(predator_number)]

    def simulate_prey_grazing(self):
        for prey in self.prey_list:
            if self.grass > 0:
                prey.eat(self)

    def simulate_predator_hunt(self):
        for predator in self.predator_list:
            for prey in self.prey_list:
                predator.try_hunt(prey)
                if predator.eaten:
                    break

    def simulate_day(self):
        self.grass += 500
        self.simulate_prey_grazing()
        self.simulate_predator_hunt()
        for prey in self.prey_list:
            prey_day = prey.day()
            if prey_day[1]:
                self.prey_list.append(prey_day[1])
        for predator in self.predator_list:
            predator_day = predator.day()
            if predator_day[1]:
                self.predator_list.append(predator_day[1])

    def simulate_days(self, days=10):
        for day in range(days):
            print(f"Day {day}: {len(self.prey_list)} prey, {len(self.predator_list)} predators, {self.grass} grass")
            self.simulate_day()



class Organism:
    total_population = 1
    reproduction_constant = 1

    def __init__(self, fitness, energy, world):
        self.clade = Clade(parent_fitness= 1)
        self.energy = energy
        self.fitness = fitness
        self.world = world
        self.eaten = False
        self.energy_consumption = 1
        type(self).total_population += 1

    def reproduce(self):
        return type(self)(self.clade.draw_clade(), self.world)

    def day(self):
        self.energy -= self.energy_consumption
        offspring = None
        if self.energy <= 0:
            self.die()
            return Dead.DEAD.value, offspring

        x = np.random.rand()
        if x > type(self).reproduction_constant and self.eaten:
            offspring = self.reproduce()
        self.eaten = False
        return Dead.ALIVE.value, offspring

    def eat(self, prey_subject):
        self.energy += 5
        prey_subject.die()
        self.eaten = True

class Predator(Organism):
    """
    A predator in the population
    """
    reproduction_constant = 0.8

    total_population = 0
    def __init__(self, clade: Clade, world):
        self.clade = clade
        fitness = self.clade.fitness
        super().__init__(fitness = fitness, energy= 5, world = world)
        self.energy_consumption = 3

    def try_hunt(self, prey_subject):
        x = np.random.rand()

        p = sigmoid(prey_subject.fitness - self.fitness)/50
        if p>x:
            self.eat(prey_subject)
        # self.energy -=1


    def die(self):
        type(self).total_population -= 1
        self.world.predator_list.remove(self)

class Prey(Organism):
    """
    A prey in the population
    """
    reproduction_constant = 0.8

    def __init__(self, clade: Clade, world):
        self.clade = clade
        fitness = self.clade.fitness
        super().__init__(fitness = fitness, energy= 5, world = world)
        self.eaten = False

    def eat(self, world):
        self.eaten = True
        world.grass -= 1
        self.energy += 1

    def die(self):
        type(self).total_population -= 1
        self.world.prey_list.remove(self)

world = World(prey_number=500, predator_number=5, grass_amount=10000)
world.simulate_days(days=100)

# class Bacterium:
#     """
#     A bacterium in the population
#     """
#
#     def __init__(self, rep_time=20, mutation=False, children=None, live_state=True):
#         self.rep_time = rep_time
#         self.mutation = mutation
#         self.children = children # initialize as None
#         self.live_state = live_state
#
#     def replicate(self, p: float, mut_mode: str):
#         """ replicates the bacterium which will generate two daughter cells and kill the original one """
#         if self.live_state: # only replicate if alive
#             child1 = Bacterium(mutation = mutate(p, self.mutation, mut_mode))
#             child2 = Bacterium(mutation = mutate(p, self.mutation, mut_mode))
#             self.children = [child1, child2]
#             self.die()
#
#     def mutate_bacterium(self, p: float, mut_mode: str):
#         """ mutates bacteria on demand by posing external stress """
#         self.mutation = mutate(p, self.mutation, mut_mode)
#
#     def die(self):
#         """ changes the live state to False (dead) """
#         self.live_state = False
#
#
# #################
# ### functions ###
# #################
#
# def mutate(p: float, parent_mutation: bool, mut_mode: str) -> bool:
#     """ determine if mutation should occur, considering the parent's mutation """
#     rand_val: float = random.random()
#     if mut_mode == "random":
#         if rand_val <= p:
#             return not parent_mutation # flip the mutation state
#         else:
#             return parent_mutation
#     else: # mutations occur on demand
#         return parent_mutation
#
#
# def simulation(p: float, t: int, rep_time: int, mut_mode: str) -> Tuple[int, float]:
#     """
#     Creates one simulation and reports number of live mutated cells at the end.
#     Args:
#         p = probability of mutation
#         t = time passing in simulation
#         rep_time = time for a bacterium to replicate
#         mut_mode: string, "random" or "on demand"
#     """
#     initial_bacterium = Bacterium()
#     generation_number = math.floor(t / rep_time)
#
#     bacteria_list = [initial_bacterium] #list to hold all bacteria
#
#     for gen in range(generation_number): #simulate each generation
#         new_bacteria = [] #list to hold new bacteria
#         for bacterium in bacteria_list:
#             if bacterium.live_state:
#                 bacterium.replicate(p, mut_mode)
#                 if bacterium.children:
#                     new_bacteria.extend(bacterium.children)
#         bacteria_list.extend(new_bacteria)
#         bacteria_list = [b for b in bacteria_list if b.live_state] #remove dead bacteria
#
#     if mut_mode == "on demand":
#         for b in bacteria_list:
#             b.mutate_bacterium(p=p, mut_mode="random") # mutate all living cells at end of exponential growth.
#
#     # Count mutations
#     mutation_count = sum(1 for b in bacteria_list if b.mutation)
#     total_bacteria = len(bacteria_list)
#     mutation_percentage = mutation_count / total_bacteria
#
#     return (mutation_count, mutation_percentage)
#
# ###########
# ### run ###
# # #########
#
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Bacterial simulation.")
#     parser.add_argument("-p", type=float, default=0.1, help="Probability of mutation.")
#     parser.add_argument("-t", type=int, default=200, help="Length of experiment (minutes).")
#     parser.add_argument("-r", "--rep_time", type=int, default=20, help="Length of generation (minutes).")
#     parser.add_argument("-n", "--num_simulations", type=int, default=100, help="Number of simulations to perform.")
#     parser.add_argument("-m", "--mut_mode", type=str, default="random", choices=["random", "on demand"], help="Mutation node: 'random' or 'on demand'.")
#
#     args = parser.parse_args()
#
#     results: List[Tuple[int, float]] = []
#     for _ in range(args.num_simulations):
#         result = simulation(args.p, args.t, args.rep_time, args.mut_mode)
#         results.append(result)
#
#     # Print results
#     print("Simulation Results:")
#
#     mutation_counts = [mc for mc, _ in results]
#
#     # Calculate mean and variance
#     mean_mutation_count = np.mean(mutation_counts)
#     variance_mutation_count = np.var(mutation_counts)
#
#     print(f"\nMean Mutated Bacteria: {mean_mutation_count:.2f}")
#     print(f"Variance Mutated Bacteria: {variance_mutation_count:.2f}")
#
#     # Plot histogram
#     plt.hist(mutation_counts, bins='auto')
#     plt.title("Histogram of Mutated Bacteria Counts")
#     plt.xlabel("Number of Mutated Bacteria")
#     plt.ylabel("Frequency")
#     plt.show()

