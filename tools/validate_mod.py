#!/usr/bin/env python3
"""Static validation for USSR Army Command. Does not run HOI4."""
import json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'USSR_Army_Command'
R=json.loads((ROOT/'tools/data/roster.json').read_text())
errors=[]; warnings=[]
def read(p): return (MOD/p).read_text(encoding='utf-8-sig')
def braces(s):
    d=0
    for ch in s:
        if ch=='{': d+=1
        elif ch=='}': d-=1
        if d<0: return False
    return d==0
for p in MOD.rglob('*.txt'):
    if not braces(p.read_text()): errors.append(f'unbalanced braces: {p}')
for p in MOD.rglob('*.gfx'):
    if not braces(p.read_text()): errors.append(f'unbalanced braces: {p}')
chars=read('common/characters/USAC_soviet_commanders.txt')
ids=re.findall(r'^\t(USAC_\w+) = \{',chars,re.M)
if len(ids)!=len(R): errors.append(f'character count {len(ids)} != {len(R)}')
if len(set(ids))!=len(ids): errors.append('duplicate character ids')
loc=read('localisation/english/USAC_l_english.yml')
for x in R:
    cid='USAC_'+x['slug']
    if cid not in ids: errors.append('missing character '+cid)
    if f' {cid}:0 ' not in loc: errors.append('missing loc '+cid)
    for suffix in ['', '_small']:
        f=MOD/f'gfx/leaders/SOV/{x["slug"]}{suffix}.dds'
        if not f.exists(): errors.append('missing portrait '+str(f))
        g=f'GFX_{cid}{suffix}'
        if g not in read('interface/USAC_portraits.gfx'): errors.append('missing sprite '+g)
    for t in x['traits']:
        if t not in (ROOT/'tools/data/unit_traits.txt').read_text():
            errors.append('unknown trait '+t)
ev=read('events/USAC_recruitment.txt')
for x in R:
    if f'recruit_character = USAC_{x["slug"]}' not in ev: errors.append('event missing recruit '+x['slug'])
if ev.index('usac_recruit.1.a')>ev.index('usac_recruit.1.b'): errors.append('decline must be first option')
on=read('common/on_actions/USAC_on_actions.txt')
if 'is_ai = no' not in on or 'tag = SOV' not in on: errors.append('on_actions not human-SOV gated')
# baseline absence
base=(ROOT/'tools/data/vanilla_sov_tokens.txt').read_text()
for x in R:
    if re.search(r'\bSOV_'+x['slug']+r'\b',base): errors.append('vanilla collision '+x['slug'])
print('ERRORS' if errors else 'OK',len(errors))
for e in errors: print(' -',e)
for w in warnings: print(' warn:',w)
sys.exit(1 if errors else 0)
