

import sys
import subprocess
from pathlib import Path


def test_repair(program_name: str):
  
    print(f"\nTesting repair for {program_name}...")
    
    # Run the tester
    cmd = [sys.executable, "Data/tester.py", program_name]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    output = result.stdout + result.stderr
    print(output)
    
    # Check if fixed matches correct
    lines = output.split('\n')
    fixed_outputs = []
    correct_outputs = []
    
    for line in lines:
        if line.startswith("Fixed Python:"):
            fixed_outputs.append(line)
        elif line.startswith("Correct Python:"):
            correct_outputs.append(line)
    
    if fixed_outputs and correct_outputs:
        matches = sum(1 for f, c in zip(fixed_outputs, correct_outputs) 
                     if f.replace("Fixed", "Correct") == c)
        total = len(correct_outputs)
        
        print(f"\nResult: {matches}/{total} test cases passed")
        return matches == total
    
    return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_single_repair.py <program_name>")
        sys.exit(1)
    
    program_name = sys.argv[1]
    success = test_repair(program_name)
    
    if success:
        print(f"✓ {program_name} is correctly fixed!")
    else:
        print(f"✗ {program_name} repair failed") 