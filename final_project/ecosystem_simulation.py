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
import matplotlib.patches as mpatches

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
    return 1 / (1 + np.exp((-x + shift)* con))


###############################################################################
# ENUMS AND CONSTANTS
###############################################################################

class LifeStatus(Enum):
    """Represents the life status of an organism."""
    DEAD = 0
    ALIVE = 1

class Season(Enum):
    WINTER = 0
    SPRING = 1
    SUMMER = 2
    AUTUMN = 3

# Season color mapping for beautiful visualizations
SEASON_COLORS = {
    Season.WINTER: '#E6F3FF',  # Light blue
    Season.SPRING: '#E8F5E8',  # Light green
    Season.SUMMER: '#FFF8DC',  # Light yellow
    Season.AUTUMN: '#FFE4B5'   # Light orange
}

SEASON_NAMES = {
    Season.WINTER: 'Winter',
    Season.SPRING: 'Spring',
    Season.SUMMER: 'Summer',
    Season.AUTUMN: 'Autumn'
}


###############################################################################
# EVOLUTIONARY CLASSES
###############################################################################

# class Clade:
#     """
#     Represents a genetic lineage with fitness and mutation rate.
#
#     Attributes:
#         mutation_rate: Rate at which mutations occur
#         fitness: Current fitness level of this clade
#     """
#
#     def __init__(self, mutation_rate: float, parent_fitness: float = 1,
#                  initial: bool = False):
#         """
#         Initialize a new clade.
#
#         Args:
#             mutation_rate: Base mutation rate
#             parent_fitness: Fitness of the parent clade
#             initial: Whether this is an initial clade (no mutations)
#         """
#         # Add noise to mutation rate
#         mutation_rate_noise = np.random.normal(loc=0, scale=0.05)
#         self.mutation_rate = max(0, mutation_rate + mutation_rate_noise)
#
#         # Add fitness mutation if not initial
#         fitness_noise = 0
#         if not initial:
#             fitness_noise = np.random.normal(loc=0, scale=self.mutation_rate)
#         self.fitness = parent_fitness + fitness_noise
#
#     def draw_clade(self) -> 'Clade':
#         """Create a new clade descended from this one."""
#         return Clade(self.mutation_rate, self.fitness)


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

    def __init__(self, fitness: float, mutation_rate: float, world: 'World'):
        """
        Initialize an organism.

        Args:
            fitness: Initial fitness value
            world: Reference to the world this organism lives in
        """
        self.age = 1
        self.energy = 5
        self.fitness = max(0.0 , fitness)
        self.mutation_rate = mutation_rate
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
            self.fitness + np.random.normal(loc=0, scale=0.1), max(0, self.mutation_rate + np.random.normal(0, 0.01)),
            world=self.world
        )

    def day(self) -> Tuple[int, Optional['Organism']]:
        """
        Simulate one day for this organism.

        Returns:
            Tuple of (life status, potential offspring)
        """
        self.age +=1
        self.energy -= self.energy_consumption
        offspring = None

        # Check death condition
        if self.energy <= 0:
            self.die()
            return LifeStatus.DEAD.value, offspring

        # Check reproduction
        x = np.random.rand()
        if self.age > 3 and x > type(self).reproduction_constant:
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

    def __init__(self, fitness, mutation_rate, world: 'World'):
        """Initialize a predator with given clade and world."""
        # self.clade = clade
        super().__init__(fitness=fitness, mutation_rate= mutation_rate, world=world)
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
        # if Predator.total_population > 10:
        type(self).total_population -= 1
        self.world.predator_list.remove(self)


class Prey(Organism):
    """
    A prey organism that grazes on grass.

    Class Attributes:
        reproduction_constant: Prey-specific reproduction rate
    """

    reproduction_constant = 0.8

    def __init__(self, fitness, mutation_rate, world: 'World'):
        """Initialize a prey with given clade and world."""

        super().__init__(fitness=fitness, mutation_rate= mutation_rate, world=world)
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
        # if Prey.total_population > 10:
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
    season_length = 125
    GRASS_PER_SEASON = {Season.WINTER: 150, Season.SPRING: 300, Season.SUMMER: 250, Season.AUTUMN: 200}

    def __init__(self, prey_number: int, predator_number: int,
                 grass_amount: int, seasonal=False):
        """
        Initialize the world with organisms and resources.

        Args:
            prey_number: Initial number of prey
            predator_number: Initial number of predators
            grass_amount: Initial amount of grass
            seasonal: Whether to enable seasonal effects
        """
        if seasonal == True:
            self.season = Season.SPRING
            self.season_counter = 0
            self.seasonal = True
        else:
            self.season = None
            self.season_counter = None
            self.seasonal = False

        self.grass = grass_amount

        # Initialize prey population
        # prey_clade = Clade(mutation_rate=0.1, initial=True)
        prey_list = [Prey(1, 0.1, self) for _ in range(prey_number)]
        self.prey_list = sorted(prey_list, key=lambda prey: prey.fitness)

        # Initialize predator population
        # predator_clade = Clade(mutation_rate=0.1, initial=True)
        self.predator_list = [
            Predator(1, 0.1, self) for _ in range(predator_number)
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
        if self.seasonal:
            self.season_counter = ((self.season_counter + 1) % World.season_length)
            if self.season_counter == 0:
                self.season = Season((self.season.value + 1) % 4)
            self.grass += World.GRASS_PER_SEASON[self.season]
        else:
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

def setup_beautiful_plot(figsize=(12, 8)):
    """Setup a beautiful plot with modern styling."""
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=figsize)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#333333')
    ax.spines['bottom'].set_color('#333333')
    return fig, ax


def add_seasonal_backgrounds(ax, days_list, seasons_list):
    """Add seasonal background colors to a plot."""
    if not seasons_list:
        return

    current_season = seasons_list[0]
    season_start = 0

    for i, season in enumerate(seasons_list + [None]):  # Add None to trigger final block
        if season != current_season or i == len(seasons_list):
            # Add background for the previous season
            if i > season_start:
                ax.axvspan(days_list[season_start],
                           days_list[i - 1] if i < len(days_list) else days_list[-1],
                           color=SEASON_COLORS[current_season],
                           alpha=0.3,
                           zorder=0)

            if i < len(seasons_list):
                current_season = season
                season_start = i


def population_size_figure(days_list: List[int], pred_pop_list: List[int],
                           prey_pop_list: List[int], seasons_list: List[Season] = None):
    """Create a beautiful population size plot with seasonal backgrounds."""
    fig, ax = setup_beautiful_plot()

    # Add seasonal backgrounds
    if seasons_list:
        add_seasonal_backgrounds(ax, days_list, seasons_list)

    # Plot population lines with beautiful styling
    ax.plot(days_list, prey_pop_list, label="Prey Population",
            color="#2E8B57", linewidth=2.5, alpha=0.8)
    ax.plot(days_list, pred_pop_list, label="Predator Population",
            color="#DC143C", linewidth=2.5, alpha=0.8)

    ax.set_xlabel("Day", fontsize=14, fontweight='bold')
    ax.set_ylabel("Population Size", fontsize=14, fontweight='bold')
    ax.set_title("Predator-Prey Population Dynamics", fontsize=16, fontweight='bold', pad=20)

    # Beautiful legend
    legend = ax.legend(fontsize=12, frameon=True, fancybox=True, shadow=True)
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_alpha(0.9)

    # Add season legend if applicable
    if seasons_list:
        season_patches = [mpatches.Patch(color=SEASON_COLORS[season], alpha=0.3,
                                         label=SEASON_NAMES[season])
                          for season in Season]
        season_legend = ax.legend(handles=season_patches, loc='upper left',
                                  bbox_to_anchor=(0.02, 0.98), fontsize=10,
                                  title="Seasons", title_fontsize=11)
        ax.add_artist(legend)  # Keep the main legend

    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    filename = "seasonal_population_size_fig.png" if seasons_list else "population_size_fig.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    # plt.show()


def prey_fitness_figure(avg_prey_fitness_list: List[float],
                        avg_prey_fitness_no_pred_list: List[float],
                        days_list: List[int], seasons_list: List[Season] = None):
    """Create a beautiful prey fitness comparison plot."""
    fig, ax = setup_beautiful_plot()

    # Add seasonal backgrounds
    if seasons_list:
        add_seasonal_backgrounds(ax, days_list, seasons_list)

    # Plot fitness lines
    ax.plot(days_list, avg_prey_fitness_list, color="#4169E1",
            label="With Predators", linewidth=2.5, alpha=0.8)
    ax.plot(days_list, avg_prey_fitness_no_pred_list, color="#FF8C00",
            label="Without Predators", linewidth=2.5, alpha=0.8)

    ax.set_xlabel("Day", fontsize=14, fontweight='bold')
    ax.set_ylabel("Average Prey Fitness", fontsize=14, fontweight='bold')
    ax.set_title("Evolutionary Pressure: Prey Fitness Over Time",
                 fontsize=16, fontweight='bold', pad=20)

    # Beautiful legend
    legend = ax.legend(fontsize=12, frameon=True, fancybox=True, shadow=True)
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_alpha(0.9)

    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    filename = "seasonal_fitness_fig.png" if seasons_list else "fitness_fig.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    # plt.show()


def predator_fitness_figure(avg_pred_fitness_list: List[float],
                            days_list: List[int], seasons_list: List[Season] = None):
    """Create a beautiful predator fitness plot."""
    fig, ax = setup_beautiful_plot()

    # Add seasonal backgrounds
    if seasons_list:
        add_seasonal_backgrounds(ax, days_list, seasons_list)

    # Plot predator fitness
    ax.plot(days_list, avg_pred_fitness_list, label="Predator Average Fitness",
            color="#8B0000", linewidth=2.5, alpha=0.8)

    ax.set_xlabel("Day", fontsize=14, fontweight='bold')
    ax.set_ylabel("Average Predator Fitness", fontsize=14, fontweight='bold')
    ax.set_title("Predator Evolution: Fitness Over Time",
                 fontsize=16, fontweight='bold', pad=20)

    # Beautiful legend
    legend = ax.legend(fontsize=12, frameon=True, fancybox=True, shadow=True)
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_alpha(0.9)

    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    filename = "seasonal_predator_fitness_fig.png" if seasons_list else "predator_fitness_fig.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    # plt.show()


def grass_availability_figure(grass_list: List[int], days_list: List[int],
                              seasons_list: List[Season] = None):
    """Create a beautiful grass availability plot."""
    fig, ax = setup_beautiful_plot()

    # Add seasonal backgrounds
    if seasons_list:
        add_seasonal_backgrounds(ax, days_list, seasons_list)

    # Plot grass availability
    ax.plot(days_list, grass_list, label="Grass Availability",
            color="#228B22", linewidth=2.5, alpha=0.8)

    ax.set_xlabel("Day", fontsize=14, fontweight='bold')
    ax.set_ylabel("Grass Amount", fontsize=14, fontweight='bold')
    ax.set_title("Seasonal Resource Availability",
                 fontsize=16, fontweight='bold', pad=20)

    # Beautiful legend
    legend = ax.legend(fontsize=12, frameon=True, fancybox=True, shadow=True)
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_alpha(0.9)

    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig("seasonal_grass_fig.png", dpi=300, bbox_inches='tight')
    # plt.show()


def mutation_rate_figure(prey_mutation_rate: List[float], predator_mutation_rate: List[float],
                         days_list: List[int] = None, seasons_list: List[Season] = None):
    """Create a beautiful mutation rate evolution plot."""
    fig, ax = setup_beautiful_plot()

    # Create days list if not provided
    if days_list is None:
        days_list = list(range(len(prey_mutation_rate)))

    # Add seasonal backgrounds
    if seasons_list:
        add_seasonal_backgrounds(ax, days_list, seasons_list)

    # Plot prey mutation rate
    ax.plot(days_list, prey_mutation_rate, label="Prey Mutation Rate",
            color="#4169E1", linewidth=2.5, alpha=0.8)

    # Plot predator mutation rate
    ax.plot(days_list, predator_mutation_rate, label="Predator Mutation Rate",
            color="#DC143C", linewidth=2.5, alpha=0.8)

    ax.set_xlabel("Day", fontsize=14, fontweight='bold')
    ax.set_ylabel("Average Mutation Rate", fontsize=14, fontweight='bold')
    ax.set_title("Evolution of Mutation Rates Over Time",
                 fontsize=16, fontweight='bold', pad=20)

    # Beautiful legend
    legend = ax.legend(fontsize=12, frameon=True, fancybox=True, shadow=True)
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_alpha(0.9)

    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    filename = "seasonal_mutation_rate_fig.png" if seasons_list else "mutation_rate_fig.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    # plt.show()


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
        self.grass_list = []
        self.seasons_list = []

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
        self.grass_list.append(world.grass)

        # Track seasons if applicable
        if world.seasonal:
            self.seasons_list.append(world.season)

        # Track prey statistics
        if len(world.prey_list) > 0:
            self.avg_prey_fitness_list.append(
                np.mean([prey.fitness for prey in world.prey_list])
            )
            self.avg_prey_mutrate_list.append(np.mean([prey.mutation_rate for prey in world.prey_list]))
        else:
            self.avg_prey_fitness_list.append(np.nan)
            self.avg_prey_mutrate_list.append(np.nan)

        # Track predator statistics
        if len(world.predator_list) > 0:
            self.avg_pred_fitness_list.append(
                np.mean([pred.fitness for pred in world.predator_list])
            )
            self.avg_pred_mutrate_list.append(np.mean([pred.mutation_rate for pred in world.predator_list]))
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

    def run_simulation_with_added_predators(self, world: World) -> None:
        """
        Run the simulation for the specified number of days, then add predators
        and run for another period of the same length.

        Args:
            world: World to simulate
        """
        print("Running initial simulation phase...")
        # First phase: run normal simulation
        for day in range(self.days):
            self.track_day(day, world)
            world.simulate_day()

        print(f"Adding 50 new predators after {self.days} days...")
        # Add predators using the last recorded average fitness and mutation rate
        if self.avg_pred_fitness_list and not np.isnan(self.avg_pred_fitness_list[-1]):
            avg_fitness = self.avg_pred_fitness_list[-1]
        else:
            avg_fitness = 1.0  # Default fitness if no predators existed

        if self.avg_pred_mutrate_list and not np.isnan(self.avg_pred_mutrate_list[-1]):
            avg_mutation_rate = self.avg_pred_mutrate_list[-1]
        else:
            avg_mutation_rate = 0.1  # Default mutation rate

        added_predators = [Predator(avg_fitness*2, avg_mutation_rate, world) for _ in range(50)]
        world.predator_list.extend(added_predators)
        Predator.total_population = len(world.predator_list)

        print("Running second simulation phase with added predators...")
        # Second phase: run another 1000 days with the added predators
        for day in range(self.days, self.days * 2):
            self.track_day(day, world)
            world.simulate_day()


    def run_control_simulation(self, prey_number: int = 300,
                               grass_amount: int = 300, seasonal: bool = False) -> List[float]:
        """
        Run control simulation without predators.

        Args:
            prey_number: Initial number of prey
            grass_amount: Initial amount of grass
            seasonal: Whether to enable seasonal effects

        Returns:
            List of average prey fitness values
        """
        world_no_pred = World(
            prey_number=prey_number,
            predator_number=0,
            grass_amount=grass_amount,
            seasonal=seasonal
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

    def plot_extended_population_figure(self, predator_addition_day: int = None):
        """
        Create population plot showing the effect of adding predators.

        Args:
            predator_addition_day: Day when predators were added (for vertical line)
        """
        fig, ax = plt.subplots(figsize=(12, 8))

        # Plot populations
        ax.plot(self.days_list, self.prey_pop_list, 'g-', label='Prey Population', linewidth=2)
        ax.plot(self.days_list, self.pred_pop_list, 'r-', label='Predator Population', linewidth=2)

        # Add vertical line at predator addition point
        if predator_addition_day:
            ax.axvline(x=predator_addition_day, color='black', linestyle='--',
                       label=f'Predators Added (Day {predator_addition_day})')

        ax.set_xlabel('Days', fontsize=12)
        ax.set_ylabel('Population Size', fontsize=12)
        ax.set_title('Population Dynamics: Before and After Adding Predators', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        filename = "predator_predator_adition_fig"
        plt.savefig(filename, dpi=300, bbox_inches='tight')

    def analyze_results(self):
        """Analyze and print correlation statistics."""
        rho, pval = spearmanr(self.avg_prey_fitness_list, self.prey_pop_list)
        print(f"Spearman correlation (avg prey fitness vs prey population): "
              f"rho={rho:.3f}, p={pval:.3g}")


    def plot_all_figures(self, avg_prey_fitness_no_pred_list: List[float], seasonal: bool = False):
        """
        Create all visualization plots.

        Args:
            avg_prey_fitness_no_pred_list: Control simulation fitness data
            seasonal: Whether seasonal effects are enabled
        """
        seasons = self.seasons_list if seasonal else None

        population_size_figure(self.days_list, self.pred_pop_list,
                               self.prey_pop_list, seasons)
        prey_fitness_figure(self.avg_prey_fitness_list,
                            avg_prey_fitness_no_pred_list, self.days_list, seasons)
        predator_fitness_figure(self.avg_pred_fitness_list, self.days_list, seasons)
        mutation_rate_figure(self.avg_prey_mutrate_list, self.avg_pred_mutrate_list, self.days_list, seasons)

        if seasonal:
            grass_availability_figure(self.grass_list, self.days_list, seasons)


###############################################################################
# MAIN FUNCTION
###############################################################################

def main():
    """Main entry point for the simulation."""
    # Initialize simulation runner for extended simulation (2000 days total)
    runner = SimulationRunner(days=1000)

    print("=== Running Extended Simulation with Added Predators ===")
    # Create world with initial populations
    world = World(prey_number=300, predator_number=10, grass_amount=300, seasonal=False)

    # Run extended simulation
    print("Running simulation with predator addition...")
    runner.run_simulation_with_added_predators(world)

    # Create visualization
    runner.plot_extended_population_figure(predator_addition_day=1000)

    # Also create a control simulation for comparison
    print("Running control simulation without added predators...")
    control_runner = SimulationRunner(days=2000)  # Run for same total time
    control_world = World(prey_number=300, predator_number=10, grass_amount=300, seasonal=False)
    control_runner.run_simulation(control_world)

    print(f"Simulation completed. Total days simulated: {len(runner.days_list)}")
    print(f"Final prey population (with added predators): {runner.prey_pop_list[-1]}")
    print(f"Final predator population (with added predators): {runner.pred_pop_list[-1]}")
    print(f"Final prey population (control): {control_runner.prey_pop_list[-1]}")
    print(f"Final predator population (control): {control_runner.pred_pop_list[-1]}")


if __name__ == "__main__":
    main()