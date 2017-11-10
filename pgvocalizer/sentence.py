import json


def generate_sentence(tree_node):
    node_data = json.loads(tree_node.data)

    action_type = node_data["Node Type"]

    # create relation list
    relations = []
    if "Relation Name" in node_data:
        relation_phrase = node_data["Relation Name"]
        if "Alias" in node_data:
            relation_phrase = relation_phrase + " with alias of {}".format(node_data["Alias"])
        relations.append(relation_phrase)
    if not (len(tree_node.children) == 0):
        for child in tree_node.children:
            child_data = json.loads(child.data)
            child_type = child_data["Node Type"]
            child_phrase = "previous {} result".format(child_type)
            relations.append(child_phrase)

    relations_string = _stringify_list(relations)
    sentence = "Perform {} on {}.".format(action_type, relations_string)

    return sentence


def _stringify_list(items):
    start, last = items[:-1], items[-1]

    if start:
        return "{} and {}".format(", ".join(start), last)
    else:
        return last
