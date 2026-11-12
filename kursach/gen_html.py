"""Интерактивный HTML-макет счётного устройства: та же логика, что в design.py."""
import json, os
from design import *

def lh(n):
    inv = n.startswith('!'); b = n.lstrip('!')
    s = '%s<sub>%s</sub>' % (b[0], b[1:]) if len(b) > 1 else b
    return '<span class="ov">%s</span>' % s if inv else s

def sop_h(terms, off=0):
    if not terms: return '0'
    if terms == [(0, 0)]: return '1'
    return ' + '.join('·'.join(lh(rename(lit(l), off)['n']) for l in term_lits(t)) for t in terms)

W = {1: 1, 2: 4, 3: 7, 4: 2}
def dec_json(ffs, off):
    out = []
    for f in ffs:
        i = int(f['q'][1:]) - off
        out.append({'q': f['q'], 'w': W[i], 'J': f['J'], 'K': f['K'],
                    'jf': sop_h(JK['J%d' % i], off), 'kf': sop_h(JK['K%d' % i], off)})
    return out

def conv_json(cv, off):
    out = []
    for s, t in cv:
        if t['k'] == 'mux':
            d = [str(x['v']) if x['k'] == 'c' else lh(x['n']) for x in t['d']]
            out.append({'s': s, 't': t, 'mux': d})
        else:
            out.append({'s': s, 't': t, 'f': sop_h(SEG_SOP[s], off)})
    return out

NET = {'dec1': dec_json(DEC1, 0), 'dec2': dec_json(DEC2, 4), 'P': P_TREE, 'pf': sop_h(P_SOP),
       'conv1': conv_json(CONV1, 0), 'conv2': conv_json(CONV2, 4)}

CORE = r'''
function lit(n, e) { return n[0] === '!' ? 1 - e[n.slice(1)] : e[n]; }
function ev(t, e) {
  if (t.k === 'c') return t.v;
  if (t.k === 'lit') return lit(t.n, e);
  if (t.k === 'nand') return t.ch.every(function (c) { return ev(c, e); }) ? 0 : 1;
  var a = 0; t.sel.forEach(function (s, i) { a |= ev(s, e) << i; });
  return ev(t.d[a], e);
}
function upd(ffs, e) {
  var o = {};
  ffs.forEach(function (f) { var q = e[f.q], j = ev(f.J, e), k = ev(f.K, e); o[f.q] = ((j && !q) || (q && !k)) ? 1 : 0; });
  return o;
}
// один входной импульс: триггеры младшего разряда переключаются по спаду C, старшего - по спаду P
function pulse(e) {
  var p0 = ev(N.P, e), n = Object.assign({}, e, upd(N.dec1, e));
  if (p0 === 1 && ev(N.P, n) === 0) Object.assign(n, upd(N.dec2, e));
  return n;
}
function zero() { var e = {}; N.dec1.concat(N.dec2).forEach(function (f) { e[f.q] = 0; }); return e; }
function litSegs(cv, e) { return cv.filter(function (c) { return ev(c.t, e) === 1; }).map(function (c) { return c.s; }).join(''); }
'''

UI = r'''
var DIG = {abcdef: 0, bc: 1, abdeg: 2, abcdg: 3, bcfg: 4, acdfg: 5, acdefg: 6, abc: 7, abcdefg: 8, abcdfg: 9};
var SEGR = {a: [10, 4, 40, 8], b: [50, 10, 8, 36], c: [50, 54, 8, 36], d: [10, 88, 40, 8], e: [2, 54, 8, 36], f: [2, 10, 8, 36], g: [10, 46, 40, 8]};
var st = zero(), hist = [st], count = 0, timer = null;
function $(id) { return document.getElementById(id); }
function seg7(id) {
  var h = '<svg viewBox="0 0 60 100" class="seg7" id="' + id + '">';
  Object.keys(SEGR).forEach(function (s) { var r = SEGR[s]; h += '<rect data-s="' + s + '" x="' + r[0] + '" y="' + r[1] + '" width="' + r[2] + '" height="' + r[3] + '" rx="3"/>'; });
  return h + '</svg>';
}
function qh(q) { return q[0] + '<sub>' + q.slice(1) + '</sub>'; }
function ffCards(ffs) {
  return ffs.map(function (f) {
    return '<div class="ff" id="ff-' + f.q + '"><div class="ffh"><b>' + qh(f.q) + '</b><span class="hl-muted">вес ' + f.w + '</span></div>' +
      '<button class="led" data-q="' + f.q + '" title="Нажмите, чтобы переключить триггер вручную">0</button>' +
      '<div class="fn">J = ' + f.jf + ' = <b data-j></b></div><div class="fn">K = ' + f.kf + ' = <b data-k></b></div></div>';
  }).join('');
}
function convTable(cv, id, qs) {
  var h = '<table id="' + id + '"><thead><tr><th>Выход</th><th>На чём</th><th>Функция / вход мультиплексора</th><th class="hl-num">Уровень</th><th>Сегмент</th></tr></thead><tbody>';
  cv.forEach(function (c) {
    h += '<tr data-s="' + c.s + '"><td>' + c.s + '</td><td>' + (c.mux ? 'MS 8→1' : 'И-НЕ') + '</td><td class="fn" data-f>' + (c.mux ? '' : c.f) + '</td><td class="hl-num" data-v></td><td data-l></td></tr>';
  });
  return h + '</tbody></table>';
}
function build() {
  $('disp').innerHTML = seg7('hg2') + seg7('hg1');
  $('d1').innerHTML = ffCards(N.dec1); $('d2').innerHTML = ffCards(N.dec2);
  $('pf').innerHTML = 'P = ' + N.pf + ' = ';
  $('c1').innerHTML = convTable(N.conv1, 't1'); $('c2').innerHTML = convTable(N.conv2, 't2');
  Array.prototype.forEach.call(document.querySelectorAll('.led'), function (b) {
    b.addEventListener('click', function () { st = Object.assign({}, st); st[b.dataset.q] ^= 1; hist.push(st); render(); });
  });
  $('step').addEventListener('click', step);
  $('reset').addEventListener('click', function () { st = zero(); hist = [st]; count = 0; render(); });
  $('auto').addEventListener('change', retime); $('speed').addEventListener('input', retime);
}
function retime() {
  if (timer) { clearInterval(timer); timer = null; }
  $('hz').textContent = $('speed').value + ' Гц';
  if ($('auto').checked) timer = setInterval(step, 1000 / +$('speed').value);
}
function step() { st = pulse(st); count++; hist.push(st); if (hist.length > 400) hist.shift(); render(); }
function value(ffs, e) { var v = 0; ffs.forEach(function (f) { v += f.w * e[f.q]; }); return v; }
function code(ffs, e) { return ffs.map(function (f) { return e[f.q]; }).join(''); }
function renderDec(ffs, cv, hg, tid, e) {
  ffs.forEach(function (f) {
    var el = $('ff-' + f.q), led = el.querySelector('.led');
    led.textContent = e[f.q]; led.classList.toggle('on', e[f.q] === 1);
    el.querySelector('[data-j]').textContent = ev(f.J, e); el.querySelector('[data-k]').textContent = ev(f.K, e);
  });
  var on = litSegs(cv, e);
  Array.prototype.forEach.call($(hg).querySelectorAll('rect'), function (r) { r.classList.toggle('on', on.indexOf(r.dataset.s) >= 0); });
  cv.forEach(function (c) {
    var tr = $(tid).querySelector('tr[data-s="' + c.s + '"]'), v = ev(c.t, e);
    tr.querySelector('[data-v]').textContent = v;
    tr.querySelector('[data-l]').innerHTML = v === 1 ? '<span class="hl-badge hl-badge-good">горит</span>' : '<span class="hl-muted">погашен</span>';
    if (c.mux) {
      var a = 0; c.t.sel.forEach(function (s, i) { a |= ev(s, e) << i; });
      tr.querySelector('[data-f]').innerHTML = 'адрес ' + qh(ffs[0].q) + qh(ffs[1].q) + qh(ffs[2].q) + ' = ' + (a + 8).toString(2).slice(1) + ' → D' + a + ' = ' + c.mux[a];
    }
  });
  return on;
}
function render() {
  var on1 = renderDec(N.dec1, N.conv1, 'hg1', 't1', st), on2 = renderDec(N.dec2, N.conv2, 'hg2', 't2', st);
  var d1 = DIG[on1], d2 = DIG[on2], ok = d1 !== undefined && d2 !== undefined && d1 === value(N.dec1, st) && d2 === value(N.dec2, st);
  $('num').textContent = ok ? '' + d2 + d1 : '—';
  $('cnt').textContent = count;
  $('code').textContent = code(N.dec2, st) + ' ' + code(N.dec1, st);
  $('warn').style.display = ok ? 'none' : '';
  $('pv').textContent = ev(N.P, st);
  timing();
}
function timing() {
  var rows = [['C', null]].concat(N.dec1.map(function (f) { return [f.q, f.q]; }), [['P', 'P']], N.dec2.map(function (f) { return [f.q, f.q]; }));
  var n = 24, h = hist.slice(-n), cw = 26, rh = 22, x0 = 34, wd = x0 + n * cw + 4, s = '<svg viewBox="0 0 ' + wd + ' ' + (rows.length * rh + 18) + '" class="tm">';
  rows.forEach(function (r, i) {
    var yb = i * rh + rh - 4, yt = yb - 13, pts = [];
    h.forEach(function (e, k) {
      var x = x0 + k * cw;
      if (r[1] === null) pts.push(x + ',' + yb, (x + cw / 2) + ',' + yb, (x + cw / 2) + ',' + yt, (x + cw) + ',' + yt, (x + cw) + ',' + yb);
      else { var v = r[1] === 'P' ? ev(N.P, e) : e[r[1]], y = v ? yt : yb; pts.push(x + ',' + y, (x + cw) + ',' + y); }
    });
    s += '<text x="2" y="' + (yb - 2) + '">' + (r[0].length > 1 ? r[0][0] + '<tspan dy="3" font-size="8">' + r[0].slice(1) + '</tspan>' : r[0]) + '</text>';
    s += '<polyline class="' + (r[0] === 'C' || r[0] === 'P' ? 'aux' : 'sig') + '" points="' + pts.join(' ') + '"/>';
  });
  h.forEach(function (e, k) {
    var v1 = value(N.dec1, e), v2 = value(N.dec2, e);
    s += '<text class="tn" x="' + (x0 + k * cw + cw / 2) + '" y="' + (rows.length * rh + 12) + '">' + (v1 < 10 && v2 < 10 ? '' + v2 + v1 : '?') + '</text>';
  });
  $('tm').innerHTML = s + '</svg>';
}
var m0 = /n=(\d+)/.exec(location.hash); build(); if (m0) for (var i0 = 0; i0 < +m0[1]; i0++) step(); render(); retime();
'''

CSS = r'''
.sim { display: flex; flex-direction: column; gap: calc(var(--spacing) * 4); }
.top { display: flex; flex-wrap: wrap; gap: calc(var(--spacing) * 6); align-items: center; }
#disp { display: flex; gap: calc(var(--spacing) * 3); padding: calc(var(--spacing) * 3); border: 1px solid var(--panel-hairline); border-radius: var(--radius-xl); }
.seg7 { width: 64px; height: 107px; }
.seg7 rect { fill: var(--panel-hairline); }
.seg7 rect.on { fill: var(--destructive); }
.ctl { display: flex; flex-wrap: wrap; gap: calc(var(--spacing) * 3); align-items: center; }
.ctl label { display: flex; gap: calc(var(--spacing) * 2); align-items: center; }
.ov { text-decoration: overline; }
.row { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: calc(var(--spacing) * 2); }
.ff { border: 1px solid var(--panel-hairline); border-radius: var(--radius-md); padding: calc(var(--spacing) * 2); display: flex; flex-direction: column; gap: calc(var(--spacing) * 1); }
.ffh { display: flex; justify-content: space-between; align-items: baseline; }
.led { font-family: var(--font-mono); font-size: var(--type-large); align-self: flex-start; min-width: 3em; }
.led.on { color: var(--destructive); font-weight: 700; }
.fn { font-family: var(--font-mono); font-size: var(--type-small); }
.tm { width: 100%; height: auto; }
.tm text { fill: var(--muted-foreground); font-size: 10px; font-family: var(--font-mono); }
.tm .tn { text-anchor: middle; font-size: 8px; }
.tm polyline { fill: none; stroke-width: 1.4; }
.tm .sig { stroke: var(--chart-1); }
.tm .aux { stroke: var(--chart-other); }
.scroll { overflow-x: auto; }
h4 { margin: 0; }
'''

BODY = r'''
<div class="sim">
  <div class="top">
    <div id="disp"></div>
    <div class="hl-grid" style="flex:1;min-width:260px">
      <div class="hl-stat"><div class="hl-stat-label">Показание</div><div class="hl-stat-value" id="num"></div></div>
      <div class="hl-stat"><div class="hl-stat-label">Импульсов подано</div><div class="hl-stat-value" id="cnt"></div></div>
      <div class="hl-stat"><div class="hl-stat-label">Код (десятки, единицы)</div><div class="hl-stat-value hl-mono" id="code"></div></div>
    </div>
  </div>
  <div class="ctl">
    <button id="step" class="hl-primary">Импульс на вход C</button>
    <label><input type="checkbox" role="switch" id="auto"> Генератор</label>
    <label><input type="range" id="speed" min="1" max="10" value="3"> <span id="hz" class="hl-muted"></span></label>
    <button id="reset">Сброс</button>
    <span id="warn" class="hl-badge hl-badge-warn">запрещённое состояние — подайте импульсы, счётчик вернётся в цикл</span>
  </div>
  <h4>Младший разряд (единицы), код 2-7-4-1</h4>
  <div class="row" id="d1"></div>
  <div class="fn"><span id="pf"></span><b id="pv"></b> <span class="hl-muted">— перенос: спад P при переходе 9 → 0 переключает старший разряд</span></div>
  <h4>Старший разряд (десятки)</h4>
  <div class="row" id="d2"></div>
  <h4>Временная диаграмма (последние 24 такта)</h4>
  <div class="scroll" id="tm"></div>
  <details open><summary>Преобразователь кода единиц (1 на выходе — сегмент горит)</summary><div class="scroll" id="c1"></div></details>
  <details><summary>Преобразователь кода десятков</summary><div class="scroll" id="c2"></div></details>
</div>
'''

FALLBACK = '''<style>
:root{--foreground:#1c1c1c;--muted-foreground:#666;--faint-foreground:#999;--card-panel:#f6f6f6;--panel-hairline:#ddd;--state-hover:#eee;
--destructive:#e02020;--status-ready:#1a9d4b;--status-waiting:#c98a00;--status-failed:#e02020;--chart-1:#2563eb;--chart-other:#9aa0a6;
--spacing:4px;--radius-md:6px;--radius-xl:12px;--type-mini:11px;--type-small:12px;--type-regular:14px;--type-large:18px;
--font-sans:system-ui,sans-serif;--font-mono:ui-monospace,Menlo,Consolas,monospace}
body{font-family:var(--font-sans);font-size:var(--type-regular);color:var(--foreground);max-width:760px;margin:16px auto;padding:0 12px}
table{border-collapse:collapse;width:100%}th,td{text-align:left;padding:4px 8px;border-bottom:1px solid var(--panel-hairline)}
.hl-num{text-align:right}.hl-muted{color:var(--muted-foreground)}.hl-mono{font-family:var(--font-mono)}
.hl-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px}
.hl-stat-label{color:var(--muted-foreground);font-size:var(--type-small)}.hl-stat-value{font-size:22px;font-weight:600}
.hl-badge{padding:2px 8px;border-radius:10px;font-size:var(--type-small);background:var(--card-panel)}
.hl-badge-good{color:var(--status-ready)}.hl-badge-warn{color:var(--status-waiting)}
button{padding:6px 12px;border:1px solid var(--panel-hairline);border-radius:6px;background:var(--card-panel);cursor:pointer}
button.hl-primary{background:var(--foreground);color:#fff}
</style>'''

def page(extra=''):
    return ('<!doctype html>\n<html lang="ru"><head><meta charset="utf-8"><title>Макет счётного устройства, вариант 9</title>\n' + extra +
            '<style>' + CSS + '</style></head><body>' + BODY + '<script>\nvar N = ' + json.dumps(NET, ensure_ascii=False) + ';\n' + CORE + UI + '</script></body></html>\n')

if __name__ == '__main__':
    art = '../.hoplite/artifacts/maket'; os.makedirs(art, exist_ok=True)
    open(art + '/maket.html', 'w').write(page())
    open('out/maket.html', 'w').write(page(FALLBACK))            # автономная копия: открывается в любом браузере
    open('/tmp/core_test.js', 'w').write('var N = ' + json.dumps(NET) + ';\n' + CORE + '''
var DIG = {abcdef: 0, bc: 1, abdeg: 2, abcdg: 3, bcfg: 4, acdfg: 5, acdefg: 6, abc: 7, abcdefg: 8, abcdfg: 9};
var e = zero();
for (var n = 0; n <= 250; n++) {
  if (DIG[litSegs(N.conv1, e)] !== n % 10 || DIG[litSegs(N.conv2, e)] !== Math.floor(n / 10) % 10) throw new Error('mismatch at ' + n);
  e = pulse(e);
}
console.log('JS OK: 00..99, 250 импульсов; порядок', N.dec1.map(function (f) { return f.q; }).join(' '), N.dec2.map(function (f) { return f.q; }).join(' '));
''')
    print('html written')
