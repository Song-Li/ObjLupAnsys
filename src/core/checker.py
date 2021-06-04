from .trace_rule import TraceRule
from .vul_func_lists import *
from .logger import loggers
import sty

def get_path_text(G, path, caller=None):
    """
    get the code by ast number
    Args:
        G: the graph
        path: the path with ast nodes
    Return:
        str: a string with text path
    """
    res_path = ""
    # debug only
    cur_path_str1 = ""
    # real output
    cur_path_str2 = ""
    for node in path:
        # need to check why node can be None
        if node is None:
            continue
        cur_node_attr = G.get_node_attr(node)

        content = None
        if cur_node_attr.get('type') != 'object' and cur_node_attr.get('lineno:int') is None:
            continue

        cur_path_str2 += "$FilePath${}\n".format(G.get_node_file_path(node))
        try:
            content = G.get_node_file_content(node)
        except Exception as e:
            print(e)

        if cur_node_attr['type'] == 'object' and len(cur_node_attr['code'].strip()) != 0:
            cur_path_str2 += "{}\n".format(cur_node_attr['code'])
            continue


        cur_path_str1 += cur_node_attr['lineno:int'] + '->'
        start_lineno = int(cur_node_attr['lineno:int'])
        end_lineno = int(cur_node_attr['endlineno:int']
                        or start_lineno)

        if content is not None:
            cur_path_str2 += "Line {}\t{}".format(start_lineno,
                    ''.join(content[start_lineno:end_lineno + 1]))

    if caller is not None and 'lineno:int' in G.get_node_attr(caller):
        cur_path_str1 += G.get_node_attr(caller).get('lineno:int')
    G.logger.debug(cur_path_str1)

    res_path += "==========================\n"
    res_path += cur_path_str2
    return res_path

def get_obj_defs(G, obj_nodes=[]):
    """
    input a list of objs and return a list of def asts
    """
    cur_creater = []
    for node in obj_nodes:
        # for each objects, store the creater of the obj and used obj
        ast_node = G.get_obj_def_ast_node(node)
        if ast_node is None:
            #print("!!!!!!!!!!!!!!11", node, G.get_node_attr(node))
            pass
        cur_creater.append(ast_node)
    return cur_creater

def obj_traceback(G, start_node):
    """
    traceback from the target object node, based on obj level dependency
    Args:
        G: the graph
        start_node: the start object node
    Returns:
        pathes(list): the pathes to the target object
        def pathes(list): AST nodes that defines the objects in the pathes
        text pathes(str): the human-friendly text pathes
    """
    text_path = ""
    ast_pathes = []
    obj_pathes = G._dfs_upper_by_edge_type(source=start_node, edge_type="CONTRIBUTES_TO")

    for obj_p in obj_pathes:
        obj_def = get_obj_defs(G, obj_p)
        ast_pathes.append(obj_def)
        text_path += get_path_text(G, obj_def)
    return obj_pathes, ast_pathes, text_path

def traceback(G, vul_type, start_node=None):
    """
    traceback from the leak point, the edge is OBJ_REACHES
    Args:
        G: the graph
        vul_type: the type of vulernability, listed below

    Return:
        the paths include the objs,
        the string description of paths,
        the list of callers,
    """
    res_path = ""
    ret_pathes = []
    caller_list = []
    if vul_type == "proto_pollution":
        # in this case, we have to specify the start_node
        if start_node is not None:
            start_cpg = G.find_nearest_upper_CPG_node(start_node)
            pathes = G._dfs_upper_by_edge_type(start_cpg, "OBJ_REACHES")

            for path in pathes:
                ret_pathes.append(path)
                path.reverse()
                res_path += get_path_text(G, path, start_cpg)
            
            return ret_pathes, res_path, caller_list

    expoit_func_list = signature_lists[vul_type]

    func_nodes = G.get_node_by_attr('type', 'AST_METHOD_CALL')
    func_nodes += G.get_node_by_attr('type', 'AST_CALL')

    for func_node in func_nodes:
        # we assume only one obj_decl edge
        func_name = G.get_name_from_child(func_node)
        if func_name in expoit_func_list:
            caller = func_node
            caller = G.find_nearest_upper_CPG_node(caller)
            caller_list.append("{} called {}".format(caller, func_name))
            pathes = G._dfs_upper_by_edge_type(caller, "OBJ_REACHES")

            for path in pathes:
                ret_pathes.append(path)
                path.reverse()
                res_path += get_path_text(G, path, caller)
    return ret_pathes, res_path, caller_list

def do_vul_checking(G, rule_list, pathes):
    """
    checking the vuleralbilities in the pathes

    Args:
        G: the graph object
        rule_list: a list of paires, (rule_function, args of rule_functions)
        pathes: the possible pathes
    Returns:
        
    """
    trace_rules = []
    for rule in rule_list:
        trace_rules.append(TraceRule(rule[0], rule[1], G))

    success_pathes = []
    flag = True
    for path in pathes:
        flag = True
        for trace_rule in trace_rules:
            if not trace_rule.check(path):
                flag = False
                break
        if flag:
            success_pathes.append(path)
    return success_pathes

def vul_checking(G, pathes, vul_type):
    """
    picking the pathes which satisfy the xss
    Args:
        G: the Graph
        pathes: the possible pathes
    return:
        a list of xss pathes
    """
    proto_pollution = [
            [('has_user_input', None), ('not_exist_func', signature_lists['sanitation'])]
            ]
    vul_type_map = {
            "proto_pollution": proto_pollution,
            }

    rule_lists = vul_type_map[vul_type]
    success_pathes = []
    print('vul_checking', vul_type)
    """
    print(pathes)
    """
    for path in pathes:
        res_text_path = get_path_text(G, path, path[0])
        loggers.main_logger.info(res_text_path)

    for rule_list in rule_lists:
        success_pathes += do_vul_checking(G, rule_list, pathes)
    print_success_pathes(G, success_pathes)
    return success_pathes

def print_success_pathes(G, success_pathes, color=None):
    title = "Dataflow of Assigned Value"
    sty_color = sty.fg.li_green
    if color == '#f00':
        sty_color = sty.fg.li_red
        title = "Dataflow of Object Property"
    elif color == '#00f':
        title = "Polluted Built-in Prototype"
        sty_color = sty.fg.li_blue
    if len(success_pathes) != 0:
        print(sty_color + "|Checker| {}:".format(title))#, success_pathes ,"color: ", color)
    path_id = 0
    history_path = set()
    for path in success_pathes:
        res_text_path = get_path_text(G, path, path[0])
        if res_text_path in history_path:
            continue
        loggers.tmp_res_logger.info("|checker| success id${}$color:{}$: ".format(path_id, color))
        loggers.tmp_res_logger.info(res_text_path)
        path_id += 1
        print("Attack Path: ")
        print(res_text_path)
        history_path.add(res_text_path)
    print(sty.rs.all)

