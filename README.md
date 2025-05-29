# QuixBugs Repair Agent

An LLM-powered agent that automatically detects and fixes single-line defects in Python programs from the QuixBugs benchmark using Google's Gemini API.

## Overview

This project implements an intelligent repair agent that:
- Analyzes defective Python programs from the QuixBugs dataset
- Identifies single-line defects using pattern recognition and LLM analysis
- Generates fixes based on 14 identified defect patterns
- Validates repairs using the built-in test harness

## Defect Patterns

Based on analysis of the 40 QuixBugs programs, we identified 14 defect classes:

1. **ARGUMENT_ORDER** - Arguments passed to function in wrong order
2. **COMPARISON_OPERATOR** - Wrong comparison operator used (>, <, >=, <=)
3. **BITWISE_OPERATOR** - Wrong bitwise operator used (&, |, ^)
4. **INCORRECT_RETURN** - Wrong value or expression returned
5. **OFF_BY_ONE** - Off-by-one error in index or boundary
6. **MISSING_CONDITION** - Missing condition in if/while statement
7. **VARIABLE_MISUSE** - Wrong variable used in expression
8. **INITIALIZATION_ERROR** - Variable initialized with wrong value
9. **LOOP_CONDITION** - Wrong loop termination condition
10. **ARITHMETIC_ERROR** - Wrong arithmetic operation or expression
11. **MISSING_STATEMENT** - Missing statement or operation
12. **COLLECTION_MODIFICATION** - Incorrect collection operation
13. **LOGICAL_OPERATOR** - Wrong logical operator (and, or, not)
14. **TYPE_ERROR** - Type-related error

## Installation

1. Install uv package manager:
```bash
pip install uv
```

2. Install dependencies:
```bash
uv add google-generativeai pytest rich pydantic python-dotenv
```

3. Set up environment variables:
```bash
cp env.example .env
# Edit .env and add your Gemini API key
```

## Usage

### Repair a single program:
```bash
uv run python repair_agent.py gcd
```

### Repair all programs:
```bash
uv run python repair_agent.py
```

### Test a repaired program:
```bash
uv run python test_single_repair.py gcd
```

## Project Structure

```
.
├── Data/
│   ├── python_programs/        # Defective programs
│   ├── correct_python_programs/# Correct versions
│   ├── fixed_programs/         # Our fixed versions
│   ├── json_testcases/         # Test cases
│   └── tester.py              # Test harness
├── defect_patterns.py         # Defect pattern definitions
├── repair_agent.py            # Main repair agent
├── test_single_repair.py      # Single program test utility
└── README.md
```

## How It Works

1. **Analysis**: The agent reads the defective program and runs tests to identify failures
2. **Pattern Matching**: Using the 14 defect patterns, it provides context to the LLM
3. **Repair Generation**: Gemini analyzes the code and generates a fix
4. **Validation**: The fix is applied and tested using the QuixBugs test harness
5. **Results**: Success rate and defect distribution are reported

## Output

The agent generates:
- Fixed programs in `Data/fixed_programs/`
- Detailed results in `repair_results.json`
- Console output with success statistics and defect type distribution

## Performance

The agent aims to achieve high success rates on the QuixBugs benchmark by:
- Leveraging pattern recognition for common defect types
- Using Gemini's code understanding capabilities
- Validating all fixes against the test suite
