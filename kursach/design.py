"""Вариант 9: счётчик М=100 в коде 2-7-4-1 на JK-триггерах, ПК в базисе И-НЕ, сегменты b, f на мультиплексорах."""
from logic import *

SEGS = 'abcdefg'
MUX_SEGS = 'bf'

def lit(n): return {'k': 'lit', 'n': n}
def const(v): return {'k': 'c', 'v': v}
def nand(*ch): return {'k': 'nand', 'ch': list(ch)}
def neg(n): return n[1:] if n.startswith('!') else '!' + n

def term_lits(imp):
    return [(n if imp[1] & (8 >> k) else '!' + n) for k, n in enumerate(VARS) if imp[0] & (8 >> k)]

def sop_to_nand(terms):
    """МДНФ -> дерево в базисе И-НЕ."""
    if not terms: return const(0)
    if terms == [(0, 0)]: return const(1)
    if len(terms) == 1:
        ls = term_lits(terms[0])
        return lit(ls[0]) if len(ls) == 1 else nand(nand(*map(lit, ls)))
    ch = []
    for t in terms:
        ls = term_lits(t)
        ch.append(lit(neg(ls[0])) if len(ls) == 1 else nand(*map(lit, ls)))
    return nand(*ch)

def rename(node, off):
    """Q1..Q4 -> Q(1+off)..Q(4+off)"""
    if node['k'] == 'lit':
        n = node['n']; inv = n.startswith('!'); b = n.lstrip('!')
        if b[0] == 'Q' and b[1:].isdigit(): b = 'Q%d' % (int(b[1:]) + off)
        return lit(('!' if inv else '') + b)
    if node['k'] == 'c': return dict(node)
    if node['k'] == 'nand': return nand(*[rename(c, off) for c in node['ch']])
    if node['k'] == 'mux':
        return {'k': 'mux', 'sel': [rename(c, off) for c in node['sel']], 'd': [rename(c, off) for c in node['d']]}

def ev_tree(node, env):
    k = node['k']
    if k == 'c': return node['v']
    if k == 'lit':
        n = node['n']
        return 1 - env[n[1:]] if n.startswith('!') else env[n]
    if k == 'nand': return 0 if all(ev_tree(c, env) for c in node['ch']) else 1
    if k == 'mux':
        a = sum(ev_tree(s, env) << i for i, s in enumerate(node['sel']))
        return ev_tree(node['d'][a], env)

JK = jk()                                  # МДНФ функций возбуждения
P_SOP = minimize([CODE[9]], DC)            # перенос
SEG_ON = {s: [CODE[d] for d in range(10) if s in SEG[d]] for s in SEGS}
SEG_OFF = {s: [CODE[d] for d in range(10) if s not in SEG[d]] for s in SEGS}
SEGN_SOP = {s: minimize(SEG_OFF[s], DC) for s in SEGS}   # инверсные функции (общий анод)

def mux_data(s):
    """Адрес Q4Q3Q2 (A2A1A0), на информационных входах 0, 1, Q1 или !Q1."""
    out = []
    for a in range(8):
        c0, c1 = a << 1, (a << 1) | 1
        v = [None if m in DC else int(m in SEG_OFF[s]) for m in (c0, c1)]
        if v[0] is None and v[1] is None: d = const(0)
        elif v[0] in (None, v[1]) or v[1] is None or v[0] == v[1]:
            d = const(v[1] if v[1] is not None else v[0])
        else: d = lit('Q1') if v[1] == 1 else lit('!Q1')
        out.append(d)
    return {'k': 'mux', 'sel': [lit('Q2'), lit('Q3'), lit('Q4')], 'd': out}

def decade(off):
    ffs = []
    for i in (1, 2, 3, 4):
        ffs.append({'q': 'Q%d' % (i + off), 'J': rename(sop_to_nand(JK['J%d' % i]), off),
                    'K': rename(sop_to_nand(JK['K%d' % i]), off), 'clk': 'C' if off == 0 else 'P'})
    return ffs

def conv(off):
    return [(s, rename(mux_data(s) if s in MUX_SEGS else sop_to_nand(SEGN_SOP[s]), off)) for s in SEGS]

DEC1, DEC2 = decade(0), decade(4)
P_TREE = sop_to_nand(P_SOP)
CONV1, CONV2 = conv(0), conv(4)

def simulate(n_pulses):
    """Возвращает список состояний после каждого спада С (включая исходное)."""
    st = {'Q%d' % i: 0 for i in range(1, 9)}
    def upd(ffs, env):
        new = {}
        for f in ffs:
            q = env[f['q']]; j = ev_tree(f['J'], env); k = ev_tree(f['K'], env)
            new[f['q']] = int((j and not q) or (q and not k))
        return new
    hist = [dict(st, P=ev_tree(P_TREE, st))]
    for _ in range(n_pulses):
        p0 = ev_tree(P_TREE, st)
        nxt = dict(st); nxt.update(upd(DEC1, st))
        if p0 == 1 and ev_tree(P_TREE, nxt) == 0: nxt.update(upd(DEC2, st))   # спад P
        st = nxt
        hist.append(dict(st, P=ev_tree(P_TREE, st)))
    return hist

def shown_digit(cv, env):
    lit_ = ''.join(s for s, t in cv if ev_tree(t, env) == 0)      # 0 - сегмент горит
    for d, segs in SEG.items():
        if segs == lit_: return d
    return None

if __name__ == '__main__':
    h = simulate(250)
    for n, st in enumerate(h):
        assert shown_digit(CONV1, st) == n % 10 and shown_digit(CONV2, st) == (n // 10) % 10, n
    print('OK: 250 импульсов, индикация 00..99 верна')
    for s in MUX_SEGS:
        print(s, [(d['v'] if d['k'] == 'c' else d['n']) for d in mux_data(s)['d']])
    cnt = {}
    def walk(t):
        if t['k'] == 'nand':
            n = max(len(t['ch']), 2); cnt[n] = cnt.get(n, 0) + 1
            for c in t['ch']: walk(c)
    for f in DEC1 + DEC2: walk(f['J']); walk(f['K'])
    walk(P_TREE)
    for _, t in CONV1 + CONV2: walk(t)
    print('gates by inputs', cnt)
