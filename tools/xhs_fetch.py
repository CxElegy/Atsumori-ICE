#!/usr/bin/env python3
"""小红书のノートを集めて xhs/notes.json と xhs/img/ に保存する。

xiaohongshu-mcp（https://github.com/xpzouying/xiaohongshu-mcp）をローカルで
起動・ログイン済みであることが前提（ログインは tools/xhs_login.py）。

  python3 tools/xhs_fetch.py themes                     # 6地区のキーワードで人気順に集める
  python3 tools/xhs_fetch.py themes --only ロンドン --per-theme 12
  python3 tools/xhs_fetch.py search 动森 伦敦 --theme ロンドン
  python3 tools/xhs_fetch.py url "https://www.xiaohongshu.com/explore/...?..." --theme 日本
"""
import argparse, io, json, os, random, re, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'xhs')
NOTES = os.path.join(OUT, 'notes.json')
API = os.environ.get('XHS_MCP', 'http://127.0.0.1:18060') + '/api/v1'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36'

# 地区 → 検索キーワード（Module Builder の地区と同じ名前）
THEMES = {
    'ロンドン': ['动森岛建 伦敦', '动森岛建 英伦风', '动森岛建 哈利波特', '动森岛建 英式街道'],
    'エジプト': ['动森岛建 埃及', '动森岛建 沙漠', '动森岛建 金字塔', '动森岛建 中东集市'],
    '日本': ['动森岛建 日式', '动森岛建 神社', '动森岛建 日式商店街', '动森岛建 和风'],
    'アメリカ': ['动森岛建 美式', '动森岛建 美式小镇', '动森岛建 美式乡村', '动森岛建 西部'],
    'ヨーロッパ': ['动森岛建 欧式', '动森岛建 欧洲小镇', '动森岛建 城堡', '动森岛建 法式'],
    '地中海': ['动森岛建 地中海', '动森岛建 圣托里尼', '动森岛建 海边', '动森岛建 希腊'],
}
# ゲーム内の島づくりらしいタイトルだけ残す（現地のコラボ・グッズ投稿を除く）
BUILD = re.compile(r'岛|建|设计|规划|布置|教程|作业|街|区|广场|角落|花园|庭院|入口|码头|机场|博物馆|商店|咖啡|站台|城|镇|村|风|式|分享')
# 地区ごとに、タイトルに入っていてほしい言葉（いいね順だと無関係な人気投稿が混ざるため）
WORDS = {
    'ロンドン': r'伦敦|英伦|英式|英国|哈利|霍格|魔法|站台|酒吧|电话亭|大本钟|维多利亚|红砖',
    'エジプト': r'埃及|沙漠|金字塔|中东|集市|阿拉伯|绿洲|沙丘|狮身|撒哈拉|摩洛哥|异域|神庙|遗迹|巴扎',
    '日本': r'日式|日本|和风|神社|鸟居|温泉|京都|商店街|樱|祭|茶屋|寺|町|居酒屋|拉面',
    'アメリカ': r'美式|美国|西部|牛仔|公路|汽车|露营|农场|纽约|餐车|加油站|汽车旅馆|diner|乡村',
    'ヨーロッパ': r'欧式|欧洲|法式|城堡|德式|意式|意大利|中世纪|教堂|荷兰|风车|巴黎|童话|小镇',
    '地中海': r'地中海|圣托里尼|希腊|海边|海滩|沙滩|码头|海岛|度假|港|蓝白|海景|渔',
}
NOISE = re.compile(r'联动|水族馆|sea ?life|周边|抱枕|门店|快闪|打卡|留子|购物|手办|盲盒|实体|线下', re.I)


def call(method, path, body=None, timeout=240):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.load(r)
    if not d.get('success', True):
        raise RuntimeError(d.get('message'))
    return d.get('data') or {}


def num(s):
    """'1.2万' → 12000"""
    s = str(s or '0').strip()
    m = re.match(r'([\d.]+)\s*([万wW千kK]?)', s)
    if not m:
        return 0
    return int(float(m.group(1)) * {'万': 10000, 'w': 10000, 'W': 10000, '千': 1000, 'k': 1000, 'K': 1000}.get(m.group(2), 1))


def search(keyword, sort='最多点赞', theme=None):
    body = {'keyword': keyword, 'filters': {'sort_by': sort, 'note_type': '图文'}}
    try:
        d = call('POST', '/feeds/search', body)
    except Exception:
        pause()
        d = call('POST', '/feeds/search', body)
    out = []
    for f in d.get('feeds') or []:
        nc = f.get('noteCard') or {}
        title = nc.get('displayTitle') or ''
        if f.get('modelType', 'note') != 'note' or not f.get('xsecToken'):
            continue
        if not BUILD.search(title) or NOISE.search(title):
            continue
        if theme in WORDS and not re.search(WORDS[theme], title, re.I):
            continue
        out.append({'id': f['id'], 'token': f['xsecToken'], 'title': nc.get('displayTitle') or '',
                    'likes': num((nc.get('interactInfo') or {}).get('likedCount')), 'keyword': keyword})
    return out


def parse_url(url):
    if 'xhslink.com' in url:  # 短縮リンクは展開
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            url = r.geturl()
    m = re.search(r'/(?:explore|discovery/item|search_result)/([0-9a-f]{24})', url)
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    if not m or not q.get('xsec_token'):
        raise SystemExit('ノートID と xsec_token を含むリンクが必要です（アプリの「共有→リンクをコピー」）: ' + url)
    return m.group(1), q['xsec_token'][0]


def save_image(url, path, max_w=1000):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Referer': 'https://www.xiaohongshu.com/'})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(raw)).convert('RGB')
        if im.width > max_w:
            im = im.resize((max_w, round(im.height * max_w / im.width)))
        im.save(path, 'JPEG', quality=72, optimize=True, progressive=True)
    except ImportError:  # Pillow がなければそのまま保存
        with open(path, 'wb') as f:
            f.write(raw)


def fetch_note(nid, token, theme, keyword='', max_images=18):
    d = call('POST', '/feeds/detail', {'feed_id': nid, 'xsec_token': token})
    n = (d.get('data') or {}).get('note') or {}
    if not n:
        raise RuntimeError('ノート本文が取れませんでした')
    it = n.get('interactInfo') or {}
    imgdir = os.path.join(OUT, 'img', nid)
    os.makedirs(imgdir, exist_ok=True)
    images = []
    for i, im in enumerate((n.get('imageList') or [])[:max_images]):
        u = im.get('urlDefault') or im.get('url')
        if not u:
            continue
        rel = f'xhs/img/{nid}/{i + 1}.jpg'
        if not os.path.exists(os.path.join(ROOT, rel)):
            save_image(u, os.path.join(ROOT, rel))
        images.append(rel)
    desc = n.get('desc') or ''
    tags = re.findall(r'#([^#\[\n]+)\[话题\]#', desc)
    desc = re.sub(r'#([^#\[\n]+)\[话题\]#', r'#\1', desc)
    return {
        'id': nid, 'theme': theme, 'title': n.get('title') or '', 'desc': desc,
        'author': (n.get('user') or {}).get('nickname') or '',
        'likes': num(it.get('likedCount')), 'collects': num(it.get('collectedCount')), 'comments': num(it.get('commentCount')),
        'tags': tags or [t.get('name') for t in n.get('tagList') or [] if t.get('name')],
        'ip': n.get('ipLocation') or '', 'time': n.get('time') or 0,
        'url': f'https://www.xiaohongshu.com/explore/{nid}?xsec_token={urllib.parse.quote(token)}&xsec_source=pc_search',
        'images': images, 'keyword': keyword, 'fetched': time.strftime('%Y-%m-%d'),
    }


def load():
    if os.path.exists(NOTES):
        with open(NOTES, encoding='utf-8') as f:
            return json.load(f)
    return {'notes': []}


def store(db, note):
    db['notes'] = [x for x in db['notes'] if x['id'] != note['id']] + [note]
    db['notes'].sort(key=lambda x: (list(THEMES).index(x['theme']) if x['theme'] in THEMES else 99, -x['likes']))
    db['updated'] = time.strftime('%Y-%m-%d')
    os.makedirs(OUT, exist_ok=True)
    tmp = NOTES + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=1)
    os.replace(tmp, NOTES)


def pause():
    time.sleep(random.uniform(3, 7))  # 連続アクセスで弾かれないように


def grab(db, cands, theme, n, max_images):
    have = {x['id'] for x in db['notes']}
    seen, got = set(), 0
    for c in sorted(cands, key=lambda c: -c['likes']):
        if got >= n:
            break
        if c['id'] in seen:
            continue
        seen.add(c['id'])
        if c['id'] in have:
            got += 1
            continue
        try:
            note = fetch_note(c['id'], c['token'], theme, c['keyword'], max_images)
        except Exception as e:
            print(f'  ! {c["title"]}: {e}', file=sys.stderr)
            pause()
            continue
        store(db, note)
        got += 1
        print(f'  ♥{note["likes"]:>6}  {note["title"]}  （画像{len(note["images"])}枚）')
        pause()


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    t = sub.add_parser('themes'); t.add_argument('--only', nargs='*'); t.add_argument('--per-theme', type=int, default=8)
    s = sub.add_parser('search'); s.add_argument('keyword', nargs='+'); s.add_argument('--theme', required=True); s.add_argument('-n', type=int, default=5)
    u = sub.add_parser('url'); u.add_argument('url'); u.add_argument('--theme', required=True)
    for p in (t, s, u):
        p.add_argument('--max-images', type=int, default=18)
    a = ap.parse_args()

    st = call('GET', '/login/status', timeout=120)
    if not st.get('is_logged_in'):
        raise SystemExit('xiaohongshu-mcp が未ログインです。tools/xhs_login.py でログインしてください')
    db = load()
    if a.cmd == 'url':
        nid, tok = parse_url(a.url)
        note = fetch_note(nid, tok, a.theme, '', a.max_images)
        store(db, note)
        print(f'♥{note["likes"]}  {note["title"]}  （画像{len(note["images"])}枚）')
    elif a.cmd == 'search':
        kw = ' '.join(a.keyword)
        grab(db, search(kw), a.theme, a.n, a.max_images)
    else:
        for theme, kws in THEMES.items():
            if a.only and theme not in a.only:
                continue
            print(f'== {theme}')
            cands = []
            for kw in kws:
                try:
                    cands += search(kw, theme=theme)
                except Exception as e:
                    print(f'  ! 検索失敗 {kw}: {e}', file=sys.stderr)
                pause()
            if len({c['id'] for c in cands}) < a.per_theme * 1.5:  # 足りなければ「综合」順でも探す
                for kw in kws:
                    try:
                        cands += search(kw, sort='综合', theme=theme)
                    except Exception as e:
                        print(f'  ! 検索失敗 {kw}: {e}', file=sys.stderr)
                    pause()
            grab(db, cands, theme, a.per_theme, a.max_images)
    print(f'保存: {NOTES}（全{len(db["notes"])}件）')


if __name__ == '__main__':
    main()
