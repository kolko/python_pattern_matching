# -*- coding: utf-8 -*-
import ast
import codegen
import pattern_mathing

what_we_need = """
def test2(x):
    t = 'xyz'
#сначала делаем проверки, потом присваиваем переменные!
    if (
#-1 проверка - что кол-во аргументов равно
#....
#1 проверка - переменная либо равна, либо пустая
        ((locals().get('t') and x[0] == locals().get('t')) or not locals().get('t'))
            and
        ((locals().get('z') and x[1] == locals().get('z')) or not locals().get('z'))
        )
#присваиваем
            and
        (
            ((not locals().get('t')) and t = x[0])
            and
            ((not locals().get('z')) and z = x[1])
        )
    #if x | mathed (t, z):
        return z
    elif x | mathed ('abc', z):
        return z
    else:
        return 'Not mached'
"""

func_str = """
def test2(x):
    t = 'xyz'
    if x | mathed (t, z):
        return z
#    elif x | mathed ('abc', z):
#        return z
    else:
        return 'Not mached'
"""

st = ast.parse(func_str)
# st = pattern_mathing.walk_tree_and_patch(st)
# print(codegen.to_source(st))
pm_transformer = pattern_mathing.PatternMatchingTransformer()
st = pm_transformer.visit(st)
code = compile(st, '<string>', 'exec')
eval(code)

assert test2(['xyz', 'passed']) == 'passed'
print(1)
assert test2(['xyz1', 'not passed']) == 'Not mached'
print(2)