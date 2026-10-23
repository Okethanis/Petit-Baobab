"""Planches de photos pour la page Catalogue : les photos du site (images/*.webp) réduites à 320 px et rangées 6 × 6 par planche,
   publiées à côté de la page (dossier sheets/). admin/sheets.json dit où se trouve chaque photo : { "<nom>": [planche, colonne, ligne] }.
   Usage : python3 -I admin/make-sheets.py"""
import os, json
from PIL import Image

SRC = 'images'; OUT = 'admin/sheets'; os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
TILE, N = 320, 6
names = sorted(f for f in os.listdir(SRC) if f.endswith('.webp'))
index = {}
for s in range(0, len(names), N * N):
    batch = names[s:s + N * N]; sheet_no = s // (N * N)
    sheet = Image.new('RGB', (TILE * N, TILE * N), (255, 255, 255))
    for i, name in enumerate(batch):
        im = Image.open(os.path.join(SRC, name)).convert('RGB'); im.thumbnail((TILE, TILE), Image.LANCZOS)
        col, row = i % N, i // N
        sheet.paste(im, (col * TILE + (TILE - im.width) // 2, row * TILE + (TILE - im.height) // 2))
        index[os.path.splitext(name)[0]] = [sheet_no, col, row]
    sheet.save(os.path.join(OUT, 'sheet-%02d.webp' % sheet_no), quality=78, method=6)
json.dump(index, open('admin/sheets.json', 'w', encoding='utf-8'), separators=(',', ':'))
total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
print(len(names), 'photos sur', len(os.listdir(OUT)), 'planches,', total // 1024, 'Ko au total')
