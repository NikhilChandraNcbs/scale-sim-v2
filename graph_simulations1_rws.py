"""
This file shall be used for studies related to layer-wise sparsity - variation of block size with fixed array size
this is for rws
"""

import os
import subprocess
import csv
import matplotlib.pyplot as plt
from collections import defaultdict

# Define paths
cfg_path = "configs/new"
csv_path = "topologies/sparsity/new"
results_path = "sparsity_results/new"
output_csv_path = "actual_rws/rws_output_results_vith.csv"
output_plot_path = "actual_rws/rws_compute_cycles_plot_vith.png"
scalesim_command_template = "python3 scalesim/scale.py -c {cfg_file} -t {csv_file} -p {results_path} -i gemm"
# scalesim_command_template = "python3 scalesim/scale.py -c {cfg_file} -t {csv_file} -p {results_path}"

# Knobs
generate_cfg = True        # Generate .cfg files
generate_csv = True        # Generate .csv files
execute_commands = True    # Execute simulation commands
generate_graphs = True     # Generate graphs

# Ensure directories exist
os.makedirs(cfg_path, exist_ok=True)
os.makedirs(csv_path, exist_ok=True)
os.makedirs(results_path, exist_ok=True)

# Function to generate .cfg content
def generate_cfg_content(array_height, array_width):
    return f"""[general]
run_name = lws_{array_height}x{array_width}

[architecture_presets]
ArrayHeight : {array_height}
ArrayWidth :  {array_width}
IfmapSramSzkB:   256
FilterSramSzkB:  256
OfmapSramSzkB:   256
IfmapOffset:    0
FilterOffset:   10000000
OfmapOffset:    20000000
Bandwidth : 50
Dataflow : ws
MemoryBanks:   1

[sparsity]
SparsitySupport : true
SparseRep : ellpack_block
OptimizedMapping : true
BlockSize : {array_height}

[run_presets]
InterfaceBandwidth: USER"""

# Function to generate .csv content
def generate_csv_content(array_height, sparsity):
    return f"L,M,N,K,Sparsity,\nL4,256,1280,5120,{sparsity},"
    # vits L4,196,384,1536
    # vitb L4,196,768,3072
    # vitl L4,196,4096,1024
    # vith L4,256,1280,5120
#     return f"""Layer name,IFMAP Height,IFMAP Width,Filter Height,Filter Width,Channels,Num Filter,Strides,Sparsity,
# Conv1,224,224,11,11,3,96,4,{sparsity},"""

# Main script
# Main script
def main():
    array_sizes = [(4, 4), (8, 8), (16, 16), (32, 32)]  # Possible ArrayHeight and ArrayWidth values
    commands = []  # To store all generated commands
    results = []  # To store results for plotting

    for ah, aw in array_sizes:
        # Generate .cfg file if enabled
        cfg_filename = f"lws_{ah}x{aw}.cfg"
        cfg_filepath = os.path.join(cfg_path, cfg_filename)
        if generate_cfg:
            with open(cfg_filepath, "w") as cfg_file:
                cfg_file.write(generate_cfg_content(ah, aw))
            print(f"Generated CFG: {cfg_filepath}")
        
        # Generate .csv files for each sparsity ratio (1:M to M:M)
        # for n in range(1, ah + 1):  # N varies from 1 to M where M=ArrayHeight
        for n in range(1):  # N varies from 1 to M where M=ArrayHeight
            sparsity_ratio = f"{n}:{ah}"
            csv_filename = f"lws_gemm_{ah}x{aw}_{n}s{ah}.csv"
            csv_filepath = os.path.join(csv_path, csv_filename)
            
            if generate_csv:
                with open(csv_filepath, "w") as csv_file:
                    csv_file.write(generate_csv_content(ah, sparsity_ratio))
                print(f"Generated CSV: {csv_filepath}")
            
            # Generate the simulation command
            command = scalesim_command_template.format(
                # cfg_file=cfg_filepath,
                cfg_file=os.path.join(cfg_path, f"lws_32x32.cfg"),
                csv_file=csv_filepath,
                results_path=results_path
            )
            commands.append((command, f"{ah}x{aw}", sparsity_ratio))  # Store command with context

    # Execute commands if enabled
    if execute_commands:
        # for command in commands:
        #     print(command) 
        # assert 1==0, "BLIM"
        print("\nExecuting Commands...\n")
        for command, array_size, sparsity_ratio in commands:
            print(f"Executing: {command}")
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout
                compute_cycles = None
                
                # Extract COMPUTE CYCLES value
                if "COMPUTE CYCLES =" in output:
                    compute_cycles = output.split("COMPUTE CYCLES =")[1].strip().split()[0]
                
                if compute_cycles:
                    results.append([f"lws_{array_size}", array_size, sparsity_ratio, int(compute_cycles)])
                    print(f"Extracted Compute Cycles: {compute_cycles} for {array_size}, {sparsity_ratio}")
                else:
                    print(f"Failed to extract compute cycles for: {command}")
            except Exception as e:
                print(f"Error executing command: {e}")
    
        # Write results to output CSV
        with open(output_csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["LWS", "Array Size", "Sparsity Ratio", "Compute Cycles"])
            writer.writerows(results)
    
        print(f"\nResults saved to {output_csv_path}")

    # Generate graphs if enabled
    if generate_graphs:
        plot_results(output_csv_path, output_plot_path)
        # plot_results_combined("output_results7.csv", "output_results8.csv", "overlapping_compute_cycles.png")
        # plot_results_combined_scatter(
        #     "output_results_vits.csv", 
        #     "rws_output_results_vits.csv", 
        #     "output_results_vitb.csv", 
        #     "rws_output_results_vitb.csv", 
        #     "output_results_vitl.csv", 
        #     "rws_output_results_vitl.csv", 
        #     "output_results_vith.csv", 
        #     "rws_output_results_vith.csv", 
        #     "overlapping_compute_cycles_scatter_vits.png")

# Function to plot results
def plot_results(output_csv_path, output_plot_path):
    # Read results from CSV file
    results = []
    with open(output_csv_path, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            results.append(row)

    # Organize data by Array Size and Sparsity Ratio
    data = defaultdict(lambda: defaultdict(int))  # {array_size: {sparsity_ratio: compute_cycles}}
    for row in results:
        array_size = row["Array Size"]
        sparsity_ratio = row["Sparsity Ratio"]
        compute_cycles = int(row["Compute Cycles"])
        data[array_size][sparsity_ratio] = compute_cycles

    # Sort array sizes and sparsity ratios
    sorted_array_sizes = sorted(data.keys(), key=lambda x: int(x.split('x')[0]))  # Sort by first dimension
    bar_width = 0.15  # Width of each bar
    x_positions = []  # X positions of bars
    sparsity_labels = []  # N:M labels
    array_labels_positions = []  # For centering array size labels
    current_x = 0  # X position counter

    plt.figure(figsize=(18, 10))

    # Generate bars
    for array_size in sorted_array_sizes:
        sparsity_ratios = sorted(data[array_size].keys(), key=lambda x: int(x.split(':')[0]))  # Sort by N
        start_x = current_x  # Start position for this array size group

        for sr in sparsity_ratios:
            # Append bar and label
            plt.bar(current_x, data[array_size][sr], width=bar_width, label=f"{sr}" if current_x == 0 else "")
            x_positions.append(current_x)
            sparsity_labels.append(sr)
            current_x += bar_width  # Move to next position

        # Calculate the center position of the group
        end_x = current_x - bar_width
        group_mid = (start_x + end_x) / 2
        array_labels_positions.append((group_mid, array_size))

        # Add space after each array size group
        current_x += bar_width * 2

    # Formatting x-axis
    plt.xticks(x_positions, sparsity_labels, rotation=45, fontsize=12)
    plt.yticks(fontsize=12)
    plt.xlabel("Sparsity Ratios", fontsize=16, labelpad=20)  # Add x-axis label with padding
    plt.ylabel("Compute Cycles", fontsize=16)
    plt.title("ViT-H: Compute Cycles vs Sparsity Ratios and Block Sizes for a 32x32 PE Array", fontsize=14)
    plt.yscale("log")  # Logarithmic Y-axis

    # Increase bottom margin to accommodate array size labels
    plt.subplots_adjust(bottom=0.2)

    # # Print array size labels centered below each group
    # for position, label in array_labels_positions:
    #     plt.text(position, min(min(d.values()) for d in data.values()) * 0.4, label,
    #              ha='center', va='top', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_plot_path)
    print("Graph saved to lws_compute_cycles_plot.png")
    plt.show()


def plot_results_combined(csv_file1, csv_file2, output_filename):
    # import matplotlib.pyplot as plt
    # from collections import defaultdict
    # import csv

    def read_csv(file):
        results = []
        with open(file, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                results.append(row)
        return results

    def organize_data(results):
        data = defaultdict(lambda: defaultdict(int))  # {array_size: {sparsity_ratio: compute_cycles}}
        for row in results:
            array_size = row["Array Size"]
            sparsity_ratio = row["Sparsity Ratio"]
            compute_cycles = int(row["Compute Cycles"])
            data[array_size][sparsity_ratio] = compute_cycles
        return data

    # Read and organize data
    results1 = read_csv(csv_file1)
    results2 = read_csv(csv_file2)
    data1 = organize_data(results1)
    data2 = organize_data(results2)

    # Sort array sizes
    sorted_array_sizes = sorted(data1.keys(), key=lambda x: int(x.split('x')[0]))
    bar_width = 0.35  # Width of each bar
    x_positions = []  # X positions of bars
    sparsity_labels = []
    array_labels_positions = []
    current_x = 0

    plt.figure(figsize=(18, 10))

    # Generate bars for both files
    for array_size in sorted_array_sizes:
        sparsity_ratios = sorted(data1[array_size].keys(), key=lambda x: int(x.split(':')[0]))  # Sort N:M
        start_x = current_x  # Start position for this array size group

        for sr in sparsity_ratios:
            # Bars for output_results1.csv (front side)
            plt.bar(current_x, data1[array_size][sr], width=bar_width, color='tab:blue', alpha=0.5, label="File 1" if current_x == 0 else "")
            # Bars for output_results7.csv (back side, slightly transparent)
            plt.bar(current_x, data2[array_size][sr], width=bar_width, color='tab:blue', label="File 2" if current_x == 0 else "")
            x_positions.append(current_x)
            sparsity_labels.append(sr)
            current_x += bar_width  # Move to next position

        # Calculate center position for array size labels
        end_x = current_x - bar_width
        group_mid = (start_x + end_x) / 2
        array_labels_positions.append((group_mid, array_size))

        # Add space after each array size group
        current_x += bar_width * 2

    # Formatting x-axis
    plt.xticks(x_positions, sparsity_labels, rotation=45, fontsize=12)
    plt.yticks(fontsize=12)
    plt.xlabel("Sparsity Ratios", fontsize=16, labelpad=20)
    plt.ylabel("Compute Cycles", fontsize=16)
    plt.title("Compute Cycles Variation for GEMM M,N,K = 1000,1000,1000", fontsize=14)
    plt.yscale("log")  # Logarithmic Y-axis

    # Increase bottom margin to accommodate array size labels
    plt.subplots_adjust(bottom=0.3)

    # Print array size labels centered below each group
    for position, label in array_labels_positions:
        plt.text(position, min(min(d.values()) for d in (data1.values())) * 0.4, label,
                 ha='center', va='top', fontsize=12, fontweight='bold', color='tab:blue', alpha=0.5)
    for position, label in array_labels_positions:
        plt.text(position, min(min(d.values()) for d in (data1.values())) * 0.33, "32x32",
                 ha='center', va='top', fontsize=12, fontweight='bold', color='tab:blue')

    # Add legend
    plt.legend(["Variable PE array with blocksize = PE array dimension", "Fixed 32x32 with variable block sizes = 4,8,16,32"], fontsize=14)

    plt.tight_layout()
    plt.savefig(output_filename)
    print(f"Graph saved to {output_filename}")
    plt.show()

def plot_results_combined_scatter(csv_file1, csv_file1_rws, csv_file2, csv_file2_rws, csv_file3, csv_file3_rws, csv_file4, csv_file4_rws, output_filename):
    def read_csv(file):
        results = []
        with open(file, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                results.append(row)
        return results

    def organize_data(results):
        data = defaultdict(lambda: defaultdict(int))  # {array_size: {sparsity_ratio: compute_cycles}}
        for row in results:
            array_size = row["Array Size"]
            sparsity_ratio = row["Sparsity Ratio"]
            compute_cycles = int(row["Compute Cycles"])
            data[array_size][sparsity_ratio] = compute_cycles
        return data

    # Read and organize data
    results1 = read_csv(csv_file1)
    results1_rws = read_csv(csv_file1_rws)
    results2 = read_csv(csv_file2)
    results2_rws = read_csv(csv_file2_rws)
    results3 = read_csv(csv_file3)
    results3_rws = read_csv(csv_file3_rws)
    results4 = read_csv(csv_file4)
    results4_rws = read_csv(csv_file4_rws)

    data1 = organize_data(results1)
    data1_rws = organize_data(results1_rws)
    data2 = organize_data(results2)
    data2_rws = organize_data(results2_rws)
    data3 = organize_data(results3)
    data3_rws = organize_data(results3_rws)
    data4 = organize_data(results4)
    data4_rws = organize_data(results4_rws)

    # Sort array sizes
    sorted_array_sizes = sorted(data1.keys(), key=lambda x: int(x.split('x')[0]))
    x_positions = []  # X positions of scatter points
    sparsity_labels = []
    array_labels_positions = []
    current_x = 0

    plt.figure(figsize=(18, 10))

    # Generate scatter points for both files
    for array_size in sorted_array_sizes:
        sparsity_ratios = sorted(data1[array_size].keys(), key=lambda x: int(x.split(':')[0]))  # Sort N:M
        start_x = current_x  # Start position for this array size group

        for sr in sparsity_ratios:
            # Scatter for output_results1.csv
            plt.scatter(
                current_x, data1[array_size][sr],
                color='tab:blue', alpha=1, label="File 1" if current_x == 0 else "", s=50
            )
            # Scatter for output_results2.csv
            plt.scatter(
                current_x, data1_rws[array_size][sr],
                color='tab:blue', alpha=0.5, label="File 1 RWS" if current_x == 0 else "", s=50
            )
            # Scatter for output_results1.csv
            plt.scatter(
                current_x, data2[array_size][sr],
                color='tab:orange', alpha=1, label="File 2" if current_x == 0 else "", s=50
            )
            # Scatter for output_results2.csv
            plt.scatter(
                current_x, data2_rws[array_size][sr],
                color='tab:orange', alpha=0.5, label="File 2 RWS" if current_x == 0 else "", s=50
            )
            # Scatter for output_results1.csv
            plt.scatter(
                current_x, data3[array_size][sr],
                color='tab:green', alpha=1, label="File 3" if current_x == 0 else "", s=50
            )
            # Scatter for output_results2.csv
            plt.scatter(
                current_x, data3_rws[array_size][sr],
                color='tab:green', alpha=0.5, label="File 3 RWS" if current_x == 0 else "", s=50
            )
            # Scatter for output_results1.csv
            plt.scatter(
                current_x, data4[array_size][sr],
                color='tab:red', alpha=1, label="File 4" if current_x == 0 else "", s=50
            )
            # Scatter for output_results2.csv
            plt.scatter(
                current_x, data4_rws[array_size][sr],
                color='tab:red', alpha=0.5, label="File 4 RWS" if current_x == 0 else "", s=50
            )

            x_positions.append(current_x)
            sparsity_labels.append(sr)
            current_x += 1  # Move to next position

        # Calculate center position for array size labels
        end_x = current_x - 1
        group_mid = (start_x + end_x) / 2
        array_labels_positions.append((group_mid, array_size))

        # Add space after each array size group
        current_x += 1

    # Formatting x-axis
    plt.xticks(x_positions, sparsity_labels, rotation=90, fontsize=20)
    plt.yticks(fontsize=26)
    plt.xlabel("Sparsity Ratios", fontsize=26, labelpad=45)
    plt.ylabel("Compute Cycles", fontsize=26)
    # plt.title("Compute Cycles Variation for GEMM M,N,K = 1000,1000,1000", fontsize=14)
    plt.yscale("log")  # Logarithmic Y-axis

    # Increase bottom margin to accommodate array size labels
    plt.subplots_adjust(bottom=0.3)

    # Print array size labels centered below each group
    for position, label in array_labels_positions:
        plt.text(position, min(min(d.values()) for d in (data1.values())) * 0.18, label,
                 ha='center', va='top', fontsize=26, color="#000000")
    for position, label in array_labels_positions:
        plt.text(position, min(min(d.values()) for d in (data1.values())) * 0.12, "32x32",
                 ha='center', va='top', fontsize=26, color="#000000", alpha=0.7)

    # Add legend
    plt.legend(["ViT-S Variable PE array with blocksize = PE array dimension", "ViT-S Fixed 32x32 with variable block sizes = 4,8,16,32",
                "ViT-B Variable PE array with blocksize = PE array dimension", "ViT-B Fixed 32x32 with variable block sizes = 4,8,16,32",
                "ViT-L Variable PE array with blocksize = PE array dimension", "ViT-L Fixed 32x32 with variable block sizes = 4,8,16,32",
                "ViT-H Variable PE array with blocksize = PE array dimension", "ViT-H Fixed 32x32 with variable block sizes = 4,8,16,32"], 
                fontsize=18)

    plt.tight_layout()
    plt.savefig(output_filename)
    print(f"Scatter plot saved to {output_filename}")
    plt.show()


if __name__ == "__main__":
    main()
