###############
### Authors ###
###############

# Sarit Moses 211772900
# Itamar Nini

###################
### Explanation ###
###################

# Possible opponent strategies:
#   tit-for-tat: starts friendly, will defect after each defection, will cooporate after each cooporation
#       best counter-strategy: coopareta as much as possible (will lead to cooperation)
#   grim trigger: starts friendly, will cooporate until 1st defection and then will defect until the end
#       best counter-strategy: always cooperate, defecting once can be bad. if there is a time limit, can defect on last move. 
#   always defect: will always defect regardless of oponnent actions
#       best counter-strategy: always defect.
#   always cooperate: will always cooperate regardless of opponent actions
#       best counter-strategy: always defect
#   random: unpredictable, will choose randomly
#       hard to predict. no best counter-strategy
#   tit for two tats: cooperate unless oponnent defects twice in row, than defect. 
#       best counter-strategy: always cooperate but you can get away with an occasional defection
#   pavlov: cooperates if both oponents used same move in previous step, else defect. 
#       best counter-strategy: cooperate. 

# by taking all the above data into account, the most reasonable behavior is probably to lead with two cooperations and then evaluate oponent's response. 
# normally the best strategy would be tit-for-tat (as a strategy for dealing with most possile oponent's strategies). 
# this strategy should perform very well agains almost all strategies, with a small loss on 1st round for always defect. 
# it will probably not have the best outcome agains always cooperate (because against it the best strategy is always defect) but also not the worst outcome. 

# try to implement - for dealing with a semi-random behavior that has a higher probability to one of the options: 
# after 10 rounds try to evaluate what is the oponnent's strategy.
# if found to be random - always defect (will have highest score). 




###############
### Imports ###
###############

from typing import List


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
    
    # in case of 1st move in the game:
    # start by cooperation. if opponent is tit-for-tat, the next round he will cooperate
    # this also applies to 2nd move, since the game in the 1st move will have a random start in any case. 
    if len(my_history) == 0:
        return "cooperate"
    return opponent_history[-1]

