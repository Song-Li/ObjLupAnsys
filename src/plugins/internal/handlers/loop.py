from src.plugins.handler import Handler
from src.core.logger import *
from ..utils import peek_variables, val_to_str, is_int
from . import vars
from ..utils import check_condition, wildcard, is_wildcard_obj, add_contributes_to
from .blocks import simurun_block

class HandleFor(Handler):
    """
    handle the for loop
    """
    def process(self):
        node_id = self.node_id
        extra = self.extra
        G = self.G
        try:
            init, cond, inc, body = G.get_ordered_ast_child_nodes(node_id)[:4]
        except ValueError as e:
            for n in G.get_ordered_ast_child_nodes(node_id):
                loggers.main_logger.error(n, G.get_node_attr(n))
                loggers.error_logger.error(n, G.get_node_attr(n))
                return None
        cond = G.get_ordered_ast_child_nodes(cond)[0]
        # switch scopes
        parent_scope = G.cur_scope
        G.cur_scope = G.add_scope('BLOCK_SCOPE', decl_ast=body,
                      scope_name=G.scope_counter.gets(f'Block{body}'))
        result = self.internal_manager.dispatch_node(init, extra) # init loop variables

        counter = 0
        while True:
            # check increment to determine loop variables
            d = peek_variables(G, ast_node=inc, extra=extra) 
            loggers.main_logger.debug('For loop variables:')
            for name, obj_nodes in d.items():
                loggers.main_logger.debug(sty.ef.i + name + sty.rs.all + ': ' +
                    ', '.join([(sty.fg.green+'{}'+sty.rs.all+' {}').format(obj,
                    val_to_str(G.get_node_attr(obj).get('code'))) for obj in obj_nodes]))

            # check if the condition is met
            check_result, deterministic = check_condition(G, cond, extra)
            loggers.main_logger.debug('Check condition {} result: {} {}'.format(sty.ef.i +
                G.get_node_attr(cond).get('code') + sty.rs.all, check_result,
                deterministic))
            # avoid infinite loop
            if (not deterministic and counter > 3) or check_result == 0 or counter > 100:
                loggers.main_logger.debug('For loop {} finished'.format(node_id))
                break
            simurun_block(G, body, branches=extra.branches) # run the body
            result = self.internal_manager.dispatch_node(inc, extra) # do the inc
            counter += 1
        # switch back the scope
        G.cur_scope = parent_scope

class HandleForEach(Handler):
    """
    handle the for each loop
    """
    def process(self):
        G = self.G
        node_id = self.node_id
        extra = self.extra
        logger = loggers.main_logger
        handle_node = self.internal_manager.dispatch_node

        obj, value, key, body = G.get_ordered_ast_child_nodes(node_id)
        handled_obj = handle_node(obj, extra)
        # switch scopes
        parent_scope = G.cur_scope
        G.cur_scope = \
            G.add_scope('BLOCK_SCOPE', decl_ast=body,
                        scope_name=G.scope_counter.gets(f'Block{body}'))
        has_branches = (len(handled_obj.obj_nodes) > 1)
        # print(sty.fg.li_green, handled_obj.obj_nodes, sty.rs.all)
        for obj in handled_obj.obj_nodes:
            if G.get_node_attr(node_id).get('flags:string[]') == 'JS_FOR_IN':
                # handle and declare the loop variable
                handled_key = handle_node(key, extra)
                if G.finished:
                    break
                # loop through object's property names
                # if it's a wildcard object, include "__proto__"
                prop_names = list(filter(lambda k: k != wildcard,
                    G.get_prop_names(obj,
                        exclude_proto=not is_wildcard_obj(G, obj)
                    )))
                if is_wildcard_obj(G, obj):
                    if G.check_proto_pollution:
                        # wildcard property for wildcard object
                        prop_names = [wildcard]
                        logger.debug(f'{obj} is a wildcard object.')
                    else:
                        # wildcard property for wildcard object
                        prop_names.insert(0, wildcard)
                        logger.debug(f'{obj} is a wildcard object.')
                for k in prop_names:
                    if G.get_node_attr(obj).get('type') == 'array' and \
                        not is_int(k):
                        continue
                    if str(k).startswith('Obj#'): # object-based keys
                        key_obj = k[4:]
                    else:
                        # assign the name to the loop variable as a new 
                        # literal object
                        key_obj = G.add_obj_node(ast_node=node_id,
                            js_type='string', value=k)
                        add_contributes_to(G, [obj], key_obj)
                    logger.debug(f'For-in loop variables: {sty.ef.i}{handled_key.name}{sty.rs.all}: '
                        f'{sty.fg.green}{key_obj}{sty.rs.all}: {k} from obj {obj}')
                    G.for_stack.append('for-in {} {} {} in {}'.format(node_id, handled_key.name, k, obj))
                    # print(G.for_stack)
                    G.assign_obj_nodes_to_name_node(handled_key.name_nodes[0],
                        [key_obj], branches=extra.branches)
                    # run the body
                    simurun_block(G, body, branches=extra.branches)
                    G.for_stack.pop()
                logger.debug('For-in loop {} finished'.format(node_id))
            elif G.get_node_attr(node_id).get('flags:string[]') == 'JS_FOR_OF':
                # handle and declare the loop variable
                handled_value = handle_node(value, extra)
                if G.finished:
                    break
                # if the object is an array, only use numeric indices
                numeric_only = (G.get_node_attr(obj).get('type') == 'array')
                # loop through object's property object nodes
                # if it's a wildcard object, include its prototype
                prop_obj_nodes = G.get_prop_obj_nodes(obj,
                    branches=extra.branches, numeric_only=numeric_only,
                    exclude_proto=not is_wildcard_obj(G, obj))
                if is_wildcard_obj(G, obj):
                    # wildcard property for wildcard object
                    wildcard_prop_obj_nodes = G.get_prop_obj_nodes(obj,
                        prop_name=wildcard, branches=extra.branches)
                    if not wildcard_prop_obj_nodes:
                        wildcard_prop_obj_nodes = [G.add_obj_as_prop(wildcard,
                            node_id, value=wildcard, parent_obj=obj)]
                    prop_obj_nodes.extend(wildcard_prop_obj_nodes)
                    prop_obj_nodes = list(set(prop_obj_nodes))
                    logger.debug(f'{obj} is a wildcard object.')
                # for v in prop_obj_nodes:
                #     G.for_stack.append('for-of {} {} {}'.format(node_id, v, G.get_node_attr(v).get("code")))
                #     print(G.for_stack)
                #     # assign the object node to the loop variable
                #     logger.debug(f'For-of loop variables: {sty.ef.i}{handled_value.name}{sty.rs.all}: {sty.fg.green}{v}{sty.rs.all}: {G.get_node_attr(v).get("code")}'
                #         f' from obj {obj}')
                #     G.assign_obj_nodes_to_name_node(handled_value.name_nodes[0],
                #         [v], branches=extra.branches)
                #     # run the body
                #     simurun_block(G, body, branches=extra.branches)
                #     G.for_stack.pop()

                G.for_stack.append('for-of {} {} {}'.format(node_id, prop_obj_nodes, [G.get_node_attr(v).get("code") for v in prop_obj_nodes]))
                # print(G.for_stack)
                # assign the object node to the loop variable
                G.assign_obj_nodes_to_name_node(handled_value.name_nodes[0],
                    prop_obj_nodes, branches=extra.branches)
                # run the body
                simurun_block(G, body, branches=extra.branches)
                G.for_stack.pop()
                logger.debug('For-of loop {} finished'.format(node_id))
        # switch back the scope
        G.cur_scope = parent_scope

class HandleWhile(Handler):
    def process(self):
        node_id = self.node_id
        G = self.G
        extra = self.extra

        try:
            test, body = G.get_ordered_ast_child_nodes(node_id)[:2]
        except ValueError as e:
            for n in G.get_ordered_ast_child_nodes(node_id):
                logger.error(n, G.get_node_attr(n))
        # test = G.get_ordered_ast_child_nodes(test)[0] # wrongly influenced by for?
        # switch scopes
        parent_scope = G.cur_scope
        G.cur_scope = G.add_scope('BLOCK_SCOPE', decl_ast=body,
                      scope_name=G.scope_counter.gets(f'Block{body}'))
        counter = 0
        while True:
            # check if the condition is met
            check_result, deterministic = check_condition(G, test, extra)
            loggers.main_logger.debug('While loop condition {} result: {} {}'.format(
                sty.ef.i + G.get_node_attr(test).get('code') + sty.rs.all,
                check_result, deterministic))
            # avoid infinite loop
            if (not deterministic and counter > 3) or check_result == 0 or \
                counter > 10:
                loggers.main_logger.debug('For loop {} finished'.format(node_id))
                break
            simurun_block(G, body, branches=extra.branches) # run the body
            counter += 1
        # switch back the scope
        G.cur_scope = parent_scope

class HandleBreak(Handler):
    def process(self):
        # TODO: implement it
        pass
