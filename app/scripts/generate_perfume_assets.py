"""
generate_perfume_assets.py
Generates high-end luxury vector SVG assets for:
1. Branding & Logos (app/static/images/branding/)
2. Hero Banners (app/static/images/hero/)
3. Collections (app/static/images/collections/)
4. Categories (app/static/images/categories/)
5. 100 Individual Perfume Product Flacons (app/static/images/products/)
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
    "app/static/images/uploads",
    "static/images/branding",
    "static/images/hero",
    "static/images/collections",
    "static/images/categories",
    "static/images/products",
]

for d in DIRS:
    os.makedirs(d, exist_ok=True)

def write_dual(rel_path, content):
    """Writes asset to both app/static and root static folders."""
    p1 = os.path.join("app", rel_path)
    p2 = rel_path
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
  <!-- Luxury Background -->
  <rect width="1920" height="800" fill="url(#bgG)"/>
  
  <!-- Subtle Islamic Geometric Lattice Overlay -->
  <g stroke="url(#goldH)" stroke-width="0.5" opacity="0.08">
    <pattern id="lattice" width="80" height="80" patternUnits="userSpaceOnUse">
      <path d="M40 0 L80 40 L40 80 L0 40 Z M40 10 L70 40 L40 70 L10 40 Z"/>
    </pattern>
    <rect width="1920" height="800" fill="url(#lattice)"/>
  </g>

  <!-- Ambient Glow Behind Flacon -->
  <circle cx="1380" cy="400" r="280" fill="#c5a059" opacity="0.18" filter="url(#heroGlow)"/>

  <!-- Luxury Perfume Flacon Showcase (Khamrah Crystal Bottle Art) -->
  <g transform="translate(1180, 160)">
    <!-- Shadow -->
    <ellipse cx="200" cy="520" rx="180" ry="32" fill="#000000" opacity="0.6"/>
    
    <!-- Crystal Heavy Base -->
    <rect x="70" y="180" width="260" height="310" rx="16" fill="url(#amberG)" stroke="url(#goldH)" stroke-width="4"/>
    
    <!-- Cut Crystal Facets -->
    <g fill="none" stroke="#ffe8a8" stroke-width="1.5" opacity="0.45">
      <line x1="70" y1="230" x2="330" y2="230"/>
      <line x1="70" y1="290" x2="330" y2="290"/>
      <line x1="70" y1="350" x2="330" y2="350"/>
      <line x1="70" y1="410" x2="330" y2="410"/>
      <line x1="120" y1="180" x2="120" y2="490"/>
      <line x1="200" y1="180" x2="200" y2="490"/>
      <line x1="280" y1="180" x2="280" y2="490"/>
      <!-- Diagonal cuts -->
      <line x1="70" y1="180" x2="330" y2="440"/>
      <line x1="330" y1="180" x2="70" y2="440"/>
    </g>

    <!-- Liquid Hue Level -->
    <rect x="85" y="220" width="230" height="255" rx="8" fill="#e59124" opacity="0.5"/>

    <!-- Gold Crest Plate -->
    <rect x="110" y="270" width="180" height="120" rx="6" fill="#18171c" stroke="url(#goldH)" stroke-width="2"/>
    <circle cx="200" cy="305" r="14" fill="none" stroke="url(#goldH)" stroke-width="1.2"/>
    <path d="M200 295 L203 303 L211 305 L203 307 L200 315 L197 307 L189 305 L197 303 Z" fill="url(#goldH)"/>
    <text x="200" y="340" font-family="'Cinzel', serif" font-size="20" font-weight="700" letter-spacing="3" fill="url(#goldH)" text-anchor="middle">KHAMRAH</text>
    <text x="200" y="360" font-family="'Inter', sans-serif" font-size="8" letter-spacing="3" fill="#cfc7b8" text-anchor="middle">EAU DE PARFUM</text>
    <text x="200" y="374" font-family="'Inter', sans-serif" font-size="7" letter-spacing="4" fill="#a49377" text-anchor="middle">LATTAFA</text>

    <!-- Golden Collar & Crystal Stopper -->
    <rect x="150" y="145" width="100" height="35" rx="4" fill="url(#goldH)"/>
    <!-- Crystal Crown Stopper -->
    <path d="M110 50 L290 50 L260 145 L140 145 Z" fill="#2b2724" stroke="url(#goldH)" stroke-width="3" opacity="0.95"/>
    <line x1="160" y1="50" x2="175" y2="145" stroke="#ffe8a8" stroke-width="1" opacity="0.6"/>
    <line x1="200" y1="50" x2="200" y2="145" stroke="#ffe8a8" stroke-width="1.5" opacity="0.8"/>
    <line x1="240" y1="50" x2="225" y2="145" stroke="#ffe8a8" stroke-width="1" opacity="0.6"/>
  </g>
</svg>"""
    write_dual("static/images/hero/perfume_hero.svg", hero_svg)
    print("Hero section banner generated.")

# ── 3. Collection Banners ────────────────────────────────────────────────────
def generate_collections():
    cols = [
        ("yara_collection.svg", "YARA COLLECTION", "Sweet Gourmand & Ethereal Florals", "#f8d5db", "#b43d5f", "#441824"),
        ("asad_collection.svg", "ASAD COLLECTION", "Masculine Power & Noble Woods", "#2c2d33", "#d4af37", "#111215"),
        ("khamrah_collection.svg", "KHAMRAH COLLECTION", "Golden Spices & Date Gourmand", "#d68729", "#ffd685", "#211406"),
        ("badee_al_oud.svg", "BADEE AL OUD", "Royal Agarwood & Opulent Blends", "#181a20", "#c5a059", "#090a0d"),
        ("lattafa_pride.svg", "LATTAFA PRIDE", "Artisanal Haute Parfumerie", "#162822", "#d4af37", "#09120e"),
        ("maison_alhambra.svg", "MAISON ALHAMBRA", "Parisian Chic with Arabian Depth", "#2a221f", "#e6c387", "#120e0d"),
        ("mainline_classics.svg", "MAINLINE CLASSICS", "Iconic Arabian Best Sellers", "#281e28", "#e3b375", "#130913")
    ]
    for filename, title, subtitle, c1, c2, bg in cols:
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
  <defs>
    <radialGradient id="g_{filename[:4]}" cx="50%" cy="40%" r="70%">
      <stop offset="0%" stop-color="{c1}" stop-opacity="0.3"/>
      <stop offset="50%" stop-color="{c2}" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="{bg}"/>
    </radialGradient>
    <linearGradient id="textG" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fff1d6"/>
      <stop offset="60%" stop-color="{c2}"/>
      <stop offset="100%" stop-color="#8a6927"/>
    </linearGradient>
  </defs>
  <rect width="800" height="600" fill="{bg}"/>
  <rect width="800" height="600" fill="url(#g_{filename[:4]})"/>
  <rect x="25" y="25" width="750" height="550" fill="none" stroke="{c2}" stroke-width="1.5" opacity="0.35"/>
  <rect x="35" y="35" width="730" height="530" fill="none" stroke="{c2}" stroke-width="0.75" stroke-dasharray="6,4" opacity="0.25"/>
  
  <!-- Silhouette Flacon Art -->
  <g transform="translate(400, 240) scale(0.9)" opacity="0.85">
    <ellipse cx="0" cy="180" rx="90" ry="18" fill="#000" opacity="0.4"/>
    <rect x="-65" y="-30" width="130" height="190" rx="16" fill="{bg}" stroke="{c2}" stroke-width="2.5"/>
    <rect x="-30" y="-70" width="60" height="40" rx="6" fill="{c2}"/>
    <circle cx="0" cy="65" r="34" fill="none" stroke="{c2}" stroke-width="1.5"/>
    <path d="M0 45 L6 59 L20 65 L6 71 L0 85 L-6 71 L-20 65 L-6 59 Z" fill="{c2}"/>
  </g>

  <!-- Typography -->
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

# ── 5. 100 Individual Perfume Bottle Images ──────────────────────────────────
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
        "Victoria": ("#d88195", "#fde6ec", "#33131c", "classic"),
        "The Kingdom Men": ("#385a7c", "#b6d7fa", "#0c1724", "classic"),
        "Liam Grey": ("#757d87", "#e1e4e8", "#181c21", "classic"),
        "Asad Zanzibar": ("#2b577a", "#b5dbfa", "#091724", "cylinder"),
        "Asad Bourbon": ("#a45e2a", "#f3b98c", "#1c0d04", "cylinder"),
        "Atheeri": ("#c5a059", "#ffefa8", "#1e1b13", "classic"),
        "Art Of Universe": ("#396b6b", "#a6dede", "#0a1919", "sculpted"),
        "Art Of Nature II": ("#436340", "#b2d6af", "#0e1a0d", "sculpted"),
        "Nebras": ("#c43d4d", "#f8b6bf", "#2d080e", "sculpted"),
        "Vintage Radio": ("#634766", "#d9b8dc", "#180d19", "sculpted"),
        "Affection": ("#8aa374", "#d8ebc7", "#17240f", "sculpted"),
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
        "Bright Peach": ("#e6673b", "#fed2c2", "#2b0d04", "minimalist_niche"),
        "Woody Oud": ("#3b3630", "#c5a059", "#11100e", "minimalist_niche"),
        "Tobacco Touch": ("#824e27", "#f3c7a3", "#1b0d04", "minimalist_niche"),
        "Fabulo Intense": ("#262626", "#dedede", "#0d0d0d", "minimalist_niche"),
        "Porto Neroli": ("#1c7987", "#b3ecf4", "#05181b", "minimalist_niche"),
        "Lovely Chèrie": ("#8e1f32", "#f8a2b0", "#1e0408", "minimalist_niche"),
        "Baroque Rouge 540": ("#b22222", "#fbc3c3", "#240404", "heavy_square"),
        "Delilah Pour Femme": ("#e39bb0", "#fde5ec", "#330e19", "frosted_niche"),
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
                accent, highlight, bg_color, shape = ("#d4af37", "#ffefa8", "#101918", "sculpted")
            elif p["gender"] == "Women":
                accent, highlight, bg_color, shape = ("#df8198", "#fde1e8", "#241016", "curve")
            elif p["gender"] == "Men":
                accent, highlight, bg_color, shape = ("#c5a059", "#f5e6c3", "#111317", "classic")
            else:
                accent, highlight, bg_color, shape = ("#cfa049", "#ffe8b3", "#171513", "classic")

        # Escaped text
        safe_name = xml.sax.saxutils.escape(name.upper())
        safe_brand = xml.sax.saxutils.escape(p["brand"].upper())
        safe_family = xml.sax.saxutils.escape(p["fragrance_family"].upper())
        safe_conc = xml.sax.saxutils.escape(p["concentration"])
        safe_size = xml.sax.saxutils.escape(p["bottle_size"])

        bottle_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 750" width="600" height="750">
  <defs>
    <radialGradient id="ambG" cx="50%" cy="45%" r="65%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.25"/>
      <stop offset="70%" stop-color="{bg_color}" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#0a0b0d"/>
    </radialGradient>
    <linearGradient id="metalG" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{highlight}"/>
      <stop offset="50%" stop-color="{accent}"/>
      <stop offset="100%" stop-color="#4d3509"/>
    </linearGradient>
    <linearGradient id="bodyG" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{bg_color}"/>
      <stop offset="25%" stop-color="{accent}" stop-opacity="0.8"/>
      <stop offset="50%" stop-color="{highlight}" stop-opacity="0.95"/>
      <stop offset="75%" stop-color="{accent}" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="{bg_color}"/>
    </linearGradient>
    <filter id="dropShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="16" stdDeviation="20" flood-color="#000000" flood-opacity="0.75"/>
    </filter>
  </defs>

  <!-- Background Canvas -->
  <rect width="600" height="750" fill="url(#ambG)"/>
  
  <!-- Subtle Framing -->
  <rect x="25" y="25" width="550" height="700" fill="none" stroke="{accent}" stroke-width="0.75" opacity="0.3"/>
  <rect x="35" y="35" width="530" height="680" fill="none" stroke="{accent}" stroke-width="0.5" stroke-dasharray="4,4" opacity="0.2"/>

  <!-- Bottle Silhouette & Construction -->
  <g transform="translate(300, 360)" filter="url(#dropShadow)">
    <!-- Flacon Pedestal / Shadow -->
    <ellipse cx="0" cy="225" rx="140" ry="24" fill="#000000" opacity="0.6"/>

    <!-- Bottle Main Body -->
    <rect x="-105" y="-120" width="210" height="320" rx="20" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="3"/>

    <!-- Inner Plate / Crest -->
    <rect x="-85" y="-60" width="170" height="200" rx="8" fill="#14151a" stroke="url(#metalG)" stroke-width="1.8"/>
    <circle cx="0" cy="-20" r="18" fill="none" stroke="url(#metalG)" stroke-width="1.2"/>
    <polygon points="0,-30 4,-22 12,-20 4,-18 0,-10 -4,-18 -12,-20 -4,-22" fill="url(#metalG)"/>
    
    <!-- Product Label Typography -->
    <text x="0" y="25" font-family="'Cinzel', 'Playfair Display', serif" font-size="16" font-weight="700" letter-spacing="2" fill="url(#metalG)" text-anchor="middle">{safe_name}</text>
    <text x="0" y="52" font-family="'Inter', sans-serif" font-size="9" font-weight="600" letter-spacing="3" fill="#dfd8cb" text-anchor="middle">{safe_brand}</text>
    <line x1="-50" y1="68" x2="50" y2="68" stroke="url(#metalG)" stroke-width="0.8" opacity="0.6"/>
    <text x="0" y="88" font-family="'Inter', sans-serif" font-size="8" letter-spacing="2" fill="#aea28e" text-anchor="middle">{safe_conc}</text>
    <text x="0" y="108" font-family="'Inter', sans-serif" font-size="8" letter-spacing="3" fill="url(#metalG)" text-anchor="middle">{safe_size}</text>

    <!-- Metallic Neck / Collar -->
    <rect x="-42" y="-155" width="84" height="35" rx="4" fill="url(#metalG)"/>
    <line x1="-42" y1="-138" x2="42" y2="-138" stroke="#121316" stroke-width="1.5"/>

    <!-- Regal Cap / Stopper -->
    <rect x="-55" y="-235" width="110" height="80" rx="12" fill="url(#metalG)" stroke="{highlight}" stroke-width="1.5"/>
    <polygon points="0,-215 5,-195 18,-190 5,-185 0,-165 -5,-185 -18,-190 -5,-195" fill="#15161a"/>
  </g>

  <!-- Bottom Brand Subtitle -->
  <text x="300" y="700" font-family="'Inter', sans-serif" font-size="10" font-weight="500" letter-spacing="5" fill="{accent}" opacity="0.8" text-anchor="middle">{safe_family}</text>
</svg>"""
        write_dual(rel_img, bottle_svg)
        count += 1

    print(f"Generated {count} luxury perfume flacon SVG assets.")

def main():
    generate_branding()
    generate_hero()
    generate_collections()
    generate_categories()
    generate_perfume_bottles()
    print("All perfume visual assets successfully created!")

if __name__ == "__main__":
    main()
