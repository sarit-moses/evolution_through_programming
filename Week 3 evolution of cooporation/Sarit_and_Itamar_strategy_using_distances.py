###############
### Authors ###
###############

# Sarit Moses 211772900
# Itamar Nini 207047150

###################
### Explanation ###
###################

"""
Possible opponent strategies:
  tit-for-tat: starts friendly, will defect after each defection, will cooporate after each cooporation
      best counter-strategy: coopareta as much as possible (will lead to cooperation)
  grim trigger: starts friendly, will cooporate until 1st defection and then will defect until the end
      best counter-strategy: always cooperate, defecting once can be bad. if there is a time limit, can defect on last move.
  always defect: will always defect regardless of oponnent actions
      best counter-strategy: always defect.
  always cooperate: will always cooperate regardless of opponent actions
      best counter-strategy: always defect
  random: unpredictable, will choose randomly
      hard to predict. no best counter-strategy
  tit for two tats: cooperate unless oponnent defects twice in row, than defect.
      best counter-strategy: always cooperate but you can get away with an occasional defection
      I think it might be better to defect and then cooperate repeatedly
  pavlov: cooperates if both oponents used same move in previous step, else defect.
      best counter-strategy: cooperate.

by taking all the above data into account, the most reasonable behavior is probably to lead with two cooperations and then evaluate oponent's response.
normally the best strategy would be tit-for-tat (as a strategy for dealing with most possile oponent's strategies).
this strategy should perform very well agains almost all strategies, with a small loss on 1st round for always defect.
it will probably not have the best outcome agains always cooperate (because against it the best strategy is always defect) but also not the worst outcome.

try to implement - for dealing with a semi-random behavior that has a higher probability to one of the options:
after 10 rounds try to evaluate what is the oponnent's strategy.
if found to be random - always defect (will have highest score).


* fix detect function
* add opponent
* build graphs - our points vs opponent poinst in time

"""

###############
### Imports ###
###############

from typing import List
import numpy as np
from scipy.stats import mannwhitneyu
import random

###########
### Run ###
###########
# if we detected it, opponent is already in 'always_defect' mode
# in case of 1st move in the game:
# start by cooperation. if opponent is tit-for-tat, the next round he will cooperate
# this also applies to 2nd move, since the game in the 1st move will have a random start in any case.

def grim_trigger(flag, opponent_history):
    if opponent_history[-1] == 'defect':
        flag = True
    if flag == True:
        return 'defect'
    else:
        return 'cooperate', flag


def tit_for_tat(my_history, opponent_history):
    if random.random() < 0.03:
        return 'defect'
    else:
        if len(my_history) == 0:
            return "cooperate"
        return opponent_history[-1]


def tit_for_two_tat(my_history, opponent_history):
    if random.random() < 0.03:
        return 'defect'
    else:
        if len(my_history) < 2:
            return "cooperate"
        elif opponent_history[-1] == 'defect' and opponent_history[-2] == 'defect':
            return 'defect'
        return 'cooperate'


def cooperarte():
    if random.random() < 0.03:
        return 'defect'
    else:
        return 'cooperate'


def defect():
    if random.random() < 0.01:
        return 'cooperate'
    return 'defect'


def random_choice(coop_probability, defect_probability):
    return np.random.choice(['cooperate', 'defect'], p=[coop_probability, defect_probability])


def detect_opponents_strategy(my_history, opponent_history):
    always_defect_distance = detect_always_defect(opponent_history)
    always_cooperate_distance = detect_always_cooperate(opponent_history)
    tit_for_tat_distance = detect_tit_for_tat(my_history, opponent_history)
    grim_trigger_distance = detect_grim_trigger(my_history, opponent_history)
    tit_for_two_tat_distance = detect_tit_for_two_tat(my_history, opponent_history)

    distances = {"always_defect": always_defect_distance, "always_cooperate": always_cooperate_distance,
                 "tit_for_tat": tit_for_tat_distance, "grim_trigger": grim_trigger_distance,
                 "tit_for_two_tat": tit_for_two_tat_distance}
    minimal_distance = min(distances.values())
    opponent_strategy_candidates = [k for k, v in distances.items() if v == minimal_distance and v < 0.175]

    opp_strategy = None
    if opponent_strategy_candidates:
        if "always_defect" in opponent_strategy_candidates:
            opp_strategy = "always_defect"
        if "always_cooperate" in opponent_strategy_candidates:
            opp_strategy = "always_cooperate"
        if "grim_trigger" in opponent_strategy_candidates:
            opp_strategy = "grim_trigger"
        if "tit_for_two_tat" in opponent_strategy_candidates:
            opp_strategy = "tit_for_two_tat"
        if "tit_for_tat" in opponent_strategy_candidates:
            opp_strategy = "tit_for_tat"
    else:
        opp_strategy = "random"
    return opp_strategy


def detect_tit_for_two_tat(my_history, opponent_history):
    # no need to expect opp_history[0] as cooperate as 0 will never be in opponents_defect_idx_if_tit_for_tat
    opponent_defect_idx = np.array(
        [1 if move == 'defect' else 0 for move in opponent_history])

    opponents_expected_binary = np.array([0, 0] + [
        1 if my_history[idx] == 'defect' and my_history[idx + 1] == 'defect' else 0
        for idx in range(len(my_history) - 2)
    ])
    distance = np.sum(opponent_defect_idx != opponents_expected_binary) / len(opponents_expected_binary)
    return distance


def detect_tit_for_tat(my_history, opponent_history):
    # no need to expect opp_history[0] as cooperate as 0 will never be in opponents_defect_idx_if_tit_for_tat
    my_defect_idx_without_last = np.array(
        [idx for idx in range(len(my_history) - 1) if my_history[idx] == 'defect'])
    opponent_defect_idx = np.array(
        [idx for idx in range(len(opponent_history)) if opponent_history[idx] == 'defect'])
    opponents_expected = (my_defect_idx_without_last + 1)

    my_defect_idx_without_last_binary = np.zeros(len(my_history), dtype=int)
    if my_defect_idx_without_last != []:
        my_defect_idx_without_last_binary[my_defect_idx_without_last] = 1

    # Create binary vectors for opponent_defect_idx
    opponent_defect_idx_binary = np.zeros(len(opponent_history), dtype=int)
    if opponent_defect_idx != []:
        opponent_defect_idx_binary[opponent_defect_idx] = 1

    # Create binary vectors for opponents_expected (shifted version of my_defect_idx_without_last)
    opponents_expected_binary = np.zeros(len(opponent_history), dtype=int)
    if opponents_expected != []:
        opponents_expected_binary[opponents_expected] = 1

    distance = np.sum(opponent_defect_idx_binary != opponents_expected_binary) / len(opponents_expected_binary)
    return distance


def detect_grim_trigger(my_history, opponent_history):
    my_defect_idx = np.array(
        [idx for idx in range(len(my_history)) if my_history[idx] == 'defect'])
    opponent_defect_idx = np.array(
        [idx for idx in range(len(opponent_history)) if opponent_history[idx] == 'defect'])
    if np.array_equal(my_defect_idx, np.array([])):
        opponents_expected = []
    else:
        my_first_defection = my_defect_idx[0]
        opponents_expected = np.array(range(my_first_defection + 1, len(my_history)))

    opponent_defect_idx_binary = np.zeros(len(opponent_history), dtype=int)
    if opponent_defect_idx != []:
        opponent_defect_idx_binary[opponent_defect_idx] = 1

    # Create binary vectors for opponents_expected
    if len(opponents_expected) > 0:
        opponents_expected_binary = np.zeros(len(opponent_history), dtype=int)
        opponents_expected_binary[opponents_expected] = 1
    else:
        opponents_expected_binary = np.zeros(len(opponent_history), dtype=int)

    distance = np.sum(opponent_defect_idx_binary != opponents_expected_binary) / len(opponents_expected_binary)
    return distance


def detect_always_defect(opponent_history):
    opponent_defect_idx = np.array(
        [idx for idx in range(len(opponent_history)) if opponent_history[idx] == 'defect'])
    opponents_expected = range(len(opponent_history))

    opponent_defect_idx_binary = np.zeros(len(opponent_history), dtype=int)
    if opponent_defect_idx != []:
        opponent_defect_idx_binary[opponent_defect_idx] = 1

    # Create binary vectors for opponents_expected (the entire history of indices)
    opponents_expected_binary = np.ones(len(opponent_history), dtype=int)

    distance = np.sum(opponent_defect_idx_binary != opponents_expected_binary) / len(opponents_expected_binary)
    return distance


def detect_always_cooperate(opponent_history):
    opponent_defect_idx = np.array(
        [idx for idx in range(len(opponent_history)) if opponent_history[idx] == 'defect'])
    opponents_expected = np.array([])

    # Create binary vector for opponent_defect_idx
    opponent_defect_idx_binary = np.zeros(len(opponent_history), dtype=int)
    if opponent_defect_idx != []:
        opponent_defect_idx_binary[opponent_defect_idx] = 1

    # Create binary vector for opponents_expected (empty, so all zeros)
    opponents_expected_binary = np.zeros(len(opponent_history), dtype=int)

    distance = np.sum(opponent_defect_idx_binary != opponents_expected_binary) / len(opponents_expected_binary)
    return distance

def strategy(my_history: List[str], opponent_history: List[str]) -> str:
    """
    This is the main function of the program.
    The purpose is to implement a version of repeated prisoner's dilemma.
    Args:
        my_history: list of previous choises by player
        opponent_history: list of previous choises by opponent
    Output:
        Either "cooperate" or "defect" """
    opp_strategy = 'random'
    if len(my_history)<=1:
        return 'cooperate'
    elif 1<len(my_history) < 29:
        return 'defect'
    elif 29<=len(my_history)<30:
        return 'cooperate'
    else:
        opp_strategy = detect_opponents_strategy(my_history[-30:], opponent_history[-30:])
    if opp_strategy == 'random':

        # return random_choice(coop_probability=0.7, defect_probability=0.3)

        return tit_for_tat(my_history, opponent_history)
    elif opp_strategy == 'tit_for_tat':
        tit_for_tat(my_history, opponent_history)
    elif opp_strategy == 'grim_trigger' or opp_strategy == 'always_defect':
        return defect()  # if we detected it, opponent is already in 'always_defect' mode
    if opp_strategy == 'always_cooperate':
        return defect()
    elif opp_strategy == 'tit_for_two_tat':
        if my_history[-1] == 'defect':
            return cooperarte()
        else:
            return defect()


my_history = ['cooperate', 'defect', 'defect', 'cooperate', 'cooperate', 'defect', 'cooperate', 'cooperate', 'cooperate', 'cooperate']
opponent_history = ['cooperate', 'cooperate','cooperate', 'defect', 'cooperate', 'cooperate', 'defect', 'cooperate', 'cooperate', 'defect',]

if __name__ == '__main__':
    print(detect_opponents_strategy(my_history, opponent_history))
