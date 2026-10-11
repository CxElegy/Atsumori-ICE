#!/usr/bin/env python3
"""モジュールDB（db/modules.sqlite）の取り込み・判定・書き出し。標準ライブラリだけ。

  import                 modules-popular.json と追加セット（DECO・TINY・VIGNETTE・SITE・STEP）を取り込む。判定は消さない
  judge                  美的センスのSKILLの基準で点をつけ、理由つきの判定ファイル db/curation-*.json を作る（記録として残す）
  apply 判定.json ...    判定をまとめて書き込む。形: [{"id","status","role","score","reason"}]。あとの判定が前を上書き
  bases テーマ           型ごとの一覧・色違いを形つきで表示（参考点つき）
  show テーマ [型]       モジュールを形つきで表示
  stats / steps          件数（段差の数も）／段差のモジュールを形と段で表示
  check                  段差のモジュールの点検（check_step）と、わざとまちがえた形の確認
  export                 採用分を modules-curated.json と .md に書き出す
"""
import glob, json, os, sqlite3, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
DB = os.path.join(ROOT, 'db', 'modules.sqlite')

import gen_popular_modules as GP
import module_sets as MS

TH = GP.TH
TH_KEY = {v: k for k, v in TH.items()}
THEME_ORDER = ['ロンドン', 'エジプト', '日本', 'アメリカ', 'ハロウィン', 'ヨーロッパ', '地中海']
ROLES = ['landmark', 'support', 'filler', 'edge', 'step', 'facility']

# 採用の枠（1地区の目安：主役2〜4・脇役8〜12・すき間うめ6〜10・道ばた2〜4・段差2〜4 を、全体293個に合わせて配る）
QUOTA = {
    'landmark': {'lon': 2, 'egy': 3, 'jpn': 3, 'usa': 3, 'hal': 2, 'eur': 2, 'port': 2},
    'support': {k: 8 for k in TH},
    'edge': {'lon': 5, 'egy': 5, 'jpn': 5, 'usa': 5, 'hal': 4, 'eur': 5, 'port': 5},
    'step': {k: 4 for k in TH},
    'filler': {'lon': 29, 'egy': 25, 'jpn': 26, 'usa': 23, 'hal': 15, 'eur': 26, 'port': 14},
    'facility': {k: 9 for k in TH},     # 島の暮らしの施設は点検に通ればすべて採用（枠の外）
}
TARGET = 293
NO_WATER = {'jpn'}     # 第14回：日本は水を使わない（枯山水）


def conn():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    c = sqlite3.connect(DB)
    c.executescript('''
    CREATE TABLE IF NOT EXISTS sources (key TEXT PRIMARY KEY, label TEXT, url TEXT);
    CREATE TABLE IF NOT EXISTS modules (id TEXT PRIMARY KEY, theme TEXT, district TEXT, name TEXT, base TEXT, mat TEXT, rows TEXT, w INT, h INT,
      note TEXT, src TEXT, cells INT, props INT, density REAL, palette REAL, road_ok INT, lv TEXT, slopes INT, role TEXT);
    CREATE TABLE IF NOT EXISTS curation (id TEXT PRIMARY KEY, status TEXT, role TEXT, score INT, reason TEXT, decided_at TEXT);
    ''')
    return c


def features(m):
    r = m['r']
    th = TH_KEY[m['th']]
    chars = [c for row in r for c in row if c != '.']
    cells = len(chars)
    props = [c for c in chars if c not in MS.GROUND_CH and c not in 'HD']
    density = len(props) / cells if cells else 0
    items = [c for c in chars if c not in 'w=Z']
    palette = sum(1 for c in items if c in MS.THEME_ITEMS[th]) / len(items) if items else 1
    road_ok = int(all(c in MS.SMALL_CH for c in props))
    slopes = sum(row.count('Z') for row in r) // 8
    return {'cells': cells, 'props': len(props), 'density': round(density, 3), 'palette': round(palette, 3), 'road_ok': road_ok, 'slopes': slopes}


def all_modules():
    """取り込む全モジュール（popular + 追加セット）。役のヒント role を持つ。"""
    P = GP.build()
    out = []
    for m in P:
        out.append(dict(m, role=GP.ROLES[m['base']]))
    for m in MS.deco() + MS.tiny() + MS.vignette() + MS.site() + MS.step() + MS.karesansui() + MS.facility():
        m = dict(m)
        m.setdefault('src', ''); m.setdefault('base', m['id'].rsplit('_', 1)[0] if m['id'].startswith(('deco', 'tiny', 'vig', 'stp')) else m['id'])
        out.append(m)
    return out


def cmd_import():
    c = conn()
    for k, (l, u) in GP.SOURCES.items():
        c.execute('INSERT OR REPLACE INTO sources VALUES (?,?,?)', (k, l, u))
    n = 0
    for m in all_modules():
        f = features(m)
        r = m['r']
        c.execute('INSERT OR REPLACE INTO modules VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                  (m['id'], m['th'], TH_KEY[m['th']], m['name'], m.get('base', ''), m.get('mat', ''), json.dumps(r, ensure_ascii=False), len(r[0]), len(r),
                   m.get('note', ''), m.get('src', ''), f['cells'], f['props'], f['density'], f['palette'], f['road_ok'],
                   json.dumps(m['lv']) if m.get('lv') else '', f['slopes'], m['role']))
        n += 1
    c.commit()
    print('取り込み:', n, '個（判定は消していません）')


def load(c):
    c.row_factory = sqlite3.Row
    rows = [dict(x) for x in c.execute('SELECT * FROM modules ORDER BY id')]
    for x in rows:
        x['r'] = json.loads(x['rows'])
        x['lv'] = json.loads(x['lv']) if x['lv'] else None
    return rows


# ---- 判定（美的センスのSKILL）------------------------------------------------
def score(m, rank):
    """m: DBの行。rank: 同じ型の中で何番目の色違いか（0始まり）。点の内訳を返す。"""
    th = TH_KEY[m['theme']]
    role = m['role']
    area = m['w'] * m['h']
    parts = {}
    t = round(25 * m['palette'])
    if m['mat'] and m['mat'] not in GP.GROUNDS[th] + MS.TINY_GROUND[th]:
        t -= 5
    parts['テーマ'] = (max(t, 0), 25)
    if role == 'landmark':
        rc = 15 if area >= 20 else 9
    elif role == 'support':
        rc = 15 if 6 <= area <= 30 else 10
    elif role == 'filler':
        rc = 15 if area <= 12 else 8
    elif role == 'edge':
        rc = 15 if area <= 2 else 8
    else:
        rc = 15
    parts['役'] = (rc, 15)
    d = m['density']
    lo, hi = (0.25, 0.7) if role == 'landmark' else (0.3, 0.7)
    if m['mat'] == 'm' or role == 'facility':   # 枯山水は余白（白砂）が主役。施設は使い方で決まる
        lo, hi = 0.05, 0.7
    dist = 0 if lo <= d <= hi else min(abs(d - lo), abs(d - hi))
    parts['密度'] = (max(20 - round(40 * dist), 4), 20)
    if role in ('filler', 'edge'):
        ov = [15, 12, 9][rank] if rank < 3 else 0
    else:
        ov = [15, 9][rank] if rank < 2 else 0
    parts['重ね'] = (ov, 15)
    tf = 15 if area <= 49 or role in ('landmark', 'facility') else 5
    if th in NO_WATER and 'w' in ''.join(m['r']):   # 日本は枯山水（水を使わない）。水の要るものは置けない
        tf = 0
    parts['地形'] = (tf, 15)
    parts['作れる'] = (10 if m['props'] <= 24 else (7 if m['props'] <= 40 else 4), 10)
    bonus = 10 if role == 'step' and m['slopes'] <= 1 else (5 if role == 'step' else 0)
    parts['段差'] = (bonus, 10)
    total = sum(v[0] for v in parts.values())
    return total, parts


def reason(m, total, parts, rank, extra=''):
    s = '・'.join('%s%d/%d' % (k, a, b) for k, (a, b) in parts.items() if k != '段差' or a)
    if rank and m['base']:
        s += '。同じ型の%d個目（色違いは重ねない）' % (rank + 1)
    return s + extra


def cmd_judge():
    c = conn()
    rows = load(c)
    today = '2026-10-11'
    # 1) 型ごとに色違いの順位をつける（先に仮の点で並べる）
    pre = {}
    for m in rows:
        t0, _ = score(m, 0)
        pre[m['id']] = t0
    by_base = {}
    for m in rows:
        by_base.setdefault((m['theme'], m['base']), []).append(m)
    rank = {}
    for k, lst in by_base.items():
        lst.sort(key=lambda m: (-pre[m['id']], m['id']))
        for i, m in enumerate(lst):
            rank[m['id']] = i
    res = {}
    for m in rows:
        t, parts = score(m, rank[m['id']])
        res[m['id']] = (t, parts)
    # 保留に決めている段差（坂を2本使う大きな階段）・旧案。枠には数えない
    forced = {'stp_jpn_5': '段々の茶畑は坂を2本使うので、坂に余りがあるときだけ（保留）', 'stp_eur_5': '城下町の大階段は坂を2本使うので保留',
              'stp_port_5': '段々のぶどう畑は坂を2本使うので保留', 'lon_court': '博物館をエジプトへ移したので、ロンドンの前庭は保留'}
    CAP = {'landmark': 2, 'support': 2, 'filler': 3, 'edge': 3, 'step': 3, 'facility': 1}
    # 2) 枠（QUOTA）に合わせて採用を決める。点が高い順
    status = {}
    for role in ROLES:
        for th in TH:
            cand = [m for m in rows if m['role'] == role and TH_KEY[m['theme']] == th and m['id'] not in forced]
            cand.sort(key=lambda m: (-res[m['id']][0], m['id']))
            n = 0
            for m in cand:
                t = res[m['id']][0]
                if t >= 70 and rank[m['id']] >= CAP[role] and m['base'] and m['id'].startswith('pop'):
                    status[m['id']] = ('reserve', '。同じ型の色違いが多すぎる（%sは%dつまで）' % ('主役・脇役' if role in ('landmark', 'support') else 'すき間うめ・道ばた', CAP[role]))
                elif t >= 70 and n < QUOTA[role][th]:
                    status[m['id']] = ('adopt', ''); n += 1
                elif t >= 70:
                    status[m['id']] = ('reserve', '。70点以上だがこの地区の%sの枠（%d個）が埋まっている' % ({'landmark': '主役', 'support': '脇役', 'filler': 'すき間うめ', 'edge': '道ばた', 'step': '段差', 'facility': '施設'}[role], QUOTA[role][th]))
                elif t >= 50:
                    status[m['id']] = ('reserve', '。50〜69点（控え）')
                else:
                    status[m['id']] = ('reject', '。50点未満')
            if n < QUOTA[role][th] and role != 'facility':
                print('警告: %s %s は採用が %d/%d' % (TH[th], role, n, QUOTA[role][th]), file=sys.stderr)
    # 3) 保留に決めている段差（坂を2本使う大きな階段）・旧案
    for k, v in forced.items():
        if k in res:
            status[k] = ('reserve', '。' + v)
    files = {'popular': [], 'sets': [], 'steps': []}
    for m in rows:
        t, parts = res[m['id']]
        st, ex = status[m['id']]
        e = {'id': m['id'], 'status': st, 'role': m['role'], 'score': t, 'reason': reason(m, t, parts, rank[m['id']], ex)}
        key = 'popular' if m['id'].startswith('pop') else ('steps' if m['role'] == 'step' else 'sets')
        files[key].append(e)
    os.makedirs(os.path.join(ROOT, 'db'), exist_ok=True)
    for k, lst in files.items():
        p = os.path.join(ROOT, 'db', 'curation-%s-%s.json' % (today, k))
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(lst, f, ensure_ascii=False, indent=0)
        print(os.path.relpath(p, ROOT), len(lst), '件')


def cmd_apply(paths):
    c = conn()
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    ids = {x[0] for x in c.execute('SELECT id FROM modules')}
    n = 0
    for p in paths:
        for e in json.load(open(p, encoding='utf-8')):
            if e['id'] not in ids:
                print('警告: 見つからない id', e['id'], file=sys.stderr); continue
            if e['status'] not in ('adopt', 'reserve', 'reject') or not e.get('reason'):
                raise SystemExit('判定には status（adopt/reserve/reject）と reason が必要: %s' % e)
            c.execute('INSERT OR REPLACE INTO curation VALUES (?,?,?,?,?,?)', (e['id'], e['status'], e.get('role', ''), int(e.get('score', 0)), e['reason'], now))
            n += 1
    c.commit()
    print('判定を書き込み:', n, '件')


def cmd_stats():
    c = conn()
    print('モジュール', c.execute('SELECT COUNT(*) FROM modules').fetchone()[0], '個')
    for st, n in c.execute('SELECT status, COUNT(*) FROM curation GROUP BY status'):
        print(' ', st, n)
    print('採用（役別）')
    tot = 0
    for r in ROLES:
        n = c.execute("SELECT COUNT(*) FROM curation WHERE status='adopt' AND role=?", (r,)).fetchone()[0]
        tot += n; print(' ', r, n)
    print('  合計', tot)
    print('採用（テーマ別）', ' '.join('%s %d' % (t, c.execute("SELECT COUNT(*) FROM modules m JOIN curation k ON m.id=k.id WHERE k.status='adopt' AND m.theme=?", (t,)).fetchone()[0]) for t in THEME_ORDER))
    print('段差のモジュール', c.execute("SELECT COUNT(*) FROM modules WHERE role='step'").fetchone()[0], '個（坂を使う', c.execute('SELECT SUM(slopes) FROM modules WHERE role="step"').fetchone()[0], '本）')


def draw(m):
    return '\n'.join('   ' + row for row in m['r'])


def cmd_bases(theme):
    c = conn(); rows = load(c)
    seen = {}
    for m in rows:
        if m['theme'] == theme:
            seen.setdefault(m['base'], []).append(m)
    for b, lst in seen.items():
        print('%s  %d個  役=%s  参考点(色合い)=%.2f' % (b, len(lst), lst[0]['role'], sum(x['palette'] for x in lst) / len(lst)))
        print(draw(lst[0]))


def cmd_show(theme, base=None):
    c = conn(); rows = load(c)
    for m in rows:
        if m['theme'] == theme and (not base or m['base'] == base):
            print(m['id'], m['name'], '%d×%d' % (m['w'], m['h'])); print(draw(m))


def cmd_steps():
    c = conn(); rows = load(c)
    for m in rows:
        if m['role'] == 'step':
            print(m['id'], m['name'])
            for r, l in zip(m['r'], m['lv']):
                print('   ', r, ' ', l)
            e = MS.check_step(m)
            print('   点検:', 'OK' if not e else e)


def cmd_check():
    bad = 0
    for m in MS.step():
        e = MS.check_step(m)
        if e:
            bad += 1; print('NG', m['id'], e)
    print('段差のモジュール %d個 点検 NG=%d' % (len(MS.step()), bad))
    stop = [bool(MS.check_step(b)) for b in MS.BAD_STEPS]
    print('わざとまちがえた形 %d種類 → 止まった %d' % (len(stop), sum(stop)))
    if bad or not all(stop):
        sys.exit(1)


def cmd_export():
    c = conn(); rows = load(c)
    cur = {r[0]: r for r in c.execute('SELECT id,status,role,score,reason FROM curation')}
    mods, used = [], set()
    for m in rows:
        k = cur.get(m['id'])
        if not k or k[1] != 'adopt':
            continue
        e = {'id': m['id'], 'th': m['theme'], 'name': m['name'], 'r': m['r'], 'note': m['note'], 'mat': m['mat'], 'src': m['src'], 'base': m['base'],
             'role': k[2], 'score': k[3], 'why': k[4]}
        if m['lv']:
            e['lv'] = m['lv']
        if m['slopes']:
            e['slopes'] = m['slopes']
        if m['src']:
            used.add(m['src'])
        mods.append(e)
    order = {t: i for i, t in enumerate(THEME_ORDER)}
    mods.sort(key=lambda e: (order.get(e['th'], 9), ROLES.index(e['role']), e['id']))
    sources = [{'key': r[0], 'label': r[1], 'url': r[2]} for r in c.execute('SELECT key,label,url FROM sources') if r[2] in used]
    with open(os.path.join(ROOT, 'modules-curated.json'), 'w', encoding='utf-8') as f:
        json.dump({'count': len(mods), 'sources': sources, 'modules': mods}, f, ensure_ascii=False, separators=(',', ':'))
    lines = ['# 採用したモジュール（%d個）' % len(mods), '', 'tools/module_db.py export が作った一覧です（生成物）。美的センスのSKILLで採用と判定したものだけです。', '',
             '| id | テーマ | 役 | 名前 | 大きさ | 点 | 理由 |', '|---|---|---|---|---|---|---|']
    for e in mods:
        lines.append('| %s | %s | %s | %s | %d×%d | %d | %s |' % (e['id'], e['th'], e['role'], e['name'], len(e['r'][0]), len(e['r']), e['score'], e['why']))
    open(os.path.join(ROOT, 'modules-curated.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('modules-curated.json:', len(mods), '個')


def main(a):
    if not a:
        print(__doc__); return
    c = a[0]
    if c == 'import': cmd_import()
    elif c == 'judge': cmd_judge()
    elif c == 'apply': cmd_apply(sorted(sum((glob.glob(p) for p in a[1:]), [])))
    elif c == 'stats': cmd_stats()
    elif c == 'bases': cmd_bases(a[1])
    elif c == 'show': cmd_show(a[1], a[2] if len(a) > 2 else None)
    elif c == 'steps': cmd_steps()
    elif c == 'check': cmd_check()
    elif c == 'export': cmd_export()
    else: print(__doc__)


if __name__ == '__main__':
    main(sys.argv[1:])
