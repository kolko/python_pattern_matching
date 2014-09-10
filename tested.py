import pattern_mathing

@pattern_mathing.have_pattern_matching
def test1(x):
    t = 'xyz'
    if x | mathed (t, z):
        return z
    else:
        return 'Not mached'

assert test1(['xyz', 'passed']) == 'passed'
assert test1(['xyz1', 'not passed']) == 'Not mached'

@pattern_mathing.have_pattern_matching
def test3(x):
    t = 'xyz'
    if x | mathed (t, _):
        return "mached"
    else:
        return 'Not mached'

assert test3(['xyz', 'passed']) == 'mached'
assert test3(['xyz1', 'not passed']) == 'Not mached'

@pattern_mathing.have_pattern_matching
def test2(x):
    t = 'xyz'
    if x | mathed (t, z):
        return z
    elif x | mathed ('abc', z):
        return z+'2'
    else:
        return 'Not mached'

assert test2(['xyz', 'passed']) == 'passed'
assert test2(['abc', 'passed']) == 'passed2'
assert test2(['xyz1', 'not passed']) == 'Not mached'