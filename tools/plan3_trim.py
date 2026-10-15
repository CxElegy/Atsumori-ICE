"""案3：8×8 のかたまりが 45 マス以上ふさがったら、柵 → パネルの順に、そのかたまりの物を減らす（島の評価のごちゃごちゃの決まり）
   python3 tools/plan3_trim.py （plan3_fill.py のあと。ICE_PLAN=3 の acnh_build で数える）"""
import json, os, sys
from collections import Counter
os.environ.setdefault('ICE_PLAN', '3')
sys.path.insert(0, os.path.dirname(__file__))
ROOT = os.path.join(os.path.dirname(__file__), '..')
PATH = os.path.join(ROOT, f"designs/build_plan{os.environ['ICE_PLAN']}.json")
TRIM = ['C-roofs', 'C-edges', 'S-fences', 'C-walls']   # へらしてよい組（先にあるほど先にへらす）
for _ in range(6):
    import importlib, acnh_build
    importlib.reload(acnh_build)
    errs = acnh_build.check()[0]
    over = [e for e in errs if e.startswith('8×8')]
    if not over:
        break
    B = json.load(open(PATH))
    blocks = {}
    for e in over:   # 「8×8 のかたまり x40〜・y48〜：家具が 47 マスをふさぐ」
        xs = int(e.split('x')[1].split('〜')[0]); ys = int(e.split('y')[1].split('〜')[0]); n = int(e.split('が ')[1].split(' マス')[0])
        blocks[(xs // 8, ys // 8)] = n - 44
    G = {g['id']: g for g in B['groups']}
    for (bx, by), need in blocks.items():
        for gid in TRIM:
            if gid not in G or need <= 0:
                continue
            its = G[gid]['items']
            inblk = [i for i, it in enumerate(its) if it[1] // 8 == bx and it[2] // 8 == by]
            drop = set(inblk[::2][:need]) if len(inblk) > need * 2 else set(inblk[:need])
            need -= len(drop)
            G[gid]['items'] = [it for i, it in enumerate(its) if i not in drop]
    json.dump(B, open(PATH, 'w'), ensure_ascii=False, indent=1)
    print('へらした 8×8：', len(blocks))
