# Avatar no clima do perfil novo: a FOTO REAL do avatar, sem fundo, em preto e branco contrastado com sombras
# arroxeadas, luz caindo da esquerda (lado do rosto) e fundo escuro. Nada de IA generativa, nada de contorno de luz.
# uso: python gerar_avatar.py <saida.png>
import sys
import numpy as np
import cv2
from pathlib import Path
from PIL import Image, ImageFilter

AQUI = Path(__file__).resolve().parent
rgba = Image.open(AQUI / "foto" / "jerry-recorte-avatar.png").convert("RGBA")
N = 920
rgba = rgba.resize((N, N), Image.LANCZOS)
rgb = np.asarray(rgba)[..., :3].astype(np.float32) / 255
# máscara: corta o resto fraco do reflexo no vidro e recua 2 px para não sobrar borda clara (cara de adesivo)
m = np.asarray(rgba.split()[-1], dtype=np.float32) / 255
m = np.clip((m - 0.35) / 0.5, 0, 1)
m = cv2.erode(m, np.ones((5, 5), np.uint8))
a = cv2.GaussianBlur(m, (0, 0), 1.6)

# preto e branco com contraste local e curva em S (luz dramática)
cinza = cv2.cvtColor((rgb * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
g = cinza.astype(np.float32) / 255
lo, hi = np.percentile(g[m > 0.5], [1, 99.5])
g = np.clip((g - lo) / (hi - lo), 0, 1)
s = 1 / (1 + np.exp(-4.0 * (g - 0.5)))       # contraste moderado: a camiseta continua preta
s = (s - s.min()) / (s.max() - s.min())
s = s ** 1.15
# luz da esquerda: o rosto fica aceso, o ombro direito cai na sombra
yy, xx = np.mgrid[0:N, 0:N] / N
luz = np.clip(1.15 - 0.75 * np.clip(xx - 0.30, 0, 1) - 0.25 * np.clip(yy - 0.55, 0, 1), 0.35, 1.1)
v = np.clip(s * luz, 0, 1)
# divisão de tons: sombra roxa, luz quase branca
sombra = np.array([27, 19, 54]) / 255
luz_c = np.array([226, 219, 238]) / 255   # sem estourar a pele
pessoa = sombra[None, None, :] * (1 - v[..., None]) + luz_c[None, None, :] * v[..., None]

# fundo: escuro com uma luz roxa suave atrás da cabeça
cx, cy = 0.40, 0.30
d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.1) ** 2)
fundo = (np.array([15, 12, 31]) / 255)[None, None, :] + (np.array([70, 40, 120]) / 255)[None, None, :] * np.clip(1 - d / 0.65, 0, 1)[..., None] ** 2
img = pessoa * a[..., None] + fundo * (1 - a[..., None])
# vinheta e grão fino de filme
vin = np.clip(1.08 - 0.55 * ((xx - 0.5) ** 2 + (yy - 0.45) ** 2) * 2.2, 0.55, 1)
img = img * vin[..., None]
img = img + np.random.default_rng(7).normal(0, 0.012, (N, N, 1))
out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.UnsharpMask(1.2, 60, 2))
destino = Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI / "previa" / "avatar.png"
out.save(destino)
print(destino)
