def diff_trees(old_tree: str, new_tree: str):

    old_lines = set(old_tree.splitlines())
    new_lines = set(new_tree.splitlines())

    added = new_lines - old_lines
    removed = old_lines - new_lines

    return {
        "added": list(added),
        "removed": list(removed)
    }
