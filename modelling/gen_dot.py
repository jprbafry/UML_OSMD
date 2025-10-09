import os
import subprocess

# Absolute paths
PYTHON_SRC = os.path.expanduser("~/OSMD")
OUTPUT_DIR = os.path.expanduser("~/OSMD_Trainees/modelling")

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

for root, dirs, files in os.walk(PYTHON_SRC):
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            base = os.path.splitext(file)[0]
            dot_path = os.path.join(f"{OUTPUT_DIR}/dot", f"{base}.dot")
            png_path = os.path.join(f"{OUTPUT_DIR}/img/png", f"DOT_{base}.png")
            
            print(f"Processing {filepath} ...")
            
            # Generate DOT file
            with open(dot_path, "w") as dot_file:
                subprocess.run(["pyan3", filepath, "--dot"], stdout=dot_file)
            
            # Convert DOT to PNG
            subprocess.run(["dot", "-Tpng", dot_path, "-o", png_path])

print(f"All call graphs saved in {OUTPUT_DIR}")
