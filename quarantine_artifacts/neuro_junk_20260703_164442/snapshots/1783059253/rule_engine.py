def detect_violations(graph):

    violations = []

    for file, imports in graph.items():

        for imp in imports:

            if "L0" in file and "L4" in imp:
                violations.append((file, imp, "L0 calling L4"))

            if "L5" in file and "L4" in imp:
                violations.append((file, imp, "API calling runtime directly"))

    return violations
