import os
import subprocess

# Specify the directory containing the config files
config_dir = os.path.join('configs', 'myconfigs128x128_alexnet')

# Check if the directory exists
if not os.path.exists(config_dir):
    print(f"Directory '{config_dir}' does not exist.")
else:
    # Iterate over all files in the directory
    for filename in os.listdir(config_dir):
        # Only process .cfg files
        if filename.endswith('.cfg'):
            file_path = os.path.join(config_dir, filename)
            try:
                # Open and read the first line of the file
                with open(file_path, 'r') as file:
                    first_line = file.readline().strip()

                # Check if the first line is a comment
                if first_line.startswith("#"):
                    # Extract the command from the comment
                    command = first_line[2:].strip()
                    print(f"Executing command from {filename}: {command}")

                    # Execute the command using subprocess
                    process = subprocess.run(command, shell=True)
                    if process.returncode != 0:
                        print(f"Command failed with return code {process.returncode}")
                    else:
                        print(f"Command executed successfully for {filename}")
                else:
                    print(f"First line of {filename} is not a comment.")
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
