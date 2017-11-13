import json
import re


def generate_sentence(tree_node):
    node_data = json.loads(tree_node.data)

    action_type = node_data["Node Type"]

    # relation
    relations = []
    relation_phrase = ""
    bool_name = False
    if "Relation Name" in node_data:
        relation_phrase = node_data["Relation Name"]
        bool_name = True
    if "CTE Name" in node_data:
        relation_phrase = "{} CTE".format(node_data["CTE Name"])
        bool_name = True
    if bool_name:
        if "Alias" in node_data:
            relation_phrase = relation_phrase + " with alias of {}".format(node_data["Alias"])
        relations.append(relation_phrase)
    if not (len(tree_node.children) == 0):
        for child in tree_node.children:
            child_data = json.loads(child.data)
            child_type = child_data["Node Type"]
            child_phrase = "previous {} result".format(child_type)
            relations.append(child_phrase)

    # Key, i.e. Group Key, Sort Key
    key_string = ""
    for key, value in node_data.items():  # checking all occurrences of ...key, don't think can use typical in
        if "Key" in key:
            key_list = []
            for elem_key in value:
                key_list.append(_normalize_expr(elem_key))
            key_string = " with {} as {}".format(_stringify_list(key_list), key)

    # Filter
    filter_string = ""
    if "Filter" in node_data:
        filter_string = " and filter keeping only those with {}".format(_normalize_expr(node_data["Filter"]))

    # Cond, i.e. Hash Cond
    cond_string = ""
    for key, value in node_data.items():  # checking all occurrences of ...key, don't think can use typical in
        if "Cond" in key:
            cond_string = " where {}".format(_normalize_expr(value))

    # Subplan Name
    subplan_string = ""
    if "Subplan Name" in node_data:
        subplan_string = ", saving this as {}".format(node_data["Subplan Name"])

    relations_string = _stringify_list(relations)
    sentence = "Perform {} on {}{}{}{}{}.".format(action_type, relations_string, key_string, cond_string, filter_string,
                                                  subplan_string)

    return sentence


def _stringify_list(items):
    start, last = items[:-1], items[-1]

    if start:
        return "{} and {}".format(", ".join(start), last)
    else:
        return last


def _normalize_expr(string):
    string = _clean_type(string)
    string = _stringify_pg_dt_fun(string)
    string = _stringify_misc_fun(string)
    string = _stringify_like_op(string)
    string = _stringify_table_column(string)
    string = _clean_symbols(string)
    return string


def _clean_type(string):
    return re.sub(r'(::([ ]?[a-zA-Z0-9]+)+)', '', string)


def _clean_symbols(string):
    return re.sub(r'[\'"(){}:;!@#$%^&*~`]', '', string)


def _stringify_pg_dt_fun(string):
    # age(timestamp)
    swap_list = []
    for func in re.finditer(r'age\(([(\']?[a-zA-Z]+\(?\)?[)\']?)\)', string):
        swap_string = "midnight of today subtract {}".format(func.group(1))
        swap = {
            'swap_string': swap_string,
            'start_idx': func.span(0)[0],
            'end_idx': func.span(0)[1]
        }
        swap_list.append(swap)
    string = _handle_substr_swap(string, swap_list)

    # age(timestamp, timestamp)
    swap_list = []
    for func in re.finditer(r'age\(([(\']?[a-zA-Z]+\(?\)?[)\']?)[ ]*,[ ]*([(\']?[a-zA-Z]+\(?\)?[)\']?)\)', string):
        swap_string = "{} subtract {}".format(func.group(1), func.group(2))
        swap = {
            'swap_string': swap_string,
            'start_idx': func.span(0)[0],
            'end_idx': func.span(0)[1]
        }
        swap_list.append(swap)
    string = _handle_substr_swap(string, swap_list)

    # date_part(text, timestamp) and date_part(text, interval)
    swap_list = []
    for func in re.finditer(r'date_part\(([(\']?[a-zA-Z]+\(?\)?[)\']?)[ ]*,[ ]*([(\']?[a-zA-Z]+\(?\)?[)\']?)\)', string):
        swap_string = "{} from {}".format(func.group(1), func.group(2))
        swap = {
            'swap_string': swap_string,
            'start_idx': func.span(0)[0],
            'end_idx': func.span(0)[1]
        }
        swap_list.append(swap)
    string = _handle_substr_swap(string, swap_list)

    # date_trunc(text, timestamp)
    swap_list = []
    for func in re.finditer(r'date_trunc\(([(\']?[a-zA-Z]+\(?\)?[)\']?)[ ]*,[ ]*([(\']?[a-zA-Z]+\(?\)?[)\']?)\)', string):
        swap_string = "truncate {} to {} precision".format(func.group(2), func.group(1))
        swap = {
            'swap_string': swap_string,
            'start_idx': func.span(0)[0],
            'end_idx': func.span(0)[1]
        }
        swap_list.append(swap)
    string = _handle_substr_swap(string, swap_list)

    # extract(field from timestamp) and extract(field from interval)
    swap_list = []
    for func in re.finditer(r'extract\((([(\']?[a-zA-Z]+\(?\)?[)\']?[ ]*)+)\)', string):
        swap_string = "{}".format(func.group(1))
        swap = {
            'swap_string': swap_string,
            'start_idx': func.span(0)[0],
            'end_idx': func.span(0)[1]
        }
        swap_list.append(swap)
    string = _handle_substr_swap(string, swap_list)

    # isfinite(date), isfinite(timestamp), isfinite(interval)
    swap_list = []
    for func in re.finditer(r'isfinite\(([(\']?[a-zA-Z]+\(?\)?[)\']?)\)', string):
        swap_string = "{} is finite".format(func.group(1))
        swap = {
            'swap_string': swap_string,
            'start_idx': func.span(0)[0],
            'end_idx': func.span(0)[1]
        }
        swap_list.append(swap)
    string = _handle_substr_swap(string, swap_list)

    return string


def _handle_substr_swap(string, swap_list):
    swap_list.reverse()
    for swap in swap_list:
        string = "{}{}{}".format(string[:swap['start_idx']], swap['swap_string'], string[swap['end_idx']:])
    return string


def _stringify_table_column(string):
    swap_list = []
    for table_col in re.finditer(r'([a-zA-Z_\-]+)\.([a-zA-Z_\-]+)', string):
        swap_string = "{} of {}".format(table_col.group(2), table_col.group(1))
        swap = {
            'swap_string': swap_string,
            'start_idx': table_col.span(0)[0],
            'end_idx': table_col.span(0)[1]
        }
        swap_list.append(swap)
    string = _handle_substr_swap(string, swap_list)

    return string


def _stringify_misc_fun(string):
    swap_list = []
    for table_col in re.finditer(r'([a-zA-Z]+)\(([(\']?[a-zA-Z.]+\(?\)?[)\']?)\)', string):
        swap_string = "{} of {}".format(table_col.group(1), table_col.group(2))
        swap = {
            'swap_string': swap_string,
            'start_idx': table_col.span(0)[0],
            'end_idx': table_col.span(0)[1]
        }
        swap_list.append(swap)
    string = _handle_substr_swap(string, swap_list)

    string = re.sub(r'\(\)', '', string)

    return string


def _stringify_like_op(string):
    swap_list = []
    for table_col in re.finditer(r'([a-zA-Z%]+)[ ]*~~[ ]*([a-zA-Z%]+)', string):
        swap_string = "{} which contains {} substring".format(table_col.group(1), table_col.group(2))
        swap = {
            'swap_string': swap_string,
            'start_idx': table_col.span(0)[0],
            'end_idx': table_col.span(0)[1]
        }
        swap_list.append(swap)
    string = _handle_substr_swap(string, swap_list)

    return string
