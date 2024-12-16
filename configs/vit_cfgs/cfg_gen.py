import os

# Define the template based on the sample formatting
template_cfg = '''# python3 scalesim/scale.py -c configs/vit_cfgs/{run_name}.cfg -t topologies/sparsity/{model}.csv -p sparsity_results/vit_results -i gemm > {run_name}.txt
[general]
run_name = {run_name}

[architecture_presets]
ArrayHeight : {ArrayHeight}
ArrayWidth :  {ArrayWidth}
IfmapSramSzkB:   {size_kb}
FilterSramSzkB:  {size_kb}
OfmapSramSzkB:   {size_kb}
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
BlockSize : {BlockSize}

[run_presets]
InterfaceBandwidth: USER
'''

# Define the parameters for generating the config files
models = ["vit_l", "vit_s", "vit_b"]
sizes = {"5mb": 5120, "1mb": 1024, "256kb": 256, "64kb": 64}
blocksize = {"b4": 4, "b8": 8, "b16": 16}
arraysizes = {"128x128": (128, 128), "64x64": (64, 64)}
commands = []

# Path to store the generated cfg files
output_path = "./"

# Ensure the output directory exists
os.makedirs(output_path, exist_ok=True)

# Function to generate a single cfg file with the correct format
def generate_formatted_cfg(model, size_label, size_value, block_label, block_value, arraysize_label, arraysize_value):
    # File name and run_name
    run_name = f"{model}_{size_label}_{block_label}_{arraysize_label}"
    
    # Prepare the content using the template
    content = template_cfg.format(
        model=model,
        arraysize=arraysize_label,
        run_name=run_name,
        ArrayHeight=arraysize_value[0],
        ArrayWidth=arraysize_value[1],
        size_kb=size_value,
        BlockSize=block_value
    )

    cmd = f"python3 scalesim/scale.py -c configs/vit_cfgs/{run_name}.cfg -t topologies/sparsity/{model}.csv -p sparsity_results/vit_results -i gemm > {run_name}.txt"
    commands.append(cmd)
    
    # Write the file to disk
    file_path = os.path.join(output_path, f"{run_name}.cfg")
    with open(file_path, 'w') as file:
        file.write(content)

# Generate all possible cfg files
for model in models:
    for arraysize_label, arraysize_value in arraysizes.items():
        for size_label, size_value in sizes.items():
            for block_label, block_value in blocksize.items():
                generate_formatted_cfg(model, size_label, size_value, block_label, block_value, arraysize_label, arraysize_value)

print(f"Configuration files generated in: {output_path}")
# for c in commands:
#     print(c)

file_path = os.path.join(output_path, f"cmds.txt")
with open(file_path, 'w') as file:
    for c in commands:
        file.write(c)
        file.write("\n")