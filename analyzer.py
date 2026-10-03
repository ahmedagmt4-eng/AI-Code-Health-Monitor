import ast
import re
from collections import Counter


def _safe_unparse(node):
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _max_nesting(tree):
    max_depth = 0
    control_nodes = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith, ast.Try)

    def walk(node, depth=0):
        nonlocal max_depth
        new_depth = depth + 1 if isinstance(node, control_nodes) else depth
        max_depth = max(max_depth, new_depth)
        for child in ast.iter_child_nodes(node):
            walk(child, new_depth)

    walk(tree)
    return max_depth


def _cyclomatic(tree):
    # Approximate cyclomatic complexity: 1 + decision points.
    decisions = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.IfExp, ast.ExceptHandler)):
            decisions += 1
        elif isinstance(node, ast.BoolOp):
            decisions += max(0, len(node.values) - 1)
        elif isinstance(node, (ast.comprehension,)):
            decisions += 1 + len(node.ifs)
    return 1 + decisions


def _function_metrics(tree):
    functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    lengths = []
    long_functions = []
    for fn in functions:
        start = getattr(fn, "lineno", 1)
        end = getattr(fn, "end_lineno", start)
        length = end - start + 1
        lengths.append(length)
        if length > 30:
            long_functions.append({"name": fn.name, "lines": length})
    return functions, lengths, long_functions


def _duplicate_lines(source):
    lines = [re.sub(r"\s+", " ", x.strip()) for x in source.splitlines()]
    meaningful = [x for x in lines if x and not x.startswith("#")]
    counts = Counter(meaningful)
    duplicated = sum(1 for line, count in counts.items() if count > 1 and len(line) >= 12)
    return duplicated


def _unused_variables(tree):
    assigned = []
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store):
                assigned.append(node.id)
            elif isinstance(node.ctx, ast.Load):
                used.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for arg in node.args.args:
                used.add(arg.arg)
    return sorted({name for name in assigned if name not in used and not name.startswith("_")})


def analyze_code(source):
    if not source or not source.strip():
        return {"valid": False, "error": "Please provide Python source code."}

    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {
            "valid": False,
            "error": f"Syntax error on line {exc.lineno or '?'}: {exc.msg}",
            "metrics": None,
            "issues": [{"severity": "High", "title": "Invalid Python syntax", "detail": str(exc)}],
        }

    lines = source.splitlines()
    code_lines = [line for line in lines if line.strip() and not line.strip().startswith("#")]
    functions, function_lengths, long_functions = _function_metrics(tree)
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
    complexity = _cyclomatic(tree)
    duplication = _duplicate_lines(source)
    unused = _unused_variables(tree)
    nesting = _max_nesting(tree)
    avg_function_length = round(sum(function_lengths) / len(function_lengths), 1) if function_lengths else 0.0

    issues = []
    if complexity > 10:
        issues.append({"severity": "High", "title": "High cyclomatic complexity", "detail": f"Approximate complexity is {complexity}; consider simplifying conditional logic."})
    elif complexity > 6:
        issues.append({"severity": "Medium", "title": "Moderate cyclomatic complexity", "detail": f"Approximate complexity is {complexity}; consider breaking complex logic into smaller functions."})

    if duplication:
        issues.append({"severity": "Medium", "title": "Repeated code detected", "detail": f"{duplication} repeated meaningful line pattern(s) were detected."})
    if long_functions:
        names = ", ".join(x["name"] for x in long_functions[:5])
        issues.append({"severity": "Medium", "title": "Long function detected", "detail": f"Function(s) over 30 lines: {names}."})
    if unused:
        names = ", ".join(unused[:8])
        issues.append({"severity": "Low", "title": "Potentially unused variables", "detail": f"Review: {names}."})
    if nesting > 4:
        issues.append({"severity": "High", "title": "Deep nesting", "detail": f"Maximum control-flow nesting is approximately {nesting} levels."})
    elif nesting > 2:
        issues.append({"severity": "Medium", "title": "Nested control flow", "detail": f"Maximum control-flow nesting is approximately {nesting} levels."})

    if not issues:
        issues.append({"severity": "Good", "title": "No major static issues detected", "detail": "The selected checks did not identify a major maintainability warning."})

    # A transparent heuristic score used alongside the ML classifier.
    score = 100
    score -= max(0, complexity - 5) * 3
    score -= duplication * 4
    score -= len(long_functions) * 5
    score -= len(unused) * 2
    score -= max(0, nesting - 2) * 5
    score = max(0, min(100, round(score)))

    metrics = {
        "lines_of_code": len(code_lines),
        "total_lines": len(lines),
        "functions": len(functions),
        "classes": len(classes),
        "imports": len(imports),
        "cyclomatic_complexity": complexity,
        "code_duplication": duplication,
        "unused_variables": len(unused),
        "max_nesting": nesting,
        "avg_function_length": avg_function_length,
        "long_functions": len(long_functions),
        "health_score": score,
    }

    features = {
        "cyclomatic_complexity": complexity,
        "code_duplication": duplication,
        "unused_variables": len(unused),
        "max_nesting": nesting,
        "avg_function_length": avg_function_length,
        "long_functions": len(long_functions),
        "lines_of_code": len(code_lines),
        "functions": len(functions),
        "classes": len(classes),
    }

    recommendations = []
    if complexity > 6:
        recommendations.append("Reduce conditional complexity by extracting smaller functions or simplifying branches.")
    if duplication:
        recommendations.append("Refactor repeated logic into reusable functions or modules.")
    if long_functions:
        recommendations.append("Break long functions into focused units with clear responsibilities.")
    if unused:
        recommendations.append("Remove unused variables or confirm that they are intentionally retained.")
    if nesting > 3:
        recommendations.append("Use guard clauses or helper functions to reduce deep nesting.")
    if not recommendations:
        recommendations.append("Continue using clear naming, modular functions, and automated testing as the codebase evolves.")

    return {
        "valid": True,
        "metrics": metrics,
        "features": features,
        "issues": issues,
        "recommendations": recommendations,
        "unused_variables": unused,
        "long_functions": long_functions,
    }
