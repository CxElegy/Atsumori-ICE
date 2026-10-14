# 第47回：あつ森で作れるものだけの鳥瞰図を組み立てる（acnh3d_tpl.html → london-birdseye.html）
# 物の絵（acnhcdn.com のゲームの絵）は scratchpad の icons/ に保存して、ページの中に埋めこむ（リポジトリには入れない）
import json, os, os, subprocess, sys, base64, io
from PIL import Image
R = os.environ.get('ICE_ROOT', '/home/user/Atsumori-ICE/')
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
sys.path.insert(0, R + 'tools')
PLAN = os.environ.get('ICE_PLAN', '2')
T = json.load(open(R + f'plan{PLAN}-terrain.json'))
B = json.load(open(R + f'designs/build_plan{PLAN}.json'))
CAT = json.load(open(R + 'designs/acnh_catalog.json'))
DES = {d['id']: d for d in json.load(open(R + 'designs/catalog.json'))['designs']}
KITS = json.load(open(R + 'designs/kits.json'))['kits']
if os.path.exists(R + f'designs/kits_plan{PLAN}.json'):
    KITS.update(json.load(open(R + f'designs/kits_plan{PLAN}.json'))['kits'])
Z = json.load(open(R + 'designs/zones_plan2.json'))
from zones import zone_cells
chk = json.loads(subprocess.run(['python3', R + 'tools/acnh_build.py', '--json'], capture_output=True, text=True).stdout)
if chk['errors']:
    print('\n'.join(chk['errors'][:20])); sys.exit('acnh_build.py が NG')
P = chk['placements']
os.makedirs('icons/ftr', exist_ok=True); os.makedirs('icons/houses', exist_ok=True)


def fetch(url, path):
    if not os.path.exists(path) or os.path.getsize(path) < 200:
        subprocess.run(['curl', '-sS', '-o', path, url])
    try:
        Image.open(path).verify(); return True
    except Exception:
        return False


def datauri(path, size):
    im = Image.open(path).convert('RGBA'); bb = im.getbbox()
    if bb: im = im.crop(bb)   # まわりの透明をけずって、絵の足もとを地面に合わせる
    im.thumbnail((size, size), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'WEBP', quality=86, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode(), im.size


icons, used = {}, {}
for p in P:
    it = CAT['items'][p['item']]
    fn = it['icon']
    if p.get('var'):
        for v in it['vars']:
            if v[0] == p['var'] and v[2]:
                fn = v[2]
    key = p['item'] + '|' + (p.get('var') or '')
    p['k'] = key
    if key in icons:
        continue
    url = 'https://acnhcdn.com/latest/FtrIcon/' + fn if '/' not in fn else 'https://acnhcdn.com/latest/' + fn
    path = 'icons/ftr/' + fn.replace('/', '_')
    if fetch(url, path):
        icons[key] = datauri(path, 160)
    else:
        print('絵なし', key, url)
    vja = next((v[1] for v in it['vars'] if v[0] == p.get('var')), '')
    used[key] = {'en': p['item'], 'ja': it['ja'], 'var': p.get('var') or '', 'varja': vja, 'size': it['size'], 'src': it['src'], 'diy': it['diy'], 'ver': it['ver'], 'sheet': it['sheet'], 'tag': it['tag']}
houses = {}
for b in B['buildings']:
    if b['kind'] == 'villager':
        v = CAT['villagers'][b['villager']]
        path = 'icons/houses/%s.png' % b['villager']
        if fetch('https://acnhcdn.com/' + v['house'], path):
            houses[b['villager']] = datauri(path, 300)
        b['ja'] = v['ja']
inc = {k: {'en': s, 'ja': CAT['construction']['Incline'][s]['ja']} for k, s in B['inclines'].items()}
bri = {k: {'en': s, 'ja': CAT['construction']['Bridge'][s]['ja']} for k, s in B['bridges'].items()}
des = {}
for p in P:
    if p.get('design') and p['design'] in DES:
        d = DES[p['design']]; des[p['design']] = {'name': d['name'], 'ma': d['ma'], 'creator': d.get('creator', '')}
for gd in B.get('ground', []):
    if gd['design'] in DES:
        d = DES[gd['design']]; des[gd['design']] = {'name': d['name'], 'ma': d['ma'], 'creator': d.get('creator', '')}
for z in B['paths'].values():
    if z.get('design') in DES:
        d = DES[z['design']]; des[z['design']] = {'name': d['name'], 'ma': d['ma'], 'creator': d.get('creator', '')}
from collections import Counter as _C
_occ = _C(); [_occ.update({(x // 8, y // 8): 1 for x in range(p['x'], p['x'] + p['w']) for y in range(p['y'], p['y'] + p['d'])}) for p in P]
_blk = _C()
for p in P:
    for x in range(p['x'], p['x'] + p['w']):
        for y in range(p['y'], p['y'] + p['d']):
            _blk[(x // 8, y // 8)] += 1
ntree = sum(r.count('t') for r in T['grid']) - sum(1 for x, y in chk['untree'] if T['grid'][y][x] == 't')
nbr = sum(1 for k in B['bridges'])
audit = [['木の数（190本くらいまで・220で5つ星にならない）', ntree, 190, ntree <= 190],
         ['8×8 マスのかたまりで家具がふさぐマスのいちばん多い所（45 未満）', max(_blk.values()), 44, max(_blk.values()) < 45],
         ['住民の家（10軒まで）', sum(1 for b in B['buildings'] if b['kind'] == 'villager'), 10, True],
         ['坂（8本・ライセンスで10本）', len(T['inclines']), 8, len(T['inclines']) <= 8], ['橋（8本・ライセンスで10本）', nbr, 8, nbr <= 8],
         ['崖・水・浜・建物・坂・橋のとなりの木', 0, 0, True], ['崖の幅（2マスから）・段の重ね方（1マス内側）', 'OK', '', True],
         ['建物の入口の前（3×2）・建物のあいだ1マス・木は建物から1マス', 'OK', '', True],
         ['外に置けない家具（壁かけ・かさ・絵）', 0, 0, True], ['花と作物は草地だけ（かたい道・地面のデザインの上は不可）', 'OK', '', True],
         ['同じ家具が 8×8 に7個以上（点が下がる）', len([w for w in chk['warnings'] if '6個をこえる' in w]), 0, True]]
_zc = {}
_Z = T['zones'] if PLAN != '2' else zone_cells(T['h'])
for _y in range(96):
    for _x in range(112):
        if T['grid'][_y][_x] not in 'Ssr':
            _zc.setdefault(_Z[_y][_x], []).append((_x, _y))
zlab = [[k, round(sum(p[0] for p in v) / len(v)), round(sum(p[1] for p in v) / len(v))] for k, v in _zc.items() if len(v) > 40]
data = {'g': T['grid'], 'audit': audit, 'zlab': zlab, 'warnings': chk['warnings'], 'h': T['h'], 'inc': T['inclines'], 'ground': {k: v for k, v in T.get('ground', {}).items() if v in 'um'},
        'zones': T['zones'] if PLAN != '2' else zone_cells(T['h']), 'buildings': B['buildings'], 'groups': [{'id': g['id'], 'zone': g['zone'], 'name': g.get('name') or KITS[g['kit']]['name'], 'kit': g.get('kit', ''), 'ref': g.get('ref') or (KITS[g['kit']]['ref'] if g.get('kit') else []), 'note': g.get('note') or (KITS[g['kit']].get('note', '') if g.get('kit') else '')} for g in B['groups']],
        'groundCells': chk['ground'], 'groundStyles': B.get('ground_styles', {}), 'groundDesigns': {gd['style'] + ':' + gd['design'] for gd in B.get('ground', [])} and sorted({(gd['style'], gd['design']) for gd in B.get('ground', [])}),
        'P': [dict({k: p[k] for k in ('k', 'x', 'y', 'w', 'd', 'rot', 'group', 'design')}, **({'piece': p['piece']} if p.get('piece') else {})) for p in P], 'untree': chk['untree'], 'plants': chk['plants'], 'plantTypes': B['rules']['plants'], 'orchards': B.get('orchards', []),
        'used': used, 'inclines': inc, 'bridges': bri, 'paths': B['paths'], 'designs': des, 'season': B['season'],
        'cannot': B['rules']['cannot'], 'sources': B['rules']['sources'], 'facilities': T['facilities']}
_sp = json.load(open(R + f'designs/plan{PLAN}_spec.json')) if os.path.exists(R + f'designs/plan{PLAN}_spec.json') else {}
data['cedar'] = _sp.get('cedar_belts', [])
data['townTones'] = _sp.get('street_tree_tones', [])   # 第60回の最終審査：町の木の色（1種類の木）
data['axisSum'] = (_sp['axis']['x0'] + _sp['axis']['x1']) if _sp.get('axis') else None   # 第60回：軸をはさむ町の木の対は同じ色に   # 第60回：杉（針葉樹）と濃い緑の低木の帯（主塔のうしろの静かな背景）
t = open('acnh3d_tpl.html').read()
js = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
t = t.replace('__DATA__', js(data)).replace('__ICONS__', js({k: v[0] for k, v in icons.items()})).replace('__ISZ__', js({k: v[1] for k, v in icons.items()})).replace('__HOUSES__', js({k: v[0] for k, v in houses.items()}))
SPECP = R + f'designs/plan{PLAN}_spec.json'
PG = json.load(open(SPECP)).get('page') if os.path.exists(SPECP) else None
if PG:   # 第59回：案ごとのページの見出しと説明（spec の page：ribbon・small・who・intro）
    import re as _re
    if PG.get('title'): t = _re.sub(r'<title>.*?</title>', '<title>%s</title>' % PG['title'], t, count=1)
    t = _re.sub(r'<div class="ribbon">.*?</div>', '<div class="ribbon">%s<small>%s</small></div>' % (PG['ribbon'], PG['small']), t, count=1, flags=_re.S)
    t = _re.sub(r"w\.textContent = '[^']*'; const p = document\.createElement\('p'\); p\.textContent = '[^']*';", lambda m: "w.textContent = %s; const p = document.createElement('p'); p.textContent = %s;" % (json.dumps(PG['who'], ensure_ascii=False), json.dumps(PG['intro'], ensure_ascii=False)), t, count=1)
OUT = os.environ.get('OUT', 'london-birdseye.html' if PLAN == '4' else f'birdseye-plan{PLAN}.html')   # 第59回：案5の候補は別のファイルに（案4のページを上書きしない）
open(OUT, 'w').write(t)
print('物', len(P), '絵', len(icons), '家', len(houses), 'サイズ', round(len(t) / 1e6, 2), 'MB')
