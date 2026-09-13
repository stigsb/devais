"""Small regression check for cable bends and bounded collision exceptions.
Run: .venv/bin/python -m cad.test_assembly
"""
from itertools import combinations
from cad.assembly import box, harness, inspect, rounded_path


def main():
    wires, length = harness([(0, 0, 0), (0, 0, 20), (0, 20, 20)], 4, .8)
    assert 39 < length < 40
    assert all(w.isValid() for w in wires)
    assert all(a.intersect(b).Volume() < 1e-5 for a, b in combinations(wires, 2))
    try:
        rounded_path([(0, 0, 0), (0, 0, 1), (1, 0, 1)], 2)
    except AssertionError:
        pass
    else:
        raise AssertionError('Accepted a bend that cannot fit')
    parts = {'a': box((2, 2, 2), (0, 0, 0)), 'b': box((2, 2, 2), (1, 0, 0))}
    assert inspect(parts, {})[0], 'Missed a solid collision'
    contact = {frozenset(('a', 'b')): ('test contact', box((.1, .1, .1), (0, 0, 0)))}
    assert inspect(parts, contact)[0], 'Contact exception hid an unrelated collision'
    parts['b'] = parts['b'].translate((3, 0, 0))
    assert not inspect(parts, {})[0]
    print('Cable bend and collision regression checks passed')


if __name__ == '__main__':
    main()
