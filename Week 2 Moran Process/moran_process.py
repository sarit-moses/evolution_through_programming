###############
### Authors ###
###############

# Sarit Moses 211772900
# Itamar Nini 207047150

###############
### Imports ###
###############
import numpy as np
import random
import matplotlib.pyplot as plt
import pandas as pd
import math
from scipy import stats
#from rope.base.libutils import relative


#################
### Functions ###
#################


def simulation(n, t, reds, s, new_s, mutation_rate, change_s_step):  # simulate single process
    blues = n-reds
    reds_absolute_fitness = 1+s
    blues_absolute_fitness = 1
    population = np.array([1 for red in range(reds)] + [0 for blue in range(blues)])
    red_fraction = [sum(population) / n]
    blue_fraction = [1 - red_fraction[-1]]
    for step in range(t):
        if step == change_s_step:
            reds_absolute_fitness = 1+new_s
        mean_fitness = reds_absolute_fitness*red_fraction[-1] + blues_absolute_fitness*blue_fraction[-1]
        to_change = random.sample(range(n), 1)
        red_relative_fitness = reds_absolute_fitness - mean_fitness
        blue_relative_fitness = blues_absolute_fitness - mean_fitness

        red_probability = red_fraction[-1] *(1+red_relative_fitness)
        blue_probability = blue_fraction[-1] *(1+blue_relative_fitness)

        rand_num = random.random()
        if rand_num <= red_probability:
            child = 1
        else:
            child = 0
        population[to_change[0]] = child  # child replaces dead individual

        if mutation_rate:
            tosses = np.random.rand(n) < mutation_rate
            mutation_indexes = np.where(tosses)[0]
            if mutation_indexes.size > 0:
                population[mutation_indexes] = 1 - population[mutation_indexes]

        red_count = sum(population)
        cur_red_fraction = red_count/n
        cur_blue_fraction = 1- cur_red_fraction
        red_fraction.append(cur_red_fraction)
        blue_fraction.append(cur_blue_fraction)
        if cur_red_fraction == 0 or cur_red_fraction == 1:  # absorbing state
            break

    return red_fraction, red_fraction[-1], step


def main(n, t, s, reds, num_simulations, new_s= None, mutation_rate= None):
    steps_record = []
    reds_record = []
    red_final_fraction = []

    if new_s:
        change_s_step = random.randint(0, t)

    for _ in range(num_simulations):
        red_fraction, final_red_fraction, step = simulation(n, t, reds, s, new_s, mutation_rate, change_s_step = None)
        if final_red_fraction == 0 or final_red_fraction == 1:
            steps_record.append(step)
        reds_record.append(red_fraction)
        red_final_fraction.append(final_red_fraction)
    # plot histogram
    plt.hist(steps_record)
    plt.xlabel("Number of Steps Until Fixation")
    plt.ylabel("Frequency")
    plt.savefig("hist.png")
    plt.show()

    # plot reds fraction
    for run in reds_record:
        plt.plot(run, color='red')
    if new_s:
        plt.axvline(x=change_s_step, color='blue', linestyle='--')
    plt.xlabel("steps")
    plt.ylabel("red fraction")
    plt.ylim(0, 1)
    plt.savefig("reds_fraction.png")
    plt.show()

    avg_time_to_fixation = reds_fixation_probability(steps_record)

    red_fixation_count = fixation_probability_calculator(red_final_fraction)
    
    print(f"Empiric probability of reds to be fixed: {red_fixation_count*100/num_simulations}%")
    
    if s != 0:
        red_theoretical_fixation_probability = theoretical_fixation_probability(n,s)
        print(f"Theoretical probability of reds to be fixed: {red_theoretical_fixation_probability}%")

        # Statistical comparison
        observed = int(red_fixation_count)
        expected = red_theoretical_fixation_probability * num_simulations

        # Perform a binomial test (since each simulation is a Bernoulli trial)
        result = stats.binomtest(observed, num_simulations, red_theoretical_fixation_probability, alternative='two-sided')
        print(f"P-value (Binomial Test) comparing empirical to theoretical fixation probability: {result.pvalue:.4f}")
        
    print(f"Average time to fixation: {avg_time_to_fixation} Steps")


def fixation_probability_calculator(red_final_fraction):
    red_fixation_count = sum(np.floor(red_final_fraction))
    return red_fixation_count


def reds_fixation_probability(steps_record):
    avg_time_to_fixation = np.mean(steps_record)
    return avg_time_to_fixation


def theoretical_fixation_probability(N, s):
    if s == 0:
        return 1/N
    rho=(1-1/(1+s))/(1-1/(1+s)**N)
    return rho


###########
### Run ###
###########


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evolutionary Simulation")

    parser.add_argument("-n", type=int, default=20, help="Population size (N)")
    parser.add_argument("-f", type=int, default=1, help="number of reds")
    parser.add_argument("-s", type=float, default=0.2, help="Selection coefficient (s)")
    parser.add_argument("-t", type=int, default=1000, help="Max number of steps")
    parser.add_argument("-r", "--runs", type=int, default=1000, help="Number of simulation runs")

    parser.add_argument("-s_n", type=float, default=None, help="New Selection coefficient (s)")
    parser.add_argument("-m", type=float, default=None, help="mutation_rate")

    args = parser.parse_args()

    main(args.n, args.t, args.s, args.f, args.runs, args.s_n, args.m)