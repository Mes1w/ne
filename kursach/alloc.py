"""Раскладка элементов по корпусам серии К555 и номера выводов."""
from design import *
LA3 = [(1, 2, 3), (4, 5, 6), (9, 10, 8), (12, 13, 11)]
LA4 = [(1, 2, 13, 12), (3, 4, 5, 6), (9, 10, 11, 8)]
LA1 = [(1, 2, 4, 5, 6), (9, 10, 12, 13, 8)]
TV9 = [dict(C=1, K=2, J=3, S=4, Q=5, nQ=6, R=15), dict(C=13, K=12, J=11, S=10, Q=9, nQ=7, R=14)]
TYPES = {'TV9': 'К555ТВ9', 'LA3': 'К555ЛА3', 'LA4': 'К555ЛА4', 'LA1': 'К555ЛА1', 'KP7': 'К555КП7'}

def gates(t, acc):
    if t['k'] == 'nand':
        acc.append(t)
        for c in t['ch']: gates(c, acc)
    elif t['k'] == 'mux': acc.append(t)
    return acc

def allocate():
    order = []
    for f in DEC1: gates(f['J'], order); gates(f['K'], order)
    gates(P_TREE, order)
    for f in DEC2: gates(f['J'], order); gates(f['K'], order)
    for _, t in CONV1 + CONV2: gates(t, order)
    pk = {}
    for i, f in enumerate(DEC1 + DEC2):
        f['ref'] = 'DD%d.%d' % (i // 2 + 1, i % 2 + 1); f['pins'] = TV9[i % 2]; pk['DD%d' % (i // 2 + 1)] = 'TV9'
    n = 5
    for typ, secs, sel in (('LA3', LA3, lambda t: t['k'] == 'nand' and len(t['ch']) <= 2),
                           ('LA4', LA4, lambda t: t['k'] == 'nand' and len(t['ch']) == 3),
                           ('LA1', LA1, lambda t: t['k'] == 'nand' and len(t['ch']) == 4)):
        gs = [t for t in order if sel(t)]
        for i, t in enumerate(gs):
            d = n + i // len(secs); t['ref'] = 'DD%d.%d' % (d, i % len(secs) + 1); t['pins'] = secs[i % len(secs)]; pk['DD%d' % d] = typ
        spare = (-len(gs)) % len(secs)
        pk['spare_' + typ] = ['DD%d.%d' % (n + (len(gs) - 1) // len(secs), len(secs) - k) for k in range(spare)][::-1]
        n += -(-len(gs) // len(secs))
    for t in order:
        if t['k'] == 'mux': t['ref'] = 'DD%d' % n; pk['DD%d' % n] = 'KP7'; n += 1
    return pk
PK = allocate()
if __name__ == '__main__':
    import collections
    c = collections.Counter(v for k, v in PK.items() if k.startswith('DD')); print(c, {k: v for k, v in PK.items() if k.startswith('spare')})
