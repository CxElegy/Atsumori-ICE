#!/usr/bin/env python3
"""第59回：2つの案の土台がどれだけ似ているか（「从0开始完全重新做」の確かめ）。動かせない所（海・浜・岩・広場・飛行場）は数えない。

  python3 tools/plan_similarity.py 4 5a        # 案4 と 案5a をくらべる（町の範囲 x10〜100・y36〜90）

道・2段目以上・水のマスの重なり（Jaccard：重なり÷どちらか）と、建物の置き場所（同じ所から3マス以内）の割合。
"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding='utf-8'))


def load(pl):
    T = J(f'plan{pl}-terrain.json'); L = J(f'designs/plan{pl}_layout_out.json')
    return T['grid'], T['h'], L['buildings']


def sim(a, b, box=(10, 36, 100, 90)):
    (Ga, Ha, Ba), (Gb, Hb, Bb) = load(a), load(b)
    x0, y0, x1, y1 = box
    cells = [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1) if Ga[y][x] not in 'SsrKP' and Gb[y][x] not in 'SsrKP']
    def jac(fa, fb):
        A = {c for c in cells if fa(*c)}; B = {c for c in cells if fb(*c)}
        return round(len(A & B) / max(1, len(A | B)), 3), len(A), len(B)
    road = jac(lambda x, y: Ga[y][x] == 'p', lambda x, y: Gb[y][x] == 'p')
    high = jac(lambda x, y: int(Ha[y][x]) >= 2, lambda x, y: int(Hb[y][x]) >= 2)
    water = jac(lambda x, y: Ga[y][x] in 'wb', lambda x, y: Gb[y][x] in 'wb')
    same_b = sum(any(abs(p['at'][0] - q['at'][0]) + abs(p['at'][1] - q['at'][1]) <= 3 for q in Ba) for p in Bb)
    return {'road': road, 'tier2plus': high, 'water': water, 'buildings_same_spot': f'{same_b}/{len(Bb)}'}


if __name__ == '__main__':
    a, b = sys.argv[1], sys.argv[2]
    r = sim(a, b)
    print(json.dumps(r, ensure_ascii=False))
    print('（目安：道・2段目以上・水の重なりはそれぞれ 0.25 まで、建物の同じ所は 3 軒まで）')
