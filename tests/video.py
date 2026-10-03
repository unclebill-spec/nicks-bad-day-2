# Records short bot-driven clips (desktop 960x540) for the GIF: elevator bank, then the boss.
import time, glob, os, shutil
from playwright.sync_api import sync_playwright
os.makedirs('tests/out/vid', exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, q, secs in [('elev', 'zone=2&bot=1&god=1&hero=kim', 9), ('boss', 'zone=5&bot=1&god=1&hero=will', 11)]:
        ctx = b.new_context(viewport={'width': 960, 'height': 540}, record_video_dir='tests/out/vid', record_video_size={'width': 960, 'height': 540})
        pg = ctx.new_page(); pg.goto('http://localhost:8731/?' + q); pg.wait_for_function('window.__loaded === true')
        time.sleep(secs); path = pg.video.path(); ctx.close(); shutil.move(path, f'tests/out/vid/{name}.webm')
    b.close()
