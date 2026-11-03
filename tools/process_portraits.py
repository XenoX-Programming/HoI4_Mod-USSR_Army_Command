#!/usr/bin/env python3
"""Crop, colorize (ChromaGAN), and export HOI4 leader portraits.
Non-generative: only chroma is predicted; luminance/geometry come from the source photo.
"""
import json, os, sys
from pathlib import Path
import numpy as np, cv2, onnxruntime as ort
from PIL import Image, ImageEnhance, ImageFilter
ROOT=Path(__file__).resolve().parents[1]
SRC=Path(os.environ.get('USAC_PORTRAITS','/home/user/research/portrait_sources'))
OUT=ROOT/'USSR_Army_Command/gfx/leaders/SOV'
MODEL=Path(os.environ.get('USAC_MODEL','/home/user/.cache/hoi4-assets/chromagan.onnx'))
R=json.loads(Path(os.environ.get('USAC_ROSTER',str(ROOT/'tools/data/roster.json'))).read_text())
# manual crop boxes (x0,y0,x1,y1) in source pixels for tricky images
CROPS={
 'basistiy': (620,140,1240,940),
 'krivoshein': None,
 'sokolovsky': (115,110,870,1130),
 'panteleyev': (60,20,440,625),
 'isakov': None,
 'kucherov': None,
 'alafuzov': None,
 'andreyev': None,
 'lyudnikov': None,
 'kozlov': None,
}
sess=ort.InferenceSession(str(MODEL),providers=['CPUExecutionProvider'])
inp=sess.get_inputs()[0].name

def colorize(im):
    arr=np.asarray(im.convert('RGB'))
    lab=cv2.cvtColor(arr,cv2.COLOR_RGB2LAB)
    L=lab[:,:,0]
    l224=cv2.resize(L,(224,224),interpolation=cv2.INTER_AREA).astype(np.float32)/255.0
    x=np.repeat(l224[None,None,:,:],3,axis=1)
    ab=sess.run(None,{inp:x})[0][0]
    ab=(ab*2-1)*150.0
    ab=cv2.resize(ab.transpose(1,2,0),(im.width,im.height),interpolation=cv2.INTER_CUBIC)
    out=np.zeros((im.height,im.width,3),np.float32)
    out[:,:,0]=L.astype(np.float32)
    out[:,:,1:]=ab+128.0
    out=np.clip(out,0,255).astype(np.uint8)
    rgb=cv2.cvtColor(out,cv2.COLOR_LAB2RGB)
    return Image.fromarray(rgb)

def crop_portrait(im,slug):
    w,h=im.size
    box=CROPS.get(slug,'auto')
    if box is None: box='auto'
    if box=='auto':
        # center crop to 156:210 aspect, biased upward for head/shoulders
        ar=156/210
        if w/h>ar:
            nw=int(h*ar); x0=(w-nw)//2; box=(x0,0,x0+nw,h)
        else:
            nh=int(w/ar); y0=max(0,int((h-nh)*0.25)); box=(0,y0,w,y0+nh)
    return im.crop(box)

def stylize(im):
    im=ImageEnhance.Contrast(im).enhance(1.08)
    im=ImageEnhance.Color(im).enhance(0.85)
    im=ImageEnhance.Sharpness(im).enhance(1.15)
    # subtle vignette
    w,h=im.size
    y,x=np.ogrid[:h,:w]
    cx,cy=w/2,h*0.42
    d=np.sqrt(((x-cx)/(w*0.75))**2+((y-cy)/(h*0.8))**2)
    v=np.clip(1.0-0.28*np.clip(d-0.45,0,1),0.72,1.0)
    arr=np.asarray(im).astype(np.float32)*v[:,:,None]
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8))

OUT.mkdir(parents=True,exist_ok=True)
preview=[]
for x in R:
    slug=x['slug']
    p=Path(x['photo'])
    if not p.is_absolute(): p=ROOT/p
    if not p.exists():
        # fallback to SRC by slug
        cand=list(SRC.glob(slug+'.*'))
        if not cand: raise SystemExit('missing '+slug)
        p=cand[0]
    im=Image.open(p).convert('RGB')
    im=crop_portrait(im,slug)
    im=im.resize((156,210),Image.LANCZOS)
    im=colorize(im)
    im=stylize(im)
    im.save(OUT/f'{slug}.png')
    small=im.resize((53,73),Image.LANCZOS)
    small.save(OUT/f'{slug}_small.png')
    preview.append((slug,im))
# contact sheet
sheet=Image.new('RGB',(8*156,((len(preview)+7)//8)*230),(30,30,30))
from PIL import ImageDraw
d=ImageDraw.Draw(sheet)
for i,(slug,im) in enumerate(preview):
    xx=(i%8)*156; yy=(i//8)*230
    sheet.paste(im,(xx,yy)); d.text((xx+4,yy+212),slug,fill='white')
sheet.save(ROOT/'docs/portrait_preview.jpg',quality=90)
print('processed',len(preview))
