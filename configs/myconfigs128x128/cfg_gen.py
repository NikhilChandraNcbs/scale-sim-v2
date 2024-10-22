import os

# Define the template based on the sample formatting
template_cfg = '''# python3 scalesim/scale.py -c configs/myconfigs{arraysize}/{run_name}.cfg -t topologies/conv_nets/{model}.csv -p sparsesim/sparsity_results > {run_name}.txt
[general]
# Name of the folder which will contain output csv files
run_name = {run_name}

[architecture_presets]

ArrayHeight : {ArrayHeight}
ArrayWidth :  {ArrayWidth}

IfmapSramSzkB:   {size_kb}
FilterSramSzkB:  {size_kb}
OfmapSramSzkB:   {size_kb}

# Dataflow can be either one of ws/os/is
Dataflow : ws

# The below numbers represent the address offsets in DRAM
IfmapOffset:    0
FilterOffset:   100
OfmapOffset:    200

MemoryBanks:   1

# The number of addresses that get fetched from DRAM to SRAM in one cycle
Bandwidth : 50

[sparsity]
# true or false
SparsitySupport : true
# csr, csc or ellpack_block
SparseRep : ellpack_block
# NonZeroElems is N in N:M
NonZeroElems : {NonZeroElems}
# BlockSize is M in N:M
BlockSize : {BlockSize}
# optimization in mapping is set to true or false
OptimizedMapping : false

[run_presets]
# CALC = no memory stalls, USER = memory stalls considered
InterfaceBandwidth: USER
'''

# Define the parameters for generating the config files
models = ["Resnet18"]
sizes = {"1kb": 1, "16kb": 16, "64kb": 64, "256kb": 256, "1mb": 1024, "5mb": 5120, "10mb": 10240, "50mb": 51200, "100mb": 102400}
sparsities = {"1s4": (1, 4), "2s4": (2, 4), "4s4": (4, 4)}
arraysizes = {"128x128": (128, 128)}

# Path to store the generated cfg files
output_path = "./"

# Ensure the output directory exists
os.makedirs(output_path, exist_ok=True)

# Function to generate a single cfg file with the correct format
def generate_formatted_cfg(model, size_label, size_value, sparsity_label, sparsity_value, arraysize_label, arraysize_value):
    # File name and run_name
    run_name = f"{model}_{size_label}_{sparsity_label}_{arraysize_label}"
    
    # Prepare the content using the template
    content = template_cfg.format(
        model=model,
        arraysize=arraysize_label,
        run_name=run_name,
        ArrayHeight=arraysize_value[0],
        ArrayWidth=arraysize_value[1],
        size_kb=size_value,
        NonZeroElems=sparsity_value[0],
        BlockSize=sparsity_value[1]
    )
    
    # Write the file to disk
    file_path = os.path.join(output_path, f"{run_name}.cfg")
    with open(file_path, 'w') as file:
        file.write(content)

# Generate all possible cfg files
for model in models:
    for size_label, size_value in sizes.items():
        for sparsity_label, sparsity_value in sparsities.items():
            for arraysize_label, arraysize_value in arraysizes.items():
                generate_formatted_cfg(model, size_label, size_value, sparsity_label, sparsity_value, arraysize_label, arraysize_value)

print(f"Configuration files generated in: {output_path}")
