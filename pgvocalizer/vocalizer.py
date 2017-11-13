import json
import ast
from pgvocalizer.connection import get_query_plan
from pgvocalizer.sentence import generate_sentence
from pgvocalizer.tree import TreeNode


def _build_tree(plan, tree_node):
    if "Plans" in plan:
        for child_plan in plan["Plans"]:
            child_node = tree_node.add_child()
            _build_tree(child_plan, child_node)
        del plan['Plans']

    tree_node.data = json.dumps(plan)


def _traverse_tree(tree_node):
    child_sentences = []
    if not (len(tree_node.children) == 0):
        for child in tree_node.children:
            child_sentences.append(_traverse_tree(child))

    return ''.join(child_sentences) + generate_sentence(tree_node) + ' '


def vocalize(query):
    plan = get_query_plan(query)
    tree_root = TreeNode()
    _build_tree(plan[0]["Plan"], tree_root)
    return _traverse_tree(tree_root)


def vocalize_plan(plan):
    plan_dict = ast.literal_eval(plan)
    tree_root = TreeNode()
    _build_tree(plan_dict["Plan"], tree_root)
    return _traverse_tree(tree_root)


def get_tree(query):
    plan = get_query_plan(query)
    tree_root = TreeNode()
    _build_tree(plan[0]["Plan"], tree_root)
    return tree_root
