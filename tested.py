import pattern_mathing

@pattern_mathing.have_pattern_matching
def test2(x):
    t = 'xyz'
    if x | mathed (t, z):
        return z
    else:
        return 'Not mached'

assert test2(['xyz', 'passed']) == 'passed'
print(1)
assert test2(['xyz1', 'not passed']) == 'Not mached'
print(2)