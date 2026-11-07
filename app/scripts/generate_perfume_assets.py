"""
generate_perfume_assets.py
Generates high-end luxury vector SVG assets for:
1. Branding & Logos (app/static/images/branding/)
2. Hero Banners (app/static/images/hero/)
3. Collections (app/static/images/collections/)
4. Categories (app/static/images/categories/)
5. 100 Individual Luxury Perfume Product Flacons (app/static/images/products/)
   with authentic distinct silhouettes, optical lighting, and intelligent text wrapping.
"""

import os
import csv
import xml.sax.saxutils

# Base directories
DIRS = [
    "app/static/images/branding",
    "app/static/images/hero",
    "app/static/images/collections",
    "app/static/images/categories",
    "app/static/images/products",
    "app/static/images/perfume",
    "app/static/images/uploads",
    "static/images/branding",
    "static/images/hero",
    "static/images/collections",
    "static/images/categories",
    "static/images/products",
    "static/images/perfume",
]

for d in DIRS:
    os.makedirs(d, exist_ok=True)

def write_dual(rel_path, content):
    """Writes asset to both app/static and root static folders."""
    p1 = os.path.join("app", rel_path)
    p2 = rel_path
    os.makedirs(os.path.dirname(p1), exist_ok=True)
    os.makedirs(os.path.dirname(p2), exist_ok=True)
    with open(p1, "w", encoding="utf-8") as f:
        f.write(content)
    with open(p2, "w", encoding="utf-8") as f:
        f.write(content)

# ── 1. Branding Assets ────────────────────────────────────────────────────────
def generate_branding():
    logo_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 120" width="500" height="120">
  <defs>
    <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#edd59e"/>
      <stop offset="50%" stop-color="#c5a059"/>
      <stop offset="100%" stop-color="#9a752e"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="1.5" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <!-- Decorative Emblem -->
  <g transform="translate(45, 60)" filter="url(#glow)">
    <circle cx="0" cy="0" r="32" fill="none" stroke="url(#gold)" stroke-width="1.8"/>
    <circle cx="0" cy="0" r="26" fill="none" stroke="url(#gold)" stroke-width="0.8" stroke-dasharray="3,2"/>
    <path d="M0 -22 L6 -6 L22 0 L6 6 L0 22 L-6 6 L-22 0 L-6 -6 Z" fill="url(#gold)"/>
    <circle cx="0" cy="0" r="4" fill="#121316"/>
  </g>
  <!-- Typography -->
  <text x="100" y="58" font-family="'Cinzel', 'Playfair Display', 'Times New Roman', serif" font-size="34" font-weight="700" letter-spacing="8" fill="url(#gold)">LATTAFA</text>
  <text x="102" y="82" font-family="'Inter', -apple-system, sans-serif" font-size="11" font-weight="500" letter-spacing="6" fill="#ded7ca">HAUTE ARABIAN PERFUMERY</text>
  <line x1="102" y1="94" x2="430" y2="94" stroke="url(#gold)" stroke-width="0.75" opacity="0.6"/>
</svg>"""
    write_dual("static/images/branding/logo.svg", logo_svg)

    brandmark_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
  <defs>
    <linearGradient id="goldM" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f5e2b5"/>
      <stop offset="50%" stop-color="#c5a059"/>
      <stop offset="100%" stop-color="#8b631b"/>
    </linearGradient>
  </defs>
  <rect width="100" height="100" rx="20" fill="#15161b"/>
  <circle cx="50" cy="50" r="38" fill="none" stroke="url(#goldM)" stroke-width="2"/>
  <circle cx="50" cy="50" r="32" fill="none" stroke="url(#goldM)" stroke-width="1" stroke-dasharray="3,3"/>
  <path d="M50 20 L58 42 L80 50 L58 58 L50 80 L42 58 L20 50 L42 42 Z" fill="url(#goldM)"/>
  <circle cx="50" cy="50" r="5" fill="#15161b"/>
</svg>"""
    write_dual("static/images/branding/brandmark.svg", brandmark_svg)
    print("Branding assets generated.")

# ── 2. Hero Section Banners ──────────────────────────────────────────────────
def generate_hero():
    hero_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 800" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
  <defs>
    <radialGradient id="bgG" cx="75%" cy="50%" r="65%">
      <stop offset="0%" stop-color="#2a2215"/>
      <stop offset="45%" stop-color="#18171d"/>
      <stop offset="100%" stop-color="#0c0d10"/>
    </radialGradient>
    <linearGradient id="goldH" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fdf0cd"/>
      <stop offset="35%" stop-color="#d4af37"/>
      <stop offset="70%" stop-color="#aa832d"/>
      <stop offset="100%" stop-color="#644910"/>
    </linearGradient>
    <linearGradient id="amberG" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ffb347" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#8a4b08" stop-opacity="0.95"/>
    </linearGradient>
    <filter id="heroGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="30" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <rect width="1920" height="800" fill="url(#bgG)"/>
  <g stroke="url(#goldH)" stroke-width="0.5" opacity="0.08">
    <pattern id="lattice" width="80" height="80" patternUnits="userSpaceOnUse">
      <path d="M40 0 L80 40 L40 80 L0 40 Z M40 10 L70 40 L40 70 L10 40 Z"/>
    </pattern>
    <rect width="1920" height="800" fill="url(#lattice)"/>
  </g>
  <circle cx="1380" cy="400" r="280" fill="#c5a059" opacity="0.18" filter="url(#heroGlow)"/>
</svg>"""
    write_dual("static/images/hero/perfume_hero.svg", hero_svg)
    print("Hero assets generated.")

# ── 3. Collection Cards ──────────────────────────────────────────────────────
def generate_collections():
    cols = [
        ("yara_collection.svg", "YARA COLLECTION", "Soft Rose & Creamy Gourmand", "#f19bb2", "#421523"),
        ("asad_collection.svg", "ASAD COLLECTION", "Black Spices & Noble Woods", "#d4af37", "#141518"),
        ("khamrah_collection.svg", "KHAMRAH COLLECTION", "Golden Spices & Date Gourmand", "#d4882c", "#241306"),
        ("badee_al_oud.svg", "BADEE AL OUD", "Royal Agarwood & Smoky Resins", "#c5a059", "#121316"),
        ("lattafa_pride.svg", "LATTAFA PRIDE", "Artisanal Haute Parfumerie", "#c5a059", "#111816"),
        ("maison_alhambra.svg", "MAISON ALHAMBRA", "Parisian Chic with Arabian Depth", "#cca059", "#1a1815"),
        ("mainline_classics.svg", "MAINLINE CLASSICS", "Timeless Arabian Formulations", "#d4af37", "#15161b")
    ]
    for filename, title, subtitle, c2, bg in cols:
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
  <defs>
    <radialGradient id="g_{filename[:4]}" cx="50%" cy="40%" r="65%">
      <stop offset="0%" stop-color="{c2}" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="{bg}"/>
    </radialGradient>
    <linearGradient id="textG" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="60%" stop-color="{c2}"/>
      <stop offset="100%" stop-color="#8a631c"/>
    </linearGradient>
  </defs>
  <rect width="800" height="600" fill="{bg}"/>
  <rect width="800" height="600" fill="url(#g_{filename[:4]})"/>
  <rect x="25" y="25" width="750" height="550" fill="none" stroke="{c2}" stroke-width="1.5" opacity="0.35"/>
  <rect x="35" y="35" width="730" height="530" fill="none" stroke="{c2}" stroke-width="0.75" stroke-dasharray="6,4" opacity="0.25"/>
  
  <g transform="translate(400, 240) scale(0.9)" opacity="0.85">
    <ellipse cx="0" cy="180" rx="90" ry="18" fill="#000" opacity="0.4"/>
    <rect x="-65" y="-30" width="130" height="190" rx="16" fill="{bg}" stroke="{c2}" stroke-width="2.5"/>
    <rect x="-30" y="-70" width="60" height="40" rx="6" fill="{c2}"/>
    <circle cx="0" cy="65" r="34" fill="none" stroke="{c2}" stroke-width="1.5"/>
    <path d="M0 45 L6 59 L20 65 L6 71 L0 85 L-6 71 L-20 65 L-6 59 Z" fill="{c2}"/>
  </g>

  <text x="400" y="465" font-family="'Cinzel', serif" font-size="28" font-weight="700" letter-spacing="4" fill="url(#textG)" text-anchor="middle">{title}</text>
  <text x="400" y="500" font-family="'Inter', sans-serif" font-size="13" font-weight="400" letter-spacing="3" fill="#cfc7b8" text-anchor="middle">{subtitle}</text>
  <line x1="320" y1="525" x2="480" y2="525" stroke="{c2}" stroke-width="1" opacity="0.6"/>
  <text x="400" y="545" font-family="'Inter', sans-serif" font-size="10" font-weight="600" letter-spacing="4" fill="{c2}" text-anchor="middle">EXPLORE COLLECTION</text>
</svg>"""
        write_dual(f"static/images/collections/{filename}", svg)
    print("Collection cards generated.")

# ── 4. Category Banners ──────────────────────────────────────────────────────
def generate_categories():
    cats = [
        ("fragrances.svg", "ALL FRAGRANCES", "The Complete Arabian Treasury", "#c5a059", "#15161b"),
        ("men.svg", "FOR HIM", "Bold Woods, Spices & Aristocratic Leathers", "#8b9dc3", "#12141a"),
        ("women.svg", "FOR HER", "Enchanting Florals, Sweet Vanilla & Sugared Fruits", "#d9829e", "#181216"),
        ("unisex.svg", "UNISEX TREASURES", "Transcendent Blends for Connoisseurs", "#c5a059", "#161513"),
        ("edp.svg", "EAU DE PARFUM", "Exceptional Sillage & Long-Lasting Mastery", "#d4af37", "#161814"),
        ("extrait.svg", "EXTRAIT DE PARFUM", "High-Concentration Artisanal Extractions", "#e5aa42", "#191410"),
        ("attar.svg", "PERFUME OILS", "Traditional Alcohol-Free Concentrated Attars", "#95ba8d", "#101612"),
        ("gift_sets.svg", "GIFT SETS & BOXES", "Curated Luxury Presentation Packaging", "#d1ab64", "#18151c")
    ]
    for filename, title, subtitle, color, bg in cats:
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <defs>
    <radialGradient id="g_{filename[:3]}" cx="50%" cy="50%" r="65%">
      <stop offset="0%" stop-color="{color}" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="{bg}"/>
    </radialGradient>
  </defs>
  <rect width="600" height="400" fill="{bg}"/>
  <rect width="600" height="400" fill="url(#g_{filename[:3]})"/>
  <rect x="20" y="20" width="560" height="360" fill="none" stroke="{color}" stroke-width="1.2" opacity="0.3"/>
  <circle cx="300" cy="170" r="60" fill="none" stroke="{color}" stroke-width="1.5" opacity="0.6"/>
  <circle cx="300" cy="170" r="48" fill="none" stroke="{color}" stroke-width="0.8" stroke-dasharray="4,4"/>
  
  <text x="300" y="275" font-family="'Cinzel', serif" font-size="22" font-weight="700" letter-spacing="3" fill="#fdf0cd" text-anchor="middle">{title}</text>
  <text x="300" y="305" font-family="'Inter', sans-serif" font-size="11" letter-spacing="2" fill="#bfb7a7" text-anchor="middle">{subtitle}</text>
  <line x1="240" y1="325" x2="360" y2="325" stroke="{color}" stroke-width="1" opacity="0.5"/>
</svg>"""
        write_dual(f"static/images/categories/{filename}", svg)
    print("Category cards generated.")

# ── 5. Intelligent Text Splitting & Label Cartouche ──────────────────────────
def split_perfume_name(name):
    """Wrap names into balanced label-safe lines, never exceeding three lines."""
    words = name.split()
    if len(name) <= 13:
        return [name]

    max_chars = 14
    lines = []
    current = []
    current_len = 0
    for word in words:
        proposed = current_len + len(word) + (1 if current else 0)
        if current and proposed > max_chars:
            lines.append(' '.join(current))
            current = [word]
            current_len = len(word)
        else:
            current.append(word)
            current_len = proposed
    if current:
        lines.append(' '.join(current))

    # Keep small catalog names elegant and long names readable rather than forcing
    # a two-line label whose second line runs outside the plaque.
    if len(lines) > 3:
        lines = [' '.join(words[:2]), ' '.join(words[2:4]), ' '.join(words[4:])]
    return [line for line in lines if line]

def build_label_svg(name, brand, conc, size, accent, highlight, width=176, height=185, y_offset=25):
    """Constructs a high-craft foil-stamped label plaque with perfectly wrapped typography."""
    lines = split_perfume_name(name)
    safe_brand = xml.sax.saxutils.escape(brand.upper())
    safe_conc = xml.sax.saxutils.escape(conc.upper())
    safe_size = xml.sax.saxutils.escape(size.upper())
    
    hw = width / 2
    hh = height / 2
    top = -hh + y_offset
    
    if len(lines) == 1:
        n = lines[0]
        fs = 17 if len(n) <= 7 else (14.5 if len(n) <= 10 else 13)
        ls = 3 if len(n) <= 7 else 2
        title_svg = f'<text x="0" y="{y_offset + 12}" font-family="\'Cinzel\', \'Playfair Display\', \'Georgia\', serif" font-size="{fs}" font-weight="700" letter-spacing="{ls}" fill="url(#metalG)" text-anchor="middle">{xml.sax.saxutils.escape(n.upper())}</text>'
    else:
        max_l = max(len(l) for l in lines)
        fs = 9.8 if len(lines) == 3 or max_l > 15 else (11.2 if max_l > 12 else 12.2)
        ls = 0.8 if fs < 10 else (1.1 if fs < 12 else 1.6)
        line_spacing = 12 if len(lines) == 3 else 14
        start_y = y_offset - ((len(lines) - 1) * line_spacing / 2) + 7
        tspans = []
        for i, l in enumerate(lines):
            dy = "0" if i == 0 else f"{line_spacing}"
            tspans.append(f'<tspan x="0" dy="{dy}">{xml.sax.saxutils.escape(l.upper())}</tspan>')
        title_svg = f'<text x="0" y="{start_y}" font-family="\'Cinzel\', \'Playfair Display\', \'Georgia\', serif" font-size="{fs}" font-weight="700" letter-spacing="{ls}" fill="url(#metalG)" text-anchor="middle">{"".join(tspans)}</text>'

    return f"""
    <!-- Label Cartouche -->
    <rect x="{-hw}" y="{top}" width="{width}" height="{height}" rx="8" fill="#111216" stroke="url(#metalG)" stroke-width="1.8"/>
    <rect x="{-hw+5}" y="{top+5}" width="{width-10}" height="{height-10}" rx="5" fill="none" stroke="url(#metalG)" stroke-width="0.75" stroke-dasharray="4,2" opacity="0.6"/>
    
    <!-- Top Emblem / Star -->
    <g transform="translate(0, {top + 26})">
      <circle cx="0" cy="0" r="11" fill="none" stroke="url(#metalG)" stroke-width="0.9"/>
      <polygon points="0,-7 2,-2 7,0 2,2 0,7 -2,2 -7,0 -2,-2" fill="url(#metalG)"/>
    </g>
    
    <!-- Brand Line -->
    <text x="0" y="{top + 48}" font-family="'Inter', -apple-system, sans-serif" font-size="8" font-weight="600" letter-spacing="3" fill="#cfc7b8" text-anchor="middle">{safe_brand}</text>
    <line x1="{-hw+20}" y1="{top + 56}" x2="{hw-20}" y2="{top + 56}" stroke="url(#metalG)" stroke-width="0.6" opacity="0.5"/>
    
    <!-- Perfume Name -->
    {title_svg}
    
    <line x1="{-hw+24}" y1="{top + height - 38}" x2="{hw-24}" y2="{top + height - 38}" stroke="url(#metalG)" stroke-width="0.6" opacity="0.5"/>
    <!-- Concentration & Volume -->
    <text x="0" y="{top + height - 23}" font-family="'Inter', -apple-system, sans-serif" font-size="7" font-weight="500" letter-spacing="2" fill="#b0a594" text-anchor="middle">{safe_conc}</text>
    <text x="0" y="{top + height - 10}" font-family="'Inter', -apple-system, sans-serif" font-size="7.5" font-weight="600" letter-spacing="2.5" fill="url(#metalG)" text-anchor="middle">{safe_size}</text>
    """

# ── 6. Flacon Architectures & SVG Renderer ───────────────────────────────────
def render_flacon_svg(name, brand, family, conc, size, accent, highlight, bg_color, shape="classic"):
    safe_family = xml.sax.saxutils.escape(family.upper())

    if shape == "crystal":
        # Cut Crystal Whisky Decanter (Khamrah style)
        bottle_elements = f"""
        <ellipse cx="0" cy="210" rx="145" ry="22" fill="#000000" opacity="0.65"/>
        <ellipse cx="0" cy="208" rx="110" ry="14" fill="{accent}" opacity="0.18"/>
        <rect x="-115" y="-85" width="230" height="280" rx="16" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="2.5"/>
        <rect x="-110" y="150" width="220" height="40" rx="10" fill="url(#baseG)" opacity="0.9"/>
        <line x1="-110" y1="150" x2="110" y2="150" stroke="{highlight}" stroke-width="1.2" opacity="0.6"/>
        
        <path d="M-105,40 L-60,95 L-15,40 L30,95 L75,40 L105,75" fill="none" stroke="{highlight}" stroke-width="1.2" opacity="0.25"/>
        <path d="M-105,95 L-60,40 L-15,95 L30,40 L75,95 L105,60" fill="none" stroke="{highlight}" stroke-width="1.2" opacity="0.25"/>
        <path d="M-105,95 L-60,150 L-15,95 L30,150 L75,95 L105,130" fill="none" stroke="{highlight}" stroke-width="1.2" opacity="0.25"/>
        <path d="M-105,150 L-60,95 L-15,150 L30,95 L75,150 L105,115" fill="none" stroke="{highlight}" stroke-width="1.2" opacity="0.25"/>

        <line x1="-100" y1="-75" x2="-100" y2="180" stroke="#ffffff" stroke-width="3" stroke-linecap="round" opacity="0.35"/>
        <line x1="-93" y1="-70" x2="-93" y2="175" stroke="{highlight}" stroke-width="1" opacity="0.5"/>

        {build_label_svg(name, brand, conc, size, accent, highlight, width=170, height=175, y_offset=15)}

        <path d="M-60,-85 L-35,-120 L35,-120 L60,-85 Z" fill="url(#metalG)"/>
        <rect x="-35" y="-135" width="70" height="20" rx="3" fill="url(#metalG)"/>
        <line x1="-35" y1="-125" x2="35" y2="-125" stroke="#121316" stroke-width="1.5"/>

        <polygon points="-55,-220 55,-220 68,-175 48,-135 -48,-135 -68,-175" fill="url(#metalG)" stroke="{highlight}" stroke-width="1.8"/>
        <polygon points="-35,-220 35,-220 22,-200 -22,-200" fill="#ffffff" opacity="0.25"/>
        <circle cx="0" cy="-175" r="14" fill="#14151a" stroke="url(#metalG)" stroke-width="1.2"/>
        <polygon points="0,-182 3,-177 8,-175 3,-173 0,-168 -3,-173 -8,-175 -3,-177" fill="url(#metalG)"/>
        """

    elif shape == "cylinder":
        # Fluted Architectural Column (Asad style)
        bottle_elements = f"""
        <ellipse cx="0" cy="215" rx="135" ry="22" fill="#000000" opacity="0.65"/>
        <ellipse cx="0" cy="213" rx="100" ry="14" fill="{accent}" opacity="0.2"/>

        <rect x="-95" y="-100" width="190" height="305" rx="28" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="2.5"/>
        
        <line x1="-80" y1="-90" x2="-80" y2="195" stroke="#ffffff" stroke-width="3" stroke-linecap="round" opacity="0.32"/>
        <line x1="-70" y1="-85" x2="-70" y2="190" stroke="{highlight}" stroke-width="1" opacity="0.45"/>
        <line x1="75" y1="-85" x2="75" y2="190" stroke="{highlight}" stroke-width="1.5" opacity="0.25"/>

        <rect x="-96" y="-60" width="192" height="10" fill="url(#metalG)"/>
        <rect x="-96" y="160" width="192" height="10" fill="url(#metalG)"/>
        <line x1="-96" y1="-55" x2="96" y2="-55" stroke="#121316" stroke-width="1"/>
        <line x1="-96" y1="165" x2="96" y2="165" stroke="#121316" stroke-width="1"/>

        {build_label_svg(name, brand, conc, size, accent, highlight, width=158, height=180, y_offset=48)}

        <rect x="-42" y="-135" width="84" height="38" rx="4" fill="url(#metalG)"/>
        <line x1="-42" y1="-118" x2="42" y2="-118" stroke="#121316" stroke-width="1.5"/>

        <rect x="-52" y="-225" width="104" height="92" rx="14" fill="url(#metalG)" stroke="{highlight}" stroke-width="1.5"/>
        <line x1="-36" y1="-220" x2="-36" y2="-138" stroke="#121316" stroke-width="1.2" opacity="0.6"/>
        <line x1="-18" y1="-220" x2="-18" y2="-138" stroke="#121316" stroke-width="1.2" opacity="0.6"/>
        <line x1="0" y1="-220" x2="0" y2="-138" stroke="#121316" stroke-width="1.2" opacity="0.6"/>
        <line x1="18" y1="-220" x2="18" y2="-138" stroke="#121316" stroke-width="1.2" opacity="0.6"/>
        <line x1="36" y1="-220" x2="36" y2="-138" stroke="#121316" stroke-width="1.2" opacity="0.6"/>
        <rect x="-44" y="-232" width="88" height="10" rx="3" fill="url(#metalG)"/>
        """

    elif shape == "curve":
        # Sculpted Sensual Hourglass (Yara style)
        bottle_elements = f"""
        <ellipse cx="0" cy="210" rx="135" ry="20" fill="#000000" opacity="0.6"/>
        <ellipse cx="0" cy="208" rx="95" ry="12" fill="{accent}" opacity="0.25"/>

        <path d="M-92,-85 Q-75,-10 -95,65 Q-105,120 -82,190 L82,190 Q105,120 95,65 Q75,-10 92,-85 Z" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="2.5"/>
        
        <path d="M-82,-75 Q-68,0 -84,70 Q-92,115 -74,180" fill="none" stroke="#ffffff" stroke-width="3" stroke-linecap="round" opacity="0.4"/>
        <path d="M-72,-70 Q-60,0 -74,70" fill="none" stroke="{highlight}" stroke-width="1" opacity="0.5"/>

        <path d="M-86,22 Q0,32 86,22" fill="none" stroke="url(#metalG)" stroke-width="3"/>
        <path d="M-88,28 Q0,38 88,28" fill="none" stroke="url(#metalG)" stroke-width="1" opacity="0.7"/>

        {build_label_svg(name, brand, conc, size, accent, highlight, width=156, height=172, y_offset=42)}

        <path d="M-38,-85 L-28,-122 L28,-122 L38,-85 Z" fill="url(#metalG)"/>
        <rect x="-30" y="-136" width="60" height="16" rx="2" fill="url(#metalG)"/>
        <line x1="-30" y1="-128" x2="30" y2="-128" stroke="#121316" stroke-width="1.2"/>

        <path d="M-48,-136 Q-50,-225 0,-230 Q50,-225 48,-136 Z" fill="url(#metalG)" stroke="{highlight}" stroke-width="1.5"/>
        <path d="M-38,-140 Q-40,-215 0,-220 Q40,-215 38,-140" fill="none" stroke="#ffffff" stroke-width="1.2" opacity="0.35"/>
        <circle cx="0" cy="-233" r="7" fill="url(#metalG)" stroke="{highlight}" stroke-width="1"/>
        """

    elif shape == "faceted":
        # Monolithic Obelisk with Arabesque Filigree (Badee Al Oud style)
        bottle_elements = f"""
        <ellipse cx="0" cy="215" rx="140" ry="22" fill="#000000" opacity="0.7"/>
        <ellipse cx="0" cy="213" rx="100" ry="14" fill="{accent}" opacity="0.22"/>

        <polygon points="-80,-105 80,-105 106,-75 106,165 80,195 -80,195 -106,165 -106,-75" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="2.5"/>
        
        <line x1="-80" y1="-105" x2="-80" y2="195" stroke="url(#metalG)" stroke-width="1.2" opacity="0.5"/>
        <line x1="80" y1="-105" x2="80" y2="195" stroke="url(#metalG)" stroke-width="1.2" opacity="0.5"/>
        <line x1="-100" y1="-70" x2="-100" y2="160" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" opacity="0.35"/>

        <g opacity="0.35" transform="translate(0, 45)">
          <circle cx="0" cy="0" r="70" fill="none" stroke="url(#metalG)" stroke-width="1.5"/>
          <circle cx="0" cy="0" r="58" fill="none" stroke="url(#metalG)" stroke-width="0.8" stroke-dasharray="4,3"/>
          <polygon points="0,-65 18,-18 65,0 18,18 0,65 -18,18 -65,0 -18,-18" fill="none" stroke="url(#metalG)" stroke-width="1"/>
          <polygon points="-46,-46 0,-25 46,-46 25,0 46,46 0,25 -46,46 -25,0" fill="none" stroke="url(#metalG)" stroke-width="0.8"/>
        </g>

        {build_label_svg(name, brand, conc, size, accent, highlight, width=164, height=178, y_offset=45)}

        <polygon points="-48,-105 -35,-140 35,-140 48,-105" fill="url(#metalG)"/>
        
        <polygon points="-42,-228 42,-228 62,-185 45,-140 -45,-140 -62,-185" fill="url(#metalG)" stroke="{highlight}" stroke-width="1.8"/>
        <circle cx="0" cy="-184" r="15" fill="#111216" stroke="url(#metalG)" stroke-width="1.2"/>
        <polygon points="0,-193 4,-186 11,-184 4,-182 0,-175 -4,-182 -11,-184 -4,-186" fill="url(#metalG)"/>
        """

    elif shape == "minimalist_niche" or shape == "frosted_niche":
        # Luxury Niche Heavy Apothecary Flacon (Maison Alhambra style)
        bottle_elements = f"""
        <ellipse cx="0" cy="210" rx="140" ry="20" fill="#000000" opacity="0.6"/>
        <ellipse cx="0" cy="208" rx="100" ry="12" fill="{accent}" opacity="0.25"/>

        <rect x="-100" y="-80" width="200" height="275" rx="10" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="2"/>
        
        <rect x="-96" y="145" width="192" height="46" rx="6" fill="url(#baseG)" opacity="0.95"/>
        <line x1="-96" y1="145" x2="96" y2="145" stroke="{highlight}" stroke-width="1.2" opacity="0.7"/>

        <line x1="-88" y1="-70" x2="-88" y2="182" stroke="#ffffff" stroke-width="3" stroke-linecap="round" opacity="0.4"/>
        <line x1="-80" y1="-65" x2="-80" y2="180" stroke="{highlight}" stroke-width="1" opacity="0.4"/>

        {build_label_svg(name, brand, conc, size, accent, highlight, width=162, height=172, y_offset=18)}

        <rect x="-24" y="-115" width="48" height="36" rx="2" fill="url(#metalG)"/>
        <line x1="-24" y1="-95" x2="24" y2="-95" stroke="#121316" stroke-width="1.2"/>

        <rect x="-48" y="-215" width="96" height="102" rx="6" fill="url(#metalG)" stroke="{highlight}" stroke-width="1.5"/>
        <line x1="-48" y1="-190" x2="48" y2="-190" stroke="#121316" stroke-width="1.5"/>
        <line x1="-48" y1="-165" x2="48" y2="-165" stroke="#121316" stroke-width="1.5"/>
        <line x1="-48" y1="-140" x2="48" y2="-140" stroke="#121316" stroke-width="1.5"/>
        <rect x="-38" y="-222" width="76" height="8" rx="2" fill="url(#metalG)"/>
        """

    elif shape == "tall_luxury":
        # Tall Columnar Niche Flacon (Jean Lowe style)
        bottle_elements = f"""
        <ellipse cx="0" cy="215" rx="130" ry="20" fill="#000000" opacity="0.65"/>
        <ellipse cx="0" cy="213" rx="90" ry="12" fill="{accent}" opacity="0.2"/>

        <rect x="-85" y="-115" width="170" height="325" rx="18" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="2.5"/>
        <rect x="-80" y="165" width="160" height="42" rx="8" fill="url(#baseG)" opacity="0.9"/>
        <line x1="-80" y1="165" x2="80" y2="165" stroke="{highlight}" stroke-width="1" opacity="0.6"/>

        <line x1="-72" y1="-105" x2="-72" y2="195" stroke="#ffffff" stroke-width="3" stroke-linecap="round" opacity="0.35"/>
        <line x1="-64" y1="-100" x2="-64" y2="190" stroke="{highlight}" stroke-width="1" opacity="0.45"/>

        {build_label_svg(name, brand, conc, size, accent, highlight, width=148, height=185, y_offset=28)}

        <rect x="-32" y="-148" width="64" height="35" rx="3" fill="url(#metalG)"/>
        <rect x="-42" y="-232" width="84" height="88" rx="10" fill="url(#metalG)" stroke="{highlight}" stroke-width="1.5"/>
        <circle cx="0" cy="-188" r="12" fill="#121316" stroke="url(#metalG)" stroke-width="1"/>
        <circle cx="0" cy="-238" r="6" fill="url(#metalG)" stroke="{highlight}" stroke-width="1"/>
        """

    elif shape == "heavy_square":
        # Monumental Thick-Walled Cube (Qaed Al Fursan / Baroque Rouge style)
        bottle_elements = f"""
        <ellipse cx="0" cy="210" rx="145" ry="22" fill="#000000" opacity="0.7"/>
        <ellipse cx="0" cy="208" rx="105" ry="14" fill="{accent}" opacity="0.25"/>

        <rect x="-110" y="-85" width="220" height="280" rx="14" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="3"/>
        <rect x="-104" y="145" width="208" height="46" rx="8" fill="url(#baseG)" opacity="0.95"/>
        <line x1="-104" y1="145" x2="104" y2="145" stroke="{highlight}" stroke-width="1.2" opacity="0.7"/>

        <line x1="-96" y1="-75" x2="-96" y2="180" stroke="#ffffff" stroke-width="3" stroke-linecap="round" opacity="0.38"/>
        
        {build_label_svg(name, brand, conc, size, accent, highlight, width=172, height=175, y_offset=18)}

        <rect x="-40" y="-125" width="80" height="42" rx="3" fill="url(#metalG)"/>
        <rect x="-56" y="-220" width="112" height="98" rx="8" fill="url(#metalG)" stroke="{highlight}" stroke-width="2"/>
        <rect x="-46" y="-210" width="92" height="78" rx="4" fill="none" stroke="#121316" stroke-width="1.5"/>
        """

    elif shape == "shield":
        # Curved Shield Silhouette (Fakhar style)
        bottle_elements = f"""
        <ellipse cx="0" cy="215" rx="140" ry="22" fill="#000000" opacity="0.65"/>
        <ellipse cx="0" cy="213" rx="100" ry="14" fill="{accent}" opacity="0.2"/>

        <path d="M-105,-85 L105,-85 L105,100 Q105,195 0,205 Q-105,195 -105,100 Z" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="2.5"/>
        <path d="M-95,-75 L95,-75 L95,95 Q95,185 0,195 Q-95,185 -95,95 Z" fill="none" stroke="{highlight}" stroke-width="1" opacity="0.4"/>

        <line x1="-90" y1="-75" x2="-90" y2="120" stroke="#ffffff" stroke-width="3" stroke-linecap="round" opacity="0.35"/>

        {build_label_svg(name, brand, conc, size, accent, highlight, width=160, height=172, y_offset=28)}

        <polygon points="-50,-85 -30,-125 30,-125 50,-85" fill="url(#metalG)"/>
        <rect x="-30" y="-138" width="60" height="15" rx="2" fill="url(#metalG)"/>
        
        <path d="M-45,-138 Q-48,-225 0,-228 Q48,-225 45,-138 Z" fill="url(#metalG)" stroke="{highlight}" stroke-width="1.5"/>
        <circle cx="0" cy="-233" r="6" fill="url(#metalG)"/>
        """

    elif shape == "equine" or shape == "sculpted":
        # Sculpted Faceted Imperial Flacon (Maahir / Teriaq style)
        bottle_elements = f"""
        <ellipse cx="0" cy="215" rx="145" ry="22" fill="#000000" opacity="0.7"/>
        <ellipse cx="0" cy="213" rx="105" ry="14" fill="{accent}" opacity="0.22"/>

        <polygon points="-85,-95 85,-95 110,-50 95,150 75,198 -75,198 -95,150 -110,-50" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="2.5"/>
        
        <line x1="-85" y1="-95" x2="-75" y2="198" stroke="url(#metalG)" stroke-width="1.2" opacity="0.5"/>
        <line x1="85" y1="-95" x2="75" y2="198" stroke="url(#metalG)" stroke-width="1.2" opacity="0.5"/>
        <line x1="-102" y1="-40" x2="-88" y2="150" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" opacity="0.35"/>

        {build_label_svg(name, brand, conc, size, accent, highlight, width=162, height=178, y_offset=38)}

        <polygon points="-46,-95 -32,-132 32,-132 46,-95" fill="url(#metalG)"/>
        
        <!-- Sculpted Imperial Finial Cap -->
        <polygon points="-48,-232 48,-232 58,-190 40,-132 -40,-132 -58,-190" fill="url(#metalG)" stroke="{highlight}" stroke-width="1.8"/>
        <path d="M-25,-232 L0,-255 L25,-232 Z" fill="url(#metalG)" stroke="{highlight}" stroke-width="1.2"/>
        <circle cx="0" cy="-182" r="13" fill="#121316" stroke="url(#metalG)" stroke-width="1"/>
        <polygon points="0,-189 3,-184 8,-182 3,-180 0,-175 -3,-180 -8,-182 -3,-184" fill="url(#metalG)"/>
        """

    else:
        # Classic Royal Arabian Flacon (Default / Versatile)
        bottle_elements = f"""
        <ellipse cx="0" cy="215" rx="140" ry="22" fill="#000000" opacity="0.65"/>
        <ellipse cx="0" cy="213" rx="100" ry="14" fill="{accent}" opacity="0.2"/>

        <rect x="-105" y="-95" width="210" height="295" rx="22" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="2.5"/>
        
        <rect x="-98" y="155" width="196" height="40" rx="14" fill="url(#baseG)" opacity="0.9"/>
        <line x1="-98" y1="155" x2="98" y2="155" stroke="{highlight}" stroke-width="1" opacity="0.6"/>

        <line x1="-92" y1="-85" x2="-92" y2="185" stroke="#ffffff" stroke-width="3" stroke-linecap="round" opacity="0.35"/>
        <line x1="-84" y1="-80" x2="-84" y2="180" stroke="{highlight}" stroke-width="1" opacity="0.45"/>

        {build_label_svg(name, brand, conc, size, accent, highlight, width=166, height=180, y_offset=22)}

        <path d="M-65,-95 L-35,-130 L35,-130 L65,-95 Z" fill="url(#metalG)"/>
        <rect x="-34" y="-145" width="68" height="18" rx="3" fill="url(#metalG)"/>
        <line x1="-34" y1="-136" x2="34" y2="-136" stroke="#121316" stroke-width="1.2"/>

        <rect x="-50" y="-225" width="100" height="82" rx="10" fill="url(#metalG)" stroke="{highlight}" stroke-width="1.5"/>
        <circle cx="0" cy="-184" r="15" fill="#121316" stroke="url(#metalG)" stroke-width="1.2"/>
        <polygon points="0,-192 3.5,-186 10,-184 3.5,-182 0,-176 -3.5,-182 -10,-184 -3.5,-186" fill="url(#metalG)"/>
        <circle cx="0" cy="-232" r="7" fill="url(#metalG)" stroke="{highlight}" stroke-width="1"/>
        """

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 750" width="600" height="750">
  <defs>
    <radialGradient id="ambG" cx="50%" cy="40%" r="68%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.32"/>
      <stop offset="55%" stop-color="{bg_color}" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#08080a"/>
    </radialGradient>
    
    <linearGradient id="metalG" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.7"/>
      <stop offset="15%" stop-color="{highlight}"/>
      <stop offset="50%" stop-color="{accent}"/>
      <stop offset="85%" stop-color="#4a350b"/>
      <stop offset="100%" stop-color="{highlight}"/>
    </linearGradient>

    <linearGradient id="bodyG" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{bg_color}"/>
      <stop offset="20%" stop-color="{accent}" stop-opacity="0.75"/>
      <stop offset="48%" stop-color="{highlight}" stop-opacity="0.92"/>
      <stop offset="52%" stop-color="{highlight}" stop-opacity="0.92"/>
      <stop offset="80%" stop-color="{accent}" stop-opacity="0.75"/>
      <stop offset="100%" stop-color="{bg_color}"/>
    </linearGradient>

    <linearGradient id="baseG" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#000000" stop-opacity="0.8"/>
      <stop offset="30%" stop-color="{highlight}" stop-opacity="0.4"/>
      <stop offset="50%" stop-color="#ffffff" stop-opacity="0.6"/>
      <stop offset="70%" stop-color="{highlight}" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0.8"/>
    </linearGradient>

    <filter id="flaconShadow" x="-30%" y="-20%" width="160%" height="150%">
      <feDropShadow dx="0" dy="20" stdDeviation="22" flood-color="#000000" flood-opacity="0.85"/>
    </filter>
  </defs>

  <rect width="600" height="750" fill="url(#ambG)"/>
  <rect x="25" y="25" width="550" height="700" fill="none" stroke="{accent}" stroke-width="0.75" opacity="0.32"/>
  <rect x="33" y="33" width="534" height="684" fill="none" stroke="{accent}" stroke-width="0.5" stroke-dasharray="4,4" opacity="0.2"/>

  <g transform="translate(300, 365)" filter="url(#flaconShadow)">
    {bottle_elements}
  </g>

  <text x="300" y="705" font-family="'Inter', -apple-system, sans-serif" font-size="9.5" font-weight="600" letter-spacing="4.5" fill="{accent}" opacity="0.85" text-anchor="middle">{safe_family}</text>
</svg>"""
    return svg

# ── 7. Batch Generator for 100 Perfume Products ──────────────────────────────
def generate_perfume_bottles():
    csv_file = "PERFUME_CATALOG_DATA.csv"
    if not os.path.exists(csv_file):
        print("Catalog CSV not found!")
        return

    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        products = list(reader)

    palette_map = {
        "Khamrah": ("#d4882c", "#ffcf75", "#241306", "crystal"),
        "Asad": ("#d4af37", "#f3e1a6", "#141518", "cylinder"),
        "Yara": ("#f19bb2", "#fde5ec", "#421523", "curve"),
        "Yara Candy": ("#f43f75", "#ffd2de", "#3a0918", "curve"),
        "Yara Tous": ("#f6ba33", "#ffefc2", "#3a2602", "curve"),
        "Yara Moi": ("#edeae4", "#ffffff", "#3b342e", "curve"),
        "Eclaire": ("#cca059", "#fcedcd", "#2d1d0c", "classic"),
        "Angham": ("#b37a51", "#fadcc2", "#2e1b10", "classic"),
        "Khamrah Dukhan": ("#9c5825", "#d6945e", "#120a05", "crystal"),
        "Teriaq": ("#2b2b2b", "#d4af37", "#0d0d0f", "sculpted"),
        "Badee Al Oud Noble Blush": ("#e89ab0", "#fdedf1", "#3d1320", "faceted"),
        "Badee Al Oud Oud For Glory": ("#c5a059", "#eed8a3", "#121316", "faceted"),
        "Badee Al Oud Sublime": ("#a6212b", "#f79ca3", "#210305", "faceted"),
        "Badee Al Oud Honor & Glory": ("#dfc585", "#ffffff", "#2c2415", "faceted"),
        "Badee Al Oud Amethyst": ("#6f3b7d", "#d8a4e6", "#19081e", "faceted"),
        "His Confession": ("#9e6f3b", "#eec798", "#1c1208", "classic"),
        "Victoria": ("#d88195", "#fde6ec", "#33131c", "curve"),
        "The Kingdom Men": ("#385a7c", "#b6d7fa", "#0c1724", "tall_luxury"),
        "Liam Grey": ("#757d87", "#e1e4e8", "#181c21", "tall_luxury"),
        "Asad Zanzibar": ("#2b577a", "#b5dbfa", "#091724", "cylinder"),
        "Asad Bourbon": ("#a45e2a", "#f3b98c", "#1c0d04", "cylinder"),
        "Atheeri": ("#c5a059", "#ffefa8", "#1e1b13", "classic"),
        "Art Of Universe": ("#396b6b", "#a6dede", "#0a1919", "sculpted"),
        "Art Of Nature II": ("#436340", "#b2d6af", "#0e1a0d", "sculpted"),
        "Nebras": ("#c43d4d", "#f8b6bf", "#2d080e", "sculpted"),
        "Vintage Radio": ("#634766", "#d9b8dc", "#180d19", "sculpted"),
        "Affection": ("#8aa374", "#d8ebc7", "#17240f", "curve"),
        "Eternal Oud": ("#c88a35", "#fde1a5", "#1c1103", "crystal"),
        "Fakhar Black": ("#c5a059", "#f3e2ba", "#0d0f12", "shield"),
        "Fakhar Rose": ("#df92a5", "#fde2ea", "#2d0c15", "shield"),
        "Qaed Al Fursan": ("#c5a059", "#ffefa8", "#111215", "heavy_square"),
        "Qaed Al Fursan Unlimited": ("#d9d3c5", "#ffffff", "#211f1c", "heavy_square"),
        "Ameer Al Oudh Intense Oud": ("#b86d2f", "#f8c59c", "#1c0e04", "classic"),
        "Maahir Black Edition": ("#2b2b2b", "#c5a059", "#090a0c", "equine"),
        "Maahir Legacy": ("#8f9ca6", "#d9e2e8", "#111518", "equine"),
        "Najdia": ("#357388", "#a6ddef", "#08151a", "classic"),
        "Mayar": ("#df6f88", "#fcdde4", "#2c0912", "curve"),
        "Mayar Natural Intense": ("#387d55", "#bce9cf", "#0b1c11", "curve"),
        "Bright Peach": ("#e6673b", "#fed2c2", "#2b0d04", "minimalist_niche"),
        "Woody Oud": ("#3b3630", "#c5a059", "#11100e", "minimalist_niche"),
        "Tobacco Touch": ("#824e27", "#f3c7a3", "#1b0d04", "minimalist_niche"),
        "Fabulo Intense": ("#262626", "#dedede", "#0d0d0d", "minimalist_niche"),
        "Porto Neroli": ("#1c7987", "#b3ecf4", "#05181b", "minimalist_niche"),
        "Lovely Chèrie": ("#8e1f32", "#f8a2b0", "#1e0408", "minimalist_niche"),
        "Baroque Rouge 540": ("#b22222", "#fbc3c3", "#240404", "heavy_square"),
        "Delilah Pour Femme": ("#e39bb0", "#fde5ec", "#330e19", "curve"),
        "Jean Lowe Immortal": ("#c5a059", "#ffefa8", "#14161a", "tall_luxury"),
        "Jean Lowe Nouveau": ("#7c4021", "#eab598", "#1c0b03", "tall_luxury"),
        "Jean Lowe Ombre": ("#2e2520", "#c5a059", "#0e0906", "tall_luxury")
    }

    count = 0
    for p in products:
        name = p["name"]
        rel_img = p["image_path"] # e.g. static/images/products/khamrah.svg
        
        # Color match or fallback by brand & gender
        if name in palette_map:
            accent, highlight, bg_color, shape = palette_map[name]
        else:
            if p["brand"] == "Maison Alhambra":
                accent, highlight, bg_color, shape = ("#cca059", "#faebc9", "#151518", "minimalist_niche")
            elif p["brand"] == "Lattafa Pride":
                accent, highlight, bg_color, shape = ("#d4af37", "#ffefa8", "#101918", "faceted")
            elif p["gender"] == "Women":
                accent, highlight, bg_color, shape = ("#df8198", "#fde1e8", "#241016", "curve")
            elif p["gender"] == "Men":
                accent, highlight, bg_color, shape = ("#c5a059", "#f5e6c3", "#111317", "classic")
            else:
                accent, highlight, bg_color, shape = ("#cfa049", "#ffe8b3", "#171513", "classic")

        family = p.get("fragrance_family", "Arabian Luxury Perfume")
        conc = p.get("concentration", "Eau de Parfum (EDP)")
        size = p.get("bottle_size", "100ml")
        brand = p.get("brand", "Lattafa Perfumes")

        bottle_svg = render_flacon_svg(name, brand, family, conc, size, accent, highlight, bg_color, shape)
        write_dual(rel_img, bottle_svg)
        count += 1

    print(f"Generated {count} high-craft luxury perfume flacon SVG assets.")

def main():
    generate_branding()
    generate_hero()
    generate_collections()
    generate_categories()
    generate_perfume_bottles()
    print("All perfume visual assets successfully created!")

if __name__ == "__main__":
    main()
