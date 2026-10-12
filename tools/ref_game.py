"""集めた作例が「あつ森（ゲームの画面）」かどうかを CLIP で見分ける（第41回）。

Pinterest は検索語に acnh を入れても、本物の写真（お店・旅行かばんの展示など）や家具の商品写真・3D の絵が混ざる。
  python3 tools/ref_game.py <CLIP の置き場> <写真の置き場> [<小红书の置き場>]
    CLIP の置き場：Xenova/clip-vit-base-patch32 の vision_model_quantized.onnx・text_model_quantized.onnx・tokenizer.json
  → 番号ごとの点数（あつ森らしさ 0〜1）を designs/ref_game.json の score に書く。
    CLIP は暗い室内のあつ森も低く出すので自動では外さない（cut 0）。点数の低い順に並べて見て、ちがうものを fix に false で書く → notgame
    （第41回：荷物・旅行かばんの展示、街灯、2階建てバス、ガソリンスタンド、レモン（アマルフィ）の検索に本物の写真・商品写真が多かった）
"""
import json, os, sys
import numpy as np
from PIL import Image
ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'designs', 'ref_game.json')
GAME = ['a screenshot of the video game Animal Crossing New Horizons', 'a cute cartoon video game screenshot of an island town',
        'a screenshot of a custom design pattern in Animal Crossing', 'an Animal Crossing island scene with villagers and furniture']
REAL = ['a real photograph of a store', 'a real photograph of a city street', 'a product photo of real furniture', 'a real photograph of luggage',
        'a photo of a real building', 'a 3D render of a real interior', 'a real photograph of people', 'a photo of real food']
MEAN, STD = np.array([0.48145466, 0.4578275, 0.40821073]), np.array([0.26862954, 0.26130258, 0.27577711])

def prep(path):
    im = Image.open(path).convert('RGB'); w, h = im.size; s = 224 / min(w, h)
    im = im.resize((max(224, round(w * s)), max(224, round(h * s))), Image.BICUBIC); w, h = im.size
    im = im.crop(((w - 224) // 2, (h - 224) // 2, (w - 224) // 2 + 224, (h - 224) // 2 + 224))
    return ((np.asarray(im, dtype=np.float32) / 255 - MEAN) / STD).transpose(2, 0, 1).astype(np.float32)

def main():
    import onnxruntime as ort
    from tokenizers import Tokenizer
    md, cache = sys.argv[1], sys.argv[2]
    tok = Tokenizer.from_file(os.path.join(md, 'tokenizer.json')); tok.enable_padding(length=77, pad_id=49407); tok.enable_truncation(77)
    tm = ort.InferenceSession(os.path.join(md, 'text_model_quantized.onnx')); vm = ort.InferenceSession(os.path.join(md, 'vision_model_quantized.onnx'))
    enc = tok.encode_batch(GAME + REAL); ids = np.array([e.ids for e in enc], dtype=np.int64); att = np.array([e.attention_mask for e in enc], dtype=np.int64)
    tin = {i.name: (ids if 'ids' in i.name else att) for i in tm.get_inputs()}
    te = [o for o in tm.run(None, tin) if o.ndim == 2 and o.shape[0] == len(GAME + REAL)][0]; te = te / np.linalg.norm(te, axis=1, keepdims=True)
    files = {t[1]: os.path.join(cache, '%03d.jpg' % t[0]) for t in json.load(open(os.path.join(cache, 'index.json')))}
    refs = json.load(open(os.path.join(ROOT, 'designs', 'refs.json'), encoding='utf8'))
    todo = [(r['no'], files[r['url']]) for r in refs if r['url'] in files]
    if len(sys.argv) > 3:
        xr = json.load(open(os.path.join(ROOT, 'designs', 'xhs_refs.json'), encoding='utf8'))['refs']
        todo += [(r['no'], os.path.join(sys.argv[3], r['url'])) for r in xr]
    old = json.load(open(OUT, encoding='utf8')) if os.path.exists(OUT) else {}
    score = {}
    for k in range(0, len(todo), 32):
        batch = todo[k:k + 32]
        x = np.stack([prep(p) for _, p in batch])
        ie = [o for o in vm.run(None, {vm.get_inputs()[0].name: x}) if o.ndim == 2 and o.shape[0] == len(batch)][0]; ie = ie / np.linalg.norm(ie, axis=1, keepdims=True)
        lg = 100 * ie @ te.T; p = np.exp(lg - lg.max(1, keepdims=True)); p /= p.sum(1, keepdims=True)
        for (no, _), row in zip(batch, p): score[no] = round(float(row[:len(GAME)].sum()), 3)
        print(k + len(batch), '/', len(todo), end='\r', flush=True)
    fix = old.get('fix', {})
    notgame = sorted(no for no, s in score.items() if (fix[no] is False if no in fix else s < old.get('cut', 0.0)))
    json.dump({'note': old.get('note', 'あつ森らしさ（CLIP、0〜1）。fix は見て直した分（true＝あつ森、false＝ちがう）'),
               'cut': old.get('cut', 0.0), 'fix': fix, 'notgame': notgame, 'score': score}, open(OUT, 'w', encoding='utf8'), ensure_ascii=False, indent=0)
    print('\nあつ森ではない', len(notgame), '/', len(score))

if __name__ == '__main__':
    main()
