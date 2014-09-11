# -*- coding: utf-8 -*-
import sys
import ast
import inspect
import codegen

def walk_tree_and_patch(st):
    if is_pattern_mathing(st):
        return walk_tree_and_patch(patch_tree(st))
    if hasattr(st, 'body'):
        new_body = [walk_tree_and_patch(_st) for _st in st.body]
        st.body = new_body
    if isinstance(st, ast.If):
        new_orelse = [walk_tree_and_patch(_st) for _st in st.orelse]
        st.orelse = new_orelse
    return st

def is_pattern_mathing(st) -> bool:
    if isinstance(st, ast.If):
        if isinstance(st.test.op, ast.BitOr) and\
            isinstance(st.test.right, ast.Call) and\
            st.test.right.func.id == 'mathed':
            return True
    return False

def patch_tree(st):
    body = st.body
    orelse = st.orelse
    mathed_variable = st.test.left
    args = st.test.right.args
    print(args)
    test_1 = '(%s)' % ' and '.join(['((locals().get(\'%s\') and x[%s] == locals().get(\'%s\')) or not locals().get(\'%s\'))' % (var.id, n, var.id, var.id) for n, var in enumerate(args)])
    payload = '\n    '.join(['if not locals().get(\'%s\'): %s = %s[%s]' % (var.id, var.id, mathed_variable.id, n) for n, var in enumerate(args) ])
    code = '''if (%s):
    %s
else:
    pass
''' % (test_1, payload)
    print(code)
    new_st = ast.parse(code).body[0]
    new_st.body += body
    new_st.orelse = orelse
    st = new_st
    # st.test.right.func.id = '_mathed'
    return st


class PatternMatchingTransformer(ast.NodeTransformer):
    def visit_If(self, node):
        if not isinstance(node.test.right, ast.Call) or\
            node.test.right.func.id != 'mathed':
            return node

        body = node.body
        orelse = node.orelse
        mathed_variable = node.test.left
        args = node.test.right.args
        #Если переменная назначена - выполнить сравнение
        test_1 = '(%s)' % ' and '.join(['((locals().get(\'%s\') and %s[%s] == locals().get(\'%s\')) or not locals().get(\'%s\'))' % (var.id, mathed_variable.id, n, var.id, var.id) for n, var in enumerate(args) if isinstance(var, ast.Name)])
        #если не переменная - сравнить
        _test_2 = ' and '.join(['(%s == %s[%s])' % (codegen.to_source(var), mathed_variable.id, n) for n, var in enumerate(args) if not isinstance(var, ast.Name)])
        if _test_2:
            test_2 = 'and (%s)' % _test_2
        else:
            test_2 = ''
        #назначить переменные
        payload = '\n    '.join(['if not locals().get(\'%s\'): %s = %s[%s]' % (var.id, var.id, mathed_variable.id, n) for n, var in enumerate(args)  if isinstance(var, ast.Name)])
        code = '''if (%s %s):
    %s
else:
    pass
''' % (test_1, test_2, payload)
        # print(code)
        new_node = ast.parse(code).body[0]
        new_node.body += body
        new_node.orelse = [self.visit(x) for x in orelse]




        ########new_node 2
        ####test 1
        #Если переменная назначена - выполнить сравнение
        need_test1 = any([var for var in args
                            if isinstance(var, ast.Name)])
        test1_item_code = "((locals().get('%(var_id)s') " \
                          "and %(mathed_var)s[%(slice)s] == locals().get('%(var_id)s')) " \
                          "or not locals().get('%(var_id)s'))"
        test1_bolop_body_ast = [
            ast.parse(
                test1_item_code % {
                            'var_id': var.id,
                            'mathed_var': mathed_variable.id,
                            'slice': n,
                                    }
            ).body[0].value for n, var in enumerate(args)
            if isinstance(var, ast.Name)
        ]
        if len(test1_bolop_body_ast) > 1:
            test1_body_ast = ast.BoolOp(
                op = ast.And(),
                values = test1_bolop_body_ast,
            )
        elif len(test1_bolop_body_ast) == 1:
            test1_body_ast = test1_bolop_body_ast[0]
        else:
            need_test1 = False
        ###test 2
        #если не переменная - сравнить
        need_test2 = any([var for var in args
                    if not isinstance(var, ast.Name)])
        test2_compare_items_ast = [
            ast.Compare(
                left = var,
                ops = [ast.Eq()],
                comparators = [ast.parse('%(mathed_var)s[%(slice)s]' % {
                                                    'mathed_var': mathed_variable.id,
                                                    'slice': n,
                                                                       }).body[0].value]
            ) for n, var in enumerate(args) if not isinstance(var, ast.Name)
        ]
        if len(test2_compare_items_ast) > 1:
            test2_body_ast = ast.BoolOp(
                op = ast.And(),
                values = test2_compare_items_ast
            )
        elif len(test2_compare_items_ast) == 1:
            test2_body_ast = test2_compare_items_ast[0]
        else:
            need_test2 = False

        all_test_list = []
        if need_test1:
            all_test_list.append(test1_body_ast)
        if need_test2:
            all_test_list.append(test2_body_ast)

        if len(all_test_list) > 1:
            all_test_ast = ast.BoolOp(
                op = ast.And(),
                values = all_test_list
            )
        else:
            all_test_ast = all_test_list[0]

        #set unbound variables in if body payload
        payload_item_code = "if not locals().get('%(var_id)s'): %(var_id)s = %(mathed_var)s[%(slice)s]"
        payload_body_ast = [
            ast.parse(
                payload_item_code % {
                            'var_id': var.id,
                            'mathed_var': mathed_variable.id,
                            'slice': n,
                                    }
            ).body[0] for n, var in enumerate(args)
            if isinstance(var, ast.Name)
        ]


        new_node2 = ast.If(
            body = payload_body_ast + body,
            orelse = [self.visit(x) for x in orelse],
            test = all_test_ast
        )

        new_node2 = ast.fix_missing_locations(new_node2)

        # print(codegen.to_source(new_node))
        # print(codegen.to_source(new_node2))
        #
        # print()
        # print()
        # print(ast.dump(new_node))
        # print()
        # print(ast.dump(new_node2))

        return new_node2

def have_pattern_matching(func):
    '''Decorator for functions, containings pattern_matching'''

    source = inspect.getsource(func)
    func_file = getattr(sys.modules[func.__module__], '__file__', '<nofile>')
    # func_file = '<string>'
    # func_file = '<ast>'
    tree = ast.parse(source, func_file, 'single')
    pm_transformer = PatternMatchingTransformer()
    tree = pm_transformer.visit(tree)

    tree.body[0].decorator_list = [x for x in tree.body[0].decorator_list if x.attr != 'have_pattern_matching']

    # tree = ast.fix_missing_locations(tree)

    code = compile(tree, func_file, 'single')
    # print(codegen.to_source(tree))
    eval(code)

    #не трогаем окружение функции, просто заменяем ее код
    func.__code__ = locals()[func.__name__].__code__
    return func
    #альтернатива: просто возвращаем новую функцию
    # return locals()[func.__name__]

    # context = sys._getframe(2).f_locals
    # exec(code, context)
    #
    # return context[func.__name__]