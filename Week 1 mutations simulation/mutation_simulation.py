###############
### Authors ###
###############

# Sarit Moses 211772900
# Itamar Nini 207047150

###############
### Imports ###
###############
import sys
import random
import argparse
import numpy as np
#import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
########################
### Class definition ###
########################

class Bacterium:
    """
    A bacterium in the population
    """
    mutations_occurred = 0
    active_mutations = None
    current_bacterium_population = []
    id_counter =0
    state = 'Darwinian'

    def __init__(self, father, replication_rate=1, mutation_rate=0.1, death_rate = 0.01, root=False):
        #id counter uses for visualizing the tree
        self.id = Bacterium.id_counter
        Bacterium.id_counter += 1
        if father:
            self.mutation = father.mutation
        else:
            self.mutation = 0
        self.live_state = True
        self.left_child = None
        self.right_child = None
        self.mutation_rate = mutation_rate
        self.death_rate = death_rate
        self.replication_rate= replication_rate
        self.father = father
        #mutate by chance.
        #mutations can only occur during intialization
        mutation_now = random.random()
        if not root and Bacterium.active_mutations and mutation_now <= mutation_rate:
            Bacterium.mutations_occurred += 1
            self.mutate_bacterium()

    def replicate(self, current_bacteria_population_copy):
        """ replicates the bacterium which will generate two daughter cells and kill the original one """
         # only replicate if alive
        child1 = Bacterium(father= self, replication_rate= self.replication_rate, mutation_rate=self.mutation_rate, death_rate= self.death_rate)
        child2 = Bacterium(father = self, replication_rate= self.replication_rate, mutation_rate=self.mutation_rate, death_rate= self.death_rate)
        self.left_child = child1
        self.right_child= child2
        current_bacteria_population_copy.extend([child1, child2])
        self.die()

    def mutate_bacterium(self):
        """ mutates bacteria on demand by posing external stress """

        self.mutation = Bacterium.mutations_occurred

        mutation_rate_noise = np.random.normal(loc=0, scale=0.01)
        new_mutation_rate = np.clip(self.mutation_rate + mutation_rate_noise, 0, 1)

        die_rate_noise = abs(np.random.normal(loc=0, scale=0.1))
        new_die_rate = np.clip(self.death_rate - die_rate_noise, 0, 1) # substract beacuse lamark stated that mutations should increase fittness

        self.death_rate = new_die_rate
        self.mutation_rate = new_mutation_rate

    def die(self):
        """ changes the live state to False (dead) """
        self.live_state = False

    def cycle(self, current_bacteria_population_copy):
        die_now = random.random()
        if die_now <= self.death_rate:
            self.die()
            return
        replicate_now = random.random()
        if replicate_now <= self.replication_rate:
            self.replicate(current_bacteria_population_copy)
            return



#################
### functions ###
#################
    
def initialize(replication_rate, mutation_rate, die_rate):
    return Bacterium(father = None, replication_rate= replication_rate, mutation_rate=mutation_rate, death_rate= die_rate, root= True)

def simulation(simulation_time, generations_archive):
    """
    Creates one simulation and reports number of live mutated cells at the end.
    Args:
        p = probability of mutation
        t = time passing in simulation
        rep_time = time for a bacterium to replicate
        mut_mode: string, "random" or "on demand"
    """
    for time_unit in range(simulation_time):
        generations_archive.append(Bacterium.current_bacterium_population[:])
        current_bacteria_population_copy = Bacterium.current_bacterium_population[:]
        for bacteria in Bacterium.current_bacterium_population:
            bacteria.cycle(current_bacteria_population_copy)
        Bacterium.current_bacterium_population = [bacteria for bacteria in current_bacteria_population_copy if bacteria.live_state]

    generations_archive.append(Bacterium.current_bacterium_population[:])
    return generations_archive


def add_stress(mutation_die_rate_dict, bacterium):
    """
    Applies stress to a bacterial population by adjusting their death rates based on mutation levels.
    """
    if bacterium.mutation == 0:
        mutation_die_rate_dict[bacterium.mutation] = random.uniform(0.9, 1)
    elif bacterium.mutation in mutation_die_rate_dict.keys():
        bacterium.death_rate = mutation_die_rate_dict[bacterium.mutation]
    else:
        die_rate_noise = np.random.normal(loc=0, scale=0.5)
        mutation_die_rate_dict[bacterium.mutation] = np.clip(mutation_die_rate_dict[bacterium.father.mutation] + die_rate_noise, 0, 1)
    if bacterium.left_child:
        add_stress(mutation_die_rate_dict, bacterium.left_child)
    if bacterium.right_child:
        add_stress(mutation_die_rate_dict, bacterium.right_child)
    # TODO should we also change replication rate? how?


def draw_tree(root, time_no_stress, filename="phylo_tree.png"):
    graph = nx.DiGraph()
    pos = {}
    labels = {}
    colors = {}
    layer_nodes = {}  # Track y-positions for each layer

    mutation_types = range(Bacterium.mutations_occurred)
    colors_palette = list(mcolors.TABLEAU_COLORS.values())  # Get distinct colors
    mutation_color_map = {mutation: colors_palette[i % len(colors_palette)] for i, mutation in
                          enumerate(mutation_types)}

    def add_edges(graph, node, pos, labels, colors, layer_nodes, x=0, y=0, layer=1, x_offset=2.0, y_offset=2.0):
        """ Recursively add nodes and edges to the graph with increased spacing. """
        if node:
            graph.add_node(node.id, pos=(x, -y * y_offset))  # Spread out vertically
            labels[node.id] = node.mutation

            if layer not in layer_nodes:
                layer_nodes[layer] = []
            layer_nodes[layer].append(-y * y_offset)

            colors[node.id] = mutation_color_map.get(node.mutation, "gray")

            new_x_offset = x_offset / 1.5

            if node.left_child:
                graph.add_edge(node.id, node.left_child.id)
                add_edges(graph, node.left_child, pos, labels, colors, layer_nodes, x - new_x_offset, y + 1, layer + 1, new_x_offset, y_offset)
            if node.right_child:
                graph.add_edge(node.id, node.right_child.id)
                add_edges(graph, node.right_child, pos, labels, colors, layer_nodes, x + new_x_offset, y + 1, layer + 1, new_x_offset, y_offset)

    add_edges(graph, root, pos, labels, colors, layer_nodes)

    # **Auto-Adjust for Large Trees**
    num_nodes = len(graph.nodes)
    if num_nodes > 30:
        pos = nx.spring_layout(graph, k=0.7, seed=42)  # Adjust spacing automatically
    else:
        pos = nx.get_node_attributes(graph, 'pos')

    node_colors = [colors[node] for node in graph.nodes()]

    # **Dynamic Figure Size**
    width = max(12, num_nodes * 0.5)
    height = max(10, len(layer_nodes) * 0.8)

    plt.figure(figsize=(width, height))
    node_size = max(3000 - num_nodes * 40, 500)

    nx.draw(graph, pos, with_labels=False, node_size=node_size, node_color=node_colors, edge_color="gray")

    # **Show labels only for key nodes if too large**
    if num_nodes < 50:
        nx.draw_networkx_labels(graph, pos, labels=labels, font_size=8, font_weight="bold")

    # **Dashed Red Line for Stress**
    stress_layer = time_no_stress + 1
    if stress_layer in layer_nodes:
        y_stress = min(layer_nodes[stress_layer]) - 1.0
        plt.axhline(y=y_stress, color="red", linestyle="dashed", linewidth=2, label="Stress Applied")

    # **Legend**
    legend_patches = []
    legend_patches.append(plt.Line2D([0], [0], color="red", linestyle="dashed", linewidth=2, label="Stress Applied"))

    plt.legend(handles=legend_patches, title="Mutation Types", loc="upper left", bbox_to_anchor=(1, 1))

    plt.savefig(filename, bbox_inches="tight", dpi=300)
    plt.show()
    plt.close()

def main(assignment, initial_mutation_p, initial_die_p, initial_replication_p, number_of_assay_replications, time_no_stress, time_with_stress, visualize_tree = False):
    results = []
    if assignment == 'd':
        task_dict = {0: 'Mutations only prestress', 1: 'Mutations only poststress', 2: 'Mutations at both'}

        results.append(run('a', initial_die_p, initial_mutation_p, initial_replication_p,
                           number_of_assay_replications, time_no_stress, time_with_stress, visualize_tree))
        results.append(run('b', initial_die_p, initial_mutation_p, initial_replication_p,
            number_of_assay_replications, time_no_stress, time_with_stress, visualize_tree))
        results.append(run('c', initial_die_p, initial_mutation_p, initial_replication_p,
            number_of_assay_replications, time_no_stress, time_with_stress, visualize_tree))

        plt.figure(figsize=(10, 6))

        # Loop through the vectors and plot each histogram
        for i, vector in enumerate(results):
            mean = np.mean(vector)
            variance = np.var(vector)

            # Print the mean and variance for each dataset
            print(f'{task_dict[i]}: Mean = {mean:.2f}, Variance = {variance:.2f}')

            plt.hist(vector, bins=30, alpha=0.5, label=f'Assignment {task_dict[i]} Mean: {mean:.2f}, Variance: {variance:.2f}')

        # Add labels and title
        plt.title("Histogram of Survived Bacteria Counts")
        plt.xlabel('Number of Survived Bacteria')
        plt.ylabel('Frequency')

        # Show legend
        plt.legend()

        # Show the plot
        plt.savefig('comparing_prestrees_poststress_both_histogram.png')
        plt.show()


def run(assignment, initial_die_p, initial_mutation_p, initial_replication_p, number_of_assay_replications,
        time_no_stress, time_with_stress, visualize_tree):

    mutations_after_stress, mutations_before_stress = set_assingment(assignment)

    survivals_at_end = []
    for replica in range(number_of_assay_replications):
        Bacterium.mutations_occurred = 0
        Bacterium.active_mutations = None
        Bacterium.current_bacterium_population = []
        Bacterium.id_counter = 0
        Bacterium.state = 'Darwinian'

        Bacterium.active_mutations = mutations_before_stress
        root_bacterium = initialize(initial_replication_p, initial_mutation_p, initial_die_p)
        Bacterium.current_bacterium_population = [root_bacterium]

        generation_archive = simulation(time_no_stress, [])

        # Stress mode on
        mutation_die_rate_dict = {}
        add_stress(mutation_die_rate_dict, root_bacterium)
        for bacteria in Bacterium.current_bacterium_population:
            bacteria.death_rate= mutation_die_rate_dict[bacteria.mutation]

        Bacterium.active_mutations = mutations_after_stress

        generation_archive = simulation(time_with_stress, generation_archive)
        if replica == 0 and visualize_tree:
            draw_tree(root_bacterium, time_no_stress)
        survivals_at_end.append(len(Bacterium.current_bacterium_population))
    return survivals_at_end


def set_assingment(assignment):
    mutations_after_stress, mutations_before_stress = None, None
    if assignment == 'a':
        mutations_before_stress = True
        mutations_after_stress = False
    elif assignment == 'b':
        mutations_before_stress = False
        mutations_after_stress = True
    elif assignment == 'c':
        mutations_before_stress = True
        mutations_after_stress = True

    return mutations_after_stress, mutations_before_stress


###########
### run ###
# #########    

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Bacterial simulation.")

    parser.add_argument("-p", type=float, default=0.01, help="initial Probability of mutation.")
    parser.add_argument("-d", type=float, default=0.01, help="initial Probability to die.")
    parser.add_argument("-r", type=float, default=1, help="initial Probability of the bacterium to replicate.")

    parser.add_argument("-n", type=int, default=100, help="number of assay replicates")
    parser.add_argument("-t", type=int, default=100, help="Length of experiment before stress (cycles).")
    parser.add_argument("-s", type=int, default=1, help="Length of experiment after stress (cycles).")
    parser.add_argument("-v", type=int, default=0, help="visualize_tree. 0 for false 1 for true")
    parser.add_argument("-a", type=str, default='d', help="assignment number: 'a' for mutations only before stress occurs. "
                                                        "'b' for mutation to occur only after stress is on."
                                                        "'c' for mutations in both periods."
                                                          "'d' for running the 3 Random, induced, combined and compare"
                                                          "'f' for running a comparison between the Darwinian to the Lamarkian models")

    args = parser.parse_args()

    main(args.a, args.p, args.d, args.r, args.n, args.t, args.s, visualize_tree=args.v)

