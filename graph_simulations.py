import os
import subprocess
import csv

# Define paths
cfg_path = "configs/new"
csv_path = "topologies/sparsity/new"
results_path = "sparsity_results/new"
output_csv_path = "output_results.csv"
scalesim_command_template = "python3 scalesim/scale.py -c {cfg_file} -t {csv_file} -p {results_path} -i gemm"

# Ensure directories exist
os.makedirs(cfg_path, exist_ok=True)
os.makedirs(csv_path, exist_ok=True)
os.makedirs(results_path, exist_ok=True)

# Toggle knobs
generate_cfg = True  # Switch to False to skip .cfg file generation
generate_csv = True  # Switch to False to skip .csv file generation

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
OptimizedMapping : false
BlockSize : {array_height}

[run_presets]
InterfaceBandwidth: USER"""

# Function to generate .csv content
def generate_csv_content(array_height, array_width, sparsity):
    return f"L,M,N,K,Sparsity,\nL0,256,512,768,{sparsity},"

# Main script
def main():
    array_sizes = [(4, 4), (8, 8), (16, 16), (32, 32)]  # Possible ArrayHeight and ArrayWidth values
    commands = []  # To store all generated commands
    results = []  # To store results for the output CSV

    for ah, aw in array_sizes:
        # Generate .cfg file if enabled
        cfg_filename = f"lws_{ah}x{aw}.cfg"
        cfg_filepath = os.path.join(cfg_path, cfg_filename)
        if generate_cfg:
            with open(cfg_filepath, "w") as cfg_file:
                cfg_file.write(generate_cfg_content(ah, aw))
            print(f"Generated CFG: {cfg_filepath}")
        else:
            print(f"Skipping CFG generation for: {cfg_filepath}")
        
        # Generate .csv files for each sparsity ratio (1:M to M:M)
        for n in range(1, ah + 1):  # N varies from 1 to M where M=ArrayHeight
            sparsity_ratio = f"{n}:{ah}"
            csv_filename = f"lws_gemm_{ah}x{aw}_{n}x{ah}.csv"
            csv_filepath = os.path.join(csv_path, csv_filename)
            
            if generate_csv:
                with open(csv_filepath, "w") as csv_file:
                    csv_file.write(generate_csv_content(ah, aw, sparsity_ratio))
                print(f"Generated CSV: {csv_filepath}")
            else:
                print(f"Skipping CSV generation for: {csv_filepath}")
            
            # Generate the simulation command
            command = scalesim_command_template.format(
                cfg_file=cfg_filepath,
                csv_file=csv_filepath,
                results_path=results_path
            )
            commands.append((command, f"{ah}x{aw}", sparsity_ratio))  # Store command with context

    print("\nExecuting Commands...\n")
    
    for command, array_size, sparsity_ratio in commands:
        try:
            # Execute the command
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            # Parse the output to extract compute cycles
            output = result.stdout
            error = result.stderr
            compute_cycles = None
            if "COMPUTE CYCLES =" in output:
                compute_cycles = output.split("COMPUTE CYCLES =")[1].strip().split()[0]
            elif error:
                print(f"Error encountered: {error}")

            # Store result in the results list
            if compute_cycles:
                results.append([f"lws_{array_size}", array_size, sparsity_ratio, compute_cycles])
                print(f"Extracted: {array_size}, {sparsity_ratio}, {compute_cycles}")
            else:
                print(f"Failed to extract compute cycles for command: {command}")
        
        except Exception as e:
            print(f"Error executing command: {command}\n{e}")
    
    # Write results to output CSV
    with open(output_csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["LWS", "Array Size", "Sparsity Ratio", "Compute Cycles"])  # Header
        writer.writerows(results)
    
    print(f"\nResults saved to {output_csv_path}")

if __name__ == "__main__":
    main()
