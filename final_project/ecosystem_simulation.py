"""
Predator-Prey Evolution Simulation with Seasonal Dynamics
Authors: Sarit Moses (211772900), Itamar Nini (207047150)

A simulation of predator-prey dynamics with evolutionary fitness, mutation rates,
and seasonal grass growth patterns.
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
from matplotlib.patches import Rectangle
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


class Season(Enum):
    """Represents the four seasons."""
    SPRING = 0
    SUMMER = 1
    AUTUMN = 2
    WINTER = 3


###############################################################################
# SEASONAL DYNAMICS
###############################################################################

class SeasonalEnvironment:
    """
    Manages seasonal changes in the environment.

    Attributes:
        days_per_season: Number of days in each season
        current_day: Current day of the simulation
        grass_growth_rates: Grass growth rate for each season
    """

    def __init__(self, days_per_season: int = 30):
        """
        Initialize seasonal environment.

        Args:
            days_per_season: Number of days per season
        """
        self.days_per_season = days_per_season
        self.current_day = 0

        # Define grass growth rates for each season
        self.grass_growth_rates = {
            Season.SPRING: 500,  # High growth in spring
            Season.SUMMER: 350,  # Moderate growth in summer
            Season.AUTUMN: 200,  # Declining growth in autumn
            Season.WINTER: 50    # Minimal growth in winter
        }

        # Define grass decay rates (grass dies naturally)
        self.grass_decay_rates = {
            Season.SPRING: 50,
            Season.SUMMER: 100,
            Season.AUTUMN: 150,
            Season.WINTER: 200
        }

    def get_current_season(self) -> Season:
        """Get the current season based on the day."""
        season_index = (self.current_day // self.days_per_season) % 4
        return Season(season_index)

    def get_daily_grass_growth(self) -> int:
        """
        Calculate daily grass growth based on current season.

        Returns:
            Net grass growth for the day
        """
        season = self.get_current_season()
        growth = self.grass_growth_rates[season]
        decay = self.grass_decay_rates[season]

        # Add some daily variation
        growth_variation = np.random.normal(1.0, 0.1)
        actual_growth = int(growth * growth_variation)

        # Net growth can be negative in harsh conditions
        net_growth = actual_growth - decay

        return net_growth

    def advance_day(self):
        """Advance to the next day."""
        self.current_day += 1

    def get_season_name(self) -> str:
        """Get the name of the current season."""
        return self.get_current_season().name.capitalize()

    def get_year_progress(self) -> float:
        """Get progress through the current year (0-1)."""
        days_per_year = self.days_per_season * 4
        return (self.current_day % days_per_year) / days_per_year


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
        # Seasonal effects on energy consumption
        season = self.world.environment.get_current_season()
        seasonal_multiplier = 1.0
        if season == Season.WINTER:
            seasonal_multiplier = 1.5  # Higher energy cost in winter
        elif season == Season.SUMMER:
            seasonal_multiplier = 1.2  # Slightly higher in summer (heat)

        self.energy -= self.energy_consumption * seasonal_multiplier
        offspring = None

        # Check death condition
        if self.energy <= 0 and type(self).total_population > 10:
            self.die()
            return LifeStatus.DEAD.value, offspring

        # Check reproduction (more likely in spring)
        reproduction_modifier = 1.0
        if season == Season.SPRING:
            reproduction_modifier = 0.7  # Lower threshold = more reproduction
        elif season == Season.WINTER:
            reproduction_modifier = 1.3  # Higher threshold = less reproduction

        x = np.random.rand()
        if x > 2 * (type(self).reproduction_constant / (self.eaten + 1)) * reproduction_modifier:
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
        self.environment = SeasonalEnvironment()

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
        # Seasonal effects on hunting success
        for predator in random.sample(self.predator_list,
                                      len(self.predator_list)):
            for prey in self.prey_list:
                win = np.random.rand()

                # Calculate encounter and success probabilities
                chance_to_meet = sigmoid(
                    Prey.total_population * predator.fitness / World.area *
                    predator.eaten,
                    shift=1
                )
                chance_to_win = sigmoid(
                    predator.fitness - prey.fitness,
                    con=5
                ) / 50

                if win < chance_to_meet * chance_to_win:
                    predator.eat(prey)

    def simulate_day(self):
        """Simulate one complete day in the world."""
        # Morning: prey graze
        self.simulate_prey_grazing()

        # Seasonal grass regrowth
        grass_growth = self.environment.get_daily_grass_growth()
        self.grass = max(0, self.grass + grass_growth)  # Grass can't go negative

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

        # Advance to next day
        self.environment.advance_day()


###############################################################################
# VISUALIZATION FUNCTIONS
###############################################################################

def population_size_figure(days_list: List[int], pred_pop_list: List[int],
                           prey_pop_list: List[int], days_per_season: int = 90):
    """Create population size plot with seasonal indicators."""
    fig, ax = plt.subplots(figsize=(14, 8))

    # Plot population lines
    ax.plot(days_list, prey_pop_list, label="Prey Population", color="green", linewidth=2)
    ax.plot(days_list, pred_pop_list, label="Predator Population", color="red", linewidth=2)

    # Add seasonal background colors
    season_colors = {
        0: ('#90EE90', 'Spring'),  # Light green
        1: ('#FFD700', 'Summer'),  # Gold
        2: ('#FF8C00', 'Autumn'),  # Dark orange
        3: ('#87CEEB', 'Winter')   # Sky blue
    }

    max_pop = max(max(prey_pop_list), max(pred_pop_list))

    # Draw seasonal backgrounds
    for day in range(0, max(days_list) + 1, days_per_season):
        season_idx = (day // days_per_season) % 4
        color, name = season_colors[season_idx]

        if day + days_per_season <= max(days_list):
            rect = Rectangle((day, 0), days_per_season, max_pop * 1.1,
                           facecolor=color, alpha=0.2, edgecolor='none')
            ax.add_patch(rect)

    # Add season labels at the bottom
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())

    season_positions = []
    season_labels = []
    for i in range(0, max(days_list), days_per_season):
        season_positions.append(i + days_per_season/2)
        season_idx = (i // days_per_season) % 4
        season_labels.append(season_colors[season_idx][1])

    ax2.set_xticks(season_positions)
    ax2.set_xticklabels(season_labels)
    ax2.xaxis.set_ticks_position('bottom')
    ax2.xaxis.set_label_position('bottom')
    ax2.spines['bottom'].set_position(('outward', 40))

    # Format main plot
    ax.set_xlabel("Day", fontsize=12)
    ax.set_ylabel("Population Size", fontsize=12)
    ax.set_title("Prey vs Predator Population Over Time with Seasonal Dynamics", fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, max_pop * 1.1)

    # Add year markers
    years = max(days_list) // (days_per_season * 4)
    for year in range(1, years + 1):
        year_day = year * days_per_season * 4
        if year_day <= max(days_list):
            ax.axvline(x=year_day, color='black', linestyle='--', alpha=0.3, linewidth=1)
            ax.text(year_day, max_pop * 1.05, f'Year {year}', rotation=90,
                   verticalalignment='bottom', fontsize=9)

    plt.tight_layout()
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
    plt.xticks(range(0, max(days_list) + 1, 50))
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
    plt.xticks(range(0, max(days_list) + 1, 50))
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
    plt.xticks(range(0, max(days_list) + 1, 50))
    plt.grid(True)
    plt.show()


def grass_availability_figure(grass_list: List[int], days_list: List[int],
                              days_per_season: int = 90):
    """Create grass availability plot with seasonal indicators."""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot grass availability
    ax.plot(days_list, grass_list, label="Grass Available", color="darkgreen", linewidth=2)

    # Add seasonal background colors
    season_colors = {
        0: ('#90EE90', 'Spring'),
        1: ('#FFD700', 'Summer'),
        2: ('#FF8C00', 'Autumn'),
        3: ('#87CEEB', 'Winter')
    }

    max_grass = max(grass_list) if grass_list else 1000

    # Draw seasonal backgrounds
    for day in range(0, max(days_list) + 1, days_per_season):
        season_idx = (day // days_per_season) % 4
        color, name = season_colors[season_idx]

        if day + days_per_season <= max(days_list):
            rect = Rectangle((day, 0), days_per_season, max_grass * 1.1,
                           facecolor=color, alpha=0.2, edgecolor='none')
            ax.add_patch(rect)

    ax.set_xlabel("Day", fontsize=12)
    ax.set_ylabel("Grass Availability", fontsize=12)
    ax.set_title("Grass Availability Over Time with Seasonal Growth", fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, max_grass * 1.1)

    plt.tight_layout()
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
        self.grass_list = []
        self.season_list = []

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
        self.season_list.append(world.environment.get_current_season().value)

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

            # Print progress every 100 days
            if day % 100 == 0:
                season = world.environment.get_season_name()
                print(f"Day {day} ({season}): Prey={len(world.prey_list)}, "
                      f"Predators={len(world.predator_list)}, Grass={world.grass}")

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
        # Remove NaN values for correlation
        valid_indices = ~np.isnan(self.avg_prey_fitness_list)
        if np.sum(valid_indices) > 1:
            valid_fitness = np.array(self.avg_prey_fitness_list)[valid_indices]
            valid_population = np.array(self.prey_pop_list)[valid_indices]

            rho, pval = spearmanr(valid_fitness, valid_population)
            print(f"\nSpearman correlation (avg prey fitness vs prey population): "
                  f"rho={rho:.3f}, p={pval:.3g}")

        # Analyze seasonal effects
        print("\nSeasonal Population Statistics:")
        for season in Season:
            season_days = [i for i, s in enumerate(self.season_list) if s == season.value]
            if season_days:
                avg_prey = np.mean([self.prey_pop_list[i] for i in season_days])
                avg_pred = np.mean([self.pred_pop_list[i] for i in season_days])
                avg_grass = np.mean([self.grass_list[i] for i in season_days])
                print(f"{season.name}: Avg Prey={avg_prey:.1f}, "
                      f"Avg Predators={avg_pred:.1f}, Avg Grass={avg_grass:.1f}")

    def plot_all_figures(self, avg_prey_fitness_no_pred_list: List[float]):
        """
        Create all visualization plots.

        Args:
            avg_prey_fitness_no_pred_list: Control simulation fitness data
        """
        population_size_figure(self.days_list, self.pred_pop_list,
                               self.prey_pop_list)
        grass_availability_figure(self.grass_list, self.days_list)
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
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run predator-prey evolution simulation')
    parser.add_argument('--days', type=int, default=720,
                       help='Number of days to simulate (default: 720, ~2 years)')
    parser.add_argument('--prey', type=int, default=300,
                       help='Initial prey population (default: 300)')
    parser.add_argument('--predators', type=int, default=10,
                       help='Initial predator population (default: 10)')
    parser.add_argument('--grass', type=int, default=1000,
                       help='Initial grass amount (default: 1000)')
    args = parser.parse_args()

    # Initialize simulation runner
    runner = SimulationRunner(days=args.days)

    # Create world with initial populations
    world = World(prey_number=args.prey, predator_number=args.predators,
                  grass_amount=args.grass)

    # Run main simulation
    print(f"Running main simulation with predators for {args.days} days...")
    print(f"Initial conditions: {args.prey} prey, {args.predators} predators, {args.grass} grass")
    print("-" * 60)
    runner.run_simulation(world)

    # Run control simulation without predators
    print("\n" + "-" * 60)
    print("Running control simulation without predators...")
    avg_prey_fitness_no_pred = runner.run_control_simulation(
        prey_number=args.prey, grass_amount=args.grass
    )

    # Analyze results
    runner.analyze_results()

    # Create visualizations
    print("\nGenerating plots...")
    runner.plot_all_figures(avg_prey_fitness_no_pred)

    print("\nSimulation complete!")


if __name__ == '__main__':
    main()