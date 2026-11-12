from figs import *
import alloc

def fig_counter2():
    cv = Canvas(); r1 = HRails(cv, rn(1, 4, 'C'), 0)
    x, g = draw_decade(cv, 0, r1.bottom + 18, DEC1, r1, False)
    y2 = g['bot'] + 40
    r2 = HRails(cv, rn(5, 8, 'P'), y2)
    x2 = draw_tree_block(cv, x + 6, g['C'], P_TREE, Both(r1, r2), 'P', False)
    draw_decade(cv, 0, r2.bottom + 18, DEC2, r2, False)
    r1.finish(-6, {'C': 'вход C'}); r2.finish(-6)
    cv.save(OUT + 'fig_counter')

def resistor(cv, x, y, ref, w=20):
    cv.rect(x, y - 4, w, 8, 1.0); cv.text(x + w / 2, y - 6, ref, size=5, va='bottom')

def gnd(cv, x, y):
    cv.line([(x, y), (x, y + 8)]); cv.line([(x - 5, y + 8), (x + 5, y + 8)], 1.8)

HG_PINS = dict(a=1, b=13, c=10, d=8, e=7, f=2, g=11)
def fig_principal():
    import draw; draw.GAP = 14
    cv = Canvas(); BX = -46
    names = rn(1, 8, 'C') + ['P', 'H', 'R']
    b1 = HRails(cv, names, 0, bus=True)
    x1, g = draw_decade(cv, 0, 62, DEC1, b1, True)
    xp = draw_tree_block(cv, x1 + 6, g['C'], P_TREE, b1, 'P', True)
    y2 = g['bot'] + 46
    b2 = HRails(cv, names, y2, bus=True)
    x2, g2 = draw_decade(cv, 0, y2 + 62, DEC2, b2, True)
    cv.text(x1 / 2, g['bot'] + 20, 'Младший разряд (единицы)', size=7); cv.text(x1 / 2, g2['bot'] + 20, 'Старший разряд (десятки)', size=7)
    # преобразователи кода
    xc = xp + 40; rnum = 1; ybm = 0; xend = xc
    for k, (cvn, hg) in enumerate(((CONV1, 'HG1'), (CONV2, 'HG2'))):
        outs, xr, yb = draw_conv(cv, xc, 34, cvn, names, True, bus=True)
        cv.line([(xc, 0), (xc, yb + 10)], 3.2); ybm = max(ybm, yb)
        xi = xr + 6 + 14 + 20 + 12 + 7 * 6 + 22; n = len(outs)
        yi0 = (34 + yb) / 2 - n * P / 2
        cv.rect(xi, yi0 - 14, 62, n * P + 28); cv.line([(xi + 14, yi0 - 14), (xi + 14, yi0 + n * P + 14)], 0.8)
        cv.text(xi + 31, yi0 - 17, hg, size=5.5, va='bottom')
        py = [yi0 + P / 2 + i * P for i in range(n)]
        up = [i for i in range(n) if outs[i][2] < py[i]]; dn = [i for i in range(n) if outs[i][2] > py[i]]
        jog = {}
        for r, i in enumerate(up): jog[i] = xi - 16 - 6 * r
        for r, i in enumerate(reversed(dn)): jog[i] = xi - 16 - 6 * r
        for i, (s, xo, yo) in enumerate(outs):
            jx = jog.get(i, xi - 16); xt = xr + 34
            cv.line([(xo, yo), (jx, yo), (jx, py[i]), (xi, py[i])])
            # подтягивающий резистор к +5 В: ток сегмента при «1» на выходе
            cv.dot(xt, yo); cv.line([(xt, yo), (xt, yo - 6)]); cv.rect(xt - 4, yo - 22, 8, 16, 1.0); cv.line([(xt, yo - 22), (xt, yo - 26)])
            cv.line([(xt - 5, yo - 26), (xt + 5, yo - 26)], 1.4)
            cv.text(xt + 6, yo - 14, 'R%d' % rnum, size=5, ha='left'); cv.text(xt, yo - 28, '+5 В', size=4.5, va='bottom'); rnum += 1
            cv.text(xi + 7, py[i], s, size=6.5); cv.text(xi - 2, py[i] - 1.5, str(HG_PINS[s]), size=4.5, ha='right', va='bottom')
        # условное изображение цифры и общий катод
        cx, cy = xi + 38, (34 + yb) / 2
        for seg in ([(-8, -14), (8, -14)], [(8, -14), (8, 0)], [(8, 0), (8, 14)], [(-8, 14), (8, 14)], [(-8, 0), (-8, 14)], [(-8, -14), (-8, 0)], [(-8, 0), (8, 0)]):
            cv.line([(cx + a, cy + b_) for a, b_ in seg], 2.0)
        ya = yi0 + n * P + 4
        cv.line([(xi + 62, ya), (xi + 80, ya)]); cv.text(xi + 64, ya - 1.5, '3, 14', size=4.5, ha='left', va='bottom')
        cv.text(xi + 56, ya, 'K', size=6); gnd(cv, xi + 80, ya)
        cv.text((xc + xi + 62) / 2, 14, 'Преобразователь кода %s' % ('единиц' if k == 0 else 'десятков'), size=7)
        xlast = xc; xend = xi + 110; xc = xend + 20
    # магистраль
    cv.line([(BX, 0), (xlast, 0)], 3.2); cv.line([(BX, 0), (BX, g2['bot'] + 150)], 3.2); cv.line([(BX, y2), (x2 + 4, y2)], 3.2)
    # вспомогательные цепи
    yq = g2['bot'] + 50
    def tapv(y, name): cv.text(BX + 3, y - 1.5, name, size=5, ha='left', va='bottom')
    cv.line([(BX, yq), (60, yq)]); tapv(yq, 'C'); cv.rect(60, yq - 10, 70, 62); cv.text(95, yq - 13, 'XP1', size=5.5, va='bottom')
    for i, (t, extra) in enumerate((('Счётный вход', None), ('+5 В', '+5 В'), ('Общий', 'gnd'))):
        yy = yq + i * 20; cv.text(124, yy, t, size=5.5, ha='right'); cv.text(57, yy - 1.5, str(i + 1), size=4.5, ha='right', va='bottom')
        if i: cv.line([(30, yy), (60, yy)])
        if extra == '+5 В': cv.text(28, yy, '+5 В', size=6, ha='right')
        if extra == 'gnd': gnd(cv, 30, yy)
    xa = 200
    cv.line([(BX, yq + 80), (xa, yq + 80)]); tapv(yq + 80, 'H')
    cv.line([(xa, yq + 80), (xa, yq + 40)]); cv.line([(xa, yq + 20), (xa, yq)]); cv.rect(xa - 4, yq + 20, 8, 20, 1.0); cv.text(xa + 7, yq + 30, 'R15', size=5, ha='left'); cv.text(xa, yq - 5, '+5 В', size=6)
    xb = 280
    cv.line([(BX, yq + 96), (xb, yq + 96)]); tapv(yq + 96, 'R')
    cv.line([(xb, yq + 96), (xb, yq + 40)]); cv.line([(xb, yq + 20), (xb, yq)]); cv.rect(xb - 4, yq + 20, 8, 20, 1.0); cv.text(xb + 7, yq + 30, 'R16', size=5, ha='left'); cv.text(xb, yq - 5, '+5 В', size=6)
    cv.dot(xb, yq + 96); cv.line([(xb, yq + 96), (xb + 30, yq + 96)]); cv.line([(xb + 30, yq + 96), (xb + 48, yq + 88)]); cv.line([(xb + 50, yq + 96), (xb + 70, yq + 96)])
    cv.text(xb + 40, yq + 84, 'SB1 «Сброс»', size=5, va='bottom'); gnd(cv, xb + 70, yq + 96)
    xk = 420
    for i, (ref, lbl) in enumerate((('C1', '10 мкФ'), ('C2–C7', '0,1 мкФ'))):
        xx = xk + i * 70
        cv.line([(xx, yq), (xx, yq + 26)]); cv.line([(xx - 7, yq + 26), (xx + 7, yq + 26)], 1.6); cv.line([(xx - 7, yq + 31), (xx + 7, yq + 31)], 1.6)
        cv.line([(xx, yq + 31), (xx, yq + 56)]); gnd(cv, xx, yq + 56); cv.text(xx, yq - 5, '+5 В', size=6)
        cv.text(xx + 10, yq + 24, ref, size=5, ha='left'); cv.text(xx + 10, yq + 34, lbl, size=5, ha='left')
    A = alloc
    notes = ['1. %s – К555ТВ9; %s – К555ЛА3; %s – К555ЛА4; %s – К555ЛА1; %s – К555КП7; HG1, HG2 – АЛС324А (общий катод).' % tuple(A.RNG[t] for t in ('TV9', 'LA3', 'LA4', 'LA1', 'KP7')),
             '2. Выводы питания: +5 В – выв. 14 {0}, выв. 16 {1}, {2}; общий – выв. 7 {0}, выв. 8 {1}, {2}.'.format(A.RNG14, A.RNG['TV9'], A.RNG['KP7']),
             '3. Цепи шины: C – счётный вход; P – перенос в старший разряд; H – лог. «1» (через R15); R – сброс (активный уровень «0»).',
             '4. ' + A.SPARE_TXT + ' R1–R14 – 620 Ом; R15, R16 – 1 кОм.']
    for i, t in enumerate(notes): cv.text(0, yq + 130 + i * 13, t, size=6, ha='left')
    cv.xs += [0, 900]
    cv.save(OUT + 'principal', dpi=250); draw.GAP = 8

if __name__ == '__main__':
    fig_counter2(); fig_principal()
    from PIL import Image
    im = Image.open(OUT + 'principal.png'); print(im.size)
    im.crop((0, 0, im.size[0] // 2, im.size[1] // 2)).save('/tmp/p_tl.png'); im.crop((im.size[0] // 2, 0, im.size[0], im.size[1] // 2)).save('/tmp/p_tr.png')
    im.crop((0, im.size[1] // 2, im.size[0] // 2, im.size[1])).save('/tmp/p_bl.png'); im.crop((im.size[0] // 2, im.size[1] // 2, im.size[0], im.size[1])).save('/tmp/p_br.png')
    im.resize((im.size[0] // 4, im.size[1] // 4)).save('/tmp/p_small.png')
