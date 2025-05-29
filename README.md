# QuixBugs Repair Agent

An LLM-powered agent that automatically detects and fixes single-line defects in Python programs from the QuixBugs benchmark using Google's Gemini API.

## Overview

This project implements an intelligent repair agent that:
- Analyzes defective Python programs from the QuixBugs dataset
- Identifies single-line defects using pattern recognition and LLM analysis
- Generates fixes based on 14 identified defect patterns
- Validates repairs using a comprehensive test framework
- **Achieved 80.5% success rate** (33/41 programs) on the QuixBugs benchmark

## Results Summary

Our agent successfully repaired **33 out of 41** programs from QuixBugs:

**✅ Successfully Fixed (33 programs):**
bitcount, breadth_first_search, bucketsort, depth_first_search, detect_cycle, find_first_in_sorted, find_in_sorted, flatten, gcd, get_factors, hanoi, is_valid_parenthesization, kheapsort, knapsack, kth, lcs_length, levenshtein, longest_common_subsequence, mergesort, minimum_spanning_tree, next_palindrome, next_permutation, quicksort, reverse_linked_list, rpn_eval, shortest_path_length, shortest_path_lengths, shortest_paths, sieve, sqrt, to_base, topological_ordering, wrap

**❌ Still Need Work (8 programs):**
lis, max_sublist_sum, node, pascal, possible_change, powerset, shunting_yard, subsequences

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
uv add google-generativeai pytest rich pydantic python-dotenv matplotlib seaborn pandas
```

3. Set up environment variables:
```bash
export GEMINI_API_KEY=your_api_key_here
```

## Usage

### Repair Programs

**Repair a single program:**
```bash
cd Data && python ../repair_agent.py gcd
```

**Repair all programs:**
```bash
python repair_agent.py
```

### Test Fixed Programs

**Test a single fixed program:**
```bash
cd Data && python tester2.py bitcount
```

**Test all fixed programs with full analysis:**
```bash
cd Data && python tester2.py
```

**Generate visualizations from saved results:**
```bash
cd Data && python create_visualizations.py
```

## Project Structure

```
.
├── Data/
│   ├── python_programs/        # Original defective programs
│   ├── correct_python_programs/# Reference correct versions
│   ├── fixed_programs/         # Our repaired versions
│   ├── json_testcases/         # Test cases for validation
│   ├── results/                # Organized test results
│   │   └── test_session_*/     # Timestamped test sessions
│   ├── tester.py              # Original test harness
│   ├── tester2.py             # Enhanced testing framework
│   └── create_visualizations.py # Standalone visualization script
├── defect_patterns.py         # Defect pattern definitions
├── repair_agent.py            # Main repair agent
├── test_single_repair.py      # Single program test utility
├── pyproject.toml            # Project dependencies
└── README.md
```

## How It Works

1. **Analysis**: The agent reads the defective program and runs tests to identify failures
2. **Pattern Matching**: Using the 14 defect patterns, it provides context to the LLM
3. **Repair Generation**: Gemini-2.0-flash analyzes the code and generates a fix
4. **Validation**: The fix is applied and tested using an enhanced test framework
5. **Results**: Comprehensive results with visualizations are generated

## Output & Results

The system generates multiple output formats:

**Fixed Programs:**
- Repaired code in `Data/fixed_programs/`
- Individual program results in JSON format

**Test Results (in `Data/results/test_session_*/`):**
- `test_results.json` - Complete detailed results
- `summary.json` - High-level statistics  
- `successful_programs.txt` - List of successful repairs
- `failed_programs.txt` - Analysis of failures
- `test_results_visualization.png/pdf` - Comprehensive charts

**Visualizations:**
- Overall success rate pie chart (80.5% success)
- Defect type distribution showing which patterns were most common
- Success rate histogram with 80% threshold line
- Test complexity vs success rate correlation
- Summary statistics and perfect scores tracking

## Performance Highlights

- **80.5% Success Rate** on QuixBugs benchmark
- **32 Perfect Scores** (100% test pass rate)
- **Robust timeout handling** for complex algorithms
- **Cross-platform compatibility** (Windows, macOS, Linux)
- **Publication-ready visualizations** (300 DPI PNG + PDF)

## Key Features

- **Smart timeout handling** - Different timeouts for complex algorithms
- **Comprehensive test validation** - Compares against reference implementations  
- **Beautiful visualizations** - Multiple chart types with professional styling
- **Organized results** - Timestamped sessions with multiple output formats
- **Error analysis** - Detailed breakdown of failure modes
- **Pattern-based repair** - Uses domain knowledge of common defect types

## Development Notes

The agent uses Gemini-2.0-flash for its strong code understanding capabilities. The testing framework includes timeout protection, cross-platform compatibility, and handles both regular programs and graph-based algorithms differently.

Results are automatically organized into timestamped sessions for easy comparison and analysis across different runs.
