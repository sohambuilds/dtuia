"""
Defect patterns and repair strategies for QuixBugs benchmark.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class DefectPattern:
    """Represents a single defect pattern with examples and repair strategy."""
    name: str
    description: str
    examples: List[Tuple[str, str]]  # (buggy_code, fixed_code)
    repair_strategy: str


# Common defect patterns found in QuixBugs
DEFECT_PATTERNS = [
    DefectPattern(
        name="ARGUMENT_ORDER",
        description="Arguments passed in wrong order to function calls",
        examples=[
            ("return gcd(a % b, b)", "return gcd(b, a % b)"),
            ("op(token, a, b)", "op(token, b, a)")
        ],
        repair_strategy="Check function signature and swap arguments"
    ),
    
    DefectPattern(
        name="COMPARISON_OPERATOR",
        description="Wrong comparison operator used",
        examples=[
            ("if x > pivot:", "if x >= pivot:"),
            ("if len(arr) == 0:", "if len(arr) <= 1:")
        ],
        repair_strategy="Review logic and use correct comparison operator"
    ),
    
    DefectPattern(
        name="BITWISE_OPERATOR",
        description="Incorrect bitwise operation",
        examples=[
            ("n ^= n - 1", "n &= n - 1")
        ],
        repair_strategy="Use correct bitwise operator for algorithm"
    ),
    
    DefectPattern(
        name="INCORRECT_RETURN",
        description="Wrong value or expression returned",
        examples=[
            ("yield flatten(x)", "yield x"),
            ("return True", "return depth == 0")
        ],
        repair_strategy="Return the correct value based on function purpose"
    ),
    
    DefectPattern(
        name="OFF_BY_ONE",
        description="Index or range off by one",
        examples=[
            ("for i in range(a, b + 1 - k):", "for i in range(a, b - k + 2):"),
            ("upright = rows[r - 1][c] if c < r else 0", "upright = rows[r - 1][c] if c < r - 1 else 0")
        ],
        repair_strategy="Adjust index/range bounds by one"
    ),
    
    DefectPattern(
        name="MISSING_CONDITION",
        description="Missing boundary check or guard condition",
        examples=[
            ("if node in nodesvisited:", "if node in nodesvisited or node is None:"),
            ("while opstack and precedence[token] <= precedence[opstack[-1]]:", 
             "while opstack and token in precedence and precedence[token] <= precedence[opstack[-1]]:")
        ],
        repair_strategy="Add necessary boundary or null checks"
    ),
    
    DefectPattern(
        name="VARIABLE_MISUSE",
        description="Wrong variable used in expression",
        examples=[
            ("for i, count in enumerate(arr):", "for i, count in enumerate(counts):"),
            ("weight_by_edge[u, v] = min(", "weight_by_node[v] = min(")
        ],
        repair_strategy="Use the correct variable name"
    ),
    
    DefectPattern(
        name="INITIALIZATION_ERROR",
        description="Variable initialized to wrong value",
        examples=[
            ("max_so_far = 0", "max_so_far = -float('inf')")
        ],
        repair_strategy="Initialize with appropriate starting value"
    ),
    
    DefectPattern(
        name="LOOP_CONDITION",
        description="Incorrect loop termination condition",
        examples=[
            ("while lo <= hi:", "while lo < hi:"),
            ("for x in arr:", "for x in arr[k:]:")
        ],
        repair_strategy="Fix loop bounds or iteration range"
    ),
    
    DefectPattern(
        name="ARITHMETIC_ERROR",
        description="Wrong arithmetic operation or operand",
        examples=[
            ("return 1 + levenshtein(source[1:], target[1:])", "return levenshtein(source[1:], target[1:])"),
            ("return kth(above, k)", "return kth(above, k - num_lessoreq)")
        ],
        repair_strategy="Use correct arithmetic operation"
    ),
    
    DefectPattern(
        name="MISSING_STATEMENT",
        description="Required statement omitted",
        examples=[
            ("return [[first] + subset for subset in rest_subsets]", 
             "return [[first] + subset for subset in rest_subsets] + rest_subsets"),
            ("return lines", "return lines + [text]")
        ],
        repair_strategy="Add the missing statement or operation"
    ),
    
    DefectPattern(
        name="COLLECTION_MODIFICATION",
        description="Modifying collection during iteration",
        examples=[
            ("for item in collection: collection.remove(item)", 
             "for item in list(collection): collection.remove(item)")
        ],
        repair_strategy="Create copy before modifying or use different approach"
    ),
    
    DefectPattern(
        name="LOGICAL_OPERATOR",
        description="Wrong logical operator (and/or/not)",
        examples=[
            ("if any(n % p > 0 for p in primes):", "if all(n % p > 0 for p in primes):")
        ],
        repair_strategy="Use correct logical operator for the condition"
    ),
    
    DefectPattern(
        name="TYPE_ERROR",
        description="Type mismatch or wrong type operation",
        examples=[
            ("if group_by_node.setdefault(u, {u}) != group_by_node.setdefault(v, {v}):",
             "if group_by_node.setdefault(u, {u}) is not group_by_node.setdefault(v, {v}):")
        ],
        repair_strategy="Use correct type comparison or operation"
    )
]


def get_pattern_by_name(name: str) -> DefectPattern:
    """Get defect pattern by name."""
    for pattern in DEFECT_PATTERNS:
        if pattern.name == name:
            return pattern
    raise ValueError(f"Unknown defect pattern: {name}")


def get_all_pattern_names() -> List[str]:
    """Get list of all defect pattern names."""
    return [pattern.name for pattern in DEFECT_PATTERNS] 