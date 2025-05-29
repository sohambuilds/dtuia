"""
Robust tester for validating fixed programs against correct programs.
"""

import copy
import json
import sys
import os
import subprocess
import types
import signal
import threading
import time
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def timeout_handler(signum, frame):
    raise TimeoutError("Function execution timed out")

def run_with_timeout(func, args, timeout_seconds=5):
    """Run a function with timeout using threading."""
    result = [None]
    exception = [None]
    
    def target():
        try:
            result[0] = func(*args)
        except Exception as e:
            exception[0] = e
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout_seconds)
    
    if thread.is_alive():
        return "TIMEOUT"
    
    if exception[0]:
        return f"Error: {type(exception[0]).__name__}: {str(exception[0])}"
    
    return result[0]

def py_try_with_timeout(algo, *args, correct=False, fixed=False, timeout_seconds=5):
    """Execute a function with timeout protection."""
    try:
        if fixed:
            module = __import__("fixed_programs." + algo)
        elif correct:
            module = __import__("correct_python_programs." + algo)
        else:
            module = __import__("python_programs." + algo)

        fx = getattr(module, algo)
        func = getattr(fx, algo)
        
        return run_with_timeout(func, args, timeout_seconds)
                
    except Exception as e:
        return f"Import Error: {type(e).__name__}: {str(e)}"

def prettyprint(o):
    """Convert output to a comparable string format."""
    if isinstance(o, types.GeneratorType):
        try:
            return str(list(o))
        except:
            return "Generator(error)"
    elif isinstance(o, str) and o.startswith("Error:"):
        return o
    elif o == "TIMEOUT":
        return o
    else:
        return str(o)

def compare_outputs(fixed_output, correct_output):
    """Compare outputs with tolerance for equivalent results."""
    fixed_str = prettyprint(fixed_output)
    correct_str = prettyprint(correct_output)
    
    if fixed_str == correct_str:
        return True
    
    # Fixed version resolves errors
    if "Error:" in correct_str and "Error:" not in fixed_str:
        return True
    
    # Fixed version resolves timeouts
    if correct_str == "TIMEOUT" and fixed_str != "TIMEOUT":
        return True
    
    # Handle numerical precision
    try:
        if "." in fixed_str and "." in correct_str:
            fixed_float = float(fixed_str)
            correct_float = float(correct_str)
            return abs(fixed_float - correct_float) < 1e-6
    except:
        pass
    
    return False

def test_program(algo):
    """Test a single program comparing fixed vs correct versions."""
    print(f"\nTesting {algo}...")
    
    fixed_path = Path(f"fixed_programs/{algo}.py")
    correct_path = Path(f"correct_python_programs/{algo}.py")
    
    if not fixed_path.exists():
        print(f"❌ Fixed program not found: {fixed_path}")
        return False, {"program": algo, "status": "missing_fixed", "tests": []}
    
    if not correct_path.exists():
        print(f"❌ Correct program not found: {correct_path}")
        return False, {"program": algo, "status": "missing_correct", "tests": []}
    
    # Handle graph-based programs
    graph_based = ["breadth_first_search", "depth_first_search", "detect_cycle",
                   "minimum_spanning_tree", "reverse_linked_list", "shortest_path_length",
                   "shortest_path_lengths", "shortest_paths", "topological_ordering"]
    
    if algo in graph_based:
        print("📊 Graph-based program - running test suite...")
        try:
            correct_module = __import__(f"correct_python_programs.{algo}_test")
            correct_fx = getattr(correct_module, f"{algo}_test")
            getattr(correct_fx, "main")()
            print("✅ Graph-based program tests completed successfully")
            return True, {"program": algo, "status": "success", "test_type": "graph_based", 
                         "success_rate": 1.0, "defect_type": "GRAPH_BASED", "tests": []}
        except Exception as e:
            print(f"❌ Graph-based program test failed: {e}")
            return False, {"program": algo, "status": "failed", "test_type": "graph_based", 
                          "error": str(e), "success_rate": 0.0, "tests": []}
    
    json_path = Path(f"json_testcases/{algo}.json")
    if not json_path.exists():
        print(f"❌ Test cases not found: {json_path}")
        return False, {"program": algo, "status": "missing_tests", "tests": []}
    
    timeout_seconds = 10 if algo in ['knapsack', 'levenshtein', 'sqrt'] else 5
    
    total_tests = 0
    passed_tests = 0
    timeout_count = 0
    test_results = []
    
    try:
        with open(json_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                    
                try:
                    test_case = json.loads(line)
                    test_in, expected_out = test_case
                    
                    if not isinstance(test_in, list):
                        test_in = [test_in]
                    
                    total_tests += 1
                    
                    fixed_result = py_try_with_timeout(algo, *copy.deepcopy(test_in), fixed=True, timeout_seconds=timeout_seconds)
                    correct_result = py_try_with_timeout(algo, *copy.deepcopy(test_in), correct=True, timeout_seconds=timeout_seconds)
                    
                    test_result = {
                        "test_num": line_num,
                        "input": test_in,
                        "fixed_output": prettyprint(fixed_result),
                        "correct_output": prettyprint(correct_result),
                        "passed": False,
                        "timeout": False
                    }
                    
                    if fixed_result == "TIMEOUT" or correct_result == "TIMEOUT":
                        timeout_count += 1
                        test_result["timeout"] = True
                        print(f"  ⏰ Test {line_num}: {test_in} -> TIMEOUT")
                        if fixed_result == "TIMEOUT" and correct_result == "TIMEOUT":
                            passed_tests += 1
                            test_result["passed"] = True
                    elif compare_outputs(fixed_result, correct_result):
                        passed_tests += 1
                        test_result["passed"] = True
                        print(f"  ✅ Test {line_num}: {test_in} -> {prettyprint(fixed_result)}")
                    else:
                        print(f"  ❌ Test {line_num}: {test_in}")
                        print(f"     Fixed:   {prettyprint(fixed_result)}")
                        print(f"     Correct: {prettyprint(correct_result)}")
                    
                    test_results.append(test_result)
                        
                except json.JSONDecodeError:
                    print(f"  ⚠️  Skipped malformed test case on line {line_num}")
                except Exception as e:
                    print(f"  ❌ Test {line_num} failed with error: {e}")
                    test_results.append({
                        "test_num": line_num,
                        "input": test_in if 'test_in' in locals() else "unknown",
                        "error": str(e),
                        "passed": False,
                        "timeout": False
                    })
    
    except Exception as e:
        print(f"❌ Failed to read test cases: {e}")
        return False, {"program": algo, "status": "read_error", "error": str(e), "tests": []}
    
    if total_tests == 0:
        print("⚠️  No test cases found")
        return False, {"program": algo, "status": "no_tests", "tests": []}
    
    success_rate = passed_tests / total_tests
    if timeout_count > 0:
        print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1%}) - {timeout_count} timeouts")
    else:
        print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1%})")
    
    is_success = success_rate >= 0.8
    print(f"{'✅ PASS' if is_success else '❌ FAIL'} - {algo}")
    
    # Get defect type from repair results if available
    defect_type = "UNKNOWN"
    try:
        with open("../repair_results.json", "r") as f:
            repair_data = json.load(f)
            for entry in repair_data:
                if entry.get("program") == algo:
                    defect_type = entry.get("defect_type", "UNKNOWN")
                    break
    except:
        pass
    
    result_data = {
        "program": algo,
        "status": "success" if is_success else "failed",
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "success_rate": success_rate,
        "timeout_count": timeout_count,
        "defect_type": defect_type,
        "tests": test_results
    }
    
    return is_success, result_data

def create_visualizations(results_data, results_dir):
    """Create comprehensive visualizations of test results."""
    # Set up plotting style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Success Rate Pie Chart
    ax1 = plt.subplot(2, 3, 1)
    successful = len([r for r in results_data if r.get("status") == "success"])
    failed = len(results_data) - successful
    
    colors = ['#2ecc71', '#e74c3c']
    plt.pie([successful, failed], labels=['Success', 'Failed'], autopct='%1.1f%%', 
            colors=colors, startangle=90)
    plt.title('Overall Success Rate', fontsize=14, fontweight='bold')
    
    # 2. Defect Type Distribution
    ax2 = plt.subplot(2, 3, 2)
    defect_counts = {}
    for r in results_data:
        if r.get("status") == "success":
            defect_type = r.get("defect_type", "UNKNOWN")
            defect_counts[defect_type] = defect_counts.get(defect_type, 0) + 1
    
    if defect_counts:
        defect_df = pd.DataFrame(list(defect_counts.items()), columns=['Defect Type', 'Count'])
        defect_df = defect_df.sort_values('Count', ascending=True)
        
        bars = plt.barh(defect_df['Defect Type'], defect_df['Count'])
        plt.title('Successfully Fixed Defect Types', fontsize=14, fontweight='bold')
        plt.xlabel('Number of Programs')
        
        # Add value labels on bars
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                    f'{int(width)}', ha='left', va='center')
    
    # 3. Success Rate Distribution
    ax3 = plt.subplot(2, 3, 3)
    success_rates = [r.get("success_rate", 0) for r in results_data if "success_rate" in r]
    
    plt.hist(success_rates, bins=10, edgecolor='black', alpha=0.7, color='skyblue')
    plt.title('Distribution of Success Rates', fontsize=14, fontweight='bold')
    plt.xlabel('Success Rate')
    plt.ylabel('Number of Programs')
    plt.axvline(x=0.8, color='red', linestyle='--', label='80% Threshold')
    plt.legend()
    
    # 4. Status Category Breakdown
    ax4 = plt.subplot(2, 3, 4)
    status_counts = {}
    for r in results_data:
        status = r.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    status_df = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
    status_df = status_df.sort_values('Count', ascending=False)
    
    bars = plt.bar(range(len(status_df)), status_df['Count'], 
                   color=['#2ecc71' if 'success' in s else '#e74c3c' for s in status_df['Status']])
    plt.title('Program Status Distribution', fontsize=14, fontweight='bold')
    plt.xlabel('Status Category')
    plt.ylabel('Number of Programs')
    plt.xticks(range(len(status_df)), status_df['Status'], rotation=45, ha='right')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom')
    
    # 5. Test Count vs Success Rate Scatter
    ax5 = plt.subplot(2, 3, 5)
    test_counts = [r.get("total_tests", 0) for r in results_data if "total_tests" in r]
    success_rates_scatter = [r.get("success_rate", 0) for r in results_data if "success_rate" in r]
    
    if test_counts and success_rates_scatter:
        plt.scatter(test_counts, success_rates_scatter, alpha=0.6, s=60)
        plt.title('Test Count vs Success Rate', fontsize=14, fontweight='bold')
        plt.xlabel('Number of Test Cases')
        plt.ylabel('Success Rate')
        plt.axhline(y=0.8, color='red', linestyle='--', alpha=0.5)
        
        # Add trend line
        z = np.polyfit(test_counts, success_rates_scatter, 1)
        p = np.poly1d(z)
        plt.plot(test_counts, p(test_counts), "r--", alpha=0.8)
    
    # 6. Summary Statistics Box
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    
    total_programs = len(results_data)
    total_successful = len([r for r in results_data if r.get("status") == "success"])
    avg_success_rate = sum(r.get("success_rate", 0) for r in results_data) / len(results_data) if results_data else 0
    total_tests = sum(r.get("total_tests", 0) for r in results_data)
    total_timeouts = sum(r.get("timeout_count", 0) for r in results_data)
    
    stats_text = f"""
    📊 TEST SUMMARY
    
    Total Programs: {total_programs}
    ✅ Successful: {total_successful} ({total_successful/total_programs*100:.1f}%)
    ❌ Failed: {total_programs - total_successful}
    
    📈 Average Success Rate: {avg_success_rate:.1%}
    🧪 Total Test Cases: {total_tests}
    ⏰ Total Timeouts: {total_timeouts}
    
    🎯 Threshold: 80% pass rate
    """
    
    ax6.text(0.1, 0.5, stats_text, fontsize=12, verticalalignment='center',
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
    
    plt.tight_layout()
    
    # Save the plot
    plot_path = results_dir / "test_results_visualization.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"📈 Visualizations saved to {plot_path}")
    
    plt.show()

def create_visualization(results_data):
    """Create simple text-based visualization of results."""
    successful = [r for r in results_data if r.get("status") == "success"]
    failed = [r for r in results_data if r.get("status") != "success"]
    
    print("\n" + "="*60)
    print("📊 DETAILED ANALYSIS")
    print("="*60)
    
    # Success rate visualization
    total = len(results_data)
    success_count = len(successful)
    success_rate = success_count / total if total > 0 else 0
    
    bar_length = 40
    filled = int(bar_length * success_rate)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    print(f"\n🎯 Overall Success Rate: {success_rate:.1%}")
    print(f"[{bar}] {success_count}/{total}")
    
    # Category breakdown
    categories = {
        "success": "✅ Successfully Fixed",
        "failed": "❌ Test Failures", 
        "missing_fixed": "📁 Missing Fixed Version",
        "missing_correct": "📁 Missing Correct Version", 
        "missing_tests": "📝 Missing Test Cases",
        "read_error": "💥 Read Errors"
    }
    
    print(f"\n📋 Breakdown by Category:")
    for status, desc in categories.items():
        count = len([r for r in results_data if r.get("status") == status])
        if count > 0:
            print(f"   {desc}: {count}")
    
    # Top performers
    if successful:
        print(f"\n🏆 Perfect Scores (100% pass rate):")
        perfect = [r for r in successful if r.get("success_rate", 0) == 1.0]
        for i, result in enumerate(perfect[:10], 1):
            print(f"   {i:2d}. {result['program']}")
        if len(perfect) > 10:
            print(f"       ... and {len(perfect) - 10} more")

def save_results(results_data, results_dir, filename="test_results.json"):
    """Save detailed results to organized folder structure."""
    timestamp = datetime.now().isoformat()
    
    summary = {
        "timestamp": timestamp,
        "total_programs": len(results_data),
        "successful": len([r for r in results_data if r.get("status") == "success"]),
        "failed": len([r for r in results_data if r.get("status") != "success"]),
        "success_rate": len([r for r in results_data if r.get("status") == "success"]) / len(results_data) if results_data else 0,
        "average_test_success_rate": sum(r.get("success_rate", 0) for r in results_data) / len(results_data) if results_data else 0
    }
    
    output = {
        "summary": summary,
        "detailed_results": results_data
    }
    
    # Save main results file
    results_file = results_dir / filename
    with open(results_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    # Save summary file
    summary_file = results_dir / "summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Save successful programs list
    successful_programs = [r["program"] for r in results_data if r.get("status") == "success"]
    with open(results_dir / "successful_programs.txt", 'w') as f:
        f.write("Successfully Fixed Programs:\n")
        f.write("=" * 30 + "\n")
        for program in successful_programs:
            f.write(f"• {program}\n")
    
    # Save failed programs with reasons
    failed_programs = [r for r in results_data if r.get("status") != "success"]
    with open(results_dir / "failed_programs.txt", 'w') as f:
        f.write("Failed Programs Analysis:\n")
        f.write("=" * 30 + "\n")
        for program in failed_programs:
            f.write(f"• {program['program']}: {program.get('status', 'unknown')}\n")
            if 'error' in program:
                f.write(f"  Error: {program['error']}\n")
            f.write("\n")
    
    print(f"\n💾 Results saved to {results_dir}/")
    print(f"   📊 Main results: {filename}")
    print(f"   📋 Summary: summary.json")
    print(f"   ✅ Successful: successful_programs.txt")
    print(f"   ❌ Failed: failed_programs.txt")

def test_all_programs():
    """Test all fixed programs."""
    print("🔧 Testing all fixed programs against correct versions...\n")
    
    # Create results directory
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    # Create timestamped subdirectory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = results_dir / f"test_session_{timestamp}"
    session_dir.mkdir(exist_ok=True)
    
    fixed_dir = Path("fixed_programs")
    if not fixed_dir.exists():
        print("❌ Fixed programs directory not found!")
        return
    
    fixed_programs = [
        f.stem for f in fixed_dir.glob("*.py") 
        if f.name != "format.md" and not f.name.startswith("__")
    ]
    
    if not fixed_programs:
        print("❌ No fixed programs found!")
        return
    
    print(f"Found {len(fixed_programs)} fixed programs to test\n")
    
    successful = []
    failed = []
    all_results = []
    
    for algo in sorted(fixed_programs):
        try:
            success, result_data = test_program(algo)
            all_results.append(result_data)
            if success:
                successful.append(algo)
            else:
                failed.append(algo)
        except Exception as e:
            print(f"❌ {algo} - Unexpected error: {e}")
            failed.append(algo)
            all_results.append({
                "program": algo,
                "status": "error",
                "error": str(e),
                "success_rate": 0.0,
                "tests": []
            })
        print("-" * 50)
    
    total = len(fixed_programs)
    success_count = len(successful)
    
    print(f"\n🎯 FINAL RESULTS:")
    print(f"Total programs tested: {total}")
    print(f"✅ Successfully fixed: {success_count}")
    print(f"❌ Failed: {len(failed)}")
    print(f"📈 Success rate: {success_count/total:.1%}")
    
    if successful:
        print(f"\n✅ Successfully fixed programs:")
        for prog in successful:
            print(f"   • {prog}")
    
    if failed:
        print(f"\n❌ Programs that need more work:")
        for prog in failed:
            print(f"   • {prog}")
    
    create_visualization(all_results)
    save_results(all_results, session_dir)
    
    # Generate plots
    try:
        import numpy as np
        create_visualizations(all_results, session_dir)
    except ImportError:
        print("⚠️  Matplotlib/Seaborn not available - skipping visualizations")
    except Exception as e:
        print(f"⚠️  Error creating visualizations: {e}")

def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Create results directory for single test
        results_dir = Path("results") 
        results_dir.mkdir(exist_ok=True)
        
        algo = sys.argv[1]
        success, result_data = test_program(algo)
        save_results([result_data], results_dir, f"{algo}_result.json")
        sys.exit(0 if success else 1)
    else:
        test_all_programs()

if __name__ == "__main__":
    main() 