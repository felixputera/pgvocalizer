import json
from pgvocalizer.connection import get_query_plan
from pgvocalizer.tree import TreeNode


def _build_tree(plan, tree_node):
    if "Plans" in plan:
        for child_plan in plan["Plans"]:
            child_node = tree_node.add_child()
            _build_tree(child_plan, child_node)
        del plan['Plans']

    tree_node.set_data(json.dumps(plan))


def vocalize(query):
    plan = get_query_plan(query)
    tree_root = TreeNode()
    _build_tree(plan[0]["Plan"], tree_root)
    return tree_root
