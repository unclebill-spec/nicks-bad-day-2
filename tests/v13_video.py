# Records docs/v13_psych.gif (~20 s: ward + GREG croon/pillow boomerang + a blackout, then "Dr." Phil-in) (the screenshot docs/v13_psych.png was taken separately).
import time, subprocess, glob, os
from playwright.sync_api import sync_playwright
U = 'http://localhost:8731/'; T = {}
def clip(b, q, name, run):
    ctx = b.new_context(viewport={'width': 960, 'height': 540}, record_video_dir='tests/out/vid13', record_video_size={'width': 960, 'height': 540})
    pg = ctx.new_page(); t0 = time.time(); pg.goto(U + q); pg.wait_for_function('window.__loaded === true', timeout=30000)
    pg.wait_for_function("__nbd.game.scene==='play' && __nbd.W.heroes.length>0", timeout=30000)
    T[name] = [time.time() - t0]; run(pg); T[name].append(time.time() - t0)
    path = pg.video.path(); ctx.close(); os.replace(path, f'tests/out/vid13/{name}.webm')
def ward(pg):
    time.sleep(2.0)
    pg.evaluate("(()=>{const W=__nbd.W,h=W.heroes[0]; W.enemies.forEach(e=>{if(e.d&&e.kind==='greg') return}); const g=__nbd.spawn('greg','R'); g.x=h.x+120; g.y=h.y; g.tx=g.x; g.ty=g.y; g.set('idle'); window.GG=g; GG.croon();})()")
    time.sleep(1.6)
    pg.evaluate("(()=>{GG.throwKind='jello'; GG.set('atk'); GG.hitDone=false; GG.t=0.05})()"); time.sleep(2.4)
    pg.evaluate("__nbd.ward.blackout()"); time.sleep(2.6)
    pg.evaluate("GG.croon()"); time.sleep(2.0)
def boss(pg):
    pg.wait_for_function("__nbd.W.boss && __nbd.W.boss.greeted", timeout=20000); time.sleep(2.4)
    pg.evaluate("(()=>{const B=__nbd.W.boss; B.set('write'); B.hitDone=false;})()"); time.sleep(2.0)
    pg.evaluate("(()=>{const B=__nbd.W.boss,h=__nbd.W.heroes[0]; B.x=h.x+75; B.y=h.y; B.face=-1; B.set('lasso'); B.hitDone=false;})()"); time.sleep(2.2)
    pg.evaluate("(()=>{const B=__nbd.W.boss; B.set('chase'); B.hp=1; B.takeHit({dmg:5, dir:1, from:__nbd.W.heroes[0], force:true});})()"); time.sleep(2.4)
with sync_playwright() as p:
    b = p.chromium.launch()
    clip(b, '?level=5&zone=1&bot=1&god=1&hero=kim', 'a', ward)
    clip(b, '?level=5&zone=4&bot=1&god=1&hero=will', 'b', boss)
    b.close()
print(T)
parts = []
for n in ('a', 'b'):
    s, e = T[n]; out = f'tests/out/vid13/{n}.mp4'; parts.append(out)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{s:.2f}', '-to', f'{e:.2f}', '-i', f'tests/out/vid13/{n}.webm', '-vf', 'fps=12,scale=480:-1:flags=neighbor', out], check=True)
open('tests/out/vid13/list.txt', 'w').write(''.join(f"file '{os.path.basename(x)}'\n" for x in parts))
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'tests/out/vid13/list.txt', '-c', 'copy', 'tests/out/vid13/all.mp4'], check=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'tests/out/vid13/all.mp4', '-vf', 'split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=none', 'docs/v13_psych.gif'], check=True)
print(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'tests/out/vid13/all.mp4'], capture_output=True, text=True).stdout, os.path.getsize('docs/v13_psych.gif'))
