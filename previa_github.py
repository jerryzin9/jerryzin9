# Abre github.com/jerryzin9 num Chromium próprio (escuro e claro) e salva em previa/github-<tema>.png
from pathlib import Path
from playwright.sync_api import sync_playwright
AQUI = Path(__file__).resolve().parent
with sync_playwright() as p:
    b = p.chromium.launch()
    for tema in ("dark", "light"):
        ctx = b.new_context(viewport={"width": 1280, "height": 900}, color_scheme=tema, device_scale_factor=1)
        pg = ctx.new_page()
        pg.goto("https://github.com/jerryzin9", wait_until="networkidle", timeout=90000)
        pg.wait_for_timeout(2500)
        pg.screenshot(path=str(AQUI / "previa" / f"github-{tema}.png"), full_page=True)
        ctx.close()
    b.close()
print("ok")
