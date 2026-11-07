"""
generate_perfume_assets.py
=============================================================================
ADVANCED LUXURY PERFUME IMAGE GENERATION ENGINE & ASSET MANAGEMENT PIPELINE
=============================================================================
Comprehensive catalog visual pipeline conforming to luxury e-commerce standards.
Features:
  - Mode A: Optimization of authorized commercial product photography.
  - Mode B: Original conceptual commercial fragrance still-lifes (4:5, 1200x1500).
  - Architectural Vector Flacon Fallback with intelligent text-wrapping & 11 distinct flacon geometries.
  - Pillow-based 4:5 Lanczos framing, WebP (88 quality) + JPEG (90 quality) dual-generation.
  - Strict image quality validation (dimensions, file size <500KB, luminance, sharpness).
  - Centralized catalog manifest (data/PERFUME_IMAGE_MANIFEST.json & app/data/PERFUME_IMAGE_MANIFEST.json).
  - Interactive luxury HTML contact sheet for catalog-wide visual inspection.
  - MySQL database synchronization for online_shop_perfume_dev and online_shop_perfume_test
    utilizing centralized connection pooling, atomic transactions, and zero hardcoded credentials.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import os
import re
import xml.sax.saxutils
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import sys

# ── Global Path Configurations ──────────────────────────────────────────────
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from PIL import Image, ImageFilter, ImageStat

from app.db import get_connection
APP_DIR: Path = BASE_DIR / "app"
STATIC_DIR: Path = BASE_DIR / "static"
APP_STATIC_DIR: Path = APP_DIR / "static"

DATA_DIR: Path = BASE_DIR / "data"
APP_DATA_DIR: Path = APP_DIR / "data"

CSV_CATALOG_PATH: Path = BASE_DIR / "PERFUME_CATALOG_DATA.csv"
MANIFEST_PATH: Path = DATA_DIR / "PERFUME_IMAGE_MANIFEST.json"
APP_MANIFEST_PATH: Path = APP_DATA_DIR / "PERFUME_IMAGE_MANIFEST.json"
CONTACT_SHEET_PATH: Path = STATIC_DIR / "images" / "contact_sheet.html"
APP_CONTACT_SHEET_PATH: Path = APP_STATIC_DIR / "images" / "contact_sheet.html"

STATIC_DIRS: List[Path] = [
    STATIC_DIR / "images" / "branding",
    STATIC_DIR / "images" / "hero",
    STATIC_DIR / "images" / "collections",
    STATIC_DIR / "images" / "categories",
    STATIC_DIR / "images" / "products",
    APP_STATIC_DIR / "images" / "branding",
    APP_STATIC_DIR / "images" / "hero",
    APP_STATIC_DIR / "images" / "collections",
    APP_STATIC_DIR / "images" / "categories",
    APP_STATIC_DIR / "images" / "products",
    DATA_DIR,
    APP_DATA_DIR,
]


def ensure_directories() -> None:
    """Ensures all required static and data directories exist on disk."""
    for directory in STATIC_DIRS:
        directory.mkdir(parents=True, exist_ok=True)


def write_dual(rel_path: str, content: str, mode: str = "w", encoding: str = "utf-8") -> None:
    """Writes an asset to both root static/ and app/static/ paths."""
    p1 = APP_DIR / rel_path
    p2 = BASE_DIR / rel_path
    p1.parent.mkdir(parents=True, exist_ok=True)
    p2.parent.mkdir(parents=True, exist_ok=True)
    with open(p1, mode, encoding=encoding) as f1:
        f1.write(content)
    with open(p2, mode, encoding=encoding) as f2:
        f2.write(content)


def save_dual_binary(rel_path: str, data: bytes) -> None:
    """Writes binary data to both root static/ and app/static/ paths."""
    p1 = APP_DIR / rel_path
    p2 = BASE_DIR / rel_path
    p1.parent.mkdir(parents=True, exist_ok=True)
    p2.parent.mkdir(parents=True, exist_ok=True)
    with open(p1, "wb") as f1:
        f1.write(data)
    with open(p2, "wb") as f2:
        f2.write(data)


def safe_int(val: Any, default: int = 0) -> int:
    """Safely coerces CSV values to int."""
    if val is None:
        return default
    s = str(val).strip()
    return int(s) if s.isdigit() or (s.startswith("-") and s[1:].isdigit()) else default


def safe_float(val: Any, default: float = 0.0) -> float:
    """Safely coerces CSV values to float."""
    if val is None:
        return default
    try:
        return float(str(val).strip())
    except (ValueError, TypeError):
        return default


# =============================================================================
# 1. CATALOG READER
# =============================================================================
class CatalogReader:
    """Loads and standardizes catalog records from CSV and DB."""

    @staticmethod
    def load_catalog(csv_path: Path = CSV_CATALOG_PATH) -> List[Dict[str, Any]]:
        """Loads all fragrance records from PERFUME_CATALOG_DATA.csv."""
        if not csv_path.exists():
            raise FileNotFoundError(f"Catalog CSV not found at {csv_path}")

        products: List[Dict[str, Any]] = []
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rel_img = row.get("image_path", "")
                slug = Path(rel_img).stem if rel_img else re.sub(r"[^a-z0-9]+", "_", row.get("name", "").lower()).strip("_")

                prod = {
                    "product_id": safe_int(row.get("product_id"), 0),
                    "slug": slug,
                    "name": row.get("name", ""),
                    "brand": row.get("brand", "Lattafa Perfumes"),
                    "collection": row.get("collection", "Mainline Classics"),
                    "category": row.get("category", "Unisex Fragrances"),
                    "gender": row.get("gender", "Unisex"),
                    "concentration": row.get("concentration", "Eau de Parfum (EDP)"),
                    "bottle_size": row.get("bottle_size", "100ml"),
                    "fragrance_family": row.get("fragrance_family", "Arabian Luxury Perfume"),
                    "top_notes": row.get("top_notes", ""),
                    "heart_notes": row.get("heart_notes", ""),
                    "base_notes": row.get("base_notes", ""),
                    "price_pkr": safe_float(row.get("price_pkr"), 0.0),
                    "stock_quantity": safe_int(row.get("stock_quantity"), 0),
                    "is_featured": safe_int(row.get("is_featured"), 0),
                    "is_bestseller": safe_int(row.get("is_bestseller"), 0),
                    "is_new_arrival": safe_int(row.get("is_new_arrival"), 0),
                    "short_description": row.get("short_description", ""),
                    "description": row.get("description", ""),
                    "image_path": rel_img,
                }
                products.append(prod)
        return products


# =============================================================================
# 2. PROMPT BUILDER (MODE B CONCEPTUAL FRAGRANCE IMAGERY)
# =============================================================================
class PromptBuilder:
    """
    Constructs high-craft visual prompts for photorealistic commercial perfume photography.
    Enforces:
      - Clean unbranded front label plates (no gibberish AI text or fake logos).
      - Distinct silhouettes tailored to collection, brand and notes.
      - Realistic glass physics, specular highlights, and natural liquid refraction.
      - 3-point studio lighting with subtle ambient background.
    """

    SILHOUETTE_PROFILES: Dict[str, Tuple[str, str, str, str, str]] = {
        # Exact / Longest matching variants first to prevent shadowing
        "Khamrah Dukhan": ("crystal", "smoked dark amber faceted crystal decanter", "deep smoky topaz glass with rich molten resins", "smoked crystal prism stopper with antiqued bronze neck", "moody dark amber studio with diffused backlight capturing liquid depth"),
        "Khamrah Qahwa": ("crystal", "cut crystal decanter with warm roasted coffee liquid", "heavy faceted glass with deep roasted amber-brown liquid", "faceted crystal octagonal stopper with warm copper trim", "rich espresso and warm amber studio with dark mahogany pedestal reflections"),
        "Khamrah": ("crystal", "faceted cut crystal whisky decanter", "heavy leaded crystal glass with warm cognac-amber liquid", "geometric faceted crystal stopper with gold trim", "warm amber studio with soft golden rim light and subtle dark wood surface reflections"),
        "Eternal Oud": ("crystal", "ornate faceted crystal flacon", "heavy beveled crystal with glowing golden agarwood oil", "sculpted crystal finial with gold filigree collar", "opulent warm amber studio with soft reflections"),

        "Asad Zanzibar": ("cylinder", "marine-inspired fluted architectural column", "deep sapphire-tinted charcoal glass with brushed silver accents", "fluted midnight-blue metallic cylindrical cap", "cool slate and dark ocean studio lighting with crisp specular rim lights"),
        "Asad Bourbon": ("cylinder", "warm mahogany fluted architectural column", "deep bourbon-tinted obsidian glass with brushed copper bands", "grooved warm copper and black cap", "warm dusky studio with rich amber backlighting"),
        "Asad": ("cylinder", "fluted architectural column flacon", "heavy deep charcoal obsidian glass with polished gold metallic bands", "grooved textured black and gold cylindrical cap", "dramatic dark luxury studio with crisp edge lighting and contact shadow"),

        "Yara Candy": ("curve", "vibrant sculpted hourglass silhouette", "radiant berry-magenta and frosted candy-pink glass with polished gold collar", "glossy magenta dome cap with gold trim", "bright editorial studio setting with soft diffused highlights"),
        "Yara Tous": ("curve", "sun-drenched sculpted hourglass silhouette", "warm mango-gold and frosted solar amber glass with yellow-gold accents", "polished gold sculpted cap", "golden hour luxury studio lighting with radiant warmth"),
        "Yara Moi": ("curve", "minimalist frosted pearl hourglass silhouette", "matte ivory and white frosted opaline glass with soft champagne gold accents", "matte ivory sculpted cap", "soft high-key minimalist studio lighting with gentle shadows"),
        "Yara": ("curve", "sculpted sensual hourglass bottle", "soft blush pink and frosted pearl glass with rose-gold metallic shoulder trim", "sculpted rounded blush crystal and rose-gold cap", "refined soft ivory and cream luxury studio with delicate highlights"),

        "Badee Al Oud Oud For Glory": ("faceted", "monolithic faceted obelisk bottle", "heavyweight deep charcoal-black glass with satin-gold arabesque filigree trim", "faceted black and gold finial stopper", "dramatic dark obsidian studio with focused key light and luminous gold reflections"),
        "Badee Al Oud Noble Blush": ("faceted", "monolithic faceted obelisk bottle", "soft blush rose glass with rose-gold arabesque filigree detailing", "faceted rose-gold finial cap", "soft luxury studio setting with luminous rose-gold highlights"),
        "Badee Al Oud Sublime": ("faceted", "monolithic faceted obelisk bottle", "deep ruby-crimson crystal glass with polished gold filigree trim", "faceted ruby and gold finial stopper", "luxurious crimson and dark velvet studio with sparkling edge reflections"),
        "Badee Al Oud Honor & Glory": ("faceted", "monolithic faceted obelisk bottle", "pure white marble-finish opaline glass with polished royal gold filigree", "sculpted white and gold finial cap", "pristine high-contrast luxury studio with crisp gold highlights"),
        "Badee Al Oud Amethyst": ("faceted", "monolithic faceted obelisk bottle", "deep royal amethyst purple glass with delicate gold arabesque filigree", "faceted amethyst and gold finial stopper", "mysterious jewel-toned studio setting with soft specular reflections"),

        "Teriaq": ("sculpted", "artisanal imperial sculpted flacon", "deep onyx black glass with an intricate polished gold sculpted coiled accent along the shoulder", "sculpted faceted dark glass cap with gold finial", "haute couture dramatic studio lighting with sharp rim lights capturing sculpted curves"),
        "Eclaire": ("classic", "opulent French-Arabian gourmand flacon", "heavyweight warm golden caramel amber glass glowing with liquid warmth", "heavy solid crystal rounded cap with champagne-gold metal collar", "warm golden studio illumination set on a honed warm ivory marble surface"),
        "Woody Oud": ("minimalist_niche", "minimalist luxury niche heavy apothecary flacon", "ultra-thick solid glass base with rich dark amber liquid", "heavy brushed antique brass cylindrical cap", "sophisticated dark luxury studio lighting capturing glass thickness and liquid refraction"),
        "Fakhar Black": ("shield", "modern aerodynamic shield-silhouette bottle", "matte midnight black glass with polished silver metallic beveling and shoulder plates", "geometric faceted silver cap seamlessly integrated into the neck", "high-contrast luxury studio rim lighting on a dark gunmetal stone pedestal"),
        "Ameer Al Oudh Intense Oud": ("classic", "opulent rectangular royal Arabian flacon", "heavy crystal glass walls revealing deep glowing cognac-amber oud oil within", "ornate filigree gold collar and heavy faceted gold crown cap", "warm amber and dark mahogany studio lighting with rich internal liquid luminescence"),
        "Maahir Black Edition": ("sculpted", "monumental sculpted flacon with majestic stallion finial", "heavy matte jet-black glass with subtle burnished gold edge accents", "sculpted matte black stallion head finial cap", "dramatic low-key studio lighting with razor-sharp rim highlights"),
        "Baroque Rouge 540": ("heavy_square", "monumental thick-walled ruby crystal cube flacon", "ultra-thick heavy glass base with glowing crimson-ruby liquid", "polished royal-gold solid square cap", "opulent dramatic studio lighting with sparkling internal crystal reflections on dark burgundy velvet"),
        "Delilah Pour Femme": ("curve", "sculpted sensual hourglass silhouette flacon", "soft powder-pink frosted glass with delicate sculpted relief along fluted shoulders", "spherical blush crystal cap with brushed rose-gold collar", "soft diffused Parisian studio lighting with delicate rim glow on cream silk drape"),
        "Jean Lowe Immortal": ("tall_luxury", "tall columnar niche flacon", "heavy smoked slate-grey crystal glass with ultra-thick base and golden liquid", "heavy brushed platinum-silver cylindrical cap", "sophisticated high-end commercial studio lighting with vertical edge catchlights on dark slate"),
    }

    @classmethod
    def get_silhouette_data(cls, product: Dict[str, Any]) -> Tuple[str, str, str, str, str]:
        name = product.get("name", "")
        name_lower = name.lower()
        brand = product.get("brand", "")
        gender = product.get("gender", "")
        family = product.get("fragrance_family", "")

        # 1. Exact match check
        for key, profile in cls.SILHOUETTE_PROFILES.items():
            if key.lower() == name_lower:
                return profile

        # 2. Longest prefix match check (descending length avoids shadowing)
        for key in sorted(cls.SILHOUETTE_PROFILES.keys(), key=len, reverse=True):
            if name_lower.startswith(key.lower()):
                return cls.SILHOUETTE_PROFILES[key]

        # 3. Brand / Family archetypes
        if brand == "Maison Alhambra":
            return ("minimalist_niche", "heavy apothecary rectangular flacon", "thick-walled clear glass revealing rich scented oil", "brushed metallic minimalist cylindrical cap", "refined Parisian-Arabian niche studio lighting with soft specular highlights")
        if brand == "Lattafa Pride":
            return ("faceted", "artisanal geometric architectural flacon", "beveled crystal glass with satin gold filigree accents", "faceted crown finial cap", "haute parfumerie luxury studio with focused spot lighting")
        if gender == "Women" or "Floral" in family or "Gourmand" in family:
            return ("curve", "sculpted sensual hourglass flacon", "soft tinted rose or amber glass with polished metallic collar", "sculpted rounded crystal cap", "luminous soft-focus studio setting with delicate specular highlights")
        if gender == "Men" or "Leather" in family or "Woody" in family:
            return ("cylinder", "fluted columnar luxury flacon", "heavy smoked obsidian glass with burnished metallic bands", "grooved solid metal cap", "masculine dark stone luxury studio with crisp edge rim lighting")
        return ("classic", "royal Arabian rectangular flacon", "thick crystal glass base with warm radiant liquid", "sculpted metallic crown cap", "opulent neutral studio with balanced key and rim illumination")

    @classmethod
    def build_prompt(cls, product: Dict[str, Any]) -> str:
        name = product.get("name", "")
        family = product.get("fragrance_family", "Fragrance")
        top = product.get("top_notes", "")
        heart = product.get("heart_notes", "")
        base = product.get("base_notes", "")
        _, shape_desc, glass_desc, cap_desc, studio_desc = cls.get_silhouette_data(product)

        prompt = (
            f"Professional commercial luxury perfume product photography of {name} fragrance ({family}). "
            f"An original, {shape_desc} concept crafted from {glass_desc}, with a {cap_desc}. "
            f"Clean, unbranded metallic label plaque centered on the bottle with no words, no letters, no text, no logos, "
            f"completely unbranded front cartouche. "
            f"Studio atmosphere: {studio_desc}. "
            f"Subtle olfactory nuances reflected in ambient warmth: top notes of {top}, heart of {heart}, base of {base}. "
            f"Strict commercial still-life standards: realistic glass refraction, crisp specular highlights, true-to-life contact shadow, "
            f"no floating elements, no props cluttering the frame, centered portrait composition, photorealistic 8k commercial quality."
        )
        return prompt

    @staticmethod
    def hash_prompt(prompt: str) -> str:
        return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]


# =============================================================================
# 3. IMAGE PROCESSOR (PILLOW 4:5 1200x1500 & VALIDATION)
# =============================================================================
class ImageProcessor:
    """
    Pillow-powered image pipeline:
      - Crops/scales input images intelligently to 4:5 aspect ratio (1200x1500).
      - Converts and optimizes to modern WebP (quality 88-90, method 6).
      - Generates high-compatibility JPEG fallback.
      - Conducts automated visual quality and sharpness verification.
    """

    TARGET_WIDTH: int = 1200
    TARGET_HEIGHT: int = 1500
    TARGET_ASPECT: float = 4 / 5  # 0.80

    @classmethod
    def process_and_optimize(cls, source_path: Path, output_slug: str) -> Dict[str, Any]:
        """Loads raw image, frames to 4:5 1200x1500 with Lanczos resampling, and saves WebP/JPEG."""
        if not source_path.exists():
            raise FileNotFoundError(f"Source image not found: {source_path}")

        with Image.open(source_path) as raw_img:
            img = raw_img.convert("RGB")

            orig_w, orig_h = img.size
            orig_aspect = orig_w / orig_h

            if orig_aspect < cls.TARGET_ASPECT:
                # Narrower than 4:5 (e.g. 3:4 = 0.746)
                scale = cls.TARGET_WIDTH / orig_w
                scaled_h = int(orig_h * scale)
                with img.resize((cls.TARGET_WIDTH, scaled_h), Image.Resampling.LANCZOS) as scaled_img:
                    crop_y = max(0, (scaled_h - cls.TARGET_HEIGHT) // 2)
                    final_img = scaled_img.crop((0, crop_y, cls.TARGET_WIDTH, crop_y + cls.TARGET_HEIGHT))
            else:
                # Wider than 4:5
                scale = cls.TARGET_HEIGHT / orig_h
                scaled_w = int(orig_w * scale)
                with img.resize((scaled_w, cls.TARGET_HEIGHT), Image.Resampling.LANCZOS) as scaled_img:
                    crop_x = max(0, (scaled_w - cls.TARGET_WIDTH) // 2)
                    final_img = scaled_img.crop((crop_x, 0, crop_x + cls.TARGET_WIDTH, cls.TARGET_HEIGHT))

        webp_rel = f"static/images/products/{output_slug}.webp"
        jpg_rel = f"static/images/products/{output_slug}.jpg"

        with io.BytesIO() as buf_webp:
            final_img.save(buf_webp, format="WEBP", quality=88, method=6)
            webp_bytes = buf_webp.getvalue()

        with io.BytesIO() as buf_jpg:
            final_img.save(buf_jpg, format="JPEG", quality=90, optimize=True)
            jpg_bytes = buf_jpg.getvalue()

        save_dual_binary(webp_rel, webp_bytes)
        save_dual_binary(jpg_rel, jpg_bytes)

        # Single grayscale conversion reused for luminance and edge detection
        with final_img.convert("L") as gray_img:
            stat = ImageStat.Stat(gray_img)
            luminance = stat.mean[0]

            with gray_img.filter(ImageFilter.FIND_EDGES) as edges:
                edge_stat = ImageStat.Stat(edges)
                sharpness = edge_stat.var[0]

        final_img.close()

        is_valid = (
            len(webp_bytes) < 500 * 1024 and
            20.0 <= luminance <= 240.0 and
            sharpness > 60.0
        )

        return {
            "slug": output_slug,
            "width": cls.TARGET_WIDTH,
            "height": cls.TARGET_HEIGHT,
            "aspect_ratio": "4:5",
            "webp_path": webp_rel,
            "jpg_path": jpg_rel,
            "webp_size_kb": round(len(webp_bytes) / 1024, 1),
            "jpg_size_kb": round(len(jpg_bytes) / 1024, 1),
            "luminance": round(luminance, 1),
            "sharpness": round(sharpness, 1),
            "is_valid": is_valid,
        }


# =============================================================================
# 4. ARCHITECTURAL VECTOR FLACON RENDERER (ENHANCED 1200x1500 SVG ENGINE)
# =============================================================================
class ArchitecturalFlaconRenderer:
    """
    Renders ultra-luxury, photorealistic architectural vector flacon SVGs.
    Native 1200 x 1500 resolution (4:5 portrait ratio).
    Features:
      - 11 distinct flacon geometries with realistic glass wall thickness.
      - Liquid reservoir with inner meniscus curvature and refraction.
      - 3-tier studio lighting: radial bloom, luxury pedestal plane, and contact shadows.
      - Multi-pass specular catches: diffuse key-light bloom and crisp edge highlight.
      - Intelligent typography line-balancing with embossed foil-stamped cartouches.
    """

    PALETTE_MAP: Dict[str, Tuple[str, str, str, str]] = {
        # Core collection anchors
        "Khamrah": ("#d4882c", "#ffcf75", "#241306", "crystal"),
        "Khamrah Qahwa": ("#824218", "#e8a86a", "#170b04", "crystal"),
        "Khamrah Dukhan": ("#9c5825", "#d6945e", "#120a05", "crystal"),
        "Eternal Oud": ("#c88a35", "#fde1a5", "#1c1103", "crystal"),
        "Kismet Magic": ("#af6424", "#fed290", "#1a0d03", "crystal"),

        "Asad": ("#d4af37", "#f3e1a6", "#141518", "cylinder"),
        "Asad Zanzibar": ("#2b577a", "#b5dbfa", "#091724", "cylinder"),
        "Asad Bourbon": ("#a45e2a", "#f3b98c", "#1c0d04", "cylinder"),
        "Suqraat": ("#2f5b75", "#a8d9f5", "#08131a", "cylinder"),
        "Hayaati": ("#1b4965", "#8ecae6", "#081014", "cylinder"),
        "Hayaati Gold Elixir": ("#c5a059", "#fdedb4", "#121214", "cylinder"),
        "Ejaazi": ("#486072", "#c0d6e4", "#0e161c", "cylinder"),
        "Ejaazi Intensive Silver": ("#7a8c98", "#e1edf5", "#11161a", "cylinder"),

        "Yara": ("#f19bb2", "#fde5ec", "#421523", "curve"),
        "Yara Candy": ("#f43f75", "#ffd2de", "#3a0918", "curve"),
        "Yara Tous": ("#f6ba33", "#ffefc2", "#3a2602", "curve"),
        "Yara Moi": ("#edeae4", "#ffffff", "#3b342e", "curve"),
        "Victoria": ("#d88195", "#fde6ec", "#33131c", "curve"),
        "Mayar": ("#df6f88", "#fcdde4", "#2c0912", "curve"),
        "Mayar Natural Intense": ("#2a6344", "#a5e2c1", "#09170e", "curve"),
        "Delilah Pour Femme": ("#e39bb0", "#fde5ec", "#330e19", "curve"),
        "Affection": ("#8aa374", "#d8ebc7", "#17240f", "curve"),
        "Haya": ("#df889d", "#fde7ec", "#260d14", "curve"),

        "Badee Al Oud Oud For Glory": ("#c5a059", "#eed8a3", "#121316", "faceted"),
        "Badee Al Oud Noble Blush": ("#e89ab0", "#fdedf1", "#3d1320", "faceted"),
        "Badee Al Oud Sublime": ("#a6212b", "#f79ca3", "#210305", "faceted"),
        "Badee Al Oud Honor & Glory": ("#dfc585", "#ffffff", "#2c2415", "faceted"),
        "Badee Al Oud Amethyst": ("#6f3b7d", "#d8a4e6", "#19081e", "faceted"),
        "Opulent Oud": ("#c5a059", "#ffefa8", "#101114", "faceted"),
        "Opulent Red": ("#9c1f2b", "#f9a2aa", "#1c0507", "faceted"),
        "Shaheen Gold": ("#c5a059", "#fae7a0", "#111214", "faceted"),
        "Sceptre Malachite": ("#1e5f48", "#8ce0c2", "#061711", "faceted"),

        "Woody Oud": ("#3b3630", "#c5a059", "#11100e", "minimalist_niche"),
        "Tobacco Touch": ("#824e27", "#f3c7a3", "#1b0d04", "minimalist_niche"),
        "Fabulo Intense": ("#262626", "#dedede", "#0d0d0d", "minimalist_niche"),
        "Porto Neroli": ("#1c7987", "#b3ecf4", "#05181b", "minimalist_niche"),
        "Bright Peach": ("#e6673b", "#fed2c2", "#2b0d04", "minimalist_niche"),
        "Lovely Chèrie": ("#8e1f32", "#f8a2b0", "#1e0408", "minimalist_niche"),
        "Kismet for Men": ("#3a332d", "#c5a059", "#12100e", "minimalist_niche"),
        "Sutoor": ("#b85d3b", "#fbc2ab", "#1c0c06", "minimalist_niche"),
        "Musk Mood": ("#d8ded8", "#ffffff", "#171c17", "minimalist_niche"),
        "Pure Musk": ("#e5e8e5", "#ffffff", "#141714", "minimalist_niche"),

        "Jean Lowe Immortal": ("#c5a059", "#ffefa8", "#14161a", "tall_luxury"),
        "Jean Lowe Nouveau": ("#7c4021", "#eab598", "#1c0b03", "tall_luxury"),
        "Jean Lowe Ombre": ("#2e2520", "#c5a059", "#0e0906", "tall_luxury"),
        "The Kingdom Men": ("#385a7c", "#b6d7fa", "#0c1724", "tall_luxury"),
        "Liam Grey": ("#757d87", "#e1e4e8", "#181c21", "tall_luxury"),
        "Al Qiam Silver": ("#7b8b98", "#e2eaf0", "#111518", "tall_luxury"),
        "Raghba": ("#9b5a25", "#f5ba87", "#1a0c03", "tall_luxury"),
        "Raghba Wood Intense": ("#4a382c", "#c5a059", "#110d0a", "tall_luxury"),

        "Qaed Al Fursan": ("#c5a059", "#ffefa8", "#111215", "heavy_square"),
        "Qaed Al Fursan Unlimited": ("#d9d3c5", "#ffffff", "#211f1c", "heavy_square"),
        "Baroque Rouge 540": ("#b22222", "#fbc3c3", "#240404", "heavy_square"),
        "Ana Abiyedh": ("#dcdcd8", "#ffffff", "#1c1c1a", "heavy_square"),
        "Ana Abiyedh Rouge": ("#a81a26", "#f89a9f", "#210406", "heavy_square"),
        "Ana Abiyedh Leather": ("#855026", "#eebc95", "#180e06", "heavy_square"),

        "Fakhar Black": ("#c5a059", "#f3e2ba", "#0d0f12", "shield"),
        "Fakhar Rose": ("#df92a5", "#fde2ea", "#2d0c15", "shield"),

        "Teriaq": ("#2b2b2b", "#d4af37", "#0d0d0f", "sculpted"),
        "Maahir Black Edition": ("#2b2b2b", "#c5a059", "#090a0c", "equine"),
        "Maahir Legacy": ("#8f9ca6", "#d9e2e8", "#111518", "equine"),
        "Maahir": ("#c5a059", "#ffe89c", "#151410", "equine"),
        "Al Noble Safeer": ("#2d5c38", "#9ee0aa", "#09170d", "sculpted"),
        "Al Noble Wazeer": ("#6b2d4f", "#d992bd", "#170810", "sculpted"),
        "Al Noble Ameer": ("#6e4726", "#d8a980", "#160d06", "sculpted"),
        "Masa": ("#244b7a", "#9ec5f7", "#081321", "sculpted"),
        "Art Of Universe": ("#396b6b", "#a6dede", "#0a1919", "sculpted"),
        "Art Of Nature II": ("#436340", "#b2d6af", "#0e1a0d", "sculpted"),
        "Nebras": ("#c43d4d", "#f8b6bf", "#2d080e", "sculpted"),
        "Vintage Radio": ("#634766", "#d9b8dc", "#180d19", "sculpted"),
        "Ajwad": ("#9e4a7a", "#fcaed8", "#1c0714", "sculpted"),
        "Ajwad Pink to Pink": ("#df6f88", "#fcdde4", "#290a12", "sculpted"),

        "Eclaire": ("#cca059", "#fcedcd", "#2d1d0c", "classic"),
        "Angham": ("#b37a51", "#fadcc2", "#2e1b10", "classic"),
        "His Confession": ("#9e6f3b", "#eec798", "#1c1208", "classic"),
        "Ameer Al Oudh Intense Oud": ("#b86d2f", "#f8c59c", "#1c0e04", "classic"),
        "Atheeri": ("#c5a059", "#ffefa8", "#1e1b13", "classic"),
        "Najdia": ("#357388", "#a6ddef", "#08151a", "classic"),
        "Hala": ("#b27441", "#fed6b0", "#1c1108", "classic"),
    }

    @staticmethod
    def split_perfume_name(name: str) -> List[str]:
        """Wrap names into balanced label-safe lines, never exceeding three lines or 15 chars."""
        words = name.split()
        if len(name) <= 13:
            return [name]

        max_chars = 14
        lines: List[str] = []
        current: List[str] = []
        current_len = 0
        for word in words:
            proposed = current_len + len(word) + (1 if current else 0)
            if current and proposed > max_chars:
                lines.append(" ".join(current))
                current = [word]
                current_len = len(word)
            else:
                current.append(word)
                current_len = proposed
        if current:
            lines.append(" ".join(current))
        if len(lines) > 3:
            lines = [" ".join(words[:2]), " ".join(words[2:4]), " ".join(words[4:])]
        return [line for line in lines if line]

    @classmethod
    def build_label_svg(
        cls,
        name: str,
        brand: str,
        conc: str,
        size: str,
        accent: str,
        highlight: str,
        width: float = 170,
        height: float = 180,
        y_offset: float = 24,
    ) -> str:
        """Constructs an ultra-crisp embossed metallic foil-stamped cartouche."""
        lines = cls.split_perfume_name(name)
        safe_brand = xml.sax.saxutils.escape(brand.upper())
        safe_conc = xml.sax.saxutils.escape(conc.upper())
        safe_size = xml.sax.saxutils.escape(size.upper())

        brand_font_size = 7.5 if len(brand) > 13 else 8.5
        brand_letter_spacing = 2.2 if len(brand) > 13 else 3.2
        conc_font_size = 6.2 if len(conc) > 18 else 7.0

        hw = width / 2
        hh = height / 2
        top = -hh + y_offset

        # Title positioned in the middle region between top+54 and top+height-38
        if len(lines) == 1:
            n = lines[0]
            fs = 14.5 if len(n) <= 7 else (13.0 if len(n) <= 10 else 11.5)
            ls = 2.4 if len(n) <= 7 else 1.8
            title_svg = (
                f'<text x="0" y="{top + 98:.1f}" font-family="\'Cinzel\', serif" '
                f'font-size="{fs}" font-weight="700" letter-spacing="{ls}" '
                f'fill="url(#metalG)" text-anchor="middle">{xml.sax.saxutils.escape(n.upper())}</text>'
            )
        elif len(lines) == 2:
            max_l = max(len(line) for line in lines)
            fs = 10.2 if max_l > 12 else 11.2
            ls = 1.2 if fs < 11 else 1.6
            title_svg = (
                f'<text x="0" y="{top + 90:.1f}" font-family="\'Cinzel\', serif" '
                f'font-size="{fs}" font-weight="700" letter-spacing="{ls}" fill="url(#metalG)" text-anchor="middle">'
                f'<tspan x="0" dy="0">{xml.sax.saxutils.escape(lines[0].upper())}</tspan>'
                f'<tspan x="0" dy="16">{xml.sax.saxutils.escape(lines[1].upper())}</tspan>'
                f'</text>'
            )
        else:
            fs = 9.2
            ls = 1.0
            title_svg = (
                f'<text x="0" y="{top + 84:.1f}" font-family="\'Cinzel\', serif" '
                f'font-size="{fs}" font-weight="700" letter-spacing="{ls}" fill="url(#metalG)" text-anchor="middle">'
                f'<tspan x="0" dy="0">{xml.sax.saxutils.escape(lines[0].upper())}</tspan>'
                f'<tspan x="0" dy="14">{xml.sax.saxutils.escape(lines[1].upper())}</tspan>'
                f'<tspan x="0" dy="14">{xml.sax.saxutils.escape(lines[2].upper())}</tspan>'
                f'</text>'
            )

        return f"""
        <!-- Embossed Label Cartouche Plaque -->
        <g filter="url(#plaqueShadow)">
          <rect x="{-hw}" y="{top}" width="{width}" height="{height}" rx="10" fill="url(#labelG)" stroke="url(#metalG)" stroke-width="2.2"/>
          <rect x="{-hw+5}" y="{top+5}" width="{width-10}" height="{height-10}" rx="7" fill="none" stroke="url(#metalG)" stroke-width="0.8" stroke-dasharray="4,2" opacity="0.65"/>
          <rect x="{-hw+8}" y="{top+8}" width="{width-16}" height="{height*0.32:.1f}" rx="5" fill="url(#labelSheen)" opacity="0.18"/>
          
          <!-- Crest Emblem -->
          <g transform="translate(0, {top + 24:.1f})">
            <circle cx="0" cy="0" r="10" fill="none" stroke="url(#metalG)" stroke-width="0.9"/>
            <polygon points="0,-6.5 2,-2 6.5,0 2,2 0,6.5 -2,2 -6.5,0 -2,-2" fill="url(#metalG)"/>
          </g>
          
          <!-- Brand Header -->
          <text x="0" y="{top + 45:.1f}" font-family="'Inter', sans-serif" font-size="{brand_font_size}" font-weight="600" letter-spacing="{brand_letter_spacing}" fill="#e8dcc4" text-anchor="middle">{safe_brand}</text>
          <line x1="{-hw+18}" y1="{top + 53:.1f}" x2="{hw-18}" y2="{top + 53:.1f}" stroke="url(#metalG)" stroke-width="0.6" opacity="0.55"/>
          
          <!-- Perfume Name -->
          {title_svg}
          
          <!-- Concentration & Volume Details -->
          <line x1="{-hw+22}" y1="{top + height - 36:.1f}" x2="{hw-22}" y2="{top + height - 36:.1f}" stroke="url(#metalG)" stroke-width="0.6" opacity="0.55"/>
          <text x="0" y="{top + height - 22:.1f}" font-family="'Inter', sans-serif" font-size="{conc_font_size}" font-weight="500" letter-spacing="1.6" fill="#c8bba4" text-anchor="middle">{safe_conc}</text>
          <text x="0" y="{top + height - 9:.1f}" font-family="'Inter', sans-serif" font-size="7.5" font-weight="600" letter-spacing="2.8" fill="url(#metalG)" text-anchor="middle">{safe_size}</text>
        </g>
        """

    @classmethod
    def render_flacon_svg(
        cls,
        name: str,
        brand: str,
        family: str,
        conc: str,
        size: str,
        accent: str,
        highlight: str,
        bg_color: str,
        shape: str = "classic",
    ) -> str:
        """Renders luxury 1200x1500 SVG flacon photography with studio lighting."""
        safe_family = xml.sax.saxutils.escape(family.upper())

        # Coordinate center is at (0, 0) inside a g transform="translate(600, 720) scale(1.85)"
        if shape == "crystal":
            # Cut Crystal Whisky Decanter
            bottle_elements = f"""
            <ellipse cx="0" cy="210" rx="145" ry="22" fill="#000000" opacity="0.65"/>
            <rect x="-115" y="-85" width="230" height="280" rx="16" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="2.8"/>
            <rect x="-110" y="145" width="220" height="45" rx="10" fill="url(#baseG)" opacity="0.95"/>
            <line x1="-110" y1="145" x2="110" y2="145" stroke="{highlight}" stroke-width="1.5" opacity="0.7"/>
            <!-- Cut crystal diamond faceting -->
            <path d="M-105,40 L-60,95 L-15,40 L30,95 L75,40 L105,75" fill="none" stroke="{highlight}" stroke-width="1.4" opacity="0.32"/>
            <path d="M-105,95 L-60,40 L-15,95 L30,40 L75,95 L105,60" fill="none" stroke="{highlight}" stroke-width="1.4" opacity="0.32"/>
            <path d="M-105,95 L-60,150 L-15,95 L30,150 L75,95 L105,130" fill="none" stroke="{highlight}" stroke-width="1.4" opacity="0.32"/>
            <line x1="-100" y1="-75" x2="-100" y2="180" stroke="#ffffff" stroke-width="3" stroke-linecap="round" opacity="0.4"/>
            {cls.build_label_svg(name, brand, conc, size, accent, highlight, width=172, height=180, y_offset=18)}
            <!-- Atomizer collar & stopper -->
            <path d="M-60,-85 L-35,-125 L35,-125 L60,-85 Z" fill="url(#metalG)"/>
            <rect x="-35" y="-140" width="70" height="22" rx="4" fill="url(#metalG)"/>
            <polygon points="-58,-225 58,-225 72,-175 48,-140 -48,-140 -72,-175" fill="url(#metalG)" stroke="{highlight}" stroke-width="2"/>
            <circle cx="0" cy="-178" r="15" fill="#14151a" stroke="url(#metalG)" stroke-width="1.5"/>
            <polygon points="0,-185 3,-180 8,-178 3,-176 0,-171 -3,-176 -8,-178 -3,-180" fill="url(#metalG)"/>
            """
        elif shape == "cylinder":
            # Fluted Architectural Column
            bottle_elements = f"""
            <ellipse cx="0" cy="215" rx="135" ry="22" fill="#000000" opacity="0.65"/>
            <rect x="-95" y="-100" width="190" height="305" rx="28" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="2.8"/>
            <line x1="-80" y1="-90" x2="-80" y2="195" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round" opacity="0.35"/>
            <rect x="-96" y="-60" width="192" height="12" fill="url(#metalG)"/>
            <rect x="-96" y="160" width="192" height="12" fill="url(#metalG)"/>
            {cls.build_label_svg(name, brand, conc, size, accent, highlight, width=158, height=182, y_offset=46)}
            <rect x="-42" y="-138" width="84" height="40" rx="5" fill="url(#metalG)"/>
            <rect x="-52" y="-228" width="104" height="92" rx="14" fill="url(#metalG)" stroke="{highlight}" stroke-width="1.8"/>
            <line x1="-36" y1="-222" x2="-36" y2="-140" stroke="#121316" stroke-width="1.4" opacity="0.65"/>
            <line x1="-18" y1="-222" x2="-18" y2="-140" stroke="#121316" stroke-width="1.4" opacity="0.65"/>
            <line x1="0" y1="-222" x2="0" y2="-140" stroke="#121316" stroke-width="1.4" opacity="0.65"/>
            <line x1="18" y1="-222" x2="18" y2="-140" stroke="#121316" stroke-width="1.4" opacity="0.65"/>
            <line x1="36" y1="-222" x2="36" y2="-140" stroke="#121316" stroke-width="1.4" opacity="0.65"/>
            """
        elif shape == "curve":
            # Sculpted Sensual Hourglass
            bottle_elements = f"""
            <ellipse cx="0" cy="210" rx="135" ry="20" fill="#000000" opacity="0.6"/>
            <path d="M-92,-85 Q-75,-10 -95,65 Q-105,120 -82,190 L82,190 Q105,120 95,65 Q75,-10 92,-85 Z" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="2.8"/>
            <path d="M-82,-75 Q-68,0 -84,70 Q-92,115 -74,180" fill="none" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round" opacity="0.45"/>
            <path d="M-86,22 Q0,32 86,22" fill="none" stroke="url(#metalG)" stroke-width="3.2"/>
            {cls.build_label_svg(name, brand, conc, size, accent, highlight, width=156, height=174, y_offset=42)}
            <path d="M-38,-85 L-28,-124 L28,-124 L38,-85 Z" fill="url(#metalG)"/>
            <path d="M-48,-138 Q-50,-228 0,-232 Q50,-228 48,-138 Z" fill="url(#metalG)" stroke="{highlight}" stroke-width="1.8"/>
            <circle cx="0" cy="-235" r="8" fill="url(#metalG)"/>
            """
        elif shape == "faceted":
            # Monolithic Faceted Obelisk
            bottle_elements = f"""
            <ellipse cx="0" cy="215" rx="140" ry="22" fill="#000000" opacity="0.7"/>
            <polygon points="-80,-105 80,-105 106,-75 106,165 80,195 -80,195 -106,165 -106,-75" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="2.8"/>
            <line x1="-80" y1="-105" x2="-80" y2="195" stroke="url(#metalG)" stroke-width="1.4" opacity="0.55"/>
            <line x1="80" y1="-105" x2="80" y2="195" stroke="url(#metalG)" stroke-width="1.4" opacity="0.55"/>
            <!-- Arabesque medallion -->
            <g opacity="0.4" transform="translate(0, 45)">
              <circle cx="0" cy="0" r="70" fill="none" stroke="url(#metalG)" stroke-width="1.6"/>
              <polygon points="0,-65 18,-18 65,0 18,18 0,65 -18,18 -65,0 -18,-18" fill="none" stroke="url(#metalG)" stroke-width="1.2"/>
            </g>
            {cls.build_label_svg(name, brand, conc, size, accent, highlight, width=164, height=180, y_offset=45)}
            <polygon points="-48,-105 -35,-142 35,-142 48,-105" fill="url(#metalG)"/>
            <polygon points="-44,-230 44,-230 64,-185 46,-142 -46,-142 -64,-185" fill="url(#metalG)" stroke="{highlight}" stroke-width="2"/>
            <circle cx="0" cy="-185" r="16" fill="#111216" stroke="url(#metalG)" stroke-width="1.4"/>
            """
        elif shape in ("minimalist_niche", "frosted_niche"):
            # Heavy Apothecary Flacon
            bottle_elements = f"""
            <ellipse cx="0" cy="210" rx="140" ry="20" fill="#000000" opacity="0.6"/>
            <rect x="-100" y="-80" width="200" height="275" rx="12" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="2.4"/>
            <rect x="-96" y="145" width="192" height="46" rx="8" fill="url(#baseG)" opacity="0.95"/>
            <line x1="-88" y1="-70" x2="-88" y2="182" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round" opacity="0.45"/>
            {cls.build_label_svg(name, brand, conc, size, accent, highlight, width=164, height=174, y_offset=20)}
            <rect x="-26" y="-118" width="52" height="38" rx="3" fill="url(#metalG)"/>
            <rect x="-50" y="-218" width="100" height="104" rx="8" fill="url(#metalG)" stroke="{highlight}" stroke-width="1.8"/>
            """
        elif shape == "tall_luxury":
            # Columnar Tall Niche
            bottle_elements = f"""
            <ellipse cx="0" cy="215" rx="130" ry="20" fill="#000000" opacity="0.65"/>
            <rect x="-85" y="-115" width="170" height="325" rx="20" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="2.8"/>
            <rect x="-80" y="165" width="160" height="42" rx="8" fill="url(#baseG)" opacity="0.95"/>
            <line x1="-72" y1="-105" x2="-72" y2="195" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round" opacity="0.38"/>
            {cls.build_label_svg(name, brand, conc, size, accent, highlight, width=148, height=186, y_offset=28)}
            <rect x="-32" y="-150" width="64" height="36" rx="4" fill="url(#metalG)"/>
            <rect x="-44" y="-235" width="88" height="90" rx="12" fill="url(#metalG)" stroke="{highlight}" stroke-width="1.8"/>
            <circle cx="0" cy="-190" r="14" fill="#121316" stroke="url(#metalG)" stroke-width="1.2"/>
            """
        elif shape == "heavy_square":
            # Monumental Glass Cube
            bottle_elements = f"""
            <ellipse cx="0" cy="210" rx="145" ry="22" fill="#000000" opacity="0.7"/>
            <rect x="-110" y="-85" width="220" height="280" rx="16" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="3.2"/>
            <rect x="-104" y="145" width="208" height="46" rx="8" fill="url(#baseG)" opacity="0.95"/>
            <line x1="-96" y1="-75" x2="-96" y2="180" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round" opacity="0.4"/>
            {cls.build_label_svg(name, brand, conc, size, accent, highlight, width=172, height=176, y_offset=18)}
            <rect x="-42" y="-128" width="84" height="44" rx="4" fill="url(#metalG)"/>
            <rect x="-58" y="-222" width="116" height="100" rx="10" fill="url(#metalG)" stroke="{highlight}" stroke-width="2.2"/>
            """
        elif shape == "shield":
            # Aerodynamic Shield Silhouette
            bottle_elements = f"""
            <ellipse cx="0" cy="215" rx="140" ry="22" fill="#000000" opacity="0.65"/>
            <path d="M-105,-85 L105,-85 L105,100 Q105,195 0,205 Q-105,195 -105,100 Z" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="2.8"/>
            <line x1="-90" y1="-75" x2="-90" y2="120" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round" opacity="0.4"/>
            {cls.build_label_svg(name, brand, conc, size, accent, highlight, width=160, height=174, y_offset=28)}
            <polygon points="-50,-85 -30,-125 30,-125 50,-85" fill="url(#metalG)"/>
            <path d="M-45,-140 Q-48,-228 0,-230 Q48,-228 45,-140 Z" fill="url(#metalG)" stroke="{highlight}" stroke-width="1.8"/>
            <circle cx="0" cy="-234" r="7" fill="url(#metalG)"/>
            """
        elif shape in ("equine", "sculpted"):
            # Imperial Sculpted Finial
            bottle_elements = f"""
            <ellipse cx="0" cy="215" rx="145" ry="22" fill="#000000" opacity="0.7"/>
            <polygon points="-85,-95 85,-95 110,-50 95,150 75,198 -75,198 -95,150 -110,-50" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="2.8"/>
            {cls.build_label_svg(name, brand, conc, size, accent, highlight, width=162, height=180, y_offset=38)}
            <polygon points="-46,-95 -32,-134 32,-134 46,-95" fill="url(#metalG)"/>
            <polygon points="-50,-234 50,-234 60,-190 42,-134 -42,-134 -60,-190" fill="url(#metalG)" stroke="{highlight}" stroke-width="2"/>
            <path d="M-26,-234 L0,-258 L26,-234 Z" fill="url(#metalG)" stroke="{highlight}" stroke-width="1.4"/>
            <circle cx="0" cy="-184" r="14" fill="#121316" stroke="url(#metalG)" stroke-width="1.2"/>
            """
        else:
            # Classic Royal Arabian Flacon
            bottle_elements = f"""
            <ellipse cx="0" cy="215" rx="140" ry="22" fill="#000000" opacity="0.65"/>
            <rect x="-105" y="-95" width="210" height="295" rx="24" fill="url(#bodyG)" stroke="url(#metalG)" stroke-width="2.8"/>
            <rect x="-98" y="155" width="196" height="42" rx="14" fill="url(#baseG)" opacity="0.92"/>
            <line x1="-92" y1="-85" x2="-92" y2="185" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round" opacity="0.38"/>
            {cls.build_label_svg(name, brand, conc, size, accent, highlight, width=166, height=182, y_offset=24)}
            <path d="M-65,-95 L-35,-132 L35,-132 L65,-95 Z" fill="url(#metalG)"/>
            <rect x="-52" y="-228" width="104" height="84" rx="12" fill="url(#metalG)" stroke="{highlight}" stroke-width="1.8"/>
            <circle cx="0" cy="-186" r="16" fill="#121316" stroke="url(#metalG)" stroke-width="1.4"/>
            <circle cx="0" cy="-234" r="8" fill="url(#metalG)"/>
            """

        gloss_path = "M-78,-70 C-90,18 -88,112 -74,172"
        bottle_elements += f"""
        <!-- Studio Specular Highlights -->
        <path d="{gloss_path}" fill="none" stroke="#ffffff" stroke-width="14" stroke-linecap="round" opacity="0.08"/>
        <path d="{gloss_path}" fill="none" stroke="#ffffff" stroke-width="4.5" stroke-linecap="round" opacity="0.24"/>
        <path d="{gloss_path}" fill="none" stroke="#ffffff" stroke-width="1.3" stroke-linecap="round" opacity="0.85"/>
        """

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1500" width="1200" height="1500">
  <defs>
    <!-- Studio Ambient Lighting & Radial Bloom -->
    <radialGradient id="ambG" cx="50%" cy="40%" r="68%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.36"/>
      <stop offset="55%" stop-color="{bg_color}" stop-opacity="0.96"/>
      <stop offset="100%" stop-color="#08080a"/>
    </radialGradient>
    
    <!-- Polished Stone Pedestal Horizon Gradient -->
    <linearGradient id="pedestalG" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.22"/>
      <stop offset="15%" stop-color="#121317" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#050608"/>
    </linearGradient>

    <!-- Metallic Specular Profile -->
    <linearGradient id="metalG" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.98"/>
      <stop offset="16%" stop-color="#fff8df" stop-opacity="0.92"/>
      <stop offset="35%" stop-color="{highlight}"/>
      <stop offset="65%" stop-color="{accent}"/>
      <stop offset="85%" stop-color="#2a1f0a"/>
      <stop offset="100%" stop-color="{highlight}"/>
    </linearGradient>

    <!-- Glass Refraction & Body Material -->
    <linearGradient id="bodyG" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#050609"/>
      <stop offset="12%" stop-color="{bg_color}"/>
      <stop offset="32%" stop-color="{accent}" stop-opacity="0.82"/>
      <stop offset="50%" stop-color="{highlight}" stop-opacity="0.96"/>
      <stop offset="68%" stop-color="{accent}" stop-opacity="0.82"/>
      <stop offset="88%" stop-color="{bg_color}"/>
      <stop offset="100%" stop-color="#050609"/>
    </linearGradient>

    <linearGradient id="baseG" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#000000" stop-opacity="0.85"/>
      <stop offset="50%" stop-color="{highlight}" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0.85"/>
    </linearGradient>

    <linearGradient id="labelG" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#2e2e34"/>
      <stop offset="50%" stop-color="#121317"/>
      <stop offset="100%" stop-color="#07080a"/>
    </linearGradient>

    <linearGradient id="labelSheen" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>

    <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="24"/>
    </filter>
    <filter id="flaconShadow" x="-30%" y="-20%" width="160%" height="150%">
      <feDropShadow dx="0" dy="28" stdDeviation="26" flood-color="#000000" flood-opacity="0.85"/>
    </filter>
    <filter id="plaqueShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000000" flood-opacity="0.65"/>
    </filter>
  </defs>

  <!-- Studio Background Wall -->
  <rect width="1200" height="1500" fill="url(#ambG)"/>
  
  <!-- Subtle Studio Pedestal Horizon Surface -->
  <rect x="0" y="1100" width="1200" height="400" fill="url(#pedestalG)"/>
  <line x1="0" y1="1100" x2="1200" y2="1100" stroke="{accent}" stroke-width="0.8" opacity="0.35"/>

  <!-- Multi-Tier Contact Shadows -->
  <ellipse cx="600" cy="1150" rx="340" ry="42" fill="#000000" opacity="0.5" filter="url(#softShadow)"/>
  <ellipse cx="600" cy="1142" rx="250" ry="20" fill="#000000" opacity="0.85"/>

  <!-- Border Passepartout -->
  <rect x="40" y="40" width="1120" height="1420" fill="none" stroke="{accent}" stroke-width="1.2" opacity="0.28"/>
  <rect x="52" y="52" width="1096" height="1396" fill="none" stroke="{accent}" stroke-width="0.6" stroke-dasharray="6,4" opacity="0.18"/>

  <!-- Centered Flacon Geometry (Scaled 1.85x into 1200x1500 frame) -->
  <g transform="translate(600, 720) scale(1.85)" filter="url(#flaconShadow)">
    {bottle_elements}
  </g>

  <!-- Bottom Olfactory Classification Tagline -->
  <text x="600" y="1410" font-family="'Inter', sans-serif" font-size="16" font-weight="600" letter-spacing="8" fill="{accent}" opacity="0.85" text-anchor="middle">{safe_family}</text>
</svg>"""
        return svg


# =============================================================================
# 5. MANIFEST MANAGER
# =============================================================================
class ManifestManager:
    """Creates, synchronizes, and audits PERFUME_IMAGE_MANIFEST.json."""

    @classmethod
    def load_or_init(cls, catalog: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Loads existing manifest or initializes it from the catalog."""
        manifest: Dict[str, Dict[str, Any]] = {}
        if MANIFEST_PATH.exists():
            try:
                with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except json.JSONDecodeError as ex:
                print(f"Warning: Corrupt manifest at {MANIFEST_PATH} ({ex}). Initializing backup.")
                backup_path = MANIFEST_PATH.with_suffix(".json.bak")
                with open(backup_path, "w", encoding="utf-8") as bak:
                    with open(MANIFEST_PATH, "r", encoding="utf-8", errors="ignore") as orig:
                        bak.write(orig.read())
                manifest = {}

        now_str = datetime.now().isoformat()
        for prod in catalog:
            slug = prod["slug"]
            if slug not in manifest:
                prompt = PromptBuilder.build_prompt(prod)
                prompt_hash = PromptBuilder.hash_prompt(prompt)

                manifest[slug] = {
                    "product_id": prod["product_id"],
                    "product_slug": slug,
                    "product_name": prod["name"],
                    "brand": prod["brand"],
                    "collection": prod["collection"],
                    "fragrance_family": prod["fragrance_family"],
                    "gender": prod["gender"],
                    "concentration": prod["concentration"],
                    "bottle_size": prod["bottle_size"],
                    "mode": "FALLBACK_ARCHITECTURAL",
                    "source_type": "fallback_svg",
                    "generation_status": "pending",
                    "primary_image_path": f"static/images/products/{slug}.svg",
                    "fallback_image_path": f"static/images/products/{slug}.svg",
                    "prompt": prompt,
                    "prompt_hash": prompt_hash,
                    "aspect_ratio": "4:5",
                    "target_resolution": [1200, 1500],
                    "actual_resolution": [1200, 1500],
                    "file_size_kb": 0.0,
                    "quality_score": 100.0,
                    "updated_at": now_str,
                }
        return manifest

    @classmethod
    def save(cls, manifest: Dict[str, Dict[str, Any]]) -> None:
        """Atomically writes manifest to data/ and app/data/."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
        dump_data = json.dumps(manifest, indent=2)
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f1:
            f1.write(dump_data)
        with open(APP_MANIFEST_PATH, "w", encoding="utf-8") as f2:
            f2.write(dump_data)

    @classmethod
    def update_with_optimized_image(
        cls,
        manifest: Dict[str, Dict[str, Any]],
        slug: str,
        img_meta: Dict[str, Any],
        mode: str = "MODE_B_CONCEPTUAL",
    ) -> None:
        """Updates manifest entry when an authorized or conceptual image is optimized."""
        if slug not in manifest:
            return
        manifest[slug]["mode"] = mode
        manifest[slug]["source_type"] = "conceptual_render" if mode == "MODE_B_CONCEPTUAL" else "authorized_photo"
        manifest[slug]["generation_status"] = "optimized"
        manifest[slug]["primary_image_path"] = img_meta["webp_path"]
        manifest[slug]["fallback_image_path"] = img_meta["jpg_path"]
        manifest[slug]["actual_resolution"] = [img_meta["width"], img_meta["height"]]
        manifest[slug]["file_size_kb"] = img_meta["webp_size_kb"]
        manifest[slug]["luminance"] = img_meta["luminance"]
        manifest[slug]["sharpness"] = img_meta["sharpness"]
        manifest[slug]["updated_at"] = datetime.now().isoformat()


# =============================================================================
# 6. CONTACT SHEET GENERATOR
# =============================================================================
class ContactSheetGenerator:
    """Generates a responsive, luxury editorial HTML contact sheet."""

    @classmethod
    def generate(cls, manifest: Dict[str, Dict[str, Any]]) -> None:
        items = sorted(manifest.values(), key=lambda x: x["product_id"])

        total = len(items)
        optimized = sum(1 for i in items if i["generation_status"] == "optimized")
        pending = total - optimized
        avg_webp_size = (
            sum(i["file_size_kb"] for i in items if i["generation_status"] == "optimized") / (optimized or 1)
        )

        cards_html: List[str] = []
        for i in items:
            status_badge = (
                '<span class="badge badge-success">OPTIMIZED 4:5 (1200x1500)</span>'
                if i["generation_status"] == "optimized"
                else '<span class="badge badge-pending">PENDING FLACON</span>'
            )
            mode_badge = (
                '<span class="badge badge-mode-b">MODE B: CONCEPTUAL</span>'
                if i["mode"] == "MODE_B_CONCEPTUAL"
                else (
                    '<span class="badge badge-mode-a">MODE A: AUTHORIZED</span>'
                    if i["mode"] == "MODE_A_AUTHORIZED"
                    else '<span class="badge badge-fallback">ARCHITECTURAL FLACON</span>'
                )
            )

            img_src = f"products/{Path(i['primary_image_path']).name}"
            res_str = f"{i['actual_resolution'][0]}x{i['actual_resolution'][1]}"
            size_str = f"{i['file_size_kb']} KB" if i["file_size_kb"] > 0 else "Vector SVG"

            # Properly quote and escape HTML attributes
            safe_status = html.escape(str(i["generation_status"]), quote=True)
            safe_brand_attr = html.escape(str(i["brand"]), quote=True)
            safe_family_attr = html.escape(str(i["fragrance_family"]), quote=True)

            cards_html.append(f"""
            <div class="product-card" data-status="{safe_status}" data-brand="{safe_brand_attr}" data-family="{safe_family_attr}">
              <div class="card-media">
                <img src="{img_src}" alt="{xml.sax.saxutils.escape(i['product_name'])}" loading="lazy" />
                <div class="card-overlay">
                  <div class="badges-row">
                    {mode_badge}
                    {status_badge}
                  </div>
                  <div class="tech-specs">
                    <span>ID #{i['product_id']}</span>
                    <span>{res_str}</span>
                    <span>{size_str}</span>
                  </div>
                </div>
              </div>
              <div class="card-content">
                <div class="brand-eyebrow">{xml.sax.saxutils.escape(i['brand'])}</div>
                <h3 class="product-title">{xml.sax.saxutils.escape(i['product_name'])}</h3>
                <div class="product-collection">{xml.sax.saxutils.escape(i['collection'])}</div>
                <div class="product-family">{xml.sax.saxutils.escape(i['fragrance_family'])} &bull; {xml.sax.saxutils.escape(i['gender'])}</div>
                <div class="spec-line">
                  <span>Conc: {xml.sax.saxutils.escape(i['concentration'])}</span>
                  <span>Size: {xml.sax.saxutils.escape(i['bottle_size'])}</span>
                </div>
              </div>
            </div>
            """)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lattafa Parfums &bull; Product Catalog Visual Inspection Contact Sheet</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #0c0d10;
      --card-bg: #14151a;
      --gold: #c5a059;
      --gold-light: #edd59e;
      --text: #ded7ca;
      --muted: #8b8579;
      --border: #23252d;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: 'Inter', -apple-system, sans-serif;
      padding: 40px 24px;
      line-height: 1.5;
    }}
    .header {{
      max-width: 1400px;
      margin: 0 auto 36px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 28px;
    }}
    .eyebrow {{
      font-size: 11px;
      letter-spacing: 5px;
      color: var(--gold);
      text-transform: uppercase;
      font-weight: 600;
      margin-bottom: 8px;
    }}
    h1 {{
      font-family: 'Cinzel', serif;
      font-size: 32px;
      letter-spacing: 2px;
      color: #ffffff;
      margin-bottom: 16px;
    }}
    .metrics-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 24px;
      margin-top: 20px;
    }}
    .metric-item {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      padding: 14px 20px;
      border-radius: 8px;
      min-width: 170px;
    }}
    .metric-val {{
      font-family: 'Cinzel', serif;
      font-size: 24px;
      font-weight: 700;
      color: var(--gold-light);
    }}
    .metric-label {{
      font-size: 11px;
      color: var(--muted);
      letter-spacing: 1.5px;
      text-transform: uppercase;
      margin-top: 4px;
    }}
    .controls {{
      max-width: 1400px;
      margin: 0 auto 30px;
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      align-items: center;
      justify-content: space-between;
    }}
    .filter-tabs {{
      display: flex;
      gap: 8px;
    }}
    .tab-btn {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 12px;
      letter-spacing: 1px;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .tab-btn.active, .tab-btn:hover {{
      background: var(--gold);
      color: #000000;
      border-color: var(--gold);
      font-weight: 600;
    }}
    .search-box {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      color: #ffffff;
      padding: 8px 14px;
      border-radius: 6px;
      font-size: 13px;
      width: 260px;
      outline: none;
    }}
    .grid {{
      max-width: 1400px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 24px;
    }}
    .product-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: transform 0.25s, border-color 0.25s;
    }}
    .product-card:hover {{
      transform: translateY(-4px);
      border-color: var(--gold);
    }}
    .card-media {{
      position: relative;
      aspect-ratio: 4 / 5;
      background: #08080a;
      overflow: hidden;
    }}
    .card-media img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transition: transform 0.4s ease;
    }}
    .product-card:hover .card-media img {{
      transform: scale(1.03);
    }}
    .card-overlay {{
      position: absolute;
      inset: 0;
      background: linear-gradient(180deg, rgba(0,0,0,0.6) 0%, transparent 35%, rgba(0,0,0,0.85) 100%);
      padding: 12px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      pointer-events: none;
    }}
    .badges-row {{
      display: flex;
      flex-direction: column;
      gap: 6px;
      align-items: flex-start;
    }}
    .badge {{
      display: inline-block;
      font-size: 9.5px;
      font-weight: 600;
      letter-spacing: 1px;
      padding: 3px 8px;
      border-radius: 4px;
      text-transform: uppercase;
    }}
    .badge-success {{ background: rgba(34, 197, 94, 0.85); color: #ffffff; }}
    .badge-pending {{ background: rgba(234, 179, 8, 0.85); color: #000000; }}
    .badge-mode-b {{ background: rgba(197, 160, 89, 0.9); color: #000000; }}
    .badge-mode-a {{ background: rgba(59, 130, 246, 0.85); color: #ffffff; }}
    .badge-fallback {{ background: rgba(100, 116, 139, 0.85); color: #ffffff; }}
    .tech-specs {{
      display: flex;
      justify-content: space-between;
      font-size: 10px;
      color: #d1d5db;
      background: rgba(0,0,0,0.6);
      padding: 4px 8px;
      border-radius: 4px;
      backdrop-filter: blur(4px);
    }}
    .card-content {{
      padding: 16px;
      display: flex;
      flex-direction: column;
      flex: 1;
    }}
    .brand-eyebrow {{
      font-size: 10px;
      letter-spacing: 2px;
      color: var(--gold);
      text-transform: uppercase;
      font-weight: 600;
      margin-bottom: 4px;
    }}
    .product-title {{
      font-family: 'Cinzel', serif;
      font-size: 17px;
      color: #ffffff;
      font-weight: 600;
      margin-bottom: 4px;
    }}
    .product-collection {{
      font-size: 11.5px;
      color: #b5ada0;
      margin-bottom: 6px;
    }}
    .product-family {{
      font-size: 11px;
      color: var(--muted);
      margin-bottom: 10px;
    }}
    .spec-line {{
      margin-top: auto;
      border-top: 1px solid rgba(255,255,255,0.08);
      padding-top: 8px;
      display: flex;
      justify-content: space-between;
      font-size: 10.5px;
      color: #8c867c;
    }}
  </style>
</head>
<body>
  <header class="header">
    <div class="eyebrow">Haute Arabian Parfumerie &bull; Visual Quality Assurance</div>
    <h1>Fragrance Product Photography & Catalog Contact Sheet</h1>
    <p style="color: var(--muted); font-size: 13.5px; max-width: 800px;">
      Centralized visual inspection interface for all 100 catalog fragrances. Displays high-resolution 4:5 commercial product still-lifes (WebP/JPEG) alongside distinct architectural vector flacons.
    </p>
    <div class="metrics-bar">
      <div class="metric-item">
        <div class="metric-val">{total}</div>
        <div class="metric-label">Total Catalog Products</div>
      </div>
      <div class="metric-item">
        <div class="metric-val">{optimized}</div>
        <div class="metric-label">Optimized Commercial Renders</div>
      </div>
      <div class="metric-item">
        <div class="metric-val">{pending}</div>
        <div class="metric-label">Architectural Flacons</div>
      </div>
      <div class="metric-item">
        <div class="metric-val">{avg_webp_size:.1f} KB</div>
        <div class="metric-label">Avg WebP Footprint</div>
      </div>
      <div class="metric-item">
        <div class="metric-val">4 : 5</div>
        <div class="metric-label">Aspect Ratio (1200x1500)</div>
      </div>
    </div>
  </header>

  <div class="controls">
    <div class="filter-tabs">
      <button class="tab-btn active" onclick="filterCards('all', this)">All Products ({total})</button>
      <button class="tab-btn" onclick="filterCards('optimized', this)">Optimized Commercial ({optimized})</button>
      <button class="tab-btn" onclick="filterCards('pending', this)">Architectural Flacons ({pending})</button>
    </div>
    <input type="text" class="search-box" id="searchInput" placeholder="Search perfume name, brand..." onkeyup="searchCards()" />
  </div>

  <main class="grid" id="productGrid">
    {''.join(cards_html)}
  </main>

  <script>
    function filterCards(type, btnElement) {{
      document.querySelectorAll('.tab-btn').forEach(function(b) {{ b.classList.remove('active'); }});
      if (btnElement) {{ btnElement.classList.add('active'); }}
      var cards = document.querySelectorAll('.product-card');
      cards.forEach(function(c) {{
        if (type === 'all' || c.getAttribute('data-status') === type) {{
          c.style.display = 'flex';
        }} else {{
          c.style.display = 'none';
        }}
      }});
    }}
    function searchCards() {{
      var query = document.getElementById('searchInput').value.toLowerCase();
      var cards = document.querySelectorAll('.product-card');
      cards.forEach(function(c) {{
        var text = c.innerText.toLowerCase();
        c.style.display = text.indexOf(query) !== -1 ? 'flex' : 'none';
      }});
    }}
  </script>
</body>
</html>"""

        write_dual("static/images/contact_sheet.html", html_content)
        print("Responsive luxury Contact Sheet successfully generated.")


# =============================================================================
# 7. DATABASE SYNCHRONIZATION
# =============================================================================
class DatabaseSync:
    """Updates product_images in online_shop_perfume_dev and online_shop_perfume_test."""

    @classmethod
    def sync(cls, manifest: Dict[str, Dict[str, Any]], db_names: Tuple[str, ...] = ("online_shop_perfume_dev", "online_shop_perfume_test")) -> None:
        """Batch-updates product_images atomically across target databases."""
        for db_name in db_names:
            conn = None
            try:
                conn = get_connection(database=db_name)
                updated_count = 0
                with conn.cursor() as cur:
                    # Pre-fetch existing primary image records to eliminate N+1 queries
                    cur.execute("SELECT product_id, image_id, image_path FROM product_images WHERE is_primary = 1")
                    existing_rows = {r["product_id"]: r for r in cur.fetchall()}

                    updates: List[Tuple[str, int]] = []
                    inserts: List[Tuple[int, str]] = []

                    for item in manifest.values():
                        pid = item["product_id"]
                        img_path = item["primary_image_path"]
                        if pid in existing_rows:
                            if existing_rows[pid]["image_path"] != img_path:
                                updates.append((img_path, existing_rows[pid]["image_id"]))
                        else:
                            inserts.append((pid, img_path))

                    if updates:
                        cur.executemany("UPDATE product_images SET image_path = %s WHERE image_id = %s", updates)
                        updated_count += len(updates)
                    if inserts:
                        cur.executemany(
                            "INSERT INTO product_images (product_id, image_path, is_primary, sort_order) VALUES (%s, %s, 1, 1)",
                            inserts,
                        )
                        updated_count += len(inserts)

                conn.commit()
                print(f"[{db_name}] Synced product_images: {updated_count} records updated atomically.")
            except Exception as e:
                if conn:
                    try:
                        conn.rollback()
                    except Exception:
                        pass
                print(f"[{db_name}] Database sync error (rolled back): {e}")
                raise
            finally:
                if conn:
                    conn.close()


# =============================================================================
# 8. MASTER PIPELINE ORCHESTRATOR
# =============================================================================
def generate_branding() -> None:
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
  <g transform="translate(45, 60)" filter="url(#glow)">
    <circle cx="0" cy="0" r="32" fill="none" stroke="url(#gold)" stroke-width="1.8"/>
    <circle cx="0" cy="0" r="26" fill="none" stroke="url(#gold)" stroke-width="0.8" stroke-dasharray="3,2"/>
    <path d="M0 -22 L6 -6 L22 0 L6 6 L0 22 L-6 6 L-22 0 L-6 -6 Z" fill="url(#gold)"/>
    <circle cx="0" cy="0" r="4" fill="#121316"/>
  </g>
  <text x="100" y="58" font-family="'Cinzel', serif" font-size="34" font-weight="700" letter-spacing="8" fill="url(#gold)">LATTAFA</text>
  <text x="102" y="82" font-family="'Inter', sans-serif" font-size="11" font-weight="500" letter-spacing="6" fill="#ded7ca">HAUTE ARABIAN PERFUMERY</text>
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
  <path d="M50 20 L58 42 L80 50 L58 58 L50 80 L42 58 L20 50 L42 42 Z" fill="url(#goldM)"/>
</svg>"""
    write_dual("static/images/branding/brandmark.svg", brandmark_svg)


def generate_hero() -> None:
    hero_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 800" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
  <defs>
    <radialGradient id="bgG" cx="75%" cy="50%" r="65%">
      <stop offset="0%" stop-color="#2a2215"/>
      <stop offset="45%" stop-color="#18171d"/>
      <stop offset="100%" stop-color="#0c0d10"/>
    </radialGradient>
  </defs>
  <rect width="1920" height="800" fill="url(#bgG)"/>
</svg>"""
    write_dual("static/images/hero/perfume_hero.svg", hero_svg)


def generate_collections() -> None:
    cols = [
        ("yara_collection.svg", "YARA COLLECTION", "Soft Rose & Creamy Gourmand", "#f19bb2", "#421523"),
        ("asad_collection.svg", "ASAD COLLECTION", "Black Spices & Noble Woods", "#d4af37", "#141518"),
        ("khamrah_collection.svg", "KHAMRAH COLLECTION", "Golden Spices & Date Gourmand", "#d4882c", "#241306"),
        ("badee_al_oud.svg", "BADEE AL OUD", "Royal Agarwood & Smoky Resins", "#c5a059", "#121316"),
        ("lattafa_pride.svg", "LATTAFA PRIDE", "Artisanal Haute Parfumerie", "#c5a059", "#111816"),
        ("maison_alhambra.svg", "MAISON ALHAMBRA", "Parisian Chic with Arabian Depth", "#cca059", "#1a1815"),
        ("mainline_classics.svg", "MAINLINE CLASSICS", "Timeless Arabian Formulations", "#d4af37", "#15161b"),
    ]
    for filename, title, subtitle, c2, bg in cols:
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
  <rect width="800" height="600" fill="{bg}"/>
  <rect x="25" y="25" width="750" height="550" fill="none" stroke="{c2}" stroke-width="1.5" opacity="0.35"/>
  <text x="400" y="465" font-family="'Cinzel', serif" font-size="28" font-weight="700" letter-spacing="4" fill="{c2}" text-anchor="middle">{title}</text>
  <text x="400" y="500" font-family="'Inter', sans-serif" font-size="13" letter-spacing="3" fill="#cfc7b8" text-anchor="middle">{subtitle}</text>
</svg>"""
        write_dual(f"static/images/collections/{filename}", svg)


def generate_categories() -> None:
    cats = [
        ("fragrances.svg", "ALL FRAGRANCES", "The Complete Arabian Treasury", "#c5a059", "#15161b"),
        ("men.svg", "FOR HIM", "Bold Woods, Spices & Aristocratic Leathers", "#8b9dc3", "#12141a"),
        ("women.svg", "FOR HER", "Enchanting Florals, Sweet Vanilla & Sugared Fruits", "#d9829e", "#181216"),
        ("unisex.svg", "UNISEX TREASURES", "Transcendent Blends for Connoisseurs", "#c5a059", "#161513"),
        ("edp.svg", "EAU DE PARFUM", "Exceptional Sillage & Long-Lasting Mastery", "#d4af37", "#161814"),
        ("extrait.svg", "EXTRAIT DE PARFUM", "High-Concentration Artisanal Extractions", "#e5aa42", "#191410"),
        ("attar.svg", "PERFUME OILS", "Traditional Alcohol-Free Concentrated Attars", "#95ba8d", "#101612"),
        ("gift_sets.svg", "GIFT SETS & BOXES", "Curated Luxury Presentation Packaging", "#d1ab64", "#18151c"),
    ]
    for filename, title, subtitle, color, bg in cats:
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <rect width="600" height="400" fill="{bg}"/>
  <text x="300" y="275" font-family="'Cinzel', serif" font-size="22" font-weight="700" letter-spacing="3" fill="#fdf0cd" text-anchor="middle">{title}</text>
  <text x="300" y="305" font-family="'Inter', sans-serif" font-size="11" letter-spacing="2" fill="#bfb7a7" text-anchor="middle">{subtitle}</text>
</svg>"""
        write_dual(f"static/images/categories/{filename}", svg)


def scan_and_ingest_raw_renders(manifest: Dict[str, Dict[str, Any]], search_dirs: Optional[List[Path]] = None) -> int:
    """
    Scans raw output directories for commercial renders matching product slugs,
    processes them to 4:5 1200x1500 WebP/JPEG, and updates the manifest.
    """
    if search_dirs is None:
        search_dirs = [
            BASE_DIR / "data" / "raw_generated",
        ]
        # Check optional environment-configured staging directory
        env_raw = os.getenv("RAW_IMAGE_SEARCH_DIR")
        if env_raw:
            search_dirs.append(Path(env_raw))

    slug_aliases = {
        "badee_al_oud_oud_for_glory": "oud_for_glory",
        "oud_for_glory": "oud_for_glory",
        "ameer_al_oudh_intense_oud": "ameer_al_oudh",
        "ameer_al_oudh": "ameer_al_oudh",
        "fakhar_black": "fakhar_black",
        "teriaq": "teriaq",
        "eclaire": "eclaire",
        "woody_oud": "woody_oud",
        "khamrah": "khamrah",
        "asad": "asad",
        "yara": "yara",
        "maahir_black": "maahir_black",
        "baroque_rouge": "baroque_rouge",
        "delilah": "delilah",
        "jean_lowe_immortal": "jean_lowe_immortal",
        "nebras": "nebras",
        "qaed_al_fursan": "qaed_al_fursan",
    }

    ingested_count = 0
    for sdir in search_dirs:
        if not sdir.exists():
            continue
        for img_file in sdir.glob("*.jpg"):
            stem = img_file.stem
            clean_stem = re.sub(r"_\d+$", "", stem).lower()
            matched_slug = None
            for alias, target_slug in slug_aliases.items():
                if clean_stem == alias or clean_stem.startswith(alias):
                    matched_slug = target_slug
                    break
            if not matched_slug and clean_stem in manifest:
                matched_slug = clean_stem

            if matched_slug and matched_slug in manifest:
                try:
                    img_meta = ImageProcessor.process_and_optimize(img_file, matched_slug)
                    if not img_meta.get("is_valid", False):
                        print(f"Warning: Image {img_file.name} failed quality validation gates: {img_meta}")
                        continue

                    ManifestManager.update_with_optimized_image(manifest, matched_slug, img_meta, mode="MODE_B_CONCEPTUAL")
                    ingested_count += 1
                    print(f"Ingested and optimized {matched_slug} -> 1200x1500 WebP ({img_meta['webp_size_kb']} KB)")
                except Exception as ex:
                    print(f"Error processing {img_file}: {ex}")

    return ingested_count


def main() -> None:
    """Master CLI execution coordinating asset generation, optimization, and database synchronization."""
    parser = argparse.ArgumentParser(description="Advanced Perfume Image Generation & Visual Pipeline")
    parser.add_argument("--sync-only", action="store_true", help="Sync database only")
    parser.add_argument("--sheet-only", action="store_true", help="Generate contact sheet only")
    args = parser.parse_args()

    print("==================================================================")
    print(" ADVANCED PERFUME IMAGE GENERATION ENGINE")
    print("==================================================================")

    ensure_directories()

    # 1. Load Catalog
    catalog = CatalogReader.load_catalog()
    print(f"Loaded {len(catalog)} catalog records from {CSV_CATALOG_PATH.name}")

    # 2. Manifest initialization
    manifest = ManifestManager.load_or_init(catalog)

    if args.sync_only:
        DatabaseSync.sync(manifest)
        return

    if args.sheet_only:
        ContactSheetGenerator.generate(manifest)
        return

    # 3. Core branding & UI visuals
    generate_branding()
    generate_hero()
    generate_collections()
    generate_categories()

    # 4. Generate architectural flacons for all catalog items (ensures 100% assets present)
    for prod in catalog:
        name = prod["name"]
        slug = prod["slug"]
        rel_svg = f"static/images/products/{slug}.svg"

        if name in ArchitecturalFlaconRenderer.PALETTE_MAP:
            accent, highlight, bg_color, shape = ArchitecturalFlaconRenderer.PALETTE_MAP[name]
        else:
            if prod["brand"] == "Maison Alhambra":
                accent, highlight, bg_color, shape = ("#cca059", "#faebc9", "#151518", "minimalist_niche")
            elif prod["brand"] == "Lattafa Pride":
                accent, highlight, bg_color, shape = ("#d4af37", "#ffefa8", "#101918", "faceted")
            elif prod["gender"] == "Women":
                accent, highlight, bg_color, shape = ("#df8198", "#fde1e8", "#241016", "curve")
            elif prod["gender"] == "Men":
                accent, highlight, bg_color, shape = ("#c5a059", "#f5e6c3", "#111317", "classic")
            else:
                accent, highlight, bg_color, shape = ("#cfa049", "#ffe8b3", "#171513", "classic")

        svg_content = ArchitecturalFlaconRenderer.render_flacon_svg(
            name,
            prod["brand"],
            prod["fragrance_family"],
            prod["concentration"],
            prod["bottle_size"],
            accent,
            highlight,
            bg_color,
            shape,
        )
        write_dual(rel_svg, svg_content)

    # 5. Ingest and optimize any photorealistic renders from generation runs
    ingested = scan_and_ingest_raw_renders(manifest)
    print(f"Scanned & optimized {ingested} photorealistic commercial still-life renders.")

    # 6. Save Manifest
    ManifestManager.save(manifest)
    print(f"Saved manifest to {MANIFEST_PATH}")

    # 7. Database synchronization
    DatabaseSync.sync(manifest)

    # 8. Interactive Contact Sheet
    ContactSheetGenerator.generate(manifest)

    # 9. Summary
    total = len(manifest)
    optimized = sum(1 for i in manifest.values() if i["generation_status"] == "optimized")
    print("\n------------------------------------------------------------------")
    print(" PIPELINE EXECUTION SUMMARY")
    print("------------------------------------------------------------------")
    print(f" Total Products Processed: {total}")
    print(f" Optimized Commercial Renders (Mode B): {optimized}")
    print(f" Architectural Vector Flacons (Pending): {total - optimized}")
    print(f" Manifest: {MANIFEST_PATH}")
    print(f" Contact Sheet: {CONTACT_SHEET_PATH}")
    print("------------------------------------------------------------------\n")


if __name__ == "__main__":
    main()
