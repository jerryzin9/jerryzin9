# Renderiza os SVG como o GitHub mostra (<img>, sem fontes externas) para conferir: previa/<tema>.png
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
AQUI = Path(__file__).resolve().parent
(AQUI / "previa").mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    for tema, bg in (("dark", "#0d1117"), ("light", "#ffffff")):
        pg = b.new_page(viewport={"width": 1040, "height": 900}, device_scale_factor=float(sys.argv[1]) if len(sys.argv) > 1 else 1.5)
        src = (AQUI / f"{tema}_mode.svg").as_uri()
        pag = AQUI / "previa" / f"_{tema}.html"
        pag.write_text(f'<body style="margin:0;padding:20px;background:{bg}"><img src="{src}" style="width:1000px;display:block"></body>', encoding="utf-8")
        pg.goto(pag.as_uri())
        pg.wait_for_timeout(600)
        pg.locator("img").screenshot(path=str(AQUI / "previa" / f"{tema}.png"))
    b.close()
print("ok")
