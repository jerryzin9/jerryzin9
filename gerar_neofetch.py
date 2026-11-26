# Gera o cartão do topo do perfil do GitHub (jerryzin9) no estilo "neofetch":
# retrato do Jerry em arte ASCII (feita da FOTO REAL dele, a do avatar do GitHub recortada com rembg; nada de ilustração)
# + painel de terminal com stack, contato e números. Saída: dark_mode.svg e light_mode.svg.
# uso: python gerar_neofetch.py            (dados ficam no bloco PAINEL abaixo)
import html
from pathlib import Path

import numpy as np
import cv2
from PIL import Image

AQUI = Path(__file__).resolve().parent
# foto/avatar-original.jpg = avatar do GitHub (460 px); recorte = interseção u2net_human_seg × isnet-general-use
# (um pegava o reflexo no vidro, o outro a placa da barbearia). A pasta foto/ fica fora do git.
FOTO = AQUI / "foto" / "jerry-recorte-avatar.png"

# ---------- arte ASCII ----------
CANDIDATOS = " .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
COLS = 126           # colunas da arte (letra miúda: a foto aparece pela densidade, como na referência)
CORTE = (110, 30, 400, 420)  # cabeça de perfil e ombros, na foto de 460 px
CLAHE = 3.0                # contraste local
CURVA = 6.0                # curva em S (luz dramática: brilho no rosto, sombra na camiseta)
FS_ASCII = 5.2       # tamanho da fonte da arte
LH_ASCII = 5.9       # altura da linha da arte
ASPECTO = 0.55 * FS_ASCII / LH_ASCII  # largura/altura de uma célula (Consolas ~0,55 em)


def rampa_calibrada():
    """Mede a tinta de cada caractere no Consolas e devolve (caracteres, densidades) em ordem crescente.
    A rampa "clássica" erra feio (o * tem pouca tinta, o L tem mais que o v...), por isso a medição."""
    from PIL import ImageDraw, ImageFont
    f = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 40)
    med = []
    for ch in CANDIDATOS:
        im = Image.new("L", (22, 47), 0)
        ImageDraw.Draw(im).text((0, 0), ch, font=f, fill=255)
        med.append((np.asarray(im).mean() / 255, ch))
    med.sort()
    return "".join(c for _, c in med), np.array([d for d, _ in med])


def arte(claro_e_denso: bool):
    """Foto real -> contraste local + curva em S -> caractere com a tinta certa. Fora da silhueta fica vazio."""
    im = Image.open(FOTO).convert("RGBA").crop(CORTE)
    rgba = np.asarray(im)
    alfa = rgba[..., 3].astype(np.float32) / 255
    cinza = cv2.cvtColor(np.ascontiguousarray(rgba[..., :3]), cv2.COLOR_RGB2GRAY)
    cl = cv2.createCLAHE(clipLimit=CLAHE, tileGridSize=(4, 4)).apply(cinza).astype(np.float32) / 255
    dentro = alfa > 0.5
    lo, hi = np.percentile(cl[dentro], [2, 99.7])
    g = np.clip((cl - lo) / (hi - lo), 0, 1)
    g = 1 / (1 + np.exp(-CURVA * (g - 0.5)))
    g = (g - g.min()) / (g.max() - g.min())
    w, h = im.size
    linhas = max(1, round(COLS * (h / w) * ASPECTO))
    G = cv2.resize(g, (COLS, linhas), interpolation=cv2.INTER_AREA)
    A = cv2.resize(alfa, (COLS, linhas), interpolation=cv2.INTER_AREA)
    chars, dens = rampa_calibrada()
    alvo_max = dens[-1]
    saida = []
    for y in range(linhas):
        s = ""
        for x in range(COLS):
            if A[y, x] < 0.45:
                s += " "
                continue
            # no tema claro a tinta segue o escuro da foto; limite para a camiseta preta não virar um bloco de @
            v = G[y, x] if claro_e_denso else 0.68 * (1 - G[y, x])
            i = int(np.abs(dens - v * alvo_max).argmin())
            s += chars[max(2, i)]   # dentro da silhueta nunca fica vazio (a camiseta preta aparece)
        saida.append(s.rstrip())
    while saida and not saida[0].strip():
        saida.pop(0)
    while saida and not saida[-1].strip():
        saida.pop()
    return saida


# ---------- painel ----------
LARG = 62  # caracteres por linha do painel
PAINEL = [
    ("cab", "jerry@silva"),
    ("kv", "OS", "Windows 11 · Linux (servidores)"),
    ("kv", "Uptime", "agentes de IA rodando 24/7"),
    ("kv", "Host", "GR Negócios Digitais"),
    ("kv", "Kernel", "Full Stack Developer"),
    ("kv", "IDE", "VS Code · Claude Code"),
    ("vazio",),
    ("kv", "Languages.Programming", "TypeScript, JavaScript, Python"),
    ("kv", "Languages.Computer", "HTML, CSS, SQL, JSON"),
    ("kv", "Languages.Real", "Português"),
    ("vazio",),
    ("kv", "Stack.Front", "React, Next.js, Tailwind, Astro"),
    ("kv", "Stack.Back", "Node.js, Supabase, n8n, Vercel"),
    ("kv", "AI.Agents", "Claude, GPT, MCP, squads de agentes"),
    ("kv", "AI.Integrations", "API oficial da Meta"),
    ("vazio",),
    ("kv", "Hobbies.Software", "Agentes de IA, automações"),
    ("kv", "Hobbies.Real", "Anime, música"),
    ("secao", "Contact"),
    ("kv", "Site", "jerrysilva.vercel.app"),
    ("kv", "LinkedIn", "in/jerrysilvadev"),
    ("kv", "Base", "Paraíba, Brasil · remoto"),
    ("secao", "GitHub Stats"),
    ("stats", [("Repos", "3"), ("Projetos entregues", "26"), ("Sites no ar", "15+")]),
]

TEMAS = {
    "dark": dict(fundo1="#0f0c1f", fundo2="#1b1336", borda="#3a2d6e", barra="#161129", titulo="#ff5fd2",
                 sub="#8f84c9", ascii="#d9d3ff", chave="#ff79c6", valor="#8be9fd", ponto="#4f4a78",
                 cab="#f8f8f2", secao="#50fa7b", texto="#e9e6ff", ascii_claro=True, asc1="#ffd1f3", asc2="#a5b4fc"),
    "light": dict(fundo1="#fbf9ff", fundo2="#efe9ff", borda="#cbbff0", barra="#ece6fb", titulo="#c0128f",
                  sub="#6d6496", ascii="#2b2352", chave="#b0177a", valor="#0b6e86", ponto="#b5aed6",
                  cab="#1f1a3a", secao="#15803d", texto="#1f1a3a", ascii_claro=False, asc1="#831a6b", asc2="#312a70"),
}

E = html.escape


def linha_kv(chave, valor):
    pontos = LARG - len(chave) - len(valor) - 6   # ". " + ":" + " " + " " = 5..6
    pontos = max(2, pontos)
    return [("ponto", ". "), ("chave", chave), ("texto", ":"), ("ponto", " " + "." * pontos + " "), ("valor", valor)]


def svg(tema):
    t = TEMAS[tema]
    asc = arte(t["ascii_claro"])
    W, PX, PY0, FS, LH = 1000, 440, 150, 14.2, 20.5
    alt_painel = PY0 + LH * (len(PAINEL) - 1)
    # arte centralizada na altura do painel (primeira linha do painel em PY0)
    topo_painel, fim_painel = PY0 - FS, alt_painel + 4
    ay0 = topo_painel + (fim_painel - topo_painel - LH_ASCII * len(asc)) / 2 + FS_ASCII
    alt_ascii = ay0 + LH_ASCII * len(asc)
    H = int(max(alt_painel, alt_ascii) + 34)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="Consolas, \'Courier New\', ui-monospace, SFMono-Regular, Menlo, monospace" xml:space="preserve" '
           f'role="img" aria-label="Jerry Silva, Full Stack Developer: agentes de IA, sites e sistemas web">',
           "<defs>",
           f'<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["fundo1"]}"/>'
           f'<stop offset="1" stop-color="{t["fundo2"]}"/></linearGradient>',
           f'<linearGradient id="tit" x1="0" x2="1"><stop offset="0" stop-color="{t["titulo"]}"/>'
           f'<stop offset="1" stop-color="{t["chave"]}"/></linearGradient>',
           f'<linearGradient id="asc" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["asc1"]}"/>'
           f'<stop offset="0.55" stop-color="{t["ascii"]}"/><stop offset="1" stop-color="{t["asc2"]}"/></linearGradient>',
           "</defs>",
           f'<style>.a{{fill:url(#asc);font-size:{FS_ASCII}px;font-weight:700}}.p{{font-size:{FS}px}}'
           f'.chave{{fill:{t["chave"]}}}.valor{{fill:{t["valor"]}}}.ponto{{fill:{t["ponto"]}}}'
           f'.texto{{fill:{t["texto"]}}}.cab{{fill:{t["cab"]};font-weight:700}}.secao{{fill:{t["secao"]};font-weight:700}}</style>',
           f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="url(#g)" stroke="{t["borda"]}" stroke-width="2"/>',
           # barra de janela
           f'<path d="M1 15a14 14 0 0 1 14-14h{W-30}a14 14 0 0 1 14 14v21H1z" fill="{t["barra"]}"/>',
           f'<line x1="1" y1="36" x2="{W-1}" y2="36" stroke="{t["borda"]}" stroke-width="1.2"/>',
           '<circle cx="24" cy="19" r="6" fill="#ff5f57"/><circle cx="44" cy="19" r="6" fill="#febc2e"/>'
           '<circle cx="64" cy="19" r="6" fill="#28c840"/>',
           f'<text x="{W/2}" y="23.5" text-anchor="middle" font-size="13" fill="{t["sub"]}">jerry@silva: ~</text>',
           # título
           f'<text x="{W/2}" y="92" text-anchor="middle" font-size="36" font-weight="700" letter-spacing="7" '
           f'fill="url(#tit)">FULL STACK DEVELOPER</text>',
           f'<text x="{W/2}" y="117" text-anchor="middle" font-size="14" letter-spacing="1.5" fill="{t["sub"]}">'
           f'agentes de IA · sites · sistemas web · automações</text>',
           ]
    # arte ASCII
    out.append('<text class="a">')
    for i, l in enumerate(asc):
        # espaço normal some no SVG (o GitHub não respeita xml:space): vira espaço não separável
        out.append(f'<tspan x="34" y="{ay0 + i*LH_ASCII:.1f}">{E(l, quote=False).replace(" ", chr(160))}</tspan>')
    out.append("</text>")
    # painel
    out.append('<text class="p">')
    y = PY0
    for item in PAINEL:
        tipo = item[0]
        if tipo == "cab":
            partes = [("cab", item[1]), ("ponto", " " + "—" * (LARG - len(item[1]) - 1))]
        elif tipo == "secao":
            partes = [("ponto", "— "), ("secao", item[1]), ("ponto", " " + "—" * (LARG - len(item[1]) - 3))]
        elif tipo == "vazio":
            partes = [("ponto", ". ")]
        elif tipo == "kv":
            partes = linha_kv(item[1], item[2])
        else:  # stats
            partes = [("ponto", ". ")]
            for k, (c, v) in enumerate(item[1]):
                if k:
                    partes.append(("ponto", " | "))
                partes += [("chave", c), ("texto", ": "), ("valor", v)]
        spans = "".join(f'<tspan class="{c}">{E(s, quote=False)}</tspan>' for c, s in partes)
        out.append(f'<tspan x="{PX}" y="{y:.1f}">{spans}</tspan>')
        y += LH
    out.append("</text>")
    out.append("</svg>")
    return "\n".join(out), asc


if __name__ == "__main__":
    for tema in TEMAS:
        conteudo, asc = svg(tema)
        (AQUI / f"{tema}_mode.svg").write_text(conteudo, encoding="utf-8")
        print(tema, f"{len(conteudo)/1024:.0f} KB", len(asc), "linhas de arte")
    print("\n".join(arte(True)))
