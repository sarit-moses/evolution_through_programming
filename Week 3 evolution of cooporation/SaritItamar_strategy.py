###############
### Authors ###
###############

# Sarit Moses 211772900
# Itamar Nini 207047150

###################
### Explanation ###
###################

"""
Strategy explanation:

We have come up with a list of possible strategies that may be used by our opponent: 
    tit-for-tat: starts friendly and then will mirror our actions. 
        Best counter-strategy: always cooperate. 
    grim trigger: starts cooperation but after 1st defection by its opponent will keep defecting until the end of the game. 
        Best counter-strategy: always cooperate
    pavlov: cooperates if both opponents used same strategy in precious rounds, else defects. 
        Best counter-strategy: always cooperate.
    tit-for-two-tats: same as tit for tat, but will only defect after two consecutive defections by opponent. 
        Best counter-strategy: always cooperate, but can randomly defect every once in a while. 
    always cooperate: will always cooperate. 
        Best counter-stategy: always defect.
    always defect: will always defect. 
        Best counter-strategy: always defect. 
    random: chooses steps randomly. 
        Best counter-strategy: this actually imitates many rounds of single iteration prisoner's dilemma, therefore best strategy is always defect. 

We start with tit-for-tat (would handle best most cases), and then re-evaluate the opponent's strategy from the 11th step forward before acting.
Evaluation is based on the last 100 rounds of the game, to shorten runtime and to deal with a changing strategy (that changes in the middle of the game).

We have included in the submission an additional code file (arena.py) that runs our code against different strategies and produces a graph describing its performance. 
"""




###############
### Imports ###
###############

from typing import List
import numpy as np
from scipy.stats import mannwhitneyu

###########
### Run ###
###########

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
    if len(my_history) > 10:
        opp_strategy = detect_opponents_strategy(my_history[-100:], opponent_history[-100:])
    if opp_strategy == 'random':

        # return random_choice(coop_probability=0.7, defect_probability=0.3)

        return tit_for_tat(my_history, opponent_history)
    elif opp_strategy == 'tit_for_tat':
        return cooperarte()
    elif opp_strategy == 'grim_trigger' or opp_strategy == 'always_defect' or opp_strategy =='always_cooperate':
        return defect() # if we detected it, opponent is already in 'always_defect' mode
    elif opp_strategy == 'tit_for_two_tat':
        if my_history[-1] == 'defect':
            return cooperarte()
        else:
            return defect()

 # if we detected it, opponent is already in 'always_defect' mode
    # in case of 1st move in the game:
    # start by cooperation. if opponent is tit-for-tat, the next round he will cooperate
    # this also applies to 2nd move, since the game in the 1st move will have a random start in any case.


def tit_for_tat(my_history, opponent_history):
    if len(my_history) == 0:
        return "cooperate"
    return opponent_history[-1]

def tit_for_two_tat(my_history, opponent_history):
    if len(my_history) == 0:
        return "cooperate"
    if opponent_history[-1] == 'defect' and opponent_history[-2] == 'defect':
        return 'defect'
    return 'cooperate'

def cooperarte():
    return'cooperate'

def defect():
    return 'defect'

def random_choice(coop_probability, defect_probability):
    return np.random.choice(['cooperate', 'defect'], p=[coop_probability, defect_probability])



def detect_opponents_strategy(my_history, opponent_history):
    opp_strategy = 'random'
    opp_strategy = detect_always_defect(opponent_history, opp_strategy)
    opp_strategy = detect_always_cooperate(opponent_history, opp_strategy)
    opp_strategy = detect_tit_for_tat(my_history, opponent_history, opp_strategy)
    opp_strategy = detect_grim_trigger(my_history, opponent_history, opp_strategy)
    opp_strategy = detect_tit_for_two_tat(my_history, opponent_history, opp_strategy)
    return opp_strategy
def detect_tit_for_two_tat(my_history, opponent_history, opp_strategy):

    #no need to expect opp_history[0] as cooperate as 0 will never be in opponents_defect_idx_if_tit_for_tat
    opponent_defect_idx = np.array(
        [idx for idx in range(len(opponent_history)) if opponent_history[idx] == 'defect'])

    opponents_expected =   np.array([idx+2 for idx in range(len(my_history) - 2) if my_history[idx] == 'defect' and my_history[idx+1] == 'defect'])
    # if len(opponents_expected > 4) and len(opponent_defect_idx > 4):
    #     _, p_value = mannwhitneyu(opponent_defect_idx, opponents_expected,  alternative='two-sided')
    #     if p_value > 0.9:
    #         opp_strategy = 'tit_for_two_tat'
    # else:
    if np.array_equal(opponent_defect_idx, opponents_expected):
        opp_strategy = 'tit_for_two_tat'
    return opp_strategy

def detect_tit_for_tat(my_history, opponent_history, opp_strategy):
    #no need to expect opp_history[0] as cooperate as 0 will never be in opponents_defect_idx_if_tit_for_tat
    my_defect_idx_without_last = np.array(
        [idx for idx in range(len(my_history) - 1) if my_history[idx] == 'defect'])
    opponent_defect_idx = np.array(
        [idx for idx in range(len(opponent_history)) if opponent_history[idx] == 'defect'])
    opponents_expected =  (my_defect_idx_without_last + 1)

    if np.array_equal(opponent_defect_idx, opponents_expected ):
        opp_strategy = 'tit_for_tat'
    return opp_strategy
def detect_grim_trigger(my_history, opponent_history, opp_strategy):

    my_defect_idx = np.array(
        [idx for idx in range(len(my_history)) if my_history[idx] == 'defect'])
    opponent_defect_idx = np.array(
        [idx for idx in range(len(opponent_history)) if opponent_history[idx] == 'defect'])
    if np.array_equal(my_defect_idx, np.array([])):
        opponents_expected = []
    else:
        my_first_defection = my_defect_idx[0]
        opponents_expected = np.array(range(my_first_defection+1,len(my_history)))

    if np.array_equal(opponent_defect_idx, opponents_expected):
        opp_strategy = 'grim_trigger'
    return opp_strategy

def detect_always_defect(opponent_history, opp_strategy):
    opponent_defect_idx = np.array(
        [idx for idx in range(len(opponent_history)) if opponent_history[idx] == 'defect'])
    opponents_expected = range(len(opponent_history))
    if np.array_equal(opponent_defect_idx, opponents_expected):
        opp_strategy = 'always_defect'
    return opp_strategy

def detect_always_cooperate(opponent_history, opp_strategy):
    opponent_defect_idx = np.array(
        [idx for idx in range(len(opponent_history)) if opponent_history[idx] == 'defect'])
    opponents_expected = np.array([])
    if np.array_equal(opponent_defect_idx, opponents_expected):
        opp_strategy = 'always_cooperate'
    return opp_strategy

my_history = ['defect', 'cooperate', 'defect', 'defect' , 'cooperate']
opponent_history = ['cooperate','defect', 'defect', 'cooperate','cooperate']


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
    if len(my_history) > 10:
        opp_strategy = detect_opponents_strategy(my_history[-100:], opponent_history[-100:])
    if opp_strategy == 'random':

        # return random_choice(coop_probability=0.7, defect_probability=0.3)

        return tit_for_tat(my_history, opponent_history)
    elif opp_strategy == 'tit_for_tat':
        return cooperarte()
    elif opp_strategy == 'grim_trigger' or opp_strategy == 'always_defect' or opp_strategy =='always_cooperate':
        return defect() # if we detected it, opponent is already in 'always_defect' mode
    elif opp_strategy == 'tit_for_two_tat':
        if my_history[-1] == 'defect':
            return cooperarte()
        else:
            return defect()

if __name__ == '__main__':
    print(detect_opponents_strategy(my_history, opponent_history))