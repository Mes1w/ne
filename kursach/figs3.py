from figs import *
import alloc

def fig_block():
    cv = Canvas(); x = 40
    cv.text(0, 30, 'Счётный\nвход', size=9); cv.line([(22, 30), (x, 30)]); cv.poly([(x - 6, 27), (x, 30), (x - 6, 33)])
    for i, t in enumerate(('Двоично-\nкодированный\nсчётчик\n(код 2-7-4-1, М = 100)', 'Преобразователь\nкода', 'Семисегментные\nиндикаторы')):
        cv.rect(x, 0, 120, 60); cv.text(x + 60, 30, t, size=8.5)
        if i < 2:
            cv.line([(x + 120, 30), (x + 160, 30)]); cv.poly([(x + 154, 27), (x + 160, 30), (x + 154, 33)])
        x += 160
    cv.save(OUT + 'fig_block')

def fig_ugo():
    cv = Canvas(); x = 0
    def stubs(leaves):
        for n, xe, y in leaves: cv.line([(xe - 16, y), (xe, y)])
    for title, secs in (('К555ЛА3', alloc.LA3), ('К555ЛА4', alloc.LA4), ('К555ЛА1', alloc.LA1)):
        y = 0
        for i, s in enumerate(secs):
            n = {'k': 'nand', 'ch': [lit('x')] * (len(s) - 1), 'ref': 'DD.%d' % (i + 1), 'pins': s}
            lv = []; h = height(n); xo, yo = place_gate(cv, n, x + 60, y + h / 2, lv, True); stubs(lv)
            cv.line([(xo, yo), (xo + 16, yo)]); y += h + 22
        cv.text(x + 45, -22, title, size=7); x += 130
    ffs = [{'J': lit('x'), 'K': lit('x'), 'ref': 'DD.%d' % (i + 1), 'pins': alloc.TV9[i]} for i in range(2)]
    for i, f in enumerate(ffs):
        g = ff_geom(ffs, i * 150); xff = x + 30; draw_ff(cv, xff, g, f, True)
        for k in 'SJCKR':
            if k in 'SCR': cv.circ(xff - 3, g[k])
            cv.line([(xff - 22, g[k]), (xff - (6 if k in 'SCR' else 0), g[k])])
        cv.line([(xff + FW, g['J']), (xff + FW + 16, g['J'])]); cv.line([(xff + FW + 6, g['K']), (xff + FW + 22, g['K'])])
    cv.text(x + 53, -22, 'К555ТВ9', size=7); x += 150
    m = {'k': 'mux', 'sel': [lit('x')] * 3, 'd': [lit('x')] * 8, 'ref': 'DD'}
    lv = []; xo, yo = place_mux(cv, m, x + 30 + MW, 100, lv, True); stubs(lv); cv.line([(xo, yo), (xo + 16, yo)])
    cv.text(x + 30 + MW / 2, -22, 'К555КП7', size=7)
    cv.save(OUT + 'fig_ugo')

def wave(ax, y, bits, label, half=False):
    xs, ys = [], []
    for i, b in enumerate(bits):
        if half: xs += [i, i + .5, i + .5, i + 1]; ys += [y + .7, y + .7, y, y]
        else: xs += [i, i + 1]; ys += [y + .7 * b, y + .7 * b]
    ax.plot(xs, ys, color='k', lw=1.0, drawstyle='default'); ax.text(-0.4, y + .35, label, ha='right', va='center', fontsize=8)

def fig_timing(fname, sigs, n, clk, digits):
    """Состояние i действует на интервале [i-0.5, i+0.5): переключение по спаду тактового импульса."""
    fig, ax = plt.subplots(figsize=(min(11, 2 + n * 0.32), 0.42 * (len(sigs) + 2) + 0.4))
    rows = len(sigs) + 1; wave(ax, rows - 1, [1] * n, clk, half=True)
    for r, (label, bits) in enumerate(sigs):
        y = rows - 2 - r; xs, ys = [0], [y + .7 * bits[0]]
        for i in range(1, len(bits)):
            xs += [i - .5, i - .5]; ys += [y + .7 * bits[i - 1], y + .7 * bits[i]]
        xs.append(n); ys.append(y + .7 * bits[-1]); ax.plot(xs, ys, color='k', lw=1.0)
        ax.text(-0.4, y + .35, label, ha='right', va='center', fontsize=8)
    for i, d in enumerate(digits):
        ax.text(i if i else 0.25, -0.55, str(d), ha='center', va='center', fontsize=6.5)
        if i: ax.axvline(i - .5, color='0.8', lw=0.4, zorder=0)
    ax.text(-0.4, -0.55, 'число', ha='right', va='center', fontsize=8)
    ax.set_xlim(-2.2, n + .2); ax.set_ylim(-1, rows + .1); ax.axis('off')
    fig.savefig(OUT + fname + '.png', dpi=200, bbox_inches='tight'); fig.savefig(OUT + fname + '.svg', bbox_inches='tight'); plt.close(fig)

def timing():
    h = simulate(40)
    q = lambda k, hh: [s[k] for s in hh]
    h1 = h[:13]
    fig_timing('fig_timing_dec1', [(lab('Q%d' % i), q('Q%d' % i, h1)) for i in (1, 2, 3, 4)], 12, 'C', [i % 10 for i in range(13)])
    h2 = simulate(125)[::10]
    fig_timing('fig_timing_dec2', [(lab('Q%d' % i), q('Q%d' % i, h2)) for i in (5, 6, 7, 8)], 12, 'P', [i % 10 for i in range(13)])
    h3 = h[:33]
    fig_timing('fig_timing_counter', [(lab('Q%d' % i), q('Q%d' % i, h3)) for i in (1, 2, 3, 4)] + [('P', q('P', h3))] +
               [(lab('Q%d' % i), q('Q%d' % i, h3)) for i in (5, 6, 7, 8)], 32, 'C', list(range(33)))

if __name__ == '__main__':
    fig_block(); fig_ugo(); timing()
