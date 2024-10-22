'''
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pprint

# Data setup: 5 values for each memory point and configuration (1:4, 2:4, dense)
on_chip_memory = [1, 5, 10, 50, 100]  # On-chip memory points (MB)

# 5 compute cycles for each memory point
compute_cycles_1_4 = [
    [310, 305, 320, 300, 295],  # At 1MB
    [270, 260, 280, 265, 255],  # At 5MB
    [230, 225, 240, 235, 220],  # At 10MB
    [190, 185, 195, 200, 180],  # At 50MB
    [160, 150, 170, 165, 155]   # At 100MB
]

compute_cycles_2_4 = [
    [320, 315, 330, 310, 305],
    [275, 265, 290, 280, 270],
    [240, 235, 250, 245, 230],
    [210, 200, 220, 215, 205],
    [170, 160, 180, 175, 165]
]

compute_cycles_dense = [
    [400, 395, 410, 390, 385],
    [350, 340, 360, 355, 345],
    [320, 310, 330, 325, 315],
    [270, 260, 280, 275, 265],
    [230, 220, 250, 240, 235]
]

# Calculate means and standard deviations for error bars
mean_1_4 = [np.mean(cycles) for cycles in compute_cycles_1_4]
std_1_4 = [np.std(cycles) for cycles in compute_cycles_1_4]

mean_2_4 = [np.mean(cycles) for cycles in compute_cycles_2_4]
std_2_4 = [np.std(cycles) for cycles in compute_cycles_2_4]

mean_dense = [np.mean(cycles) for cycles in compute_cycles_dense]
std_dense = [np.std(cycles) for cycles in compute_cycles_dense]

# Marker styles and colors for different layers
markers = ['o', 's', '^', 'D', 'P']  # Circle, Square, Triangle, Diamond, Plus
colors = sns.color_palette("Set2", 5)  # 5 distinct colors from seaborn's Set2 palette

# Creating the figure and axes
plt.figure(figsize=(10, 6))

# Plotting error bars with means and std
plt.errorbar(on_chip_memory, mean_1_4, yerr=std_1_4, label="1:4", fmt='o-', capsize=5, color='b')
plt.errorbar(on_chip_memory, mean_2_4, yerr=std_2_4, label="2:4", fmt='s-', capsize=5, color='g')
plt.errorbar(on_chip_memory, mean_dense, yerr=std_dense, label="Dense", fmt='^-', capsize=5, color='r')

# Scatter plot for individual points at each memory point with different markers and colors for each layer
for i, memory in enumerate(on_chip_memory):
    for j in range(5):  # 5 layers
        plt.scatter(memory, compute_cycles_1_4[i][j], marker=markers[j], color=colors[j], alpha=0.6, label=f'1:4 Layer {j+1}' if i == 0 else "")
        plt.scatter(memory, compute_cycles_2_4[i][j], marker=markers[j], color=colors[j], alpha=0.6, label=f'2:4 Layer {j+1}' if i == 0 else "")
        plt.scatter(memory, compute_cycles_dense[i][j], marker=markers[j], color=colors[j], alpha=0.6, label=f'Dense Layer {j+1}' if i == 0 else "")

# Labels and title
plt.xlabel("On-Chip Memory (MB)")
plt.ylabel("Compute Cycles")
plt.title("Compute Cycles vs On-Chip Memory")

# Displaying the legend, ensuring that we only show unique entries
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys())

# Show the plot
plt.grid(True)
plt.show()
'''

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pprint

# Function to read compute cycles from the COMPUTE_REPORT.csv
def read_compute_cycles(model, size, sparsity):
    file_path = f'sparsity_results/{model}_{size}_{sparsity}/COMPUTE_REPORT.csv'
    
    if os.path.exists(file_path):
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Extract LayerID and Total Cycles
        return df[['LayerID', ' Total Cycles']]
    else:
        print(f"File {file_path} not found.")
        return None

# Function to group layers and calculate total cycles for each group (Conv1, Conv2, etc.)
def group_layers_by_conv(layer_cycles):
    # Define which layers belong to which convolution groups
    conv_groups = {
        "Conv1": [0],  # Conv1 corresponds to Layer 0
        "Conv2": [1, 2, 3, 4],  # Conv2 layers
        "Conv3": [5, 6, 7, 8, 9],  # Conv3 layers
        "Conv4": [10, 11, 12, 13, 14],  # Conv4 layers
        "Conv5": [15, 16, 17, 18, 19]  # Conv5 layers
    }
    
    grouped_cycles = {}
    
    # Group total cycles by convolution groups
    for group, layer_ids in conv_groups.items():
        total_cycles = layer_cycles[layer_cycles['LayerID'].isin(layer_ids)][' Total Cycles'].sum()
        grouped_cycles[group] = total_cycles
    
    return grouped_cycles

# Function to plot scatter and error plots
def plot_cycles(on_chip_memory_sizes, cycles_dict, conv_groups):
    # Set up figure
    plt.figure(figsize=(10, 6))

    # Loop over each model and sparsity combination and plot
    for model_size_sparsity, cycles_by_memory in cycles_dict.items():
        # Extract the means and standard deviations for each memory size
        means = [np.mean(list(cycles.values())) for cycles in cycles_by_memory]  # Mean of values in the dict
        std_devs = [np.std(list(cycles.values())) for cycles in cycles_by_memory]  # Std dev of values in the dict

        # Plot error bars (mean and std deviation)
        plt.errorbar(on_chip_memory_sizes, means, yerr=std_devs, label=model_size_sparsity, fmt='o-', capsize=5)

        # Plot individual points (scatter) for each conv group
        for i, memory in enumerate(on_chip_memory_sizes):
            for conv_group in conv_groups:
                plt.scatter(memory, cycles_by_memory[i][conv_group], alpha=0.6)

    plt.xlabel("On-Chip Memory (MB)")
    plt.ylabel("Total Compute Cycles")
    plt.title("Total Compute Cycles vs On-Chip Memory (Scatter and Error Plots)")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    models = ['resnet18'] # ['resnet18', 'alexnet']
    sizes = ['1mb', '5mb', '10mb', '50mb', '100mb']
    sparsities = ['1s4', '2s4', '4s4']
    on_chip_memory_sizes = [1, 5, 10, 50, 100]  # X-axis
    conv_groups = ["Conv1", "Conv2", "Conv3", "Conv4", "Conv5"]

    cycles_dict = {}

    # Loop over models, sizes, and sparsities
    for model in models:
        for sparsity in sparsities:
            # Store cycles for each combination of model, size, and sparsity
            cycles_by_memory = []

            for size in sizes:
                # Read compute cycles for each model, size, and sparsity
                print(model, size, sparsity)
                layer_cycles = read_compute_cycles(model, size, sparsity)
                
                if layer_cycles is not None:
                    # Group layers by conv type and get total cycles for each conv group
                    grouped_cycles = group_layers_by_conv(layer_cycles)
                    cycles_by_memory.append(grouped_cycles)
            
            # Add the total cycles for plotting later
            cycles_dict[f'{model}_{sparsity}'] = cycles_by_memory

    # Printing the values
    # pprint.pprint(cycles_dict)

    # Plot the results
    plot_cycles(on_chip_memory_sizes, cycles_dict, conv_groups)
