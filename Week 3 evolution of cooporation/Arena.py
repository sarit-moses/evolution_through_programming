import SaritItamar_strategy
import matplotlib.pyplot as plt

class Player:
    def __init__(self, strategy):
        self.strategy = strategy

def changing_strategy(i, my_history, opponent_history):
    if i < 200:
        return SaritItamar_strategy.tit_for_tat(my_history, opponent_history)
    elif 200 <= i < 400:
        return SaritItamar_strategy.defect()
    elif 400 <= i <600:
        return SaritItamar_strategy.cooperarte()
    elif 600<= i < 800:
        return SaritItamar_strategy.tit_for_two_tat(my_history, opponent_history)
    else:
        return SaritItamar_strategy.random_choice(0.5, 0.5)

def run_simulation_vs_changing_strategy(pointing_rules, number_of_rounds):
    if pointing_rules == 'Prisoner Dillema':
        pointing_rules_dict = {'cooperate_cooperate': (-1, -1), 'cooperate_defect': (-3, 0), 'defect_cooperate': (0, -3), 'defect_defect': (-2,-2)}

    us = Player(strategy= SaritItamar_strategy.strategy)
    our_history = []

    changing_strategy_opp = Player(strategy=changing_strategy)
    changing_strategy_opp_history = []
    our_score = 0
    opp_score = 0
    our_score_log = []
    opp_score_log = []
    for i in range(number_of_rounds):
        our_choice = us.strategy(our_history, changing_strategy_opp_history)
        changing_strategy_opponent_choice = changing_strategy_opp.strategy(i ,changing_strategy_opp_history, our_history)

        our_history.append(our_choice)
        changing_strategy_opp_history.append(changing_strategy_opponent_choice)

        round_key = f"{our_choice}_{changing_strategy_opponent_choice}"
        round_result = pointing_rules_dict.get(round_key, (0, 0))

        our_score += round_result[0]
        opp_score += round_result[1]

        our_score_log.append(our_score/ (i +1))
        opp_score_log.append(opp_score/ (i+1))

    plot_score_log(pointing_rules, opp_score_log, our_score_log, "Changing Strategy")
def run_simulation_vs_tit_for_tat(pointing_rules, number_of_rounds):
    if pointing_rules == 'Prisoner Dillema':
        pointing_rules_dict = {'cooperate_cooperate': (-1, -1), 'cooperate_defect': (-3, 0), 'defect_cooperate': (0, -3), 'defect_defect': (-2,-2)}

    us = Player(strategy= SaritItamar_strategy.strategy)
    our_history = []

    tit_for_tat_opp = Player(strategy=SaritItamar_strategy.tit_for_tat)
    tit_for_tat_opp_history = []
    our_score = 0
    opp_score = 0
    our_score_log = []
    opp_score_log = []
    for i in range(number_of_rounds):
        our_choice = us.strategy(our_history, tit_for_tat_opp_history)
        tit_for_tat_opponent_choice = tit_for_tat_opp.strategy(tit_for_tat_opp_history, our_history)

        our_history.append(our_choice)
        tit_for_tat_opp_history.append(tit_for_tat_opponent_choice)

        round_key = f"{our_choice}_{tit_for_tat_opponent_choice}"
        round_result = pointing_rules_dict.get(round_key, (0, 0))

        our_score += round_result[0]
        opp_score += round_result[1]

        our_score_log.append(our_score/ (i +1))
        opp_score_log.append(opp_score/ (i+1))

    plot_score_log(pointing_rules, opp_score_log, our_score_log, "Tit for tat")

def run_simulation_vs_tit_for_two_tat(pointing_rules, number_of_rounds):
    if pointing_rules == 'Prisoner Dillema':
        pointing_rules_dict = {'cooperate_cooperate': (-1, -1), 'cooperate_defect': (-3, 0), 'defect_cooperate': (0, -3), 'defect_defect': (-2,-2)}

    us = Player(strategy= SaritItamar_strategy.strategy)
    our_history = []

    tit_for_tat_opp = Player(strategy=SaritItamar_strategy.tit_for_two_tat)
    tit_for_tat_opp_history = []
    our_score = 0
    opp_score = 0
    our_score_log = []
    opp_score_log = []
    for i in range(number_of_rounds):
        our_choice = us.strategy(our_history, tit_for_tat_opp_history)
        tit_for_tat_opponent_choice = tit_for_tat_opp.strategy(tit_for_tat_opp_history, our_history)

        our_history.append(our_choice)
        tit_for_tat_opp_history.append(tit_for_tat_opponent_choice)

        round_key = f"{our_choice}_{tit_for_tat_opponent_choice}"
        round_result = pointing_rules_dict.get(round_key, (0, 0))

        our_score += round_result[0]
        opp_score += round_result[1]

        our_score_log.append(our_score/ (i +1))
        opp_score_log.append(opp_score/ (i+1))

    plot_score_log(pointing_rules , opp_score_log, our_score_log, "Tit for two tat")

def run_simulation_vs_always_coop(pointing_rules, number_of_rounds):
    if pointing_rules == 'Prisoner Dillema':
        pointing_rules_dict = {'cooperate_cooperate': (-1, -1), 'cooperate_defect': (-3, 0),
                               'defect_cooperate': (0, -3), 'defect_defect': (-2, -2)}

    us = Player(strategy=SaritItamar_strategy.strategy)
    our_history = []

    always_coop_opp = Player(strategy=SaritItamar_strategy.cooperarte)
    always_coop_opp_history = []
    our_score = 0
    opp_score = 0
    our_score_log = []
    opp_score_log = []
    for i in range(number_of_rounds):
        our_choice = us.strategy(our_history, always_coop_opp_history)
        always_coop_opponent_choice = always_coop_opp.strategy()

        our_history.append(our_choice)
        always_coop_opp_history.append(always_coop_opponent_choice)

        round_key = f"{our_choice}_{always_coop_opponent_choice}"
        round_result = pointing_rules_dict.get(round_key, (0, 0))

        our_score += round_result[0]
        opp_score += round_result[1]

        our_score_log.append(our_score / (i + 1))
        opp_score_log.append(opp_score / (i + 1))

    plot_score_log(pointing_rules , opp_score_log, our_score_log, "always cooperate")

def run_simulation_vs_always_defect(pointing_rules, number_of_rounds):
    if pointing_rules == 'Prisoner Dillema':
        pointing_rules_dict = {'cooperate_cooperate': (-1, -1), 'cooperate_defect': (-3, 0),
                               'defect_cooperate': (0, -3), 'defect_defect': (-2, -2)}

    us = Player(strategy=SaritItamar_strategy.strategy)
    our_history = []

    always_defect_opp = Player(strategy=SaritItamar_strategy.defect)
    always_defect_opp_history = []
    our_score = 0
    opp_score = 0
    our_score_log = []
    opp_score_log = []
    for i in range(number_of_rounds):
        our_choice = us.strategy(our_history, always_defect_opp_history)
        always_defect_opponent_choice = always_defect_opp.strategy()

        our_history.append(our_choice)
        always_defect_opp_history.append(always_defect_opponent_choice)

        round_key = f"{our_choice}_{always_defect_opponent_choice}"
        round_result = pointing_rules_dict.get(round_key, (0, 0))

        our_score += round_result[0]
        opp_score += round_result[1]

        our_score_log.append(our_score / (i + 1))
        opp_score_log.append(opp_score / (i + 1))

    plot_score_log(pointing_rules , opp_score_log, our_score_log, "always defect")

def run_simulation_vs_random(pointing_rules, number_of_rounds):
    if pointing_rules == 'Prisoner Dillema':
        pointing_rules_dict = {'cooperate_cooperate': (-1, -1), 'cooperate_defect': (-3, 0),
                               'defect_cooperate': (0, -3), 'defect_defect': (-2, -2)}

    us = Player(strategy=SaritItamar_strategy.strategy)
    our_history = []

    random_opp = Player(strategy=SaritItamar_strategy.random_choice)
    random_opp_history = []
    our_score = 0
    opp_score = 0
    our_score_log = []
    opp_score_log = []
    for i in range(number_of_rounds):
        our_choice = us.strategy(our_history, random_opp_history)
        random_opponent_choice = random_opp.strategy(0.5, 0.5)

        our_history.append(our_choice)
        random_opp_history.append(random_opponent_choice)

        round_key = f"{our_choice}_{random_opponent_choice}"
        round_result = pointing_rules_dict.get(round_key, (0, 0))

        our_score += round_result[0]
        opp_score += round_result[1]

        our_score_log.append(our_score / (i + 1))
        opp_score_log.append(opp_score / (i + 1))

    plot_score_log(pointing_rules, opp_score_log, our_score_log, "Random")
def plot_score_log(pointing_rules, opp_score_log, our_score_log, opp_strategy):
    plt.figure(figsize=(10, 5))
    plt.plot(our_score_log, label='Our Strategy', color='blue')
    plt.plot(opp_score_log, label=f'{opp_strategy}', color='red')
    plt.xlabel('Round')
    plt.ylabel('Normalized score (absolute score / number of rounds)')
    plt.title(f'{pointing_rules}: Our Strategy vs. {opp_strategy}')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'./scoring_plots/{pointing_rules}_vs_{opp_strategy}_plot.png')



def prisoner_dillema():
    run_simulation_vs_always_defect('Prisoner Dillema', 1000)
    run_simulation_vs_always_coop('Prisoner Dillema', 1000)
    run_simulation_vs_tit_for_tat('Prisoner Dillema', 1000)
    run_simulation_vs_tit_for_two_tat('Prisoner Dillema', 1000)
    run_simulation_vs_random('Prisoner Dillema', 1000)
    run_simulation_vs_changing_strategy('Prisoner Dillema', 1000)

if __name__ == '__main__':
    prisoner_dillema()