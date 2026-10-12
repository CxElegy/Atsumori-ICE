"""小红书のノート（xhs/notes.json、ブランチ claude/intelligent-bohr-avhvea）を、集めた作例に入れる形 designs/xhs_refs.json にする（第40回）。

  python3 tools/xhs_refs.py <notes.json>
  例：git show origin/claude/intelligent-bohr-avhvea:xhs/notes.json > /tmp/notes.json && python3 tools/xhs_refs.py /tmp/notes.json

1ノート＝1作例（番号 X-0001…）。ノートの画像は全部まとめて1つの作例のグループとして見せ、評価は1つ。
画像そのもの（xhs/img/）は作者の画像なので main には入れない。ビルドガイドは --xhs で画像の置き場を渡す（Pages はそのブランチの raw を直接読む）。
番号は一度つけたら変えない（ノートの id で前の番号を引きつぐ）。
"""
import json, os, re, sys
ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'designs', 'xhs_refs.json')
TH = {'ロンドン': 'lon', 'エジプト': 'egy', '日本': 'jpn', 'アメリカ': 'usa', 'ヨーロッパ': 'eur', '地中海': 'port'}   # その他は共通（all）
# 用途（collect_refs.py の CATS と同じキー）：タイトル・本文の言葉で、上から順に最初に当たったもの
CAT = [('station', r'车站|站台|机场|火车|地铁|巴士|公交'), ('facility', r'博物馆|服务处|商店入口|裁缝|狸端|自宅|房子门口|家门口'),
       ('shop', r'店|咖啡|餐|面包|市集|集市|摊|酒吧|居酒屋|甜品|花店|书店|拉面|快餐|汉堡|巴扎'),
       ('landmark', r'城堡|神社|鸟居|教堂|神庙|金字塔|塔|遗迹|寺|宫|大本钟|风车'),
       ('water', r'码头|海|河|桥|沙滩|港|湖|瀑布|泳池|渔'), ('park', r'公园|广场|花园|庭院|游乐园|农场|露营|果园|菜园'),
       ('road', r'路|地面|小径|石板|台阶|坡'), ('design', r'图案|设计码|马克|我的设计|服装|衣服'),
       ('small', r'角落|小场景|小物|装饰|摆件'), ('street', r'街|镇|村|岛|规划|全景|造景|岛建')]

def cat_of(n):
    t = n.get('title', '') + ' ' + n.get('desc', '')
    for k, rx in CAT:
        if re.search(rx, t): return k
    return 'street'

def main():
    notes = json.load(open(sys.argv[1], encoding='utf8'))['notes']
    old = {r['id']: r['no'] for r in json.load(open(OUT, encoding='utf8'))['refs']} if os.path.exists(OUT) else {}
    nxt = max([int(v[2:]) for v in old.values()] + [0]) + 1
    refs = []
    for n in sorted(notes, key=lambda n: (list(TH).index(n['theme']) if n['theme'] in TH else 9, -n.get('likes', 0))):
        if not n.get('images'): continue
        no = old.get(n['id'])
        if not no: no = 'X-%04d' % nxt; nxt += 1
        refs.append({'no': no, 'src': 'xhs', 'id': n['id'], 'url': n['images'][0], 'imgs': n['images'], 'link': n['url'].split('?')[0],
                     'th': TH.get(n['theme'], 'all'), 'cat': cat_of(n), 'kind': 'scene', 'q': '小红书：' + n.get('keyword', ''),
                     'title': n.get('title', ''), 'author': n.get('author', ''), 'likes': n.get('likes', 0)})
    refs.sort(key=lambda r: r['no'])
    json.dump({'note': '小红书のノート（tools/xhs_refs.py が xhs/notes.json から作る）。画像は claude/intelligent-bohr-avhvea ブランチの xhs/img/', 'branch': 'claude/intelligent-bohr-avhvea', 'refs': refs},
              open(OUT, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    from collections import Counter
    print(len(refs), '件', Counter(r['th'] for r in refs), Counter(r['cat'] for r in refs), sum(len(r['imgs']) for r in refs), '枚')

if __name__ == '__main__':
    main()
