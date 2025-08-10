###############
### Authors ###
###############

# Sarit Moses 211772900
# Itamar Nini 207047150

###############
### Imports ###
###############

import random
# import math
# import argparse
from typing import Tuple, List
import matplotlib.pyplot as plt
import numpy as np
from enum import Enum
from select import select
import numpy as np

########################
### Class definition ###
########################

class Dead(Enum):
    DEAD = 0
    ALIVE = 1

class Clade:
    def __init__(self, parent_fitness =1):
        noise = np.random.normal(loc=0, scale=0.01)
        self.fitness = parent_fitness + noise # this is where mutations are induced in the model

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

        # Lists to store population data for plotting
        self.prey_populations = []
        self.predator_populations = []

    def simulate_prey_grazing(self):
        # Create a copy to avoid issues with list modification during iteration
        prey_list_copy = self.prey_list.copy()
        for prey in prey_list_copy:
            if self.grass > 0:
                prey.eat(self)

    def simulate_predator_hunt(self):
        # The hunting logic is now self-contained within try_hunt.
        # Each predator gets one attempt to hunt a single prey per day.
        for predator in self.predator_list:
            for _ in range(n_hunt_attempts_per_preditor):
                predator.try_hunt()
                if predator.eaten:
                    break
        
        # for predator in self.predator_list:
        #     for prey in self.prey_list:
        #         predator.try_hunt(prey)
        #         if predator.eaten:
        #             break

    def simulate_day(self):
        self.grass += 700
        self.simulate_prey_grazing()
        self.simulate_predator_hunt()
        
        # Update prey list, removing dead and adding offspring
        new_prey_list = []
        for prey in self.prey_list:
            status, offspring = prey.day()
            if status == Dead.ALIVE.value:
                new_prey_list.append(prey)
            if offspring:
                new_prey_list.append(offspring)
        self.prey_list = new_prey_list

        # Update predator list, removing dead and adding offspring
        new_predator_list = []
        for predator in self.predator_list:
            status, offspring = predator.day()
            if status == Dead.ALIVE.value:
                new_predator_list.append(predator)
            if offspring:
                new_predator_list.append(offspring)
        self.predator_list = new_predator_list

    def simulate_days(self, days=10):
        for day in range(days):
            print(f"Day {day}: {len(self.prey_list)} prey, {len(self.predator_list)} predators, {self.grass} grass")
            self.simulate_day()
            # Store population counts for plotting
            self.prey_populations.append(len(self.prey_list))
            self.predator_populations.append(len(self.predator_list))


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
        # Reproduction is based on a random number and the organism having eaten
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
        super().__init__(fitness = fitness, energy= 10, world = world)
        self.energy_consumption = 4

    def try_hunt(self):
        x = np.random.rand()
        
        prey_population = len(self.world.prey_list)
        predator_population = len(self.world.predator_list)
        
        if prey_population > 0:
            # Select a random prey to eat
            prey_to_eat = random.choice(self.world.prey_list)
            
            # Hunting success is a combined probability of meeting and winning
            # The chance to meet is scaled by the prey population
            chance_to_meet = min(1.0, prey_population / 100.0)
            chance_to_meet = min(1.0, prey_population / (predator_population * 20.0))
            # The chance to win is based on the fitness difference
            chance_to_win = sigmoid(self.fitness - prey_to_eat.fitness)
            # The total hunting probability
            p = chance_to_meet * chance_to_win
            
            if p > x:
                self.eat(prey_to_eat)





        # x = np.random.rand()
        
        # prey_population = len(self.world.prey_list)
        # predator_population = len(self.world.predator_list)
        
        # if prey_population > 0:
        #     # Simplified hunting probability to be a single event per day per predator
        #     # This probability is dependent on the ratio of prey to predators
        #     p = min(1.0, prey_population / (predator_population * 20.0))
            
        #     if p > x:
        #         # Select a random prey to eat
        #         prey_to_eat = random.choice(self.world.prey_list)
        #         self.eat(prey_to_eat)

    def die(self):
        type(self).total_population -= 1
        # Use try-except to handle cases where an organism is already removed
        try:
            self.world.predator_list.remove(self)
        except ValueError:
            pass

class Prey(Organism):
    """
    A prey in the population
    """
    reproduction_constant = 0.5

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
        # Use try-except to handle cases where an organism is already removed
        try:
            self.world.prey_list.remove(self)
        except ValueError:
            pass


#################
### functions ###
#################

def sigmoid(x):
    return 1 / (1 + np.exp(-x))


###########
### run ###
###########

if __name__ == "__main__":
    world = World(prey_number=500, predator_number=50, grass_amount=10000)
    days_to_simulate = 100
    n_hunt_attempts_per_preditor = 24
    world.simulate_days(days=days_to_simulate)

    # Plotting the results
    plt.plot(range(days_to_simulate), world.prey_populations, label='Prey')
    plt.plot(range(days_to_simulate), world.predator_populations, label='Predator')
    plt.title('Prey and Predator Population Over Time')
    plt.xlabel('Days')
    plt.ylabel('Population')
    plt.legend()
    plt.grid(True)
    plt.show()
