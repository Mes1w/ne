from draw import *
OUT = 'out/'
def rn(a, b, first): return [first] + [x for i in range(b, a - 1, -1) for x in ('Q%d' % i, '!Q%d' % i)]

def fig_decade(ffs, names, fname, clkname):
    cv = Canvas(); r = HRails(cv, names, 0)
    x, g = draw_decade(cv, 0, r.bottom + 18, ffs, r, False)
    r.finish(-6, {names[0]: clkname}); cv.save(OUT + fname)

class Both:                       # дерево переноса: входы с линий 1-й декады, выход на линию P
    def __init__(s, r1, r2): s.r1, s.r2 = r1, r2
    def tap(s, n, xx, y): (s.r2 if n == 'P' else s.r1).tap(n, xx, y)

def fig_counter():
    cv = Canvas(); r1 = HRails(cv, rn(1, 4, 'C'), 0); r2 = HRails(cv, rn(5, 8, 'P'), 0)
    x, g = draw_decade(cv, 0, r1.bottom + 18, DEC1, r1, False)
    x2 = draw_tree_block(cv, x + 6, g['C'], P_TREE, Both(r1, r2), 'P', False)
    x3, _ = draw_decade(cv, x2 + 22, r1.bottom + 18, DEC2, r2, False)
    r1.finish(-6, {'C': 'вход C'}); r2.finish(x2 - 14)
    cv.save(OUT + 'fig_counter')

def fig_conv():
    cv = Canvas(); names = [x for i in (4, 3, 2, 1) for x in ('Q%d' % i, '!Q%d' % i)]
    outs, xr, yb = draw_conv(cv, 0, 0, CONV1, names, False)
    for n, xo, yo in outs:
        cv.line([(xo, yo), (xr + 40, yo)]); terminal(cv, xr + 42, yo, lab('!' + n))
    cv.save(OUT + 'fig_converter')

if __name__ == '__main__':
    fig_decade(DEC1, rn(1, 4, 'C'), 'fig_decade1', 'вход C')
    fig_decade(DEC2, rn(5, 8, 'P'), 'fig_decade2', 'вход P')
    fig_counter(); fig_conv()
