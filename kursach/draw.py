"""Отрисовка схем (УГО по ГОСТ) в SVG/PNG."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from design import *

P, GW, CW, GAP, FW, MW = 14, 30, 52, 8, 46, 54
JOG0, JSTEP = 14, 5

def lab(n):
    inv = n.startswith('!'); b = n.lstrip('!')
    if len(b) > 1 and b[1:].isdigit():
        return r'$\overline{%s}_{%s}$' % (b[0], b[1:]) if inv else r'$%s_{%s}$' % (b[0], b[1:])
    return r'$\overline{%s}$' % b if inv else b

class Canvas:
    def __init__(s): s.it = []; s.xs = []; s.ys = []
    def _b(s, x, y): s.xs.append(x); s.ys.append(y)
    def line(s, pts, lw=0.8):
        for p in pts: s._b(*p)
        s.it.append(('l', pts, lw))
    def rect(s, x, y, w, h, lw=1.3): s._b(x, y); s._b(x + w, y + h); s.it.append(('r', x, y, w, h, lw))
    def circ(s, x, y, r=3, fill=False): s._b(x - r, y - r); s._b(x + r, y + r); s.it.append(('c', x, y, r, fill))
    def dot(s, x, y): s.circ(x, y, 1.8, True)
    def poly(s, pts): s.it.append(('p', pts))
    def text(s, x, y, t, size=8, ha='center', va='center', rot=0, bold=False):
        w = 0.6 * size * len(t.replace('$', '').replace('\\overline', '')) if rot == 0 else 6
        s._b(x - (w if ha != 'left' else 2), y - 5); s._b(x + (w if ha != 'right' else 2), y + 5); s.it.append(('t', x, y, t, size, ha, va, rot, bold))
    def save(s, base, m=18, dpi=300):
        x0, x1, y0, y1 = min(s.xs) - m, max(s.xs) + m, min(s.ys) - m, max(s.ys) + m
        fig = plt.figure(figsize=((x1 - x0) / 72, (y1 - y0) / 72))
        ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(x0, x1); ax.set_ylim(y1, y0); ax.axis('off')
        for i in s.it:
            if i[0] == 'l':
                ax.plot([p[0] for p in i[1]], [p[1] for p in i[1]], color='k', lw=i[2], zorder=4, solid_capstyle='round', solid_joinstyle='miter')
            elif i[0] == 'r': ax.add_patch(Rectangle((i[1], i[2]), i[3], i[4], fill=True, fc='white', ec='k', lw=i[5], zorder=3))
            elif i[0] == 'c': ax.add_patch(Circle((i[1], i[2]), i[3], fc='k' if i[4] else 'white', ec='k', lw=0.8, zorder=5))
            elif i[0] == 'p': ax.add_patch(Polygon(i[1], closed=False, fill=False, ec='k', lw=0.8, zorder=4))
            elif i[0] == 't':
                ax.text(i[1], i[2], i[3], fontsize=i[4], ha=i[5], va=i[6], rotation=i[7], zorder=5,
                        fontweight='bold' if i[8] else 'normal', rotation_mode='anchor')
        fig.savefig(base + '.svg'); fig.savefig(base + '.png', dpi=dpi); plt.close(fig)

# ---------- размеры деревьев ----------
def nin(n): return max(len(n['ch']), 2)
def height(n):
    if n['k'] == 'nand':
        ch = n['ch']; g = GAP if any(c['k'] == 'nand' for c in ch) else 0
        return max(nin(n) * P, sum(height(c) for c in ch) + g * (len(ch) - 1))
    if n['k'] == 'mux': return 14 * P
    return P
def depth(n):
    if n['k'] == 'nand': return 1 + max(depth(c) for c in n['ch'])
    return 1 if n['k'] == 'mux' else 0

def place_gate(cv, n, xr, yc, leaves, pr):
    """Элемент И-НЕ с правой гранью xr; возвращает точку выхода."""
    ch = n['ch']; k = nin(n); gh = k * P; xl = xr - GW
    cv.rect(xl, yc - gh / 2, GW, gh); cv.text(xl + 8, yc - gh / 2 + 8, '&', size=8)
    cv.circ(xr + 3, yc)
    pins = [yc - gh / 2 + P / 2 + i * P for i in range(k)]
    if pr:
        cv.text(xl + GW / 2, yc - gh / 2 - 2.5, n['ref'], size=5.5, va='bottom')
        cv.text(xr + 7.5, yc - 1.5, str(n['pins'][-1]), size=4.5, ha='left', va='bottom')
        for i, py in enumerate(pins): cv.text(xl - 2, py - 1.5, str(n['pins'][i]), size=4.5, ha='right', va='bottom')
    if len(ch) == 1:
        xt = xl - 12
        for py in pins: cv.line([(xt, py), (xl, py)])
        cv.line([(xt, pins[0]), (xt, pins[1])]); cv.dot(xt, yc)
        tg = [(xt, yc)]
    else: tg = [(xl, py) for py in pins]
    hs = [height(c) for c in ch]; g = GAP if any(c['k'] == 'nand' for c in ch) else 0
    y = yc - (sum(hs) + g * (len(ch) - 1)) / 2; cys = []
    for h in hs: cys.append(y + h / 2); y += h + g
    up = [i for i in range(len(ch)) if cys[i] < tg[i][1] - .01]
    dn = [i for i in range(len(ch)) if cys[i] > tg[i][1] + .01]
    jog = {}
    for r, i in enumerate(up): jog[i] = tg[i][0] - JOG0 - JSTEP * r
    for r, i in enumerate(reversed(dn)): jog[i] = tg[i][0] - JOG0 - JSTEP * r
    for i, c in enumerate(ch):
        tx, ty = tg[i]; jx = jog.get(i, tx - JOG0)
        if c['k'] == 'nand':
            cx, cy = place_gate(cv, c, xl - CW, cys[i], leaves, pr)
            cv.line([(cx, cy), (jx, cy), (jx, ty), (tx, ty)])
        else:
            cv.line([(jx, cys[i]), (jx, ty), (tx, ty)]); leaves.append((c, jx, cys[i]))
    return xr + 6, yc

MUX_PINS = {'A': [11, 10, 9], 'D': [4, 3, 2, 1, 15, 14, 13, 12], 'E': 7, 'Y': 5}
def place_mux(cv, n, xr, yc, leaves, pr):
    xl = xr - MW; h = 14 * P; yt = yc - h / 2
    cv.rect(xl, yt, MW, h); cv.line([(xl + 22, yt), (xl + 22, yt + h)], 0.8)
    cv.text(xl + 38, yt + 10, 'MS', size=8)
    rows = [('A0', n['sel'][0], 'A', 0), ('A1', n['sel'][1], 'A', 1), ('A2', n['sel'][2], 'A', 2)]
    rows += [('D%d' % i, n['d'][i], 'D', i) for i in range(8)] + [('E', const(0), 'E', 0)]
    y = yt + P / 2 + 2
    for name, node, grp, i in rows:
        if name in ('D0', 'E'):
            cv.line([(xl, y - 1), (xl + 22, y - 1)], 0.6); y += P / 2 + 2
        cv.text(xl + 11, y, name, size=6)
        x_end = xl
        if name == 'E': cv.circ(xl - 3, y); x_end = xl - 6
        cv.line([(xl - 14, y), (x_end, y)])
        if pr:
            num = MUX_PINS[grp][i] if grp != 'E' else MUX_PINS['E']
            cv.text(xl - 7, y - 1.5, str(num), size=4.5, ha='right', va='bottom')
        leaves.append((node, xl - 14, y)); y += P
    if pr:
        cv.text(xl + MW / 2, yt - 2.5, n['ref'], size=5.5, va='bottom')
        cv.text(xr + 2, yc - 1.5, '5', size=4.5, ha='left', va='bottom')
    cv.text(xr - 7, yc, 'Y', size=6)
    return xr, yc

def const_stub(cv, node, x, y, pr):
    cv.line([(x - 9, y), (x, y)])
    if pr and node['v'] == 0:
        cv.line([(x - 9, y - 4), (x - 9, y + 4)], 1.6)          # общий провод
    else:
        cv.text(x - 11, y, '«%d»' % node['v'] if not pr else '+E', size=5.5, ha='right')

# ---------- приёмники сигналов: горизонтальные шины-линии (сверху) ----------
class HRails:
    def __init__(s, cv, names, y0, bus=False, pitch=9):
        s.cv, s.bus, s.y0 = cv, bus, y0
        s.y = {n: (y0 if bus else y0 + i * pitch) for i, n in enumerate(names)}
        s.ext = {}; s.bottom = y0 if bus else y0 + (len(names) - 1) * pitch
    def tap(s, name, x, y):
        ry = s.y[name]; s.cv.line([(x, y), (x, ry)])
        if s.bus:
            s.cv.text(x - 1.5, ry + 4, lab(name), size=5, ha='right', va='bottom', rot=90)
        else: s.cv.dot(x, ry)
        a, b = s.ext.get(name, (x, x)); s.ext[name] = (min(a, x), max(b, x))
    def finish(s, x0, names=None):
        if s.bus: return
        for n, (a, b) in s.ext.items():
            s.cv.line([(x0, s.y[n]), (b, s.y[n])])
            s.cv.text(x0 - 4, s.y[n], (names or {}).get(n, lab(n)), size=6.5, ha='right')

def ff_geom(ffs, ytop):
    H = max([height(f['J']) for f in ffs] + [height(f['K']) for f in ffs] + [2 * P])
    yS = ytop + 12; yJ = yS + 10 + H / 2; yC = yJ + H / 2 + 10; yK = yC + 10 + H / 2; yR = yK + H / 2 + 10
    return dict(S=yS, J=yJ, C=yC, K=yK, R=yR, bot=yR + 12, top=ytop)


def draw_ff(cv, xff, g, f, pr):
    cv.rect(xff, g['top'], FW, g['bot'] - g['top']); cv.line([(xff + 16, g['top']), (xff + 16, g['bot'])], 0.8)
    for k in 'SJKR': cv.text(xff + 8, g[k], k, size=6.5)
    cv.text(xff + 11, g['C'], 'C', size=6.5); cv.poly([(xff, g['C'] - 4), (xff + 5, g['C']), (xff, g['C'] + 4)])
    cv.text(xff + 31, g['top'] + 10, 'TT', size=8)
    xr = xff + FW; cv.circ(xr + 3, g['K'])
    if pr:
        cv.text(xff + FW / 2, g['bot'] + 2.5, f['ref'], size=5.5, va='top')
        for k in 'SJCKR': cv.text(xff - 7.5, g[k] - 1.5, str(f['pins'][k]), size=4.5, ha='right', va='bottom')
        cv.text(xr + 2, g['J'] - 1.5, str(f['pins']['Q']), size=4.5, ha='left', va='bottom')
        cv.text(xr + 7.5, g['K'] - 1.5, str(f['pins']['nQ']), size=4.5, ha='left', va='bottom')

def draw_decade(cv, x0, ytop, ffs, rails, pr):
    g = ff_geom(ffs, ytop); x = x0
    for f in ffs:
        leaves = []; d = max(depth(f['J']), depth(f['K']))
        nl = 1 + (2 if pr else 0) + sum(count_leaves(f[k]) for k in 'JK')
        cp = 9 if pr else 7; xcr = x + 4 + cp * nl
        ro = 34 if pr else 20
        xff = xcr + 16 + (GW + (d - 1) * (GW + CW) + ro + 6 if d else 6)
        for k in 'JK':
            if f[k]['k'] == 'nand':
                xo, yo = place_gate(cv, f[k], xff - ro, g[k], leaves, pr); cv.line([(xo, yo), (xff, yo)])
            else: leaves.append((f[k], xff, g[k]))
        cv.circ(xff - 3, g['C']); leaves.append((lit(f['clk']), xff - 6, g['C']))
        if pr:
            for k, net in (('S', 'H'), ('R', 'R')):
                cv.circ(xff - 3, g[k]); leaves.append((lit(net), xff - 6, g[k]))
        if pr: leaves = [(lit('H') if n['k'] == 'c' else n, xe, y) for n, xe, y in leaves]
        r = 0
        for node, xe, y in sorted(leaves, key=lambda l: l[2]):
            if node['k'] == 'c': const_stub(cv, node, xe, y, pr); continue
            xc = xcr - cp * r; r += 1
            cv.line([(xc, y), (xe, y)]); rails.tap(node['n'], xc, y)
        draw_ff(cv, xff, g, f, pr)
        xr = xff + FW; xq1, xq2 = xr + 14, xr + 24
        cv.line([(xr, g['J']), (xq1, g['J'])]); rails.tap(f['q'], xq1, g['J'])
        cv.line([(xr + 6, g['K']), (xq2, g['K'])]); rails.tap('!' + f['q'], xq2, g['K'])
        x = xq2 + 14
    return x, g

def count_leaves(n):
    if n['k'] == 'nand': return sum(count_leaves(c) for c in n['ch'])
    return 1

def draw_tree_block(cv, x0, yc, tree, rails, out_net, pr):
    """Отдельное дерево (цепь переноса P): входы и выход на линии сверху."""
    cp = 9 if pr else 7; leaves = []; nl = count_leaves(tree); xcr = x0 + 4 + cp * nl; d = depth(tree)
    xr = xcr + 16 + GW + (d - 1) * (GW + CW)
    xo, yo = place_gate(cv, tree, xr, yc, leaves, pr)
    for r, (node, xe, y) in enumerate(sorted(leaves, key=lambda l: l[2])):
        xc = xcr - cp * r; cv.line([(xc, y), (xe, y)]); rails.tap(node['n'], xc, y)
    cv.line([(xo, yo), (xo + 12, yo)]); rails.tap(out_net, xo + 12, yo)
    return xo + 26

# ---------- преобразователь кода: вертикальные линии слева ----------
def draw_conv(cv, x0, ytop, funcs, names, pr, bus=False, fgap=16):
    dmax = max(depth(t) for _, t in funcs)
    if bus: xleft = x0 + 22; rx = {n: x0 for n in names}
    else: xleft = x0 + 9 * (len(names) - 1) + 14; rx = {n: x0 + 9 * i for i, n in enumerate(names)}
    xroot = xleft + 18 + GW + (dmax - 1) * (GW + CW)
    y = ytop; outs = []
    for name, tree in funcs:
        h = height(tree); yc = y + h / 2; leaves = []
        xo, yo = (place_mux if tree['k'] == 'mux' else place_gate)(cv, tree, xroot, yc, leaves, pr)
        for node, xe, ly in leaves:
            if node['k'] == 'c':
                if pr and node['v'] == 1:
                    cv.line([(rx['H'], ly), (xe, ly)]); cv.text(x0 + 3, ly - 1.5, 'H', size=5, ha='left', va='bottom')
                else: const_stub(cv, node, xe, ly, pr)
                continue
            cv.line([(rx[node['n']], ly), (xe, ly)])
            if bus: cv.text(x0 + 3, ly - 1.5, lab(node['n']), size=5, ha='left', va='bottom')
            else: cv.dot(rx[node['n']], ly)
        outs.append((name, xo, yo)); y += h + fgap
    ybot = y - fgap
    if not bus:
        for n in names:
            cv.line([(rx[n], ytop - 14), (rx[n], ybot + 4)]); cv.text(rx[n], ytop - 17, lab(n), size=6.5, va='bottom')
    return outs, xroot, ybot

def terminal(cv, x, y, label, side='right'):
    cv.circ(x, y, 2.2)
    cv.text(x + (5 if side == 'right' else -5), y, label, size=7, ha='left' if side == 'right' else 'right')
