"""
Predator-Prey Evolution Simulation
Authors: Sarit Moses (211772900), Itamar Nini (207047150)

A simulation of predator-prey dynamics with evolutionary fitness and mutation rates.
"""

###############################################################################
# IMPORTS
###############################################################################

import random
import math
import argparse
import bisect
from typing import Tuple, List, Optional
from enum import Enum

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr


###############################################################################
# UTILITY FUNCTIONS
###############################################################################

def sigmoid(x: float, shift: float = 0, con: float = 1) -> float:
    """
    Sigmoid activation function.

    Args:
        x: Input value
        shift: Horizontal shift of the sigmoid
        con: Controls the steepness of the curve

    Returns:
        Sigmoid transformed value between 0 and 1
    """
    return 1 / (1 + np.exp(-x + shift))


###############################################################################
# ENUMS AND CONSTANTS
###############################################################################

class LifeStatus(Enum):
    """Represents the life status of an organism."""
    DEAD = 0
    ALIVE = 1


###############################################################################
# EVOLUTIONARY CLASSES
###############################################################################

class Clade:
    """
    Represents a genetic lineage with fitness and mutation rate.

    Attributes:
        mutation_rate: Rate at which mutations occur
        fitness: Current fitness level of this clade
    """

    def __init__(self, mutation_rate: float, parent_fitness: float = 1,
                 initial: bool = False):
        """
        Initialize a new clade.

        Args:
            mutation_rate: Base mutation rate
            parent_fitness: Fitness of the parent clade
            initial: Whether this is an initial clade (no mutations)
        """
        # Add noise to mutation rate
        mutation_rate_noise = np.random.normal(loc=0, scale=0.05)
        self.mutation_rate = max(0, mutation_rate + mutation_rate_noise)

        # Add fitness mutation if not initial
        fitness_noise = 0
        if not initial:
            fitness_noise = np.random.normal(loc=0, scale=self.mutation_rate)
        self.fitness = parent_fitness + fitness_noise

    def draw_clade(self) -> 'Clade':
        """Create a new clade descended from this one."""
        return Clade(self.mutation_rate, self.fitness)


###############################################################################
# ORGANISM CLASSES
###############################################################################

class Organism:
    """
    Base class for all organisms in the simulation.

    Class Attributes:
        total_population: Total number of organisms of this type
        reproduction_constant: Base reproduction probability modifier
    """

    total_population = 1
    reproduction_constant = 1

    def __init__(self, fitness: float, world: 'World'):
        """
        Initialize an organism.

        Args:
            fitness: Initial fitness value
            world: Reference to the world this organism lives in
        """
        self.clade = Clade(mutation_rate=0, parent_fitness=1)
        self.energy = 5
        self.fitness = fitness
        self.world = world
        self.eaten = 0
        self.energy_consumption = 1
        type(self).total_population += 1

    def __lt__(self, other: 'Organism') -> bool:
        """Compare organisms by fitness for sorting."""
        return self.fitness < other.fitness

    def reproduce(self) -> 'Organism':
        """Create offspring from this organism."""
        return type(self)(
            Clade(self.clade.mutation_rate, self.clade.fitness),
            world=self.world
        )

    def day(self) -> Tuple[int, Optional['Organism']]:
        """
        Simulate one day for this organism.

        Returns:
            Tuple of (life status, potential offspring)
        """
        self.energy -= self.energy_consumption
        offspring = None

        # Check death condition
        if self.energy <= 0 and type(self).total_population > 10:
            self.die()
            return LifeStatus.DEAD.value, offspring

        # Check reproduction
        x = np.random.rand()
        if x > 2 * (type(self).reproduction_constant / (self.eaten + 1)):
            offspring = self.reproduce()

        self.eaten = False
        return LifeStatus.ALIVE.value, offspring

    def die(self):
        """Handle organism death. To be implemented by subclasses."""
        raise NotImplementedError


class Predator(Organism):
    """
    A predator organism that hunts prey.

    Class Attributes:
        reproduction_constant: Predator-specific reproduction rate
        total_population: Total number of predators
    """

    reproduction_constant = 0.8
    total_population = 0

    def __init__(self, clade: Clade, world: 'World'):
        """Initialize a predator with given clade and world."""
        self.clade = clade
        fitness = self.clade.fitness
        super().__init__(fitness=fitness, world=world)
        self.energy_consumption = 3

    def eat(self, prey_subject: 'Prey'):
        """
        Eat a prey organism.

        Args:
            prey_subject: The prey to consume
        """
        self.energy += 5 * self.fitness
        prey_subject.die()
        self.eaten += 1

    def die(self):
        """Remove predator from world if population is sufficient."""
        if Predator.total_population > 10:
            type(self).total_population -= 1
            self.world.predator_list.remove(self)


class Prey(Organism):
    """
    A prey organism that grazes on grass.

    Class Attributes:
        reproduction_constant: Prey-specific reproduction rate
    """

    reproduction_constant = 0.8

    def __init__(self, clade: Clade, world: 'World'):
        """Initialize a prey with given clade and world."""
        self.clade = clade
        fitness = self.clade.fitness
        super().__init__(fitness=fitness, world=world)
        self.eaten = 0

    def eat(self, world: 'World'):
        """
        Eat grass from the world.

        Args:
            world: The world to graze in
        """
        self.eaten += 1
        world.grass -= 1
        self.energy += 1

    def die(self):
        """Remove prey from world if population is sufficient."""
        if Prey.total_population > 10:
            type(self).total_population -= 1
            self.world.prey_list.remove(self)


###############################################################################
# WORLD SIMULATION
###############################################################################

class World:
    """
    The simulation world containing prey, predators, and resources.

    Class Attributes:
        area: Total area of the world (affects encounter rates)
    """

    area = 100 ** 2

    def __init__(self, prey_number: int, predator_number: int,
                 grass_amount: int):
        """
        Initialize the world with organisms and resources.

        Args:
            prey_number: Initial number of prey
            predator_number: Initial number of predators
            grass_amount: Initial amount of grass
        """
        self.grass = grass_amount

        # Initialize prey population
        prey_clade = Clade(mutation_rate=0.1, initial=True)
        prey_list = [Prey(prey_clade, self) for _ in range(prey_number)]
        self.prey_list = sorted(prey_list, key=lambda prey: prey.fitness)

        # Initialize predator population
        predator_clade = Clade(mutation_rate=0.1, initial=True)
        self.predator_list = [
            Predator(predator_clade, self) for _ in range(predator_number)
        ]

    def simulate_prey_grazing(self):
        """Simulate all prey attempting to graze."""
        for prey in random.sample(self.prey_list, len(self.prey_list)):
            if self.grass > 0:
                prey.eat(self)

    def simulate_predator_hunt(self):
        """Simulate all predators hunting prey."""
        for predator in random.sample(self.predator_list,
                                      len(self.predator_list)):
            for prey in self.prey_list:
                win = np.random.rand()

                # Calculate encounter and success probabilities
                chance_to_meet = sigmoid(
                    Prey.total_population * predator.fitness /World.area *
                    predator.eaten,
                    shift=1
                )
                chance_to_win = sigmoid(
                    (predator.fitness - prey.fitness),
                ) / 50

                if win < chance_to_meet * chance_to_win:
                    predator.eat(prey)

    def simulate_day(self):
        """Simulate one complete day in the world."""
        # Morning: prey graze
        self.simulate_prey_grazing()

        # Grass regrowth
        self.grass += 300

        # Afternoon: predators hunt
        self.simulate_predator_hunt()

        # Evening: organism daily processes (energy loss, reproduction)
        # Process prey
        for prey in self.prey_list:
            prey_day = prey.day()
            if prey_day[1]:  # If offspring was produced
                bisect.insort(self.prey_list, prey_day[1])

        # Process predators
        for predator in self.predator_list:
            predator_day = predator.day()
            if predator_day[1]:  # If offspring was produced
                self.predator_list.append(predator_day[1])


###############################################################################
# VISUALIZATION FUNCTIONS
###############################################################################

def population_size_figure(days_list: List[int], pred_pop_list: List[int],
                           prey_pop_list: List[int]):
    """Create population size plot."""
    plt.figure(figsize=(10, 6))
    plt.plot(days_list, prey_pop_list, label="Prey Population", color="green")
    plt.plot(days_list, pred_pop_list, label="Predator Population", color="red")
    plt.xlabel("Day")
    plt.ylabel("Population Size")
    plt.title("Prey vs Predator Population Over Time")
    plt.legend()
    plt.xticks(range(0, 1001, 50))
    plt.grid(True)
    plt.show()


def prey_fitness_figure(avg_prey_fitness_list: List[float],
                        avg_prey_fitness_no_pred_list: List[float],
                        days_list: List[int]):
    """Create prey fitness comparison plot."""
    plt.figure(figsize=(10, 6))
    plt.plot(days_list, avg_prey_fitness_list, color="blue",
             label="With Predators")
    plt.plot(days_list, avg_prey_fitness_no_pred_list, color="orange",
             label="Without Predators")
    plt.xlabel("Day")
    plt.ylabel("Average Prey Fitness")
    plt.title("Average Prey Fitness Over Time")
    plt.legend()
    plt.xticks(range(0, 1001, 50))
    plt.grid(True)
    plt.show()


def predator_fitness_figure(avg_pred_fitness_list: List[float],
                            days_list: List[int]):
    """Create predator fitness plot."""
    plt.figure(figsize=(10, 6))
    plt.plot(days_list, avg_pred_fitness_list, label="Predator Avg Fitness")
    plt.xlabel("Day")
    plt.ylabel("Average Predator Fitness")
    plt.title("Average Predator Fitness Over Time")
    plt.legend()
    plt.xticks(range(0, 1001, 50))
    plt.grid(True)
    plt.show()


def mutation_rate_figure(avg_pred_mutrate_list: List[float],
                         avg_prey_mutrate_list: List[float],
                         days_list: List[int]):
    """Create mutation rate comparison plot."""
    plt.figure(figsize=(10, 6))
    plt.plot(days_list, avg_prey_mutrate_list, label="Prey Avg Mutation Rate")
    plt.plot(days_list, avg_pred_mutrate_list,
             label="Predator Avg Mutation Rate")
    plt.xlabel("Day")
    plt.ylabel("Average Mutation Rate (std of fitness noise)")
    plt.title("Average Mutation Rate Over Time")
    plt.legend()
    plt.xticks(range(0, 1001, 50))
    plt.grid(True)
    plt.show()


###############################################################################
# SIMULATION RUNNER
###############################################################################

class SimulationRunner:
    """Handles running and tracking simulation data."""

    def __init__(self, days: int = 1000):
        """
        Initialize simulation runner.

        Args:
            days: Number of days to simulate
        """
        self.days = days
        self.reset_tracking()

    def reset_tracking(self):
        """Reset all tracking lists."""
        self.days_list = []
        self.prey_pop_list = []
        self.pred_pop_list = []
        self.avg_prey_fitness_list = []
        self.avg_pred_fitness_list = []
        self.avg_prey_mutrate_list = []
        self.avg_pred_mutrate_list = []

    def track_day(self, day: int, world: World):
        """
        Track statistics for a single day.

        Args:
            day: Current day number
            world: World to track statistics from
        """
        self.days_list.append(day)
        self.prey_pop_list.append(len(world.prey_list))
        self.pred_pop_list.append(len(world.predator_list))

        # Track prey statistics
        if len(world.prey_list) > 0:
            self.avg_prey_fitness_list.append(
                np.mean([prey.fitness for prey in world.prey_list])
            )
            self.avg_prey_mutrate_list.append(
                np.mean([prey.clade.mutation_rate for prey in world.prey_list])
            )
        else:
            self.avg_prey_fitness_list.append(np.nan)
            self.avg_prey_mutrate_list.append(np.nan)

        # Track predator statistics
        if len(world.predator_list) > 0:
            self.avg_pred_fitness_list.append(
                np.mean([pred.fitness for pred in world.predator_list])
            )
            self.avg_pred_mutrate_list.append(
                np.mean([pred.clade.mutation_rate for pred in world.predator_list])
            )
        else:
            self.avg_pred_fitness_list.append(np.nan)
            self.avg_pred_mutrate_list.append(np.nan)

    def run_simulation(self, world: World) -> None:
        """
        Run the simulation for the specified number of days.

        Args:
            world: World to simulate
        """
        for day in range(self.days):
            self.track_day(day, world)
            world.simulate_day()

    def run_control_simulation(self, prey_number: int = 300,
                               grass_amount: int = 300) -> List[float]:
        """
        Run control simulation without predators.

        Args:
            prey_number: Initial number of prey
            grass_amount: Initial amount of grass

        Returns:
            List of average prey fitness values
        """
        world_no_pred = World(
            prey_number=prey_number,
            predator_number=0,
            grass_amount=grass_amount
        )

        avg_prey_fitness_no_pred_list = []
        for day in range(self.days):
            if len(world_no_pred.prey_list) > 0:
                avg_prey_fitness_no_pred_list.append(
                    np.mean([prey.fitness for prey in world_no_pred.prey_list])
                )
            else:
                avg_prey_fitness_no_pred_list.append(np.nan)
            world_no_pred.simulate_day()

        return avg_prey_fitness_no_pred_list

    def analyze_results(self):
        """Analyze and print correlation statistics."""
        rho, pval = spearmanr(self.avg_prey_fitness_list, self.prey_pop_list)
        print(f"Spearman correlation (avg prey fitness vs prey population): "
              f"rho={rho:.3f}, p={pval:.3g}")

    def plot_all_figures(self, avg_prey_fitness_no_pred_list: List[float]):
        """
        Create all visualization plots.

        Args:
            avg_prey_fitness_no_pred_list: Control simulation fitness data
        """
        population_size_figure(self.days_list, self.pred_pop_list,
                               self.prey_pop_list)
        prey_fitness_figure(self.avg_prey_fitness_list,
                            avg_prey_fitness_no_pred_list, self.days_list)
        predator_fitness_figure(self.avg_pred_fitness_list, self.days_list)
        mutation_rate_figure(self.avg_pred_mutrate_list,
                             self.avg_prey_mutrate_list, self.days_list)


###############################################################################
# MAIN FUNCTION
###############################################################################

def main():
    """Main entry point for the simulation."""
    # Initialize simulation runner
    runner = SimulationRunner(days=1000)

    # Create world with initial populations
    world = World(prey_number=300, predator_number=10, grass_amount=300)

    # Run main simulation
    print("Running main simulation with predators...")
    runner.run_simulation(world)

    # Run control simulation without predators
    print("Running control simulation without predators...")
    avg_prey_fitness_no_pred = runner.run_control_simulation()

    # Analyze results
    runner.analyze_results()

    # Create visualizations
    print("Generating plots...")
    runner.plot_all_figures(avg_prey_fitness_no_pred)

    print("Simulation complete!")


if __name__ == '__main__':
    main()