"""集めた作例の画像の種類を自動で分ける（第38回）。refs.json の kind に書く。

  scene  景色：島の実景（下にマイデザインの図がついたもの、まとめ記事の表紙も）
  design マイデザインだけ：マイデザインの図・作者ID・保存画面だけで、実景がない

  python tools/ref_kinds.py <画像の置き場> <OCR の置き場.json>
    実景のある画像（どこかの帯に単色の地がない）は文字を読まずに景色。単色の地がある画像だけ tesseract で作者IDを探す（読んだ文字は OCR の置き場に残し、次は読み直さない）。
    見て直した分は designs/ref_kinds.json の fix（番号→種類）で上書きする
"""
import json, os, re, sys
import numpy as np
from PIL import Image
ROOT = os.path.join(os.path.dirname(__file__), '..')
REFS = os.path.join(ROOT, 'designs', 'refs.json')
CODE = re.compile(r'\b(M[AO]|DA)\s*[-:–]?\s*\d{4}', re.I)

def flat_bands(path):
    """横に4つに切り、どの帯にも単色の地（いちばん多い色が25%以上）があるか。実景の帯は色がばらける"""
    im = np.asarray(Image.open(path).convert('RGB').resize((96, 128))) // 24
    out = []
    for b in np.array_split(im, 4, axis=0):
        cols, cnt = np.unique(b.reshape(-1, 3), axis=0, return_counts=True)
        out.append(cnt.max() / cnt.sum())
    return out

def read_text(path):
    import subprocess
    try:
        return path, subprocess.run(['tesseract', path, '-', '-l', 'eng', '--psm', '11'], capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return path, ''

def save_screen(path):
    a = np.asarray(Image.open(path).convert('RGB').resize((40, 40)), dtype=float)
    t = a[:3].reshape(-1, 3).mean(0)
    return t[0] > 215 and t[1] < 205 and t[2] > 165 and t[0] - t[1] > 25

def main():
    cache, ocr_path = sys.argv[1], sys.argv[2]
    refs = json.load(open(REFS, encoding='utf8')); ocr = json.load(open(ocr_path)) if os.path.exists(ocr_path) else {}
    idx = json.load(open(os.path.join(cache, 'index.json'))); files = {t[1]: os.path.join(cache, '%03d.jpg' % t[0]) for t in idx}
    fix = json.load(open(os.path.join(ROOT, 'designs', 'ref_kinds.json'), encoding='utf8')).get('fix', {}) if os.path.exists(os.path.join(ROOT, 'designs', 'ref_kinds.json')) else {}
    from collections import Counter
    c = Counter()
    # 1) 単色の地がどの帯にもある画像（マイデザインだけの候補）だけ文字を読む
    import subprocess
    from multiprocessing import Pool
    bands = {r['no']: flat_bands(files[r['url']]) for r in refs if r['url'] in files}
    todo = [files[r['url']] for r in refs if r['url'] in files and r['url'] not in ocr and min(bands[r['no']]) >= .25 and not save_screen(files[r['url']])]
    print('文字を読む候補', len(todo))
    back = {files[r['url']]: r['url'] for r in refs if r['url'] in files}
    with Pool(8) as pool:
        for k, (path, txt) in enumerate(pool.imap_unordered(read_text, todo, chunksize=4)):
            ocr[back[path]] = txt
            if k % 50 == 0: json.dump(ocr, open(ocr_path, 'w'))
    json.dump(ocr, open(ocr_path, 'w'))
    for r in refs:
        p = files.get(r['url'])
        if not p:
            continue
        txt = ocr.get(r['url'], ''); title = r.get('title', '')
        bd = bands[r['no']]
        has_code = bool(CODE.search(txt)) or bool(r.get('ma'))
        if save_screen(p) or (has_code and min(bd) >= .25):
            k = 'design'
        else:
            k = 'scene'
        r['kind'] = fix.get(r['no'], k); c[r['kind']] += 1
    with open(REFS, 'w', encoding='utf8') as f:
        f.write(json.dumps(refs, ensure_ascii=False, indent=0))
    print(dict(c))

if __name__ == '__main__':
    main()
