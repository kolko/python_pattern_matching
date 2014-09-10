# -*- coding: utf-8 -*-
import sys
import ast
import inspect
# import codegen

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

        test_1 = '(%s)' % ' and '.join(['((locals().get(\'%s\') and x[%s] == locals().get(\'%s\')) or not locals().get(\'%s\'))' % (var.id, n, var.id, var.id) for n, var in enumerate(args)])
        payload = '\n    '.join(['if not locals().get(\'%s\'): %s = %s[%s]' % (var.id, var.id, mathed_variable.id, n) for n, var in enumerate(args) ])
        code = '''if (%s):
    %s
else:
    pass
''' % (test_1, payload)
        new_node = ast.parse(code).body[0]
        new_node.body += body
        new_node.orelse = orelse
        return new_node

def have_pattern_matching(func):
    '''Decorator for functions, containings pattern_matching'''

    source = inspect.getsource(func)
    func_file = getattr(sys.modules[func.__module__], '__file__', '<nofile>')
    # func_file = '<string>'
    tree = ast.parse(source, func_file, 'single')
    pm_transformer = PatternMatchingTransformer()
    tree = pm_transformer.visit(tree)

    tree.body[0].decorator_list = [x for x in tree.body[0].decorator_list if x.attr != 'have_pattern_matching']

    code = compile(tree, func_file, 'single')
    # print(codegen.to_source(tree))
    eval(code)
    return locals()[func.__name__]

    # context = sys._getframe(2).f_locals
    # exec(code, context)
    #
    # return context[func.__name__]