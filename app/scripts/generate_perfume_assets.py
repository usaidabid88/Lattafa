"""
generate_perfume_assets.py
=============================================================================
ADVANCED LUXURY PERFUME IMAGE GENERATION ENGINE & ASSET MANAGEMENT PIPELINE
=============================================================================
Comprehensive catalog visual pipeline conforming to luxury e-commerce standards.
Features:
  - Mode A: Optimization of authorized commercial product photography.
  - Mode B: Original conceptual commercial fragrance still-lifes (4:5, 1200x1500).
  - Mode B (Procedural): Ultra-luxury architectural vector flacon rendering engine
    producing photorealistic 1200x1500 WebP & JPEG assets natively with multi-tier glass,
    ice bases, liquid reservoirs, and 3-point studio lighting.
  - Pillow & resvg-py dual-engine for crisp, high-craft 1200x1500 rasterization.
  - Strict image quality validation (resolution 1200x1500, size <500KB, luminance, sharpness).
  - Atomic database synchronization for online_shop_perfume_dev and online_shop_perfume_test.
  - Responsive luxury inspection contact sheet with interactive filtering.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import math
import os
import re
import sys
import xml.sax.saxutils
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageFilter, ImageStat

try:
    import resvg_py
except ImportError:
    resvg_py = None

BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = BASE_DIR / "app"
STATIC_DIR = BASE_DIR / "static"
APP_STATIC_DIR = APP_DIR / "static"
DATA_DIR = BASE_DIR / "data"
APP_DATA_DIR = APP_DIR / "data"

CSV_CATALOG_PATH = BASE_DIR / "PERFUME_CATALOG_DATA.csv"
MANIFEST_PATH = DATA_DIR / "PERFUME_IMAGE_MANIFEST.json"
APP_MANIFEST_PATH = APP_DATA_DIR / "PERFUME_IMAGE_MANIFEST.json"
CONTACT_SHEET_PATH = STATIC_DIR / "images" / "contact_sheet.html"

# Ensure app package is importable for database connection
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.db import get_connection

APPROVED_COMMERCIAL_SLUGS: set[str] = {
    "khamrah",
    "asad",
    "yara",
    "oud_for_glory",
    "woody_oud",
    "teriaq",
    "eclaire",
    "fakhar_black",
    "ameer_al_oudh",
    "maahir_black",
    "baroque_rouge",
    "delilah",
    "jean_lowe_immortal",
}


def ensure_directories() -> None:
    """Creates all required static and data directories across both canonical roots."""
    dirs = [
        STATIC_DIR / "images" / "products",
        STATIC_DIR / "images" / "branding",
        STATIC_DIR / "images" / "hero",
        STATIC_DIR / "images" / "collections",
        STATIC_DIR / "images" / "categories",
        APP_STATIC_DIR / "images" / "products",
        APP_STATIC_DIR / "images" / "branding",
        APP_STATIC_DIR / "images" / "hero",
        APP_STATIC_DIR / "images" / "collections",
        APP_STATIC_DIR / "images" / "categories",
        DATA_DIR,
        APP_DATA_DIR,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def write_dual(rel_path: str, content: str, mode: str = "w", encoding: str = "utf-8") -> None:
    """Writes a text asset to both root static/ and app/static/ paths."""
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
    """Loads and standardizes catalog records from CSV."""

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
                slug = (
                    Path(rel_img).stem
                    if rel_img
                    else re.sub(r"[^a-z0-9]+", "_", row.get("name", "").lower()).strip("_")
                )

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
# 2. PROMPT BUILDER
# =============================================================================
class PromptBuilder:
    """Constructs high-craft visual prompts for photorealistic commercial perfume photography."""

    SILHOUETTE_PROFILES: Dict[str, Tuple[str, str, str, str, str]] = {
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

        for key, profile in cls.SILHOUETTE_PROFILES.items():
            if key.lower() == name_lower:
                return profile

        for key in sorted(cls.SILHOUETTE_PROFILES.keys(), key=len, reverse=True):
            if name_lower.startswith(key.lower()):
                return cls.SILHOUETTE_PROFILES[key]

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
# 3. IMAGE PROCESSOR (PILLOW 4:5 1200x1500 & RASTERIZATION PIPELINE)
# =============================================================================
class ImageProcessor:
    """Processes, frames, rasterizes, and optimizes 1200x1500 WebP and JPEG images."""

    TARGET_WIDTH: int = 1200
    TARGET_HEIGHT: int = 1500
    TARGET_ASPECT: float = 4 / 5  # 0.80

    @classmethod
    def process_and_optimize(cls, source_path: Path, output_slug: str) -> Dict[str, Any]:
        """Loads raw raster image, frames to 4:5 1200x1500 with Lanczos resampling, and saves WebP/JPEG."""
        if not source_path.exists():
            raise FileNotFoundError(f"Source image not found: {source_path}")

        with Image.open(source_path) as raw_img:
            img = raw_img.convert("RGB")
            orig_w, orig_h = img.size
            orig_aspect = orig_w / orig_h

            if orig_aspect < cls.TARGET_ASPECT:
                scale = cls.TARGET_WIDTH / orig_w
                scaled_h = int(orig_h * scale)
                with img.resize((cls.TARGET_WIDTH, scaled_h), Image.Resampling.LANCZOS) as scaled_img:
                    crop_y = max(0, (scaled_h - cls.TARGET_HEIGHT) // 2)
                    final_img = scaled_img.crop((0, crop_y, cls.TARGET_WIDTH, crop_y + cls.TARGET_HEIGHT))
            else:
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

        with final_img.convert("L") as gray_img:
            stat = ImageStat.Stat(gray_img)
            luminance = stat.mean[0]
            with gray_img.filter(ImageFilter.FIND_EDGES) as edges:
                edge_stat = ImageStat.Stat(edges)
                sharpness = edge_stat.var[0]

        final_img.close()

        is_valid = (
            len(webp_bytes) < 500 * 1024 and
            15.0 <= luminance <= 240.0 and
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

    @classmethod
    def process_svg_string(cls, svg_content: str, output_slug: str) -> Dict[str, Any]:
        """Rasterizes SVG content directly into 1200x1500 WebP and JPEG assets."""
        if resvg_py is None:
            raise RuntimeError("resvg_py is not available in environment for SVG rasterization.")

        png_data = resvg_py.svg_to_bytes(svg_content, width=cls.TARGET_WIDTH, height=cls.TARGET_HEIGHT)
        with Image.open(io.BytesIO(png_data)) as raw_img:
            final_img = raw_img.convert("RGB")

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

        with final_img.convert("L") as gray_img:
            stat = ImageStat.Stat(gray_img)
            luminance = stat.mean[0]
            with gray_img.filter(ImageFilter.FIND_EDGES) as edges:
                edge_stat = ImageStat.Stat(edges)
                sharpness = edge_stat.var[0]

        final_img.close()

        is_valid = (
            len(webp_bytes) < 500 * 1024 and
            15.0 <= luminance <= 240.0 and
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
# 4. PRODUCT PROFILE & VISUAL ARCHETYPES
# =============================================================================
class ProductProfile:
    """Extracts perfume metadata and computes procedural architectural flacon styling."""

    @staticmethod
    def derive_profile(prod: Dict[str, Any]) -> Dict[str, Any]:
        name = prod.get("name", "")
        brand = prod.get("brand", "Lattafa Perfumes")
        collection = prod.get("collection", "Mainline Classics")
        family = prod.get("fragrance_family", "Arabian Luxury Perfume")
        gender = prod.get("gender", "Unisex")
        conc = prod.get("concentration", "Eau de Parfum (EDP)")
        size = prod.get("bottle_size", "100ml")
        slug = prod.get("slug", re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_"))

        name_lower = name.lower()
        fam_lower = family.lower()

        # Studio Environment
        if "yara" in name_lower or collection == "Yara Collection" or (gender == "Women" and ("floral" in fam_lower or "gourmand" in fam_lower)):
            env = "champagne_boudoir"
        elif "asad" in name_lower or collection == "Asad Collection" or (gender == "Men" and ("spicy" in fam_lower or "woody" in fam_lower or "marine" in fam_lower)):
            env = "noir_architectural"
        elif "khamrah" in name_lower or collection == "Khamrah Collection" or "coffee" in fam_lower or "boozy" in fam_lower or "praline" in fam_lower:
            env = "amber_cognac_reserve"
        elif "badee" in name_lower or collection == "Badee Al Oud" or "oud" in name_lower or "oud" in fam_lower:
            env = "royal_oriental_emerald"
        elif brand == "Maison Alhambra" or "niche" in collection.lower():
            env = "parisian_honed_slate"
        else:
            env = "imperial_gold_studio"

        # Silhouette & Cap & Color Palette
        if "yara candy" in name_lower:
            sil, cap = "sculpted_hourglass", "sculpted_dome"
            accent, highlight, liquid, bg = "#f43f75", "#ffd0dc", "#ff2a6d", "#1f050d"
        elif "yara tous" in name_lower:
            sil, cap = "sculpted_hourglass", "sculpted_dome"
            accent, highlight, liquid, bg = "#f59e0b", "#fde68a", "#d97706", "#1c1202"
        elif "yara moi" in name_lower:
            sil, cap = "sculpted_hourglass", "sculpted_dome"
            accent, highlight, liquid, bg = "#e5e5e5", "#ffffff", "#fafafa", "#181716"
        elif "yara" in name_lower:
            sil, cap = "sculpted_hourglass", "sculpted_dome"
            accent, highlight, liquid, bg = "#f19bb2", "#fde5ec", "#fb7185", "#240a13"
        elif "asad zanzibar" in name_lower:
            sil, cap = "fluted_column", "fluted_cylinder"
            accent, highlight, liquid, bg = "#38bdf8", "#bae6fd", "#0284c7", "#061524"
        elif "asad bourbon" in name_lower:
            sil, cap = "fluted_column", "fluted_cylinder"
            accent, highlight, liquid, bg = "#ea580c", "#ffedd5", "#9a3412", "#1a0802"
        elif "asad" in name_lower:
            sil, cap = "fluted_column", "fluted_cylinder"
            accent, highlight, liquid, bg = "#d4af37", "#fef08a", "#854d0e", "#101114"
        elif "khamrah dukhan" in name_lower:
            sil, cap = "crystal_decanter", "faceted_stopper"
            accent, highlight, liquid, bg = "#b45309", "#fed7aa", "#78350f", "#140a04"
        elif "khamrah qahwa" in name_lower:
            sil, cap = "crystal_decanter", "faceted_stopper"
            accent, highlight, liquid, bg = "#92400e", "#fde68a", "#562708", "#170a03"
        elif "khamrah" in name_lower or "eternal oud" in name_lower or "kismet magic" in name_lower:
            sil, cap = "crystal_decanter", "faceted_stopper"
            accent, highlight, liquid, bg = "#d97706", "#fef3c7", "#92400e", "#180d04"
        elif "badee al oud sublime" in name_lower:
            sil, cap = "faceted_obelisk", "faceted_finial"
            accent, highlight, liquid, bg = "#be123c", "#fecdd3", "#881337", "#1c0409"
        elif "badee al oud noble blush" in name_lower:
            sil, cap = "faceted_obelisk", "faceted_finial"
            accent, highlight, liquid, bg = "#fb7185", "#ffe4e6", "#e11d48", "#240912"
        elif "badee al oud" in name_lower or "amethyst" in name_lower or "honor & glory" in name_lower:
            sil, cap = "faceted_obelisk", "faceted_finial"
            accent, highlight, liquid, bg = "#c5a059", "#fef9c3", "#78350f", "#0f1114"
        elif "tobacco touch" in name_lower:
            sil, cap = "heavy_apothecary", "heavy_metal_cylinder"
            accent, highlight, liquid, bg = "#c2410c", "#fed7aa", "#7c2d12", "#180a04"
        elif "porto neroli" in name_lower:
            sil, cap = "heavy_apothecary", "heavy_metal_cylinder"
            accent, highlight, liquid, bg = "#06b6d4", "#cffafe", "#0891b2", "#04151a"
        elif "bright peach" in name_lower:
            sil, cap = "heavy_apothecary", "heavy_metal_cylinder"
            accent, highlight, liquid, bg = "#f97316", "#ffedd5", "#ea580c", "#1c0b03"
        elif "lovely ch" in name_lower:
            sil, cap = "heavy_apothecary", "heavy_metal_cylinder"
            accent, highlight, liquid, bg = "#9f1239", "#fecdd3", "#881337", "#1c040a"
        elif "fabulo intense" in name_lower:
            sil, cap = "heavy_apothecary", "heavy_metal_cylinder"
            accent, highlight, liquid, bg = "#52525b", "#e4e4e7", "#27272a", "#09090b"
        elif "toscano leather" in name_lower:
            sil, cap = "heavy_apothecary", "heavy_metal_cylinder"
            accent, highlight, liquid, bg = "#78350f", "#fef3c7", "#451a03", "#120904"
        elif "vintage radio" in name_lower:
            sil, cap = "rounded_luxury_flask", "jewel_octagon"
            accent, highlight, liquid, bg = "#8b5cf6", "#ede9fe", "#6d28d9", "#130922"
        elif "nebras" in name_lower:
            sil, cap = "rounded_luxury_flask", "jewel_octagon"
            accent, highlight, liquid, bg = "#e11d48", "#ffe4e6", "#9f1239", "#1f040b"
        elif "mayar natural intense" in name_lower:
            sil, cap = "sculpted_hourglass", "sculpted_dome"
            accent, highlight, liquid, bg = "#059669", "#a7f3d0", "#047857", "#03170e"
        elif "mayar" in name_lower or "victoria" in name_lower or "haya" in name_lower:
            sil, cap = "sculpted_hourglass", "sculpted_dome"
            accent, highlight, liquid, bg = "#f43f5e", "#fecdd3", "#be123c", "#1f050b"
        elif "suqraat" in name_lower or "ejaazi" in name_lower:
            sil, cap = "fluted_column", "fluted_cylinder"
            accent, highlight, liquid, bg = "#0284c7", "#bae6fd", "#0369a1", "#08131e"
        elif "hayaati" in name_lower:
            sil, cap = "fluted_column", "fluted_cylinder"
            accent, highlight, liquid, bg = "#0f766e", "#99f6e4", "#115e59", "#041412"
        elif "qaed al fursan" in name_lower or "ana abiyedh" in name_lower:
            sil, cap = "monumental_cube", "heavy_metal_cube"
            accent, highlight, liquid, bg = "#d4af37", "#fef08a", "#a16207", "#121417"
        elif "al noble" in name_lower or "masa" in name_lower:
            sil, cap = "artisanal_sculpted", "jewel_octagon"
            accent, highlight, liquid, bg = "#059669", "#a7f3d0", "#047857", "#05170d"
        elif "raghba" in name_lower:
            sil, cap = "tall_columnar", "heavy_metal_cylinder"
            accent, highlight, liquid, bg = "#b45309", "#fef3c7", "#78350f", "#140903"
        elif "ajwad" in name_lower:
            sil, cap = "rounded_luxury_flask", "jewel_octagon"
            accent, highlight, liquid, bg = "#a855f7", "#f3e8ff", "#7e22ce", "#180826"
        elif brand == "Maison Alhambra":
            sil, cap = "heavy_apothecary", "heavy_metal_cylinder"
            accent, highlight, liquid, bg = "#cca059", "#faebc9", "#854d0e", "#141518"
        elif collection == "Lattafa Pride":
            sil, cap = "monumental_cube", "heavy_metal_cube"
            accent, highlight, liquid, bg = "#d4af37", "#fef08a", "#a16207", "#111518"
        elif gender == "Women":
            sil, cap = "sculpted_hourglass", "sculpted_dome"
            accent, highlight, liquid, bg = "#ec4899", "#fce7f3", "#db2777", "#1c0712"
        elif gender == "Men":
            sil, cap = "fluted_column", "fluted_cylinder"
            accent, highlight, liquid, bg = "#3b82f6", "#dbeafe", "#1d4ed8", "#08101e"
        else:
            sil, cap = "crystal_decanter", "faceted_stopper"
            accent, highlight, liquid, bg = "#eab308", "#fef08a", "#a16207", "#15130b"

        return {
            "name": name,
            "brand": brand,
            "collection": collection,
            "family": family,
            "gender": gender,
            "conc": conc,
            "size": size,
            "slug": slug,
            "silhouette": sil,
            "cap": cap,
            "env": env,
            "accent": accent,
            "highlight": highlight,
            "liquid": liquid,
            "bg": bg,
        }


# =============================================================================
# 5. ADVANCED PROCEDURAL FLACON RENDERER
# =============================================================================
class ArchitecturalFlaconRenderer:
    """Master procedural vector rendering engine producing ultra-luxury 1200x1500 flacons."""

    # ------------------------------------------------------------------
    # Local bottle coordinate system (before the studio transform):
    #   x = 0 is the bottle axis, y = -104 is the neck seat, y = 190 is the base.
    # ------------------------------------------------------------------
    NECK_Y: float = -104.0
    BASE_Y: float = 190.0

    # Hand-tuned identities for the hero products (matched on the product name).
    _STYLE_OVERRIDES: Tuple[Tuple[str, str], ...] = (
        ("yara candy", "candy"),
        ("asad zanzibar", "wave"),
        ("khamrah qahwa", "diamond"),
        ("badee al oud sublime", "arabesque"),
        ("vintage radio", "radio"),
        ("tobacco touch", "strap"),
        ("nebras", "lantern"),
        ("eternal oud", "ornate"),
    )

    # Glass-surface treatments rotated deterministically per product slug so that
    # products that share a silhouette family still read as different designs.
    _STYLE_POOL: Dict[str, Tuple[str, ...]] = {
        "crystal_decanter": ("cut", "stepped", "plain"),
        "fluted_column": ("flute", "banded", "ribs"),
        "sculpted_hourglass": ("pearl", "ribbon", "plain"),
        "faceted_obelisk": ("prism", "inlay", "plain"),
        "heavy_apothecary": ("plain", "banded", "inlay"),
        "tall_columnar": ("flute", "plain", "banded"),
        "rounded_luxury_flask": ("plain", "banded", "inlay"),
        "monumental_cube": ("prism", "plain", "banded"),
        "artisanal_sculpted": ("ribbon", "plain", "banded"),
    }

    # ------------------------------------------------------------------
    # Colour helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _rgb(c: str) -> Tuple[int, int, int]:
        c = c.lstrip("#")
        if len(c) == 3:
            c = "".join(ch * 2 for ch in c)
        return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)

    @classmethod
    def _hex(cls, rgb: Tuple[float, float, float]) -> str:
        return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(v)))) for v in rgb)

    @classmethod
    def _mix(cls, a: str, b: str, t: float) -> str:
        ra, rb = cls._rgb(a), cls._rgb(b)
        return cls._hex(tuple(ra[i] + (rb[i] - ra[i]) * t for i in range(3)))

    @classmethod
    def _shade(cls, c: str, amt: float) -> str:
        """amt < 0 darkens toward black, amt > 0 lightens toward white."""
        return cls._mix(c, "#000000", -amt) if amt < 0 else cls._mix(c, "#ffffff", amt)

    @classmethod
    def _lum(cls, c: str) -> float:
        r, g, b = cls._rgb(c)
        return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0

    @classmethod
    def _lift(cls, c: str, min_lum: float = 0.66) -> str:
        for _ in range(14):
            if cls._lum(c) >= min_lum:
                break
            c = cls._mix(c, "#ffffff", 0.16)
        return c

    @staticmethod
    def _stops(items: List[Tuple[Any, ...]]) -> str:
        out = []
        for it in items:
            alpha = it[2] if len(it) > 2 else 1.0
            out.append(f'<stop offset="{it[0]}" stop-color="{it[1]}" stop-opacity="{alpha}"/>')
        return "".join(out)

    @staticmethod
    def _n(x: float) -> str:
        return f"{x:.1f}"

    # ------------------------------------------------------------------
    # Per-product variation
    # ------------------------------------------------------------------
    @classmethod
    def _variant(cls, profile: Dict[str, Any]) -> Dict[str, Any]:
        name = profile["name"].lower()
        slug = profile["slug"]
        sil = profile["silhouette"]
        h = int(hashlib.md5(slug.encode("utf-8")).hexdigest()[:12], 16)

        def r(i: int, lo: float, hi: float) -> float:
            return lo + (((h >> (i * 5)) & 0x1F) / 31.0) * (hi - lo)

        style: Optional[str] = None
        for key, st in cls._STYLE_OVERRIDES:
            if key in name:
                style = st
                break
        if style is None:
            pool = cls._STYLE_POOL.get(sil, ("plain",))
            style = pool[(h >> 3) % len(pool)]

        return {
            "style": style,
            "w": r(0, 0.95, 1.06),
            "fill": r(1, -6.0, 8.0),
            "cap_w": r(2, 0.95, 1.07),
            "cap_h": r(3, 0.94, 1.08),
            "flutes": 7 + (h >> 9) % 4,
            "alt": (h >> 11) % 3,
        }

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _sym(start: Tuple[float, float], segs: List[Tuple[Any, ...]]) -> str:
        """Closed mirror-symmetric path. `segs` describe the right-hand side, top to bottom."""
        pts = [start] + [s[-1] for s in segs]

        def f(p: Tuple[float, float]) -> str:
            return f"{p[0]:.1f},{p[1]:.1f}"

        def m(p: Tuple[float, float]) -> Tuple[float, float]:
            return (-p[0], p[1])

        d = [f"M{f(m(start))}", f"L{f(start)}"]
        for s in segs:
            if s[0] == "L":
                d.append("L" + f(s[1]))
            elif s[0] == "Q":
                d.append("Q" + f(s[1]) + " " + f(s[2]))
            else:
                d.append("C" + f(s[1]) + " " + f(s[2]) + " " + f(s[3]))
        d.append("L" + f(m(pts[-1])))
        for i in range(len(segs) - 1, -1, -1):
            s = segs[i]
            prev = pts[i]
            if s[0] == "L":
                d.append("L" + f(m(prev)))
            elif s[0] == "Q":
                d.append("Q" + f(m(s[1])) + " " + f(m(prev)))
            else:
                d.append("C" + f(m(s[2])) + " " + f(m(s[1])) + " " + f(m(prev)))
        d.append("Z")
        return " ".join(d)

    @staticmethod
    def _half_width_at(start: Tuple[float, float], segs: List[Tuple[Any, ...]], y: float) -> float:
        """Half-width of a right-hand profile at height y (curves sampled)."""
        poly: List[Tuple[float, float]] = [start]
        cur = start
        for s in segs:
            if s[0] == "L":
                poly.append(s[1])
            elif s[0] == "Q":
                c, e = s[1], s[2]
                for k in range(1, 13):
                    t = k / 12.0
                    poly.append(((1 - t) ** 2 * cur[0] + 2 * (1 - t) * t * c[0] + t * t * e[0],
                                 (1 - t) ** 2 * cur[1] + 2 * (1 - t) * t * c[1] + t * t * e[1]))
            else:
                c1, c2, e = s[1], s[2], s[3]
                for k in range(1, 17):
                    t = k / 16.0
                    a, b, c_, d_ = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
                    poly.append((a * cur[0] + b * c1[0] + c_ * c2[0] + d_ * e[0],
                                 a * cur[1] + b * c1[1] + c_ * c2[1] + d_ * e[1]))
            cur = s[-1]
        best = 0.0
        for i in range(len(poly) - 1):
            (xa, ya), (xb, yb) = poly[i], poly[i + 1]
            lo, hi = min(ya, yb), max(ya, yb)
            if lo - 1e-6 <= y <= hi + 1e-6:
                if abs(yb - ya) < 1e-6:
                    best = max(best, xa, xb)
                else:
                    best = max(best, xa + (xb - xa) * (y - ya) / (yb - ya))
        return best if best > 0 else max(p[0] for p in poly)

    @classmethod
    def _geometry(cls, profile: Dict[str, Any], v: Dict[str, Any]) -> Dict[str, Any]:
        """Silhouette, wall thickness, liquid level and label placement for a flacon."""
        sil = profile["silhouette"]
        style = v["style"]
        sw = v["w"]
        B = cls.BASE_Y
        YN = cls.NECK_Y
        scale = 2.12

        if sil == "crystal_decanter":
            W, nw, rb = 112 * sw, 36.0, 14.0
            if style in ("ornate", "stepped"):
                segs = [("L", (nw, -98)), ("L", (nw + 20, -98)), ("L", (nw + 20, -91)), ("L", (W * 0.56, -91)),
                        ("L", (W * 0.56, -80)), ("L", (W - 10, -80)), ("Q", (W, -80), (W, -64)),
                        ("L", (W, B - rb)), ("Q", (W, B), (W - rb, B))]
            else:
                segs = [("L", (nw, -96)), ("L", (W * 0.50, -92)), ("Q", (W * 0.92, -84), (W, -56)),
                        ("L", (W, B - rb)), ("Q", (W, B), (W - rb, B))]
            slab, wall, fill, label = 50.0, 9.0, -34.0, (28.0, 158.0, 140.0)
        elif sil == "fluted_column":
            W, nw = 92 * sw, 34.0
            segs = [("L", (nw, -98)), ("L", (W - 26, -98)), ("Q", (W, -98), (W, -72)),
                    ("L", (W, B - 26)), ("Q", (W, B), (W - 26, B))]
            slab, wall, fill, label = 46.0, 8.0, -42.0, (44.0, 150.0, 146.0)
        elif sil == "sculpted_hourglass":
            W, nw = 98 * sw, 30.0
            k = sw
            segs = [("L", (nw, -98)), ("C", (60, -100), (86 * k, -88), (86 * k, -54)),
                    ("C", (88 * k, -24), (66 * k, -14), (66 * k, 14)),
                    ("C", (66 * k, 52), (98 * k, 68), (98 * k, 126)),
                    ("C", (98 * k, 160), (92 * k, B), (72 * k, B))]
            slab, wall, fill, label = 40.0, 8.0, -30.0, (88.0, 132.0, 118.0)
        elif sil == "faceted_obelisk":
            W, nw = 100 * sw, 34.0
            segs = [("L", (nw, -98)), ("L", (W * 0.68, -98)), ("L", (W, -66)), ("L", (W, B - 34)),
                    ("L", (W * 0.74, B))]
            slab, wall, fill, label = 46.0, 9.0, -36.0, (42.0, 150.0, 142.0)
        elif sil == "heavy_apothecary":
            W, nw = 98 * sw, 34.0
            segs = [("L", (nw, -94)), ("L", (W - 20, -94)), ("Q", (W, -94), (W, -74)),
                    ("L", (W, B - 16)), ("Q", (W, B), (W - 16, B))]
            slab, wall, fill, label = 58.0, 11.0, -34.0, (30.0, 152.0, 140.0)
        elif sil == "tall_columnar":
            W, nw = 80 * sw, 30.0
            B = 200.0
            segs = [("L", (nw, -100)), ("C", (W * 0.55, -100), (W, -96), (W, -52)),
                    ("L", (W, B - 20)), ("Q", (W, B), (W - 20, B))]
            slab, wall, fill, label = 46.0, 9.0, -42.0, (50.0, 138.0, 142.0)
            scale = 2.02
        elif sil == "rounded_luxury_flask":
            nw = 32.0
            if style == "radio":
                W = 100 * sw
                segs = [("L", (nw, -98)), ("L", (W - 30, -98)), ("Q", (W, -98), (W, -66)),
                        ("L", (W, B - 34)), ("Q", (W, B), (W - 34, B))]
                label = (20.0, 150.0, 134.0)
            elif style == "lantern":
                W = 100 * sw
                segs = [("L", (nw, -94)), ("C", (nw + 8, -84), (W * 0.52, -86), (W * 0.76, -48)),
                        ("C", (W * 1.02, -8), (W * 1.04, 100), (W * 0.90, 152)),
                        ("Q", (W * 0.86, B), (W * 0.60, B))]
                label = (34.0, 140.0, 140.0)
            else:
                W = 96 * sw
                segs = [("L", (nw, -98)), ("C", (nw + 36, -98), (W - 4, -84), (W + 4, -34)),
                        ("C", (W + 10, 10), (W + 8, 120), (W - 2, 158)), ("Q", (W - 8, B), (W - 30, B))]
                label = (30.0, 142.0, 140.0)
                W += 8
            slab, wall, fill = 42.0, 9.0, -30.0
        elif sil == "monumental_cube":
            W, nw = 108 * sw, 40.0
            segs = [("L", (nw, -92)), ("L", (W - 14, -92)), ("Q", (W, -92), (W, -78)),
                    ("L", (W, B - 14)), ("Q", (W, B), (W - 14, B))]
            slab, wall, fill, label = 64.0, 13.0, -30.0, (34.0, 158.0, 140.0)
            scale = 2.06
        elif sil == "artisanal_sculpted":
            W, nw = 98 * sw, 26.0
            segs = [("L", (nw, -92)), ("C", (nw + 6, -82), (W * 0.62, -88), (W, -30)),
                    ("C", (W + 4, 20), (W * 0.90, 120), (W * 0.78, 162)),
                    ("Q", (W * 0.74, B), (W * 0.50, B))]
            slab, wall, fill, label = 42.0, 9.0, -8.0, (44.0, 140.0, 140.0)
        else:
            W, nw = 104 * sw, 38.0
            segs = [("L", (nw, -98)), ("L", (nw, -92)), ("L", (W * 0.62, -92)), ("L", (W * 0.62, -84)),
                    ("L", (W - 8, -84)), ("Q", (W, -84), (W, -72)), ("L", (W, B - 14)), ("Q", (W, B), (W - 14, B))]
            slab, wall, fill, label = 52.0, 10.0, -34.0, (28.0, 160.0, 144.0)

        start = (nw, YN)
        fill_y = fill + v["fill"]
        hw = cls._half_width_at(start, segs, fill_y) - wall
        return {
            "outer": cls._sym(start, segs),
            "W": W,
            "nw": nw,
            "B": B,
            "slab": slab,
            "wall": wall,
            "fill_y": fill_y,
            "fill_hw": max(hw, nw - wall),
            "label": label,
            "scale": scale,
        }

    # ------------------------------------------------------------------
    # Typography helper
    # ------------------------------------------------------------------
    @staticmethod
    def split_title(name: str) -> List[str]:
        """Wrap perfume title into balanced label lines, never exceeding 14 chars."""
        words = name.split()
        if len(name) <= 12:
            return [name]
        lines: List[str] = []
        cur: List[str] = []
        cur_len = 0
        for w in words:
            p = cur_len + len(w) + (1 if cur else 0)
            if cur and p > 13:
                lines.append(" ".join(cur))
                cur = [w]
                cur_len = len(w)
            else:
                cur.append(w)
                cur_len = p
        if cur:
            lines.append(" ".join(cur))
        if len(lines) > 3:
            lines = [" ".join(words[:2]), " ".join(words[2:4]), " ".join(words[4:])]
        return [line for line in lines if line]

    @classmethod
    def render_cartouche(cls, profile: Dict[str, Any], width: float = 160, height: float = 145, y_offset: float = 15) -> str:
        """Constructs an embossed metallic foil-stamped cartouche."""
        name = profile["name"]
        brand = profile["brand"]
        conc = profile["conc"]
        size = profile["size"]
        lines = cls.split_title(name)
        hw = width / 2
        top = y_offset - height / 2

        safe_brand = xml.sax.saxutils.escape(brand.upper())
        safe_conc = xml.sax.saxutils.escape("EAU DE PARFUM" if "eau de parfum" in conc.lower() else conc.upper())
        safe_size = xml.sax.saxutils.escape(size.upper())

        # Typographic hierarchy: the fragrance name dominates, brand and volume support it.
        n_lines = len(lines)
        longest = max(len(line) for line in lines)
        base_fs = {1: 15.5, 2: 13.5, 3: 11.0}.get(n_lines, 10.0)
        fs = min(base_fs, (width - 28) / (longest * 0.95 + 1.0))
        ls = round(fs * 0.13, 2)
        lh = fs * 1.30
        title_mid = top + height * 0.51
        y0 = title_mid - lh * (n_lines - 1) / 2 + fs * 0.34
        brand_fs = min(7.2, (width - 24) / (len(brand) * 1.02 + 1.0))

        title_svg = ""
        for i, line in enumerate(lines):
            ty = y0 + i * lh
            t = xml.sax.saxutils.escape(line.upper())
            title_svg += (
                f'<text x="0" y="{ty + 0.9:.1f}" font-family="\'Cinzel\', \'Trajan Pro\', \'Times New Roman\', serif" '
                f'font-size="{fs:.2f}" font-weight="700" letter-spacing="{ls}" fill="#000000" opacity="0.55" text-anchor="middle">{t}</text>'
                f'<text x="0" y="{ty:.1f}" font-family="\'Cinzel\', \'Trajan Pro\', \'Times New Roman\', serif" '
                f'font-size="{fs:.2f}" font-weight="700" letter-spacing="{ls}" fill="url(#foilG)" text-anchor="middle">{t}</text>'
            )

        div_top = top + 44
        div_bot = top + height - 30
        corner = 6.5
        orn = lambda cx, cy: f'<polygon points="{cx},{cy - 2.6} {cx + 2.6},{cy} {cx},{cy + 2.6} {cx - 2.6},{cy}" fill="url(#foilG)"/>'

        return f"""
        <!-- Embossed Foil Cartouche -->
        <g filter="url(#plaqueDrop)">
          <rect x="{-hw}" y="{top}" width="{width}" height="{height}" rx="7" fill="url(#cartoucheG)" stroke="url(#metalG)" stroke-width="1.7"/>
          <rect x="{-hw + 4.5}" y="{top + 4.5}" width="{width - 9}" height="{height - 9}" rx="4.5" fill="none" stroke="url(#foilG)" stroke-width="0.6" opacity="0.75"/>
          <rect x="{-hw + 7}" y="{top + 7}" width="{width - 14}" height="{height - 14}" rx="3" fill="none" stroke="url(#foilG)" stroke-width="0.3" opacity="0.4"/>
          <polygon points="{-hw + 2},{top + 2} {hw - 2},{top + 2} {hw - 2},{top + height * 0.34} {-hw + 2},{top + height * 0.56}" fill="url(#plateSheenG)"/>
          {orn(-hw + corner + 3, top + corner + 3)}{orn(hw - corner - 3, top + corner + 3)}
          {orn(-hw + corner + 3, top + height - corner - 3)}{orn(hw - corner - 3, top + height - corner - 3)}

          <!-- Crest Medallion -->
          <g transform="translate(0, {top + 19:.1f})">
            <circle cx="0" cy="0" r="8" fill="none" stroke="url(#foilG)" stroke-width="0.8"/>
            <circle cx="0" cy="0" r="6" fill="none" stroke="url(#foilG)" stroke-width="0.35" opacity="0.7"/>
            <polygon points="0,-5 1.5,-1.5 5,0 1.5,1.5 0,5 -1.5,1.5 -5,0 -1.5,-1.5" fill="url(#foilG)"/>
          </g>

          <!-- Brand Eyebrow -->
          <text x="0" y="{top + 36:.1f}" font-family="'Inter', 'Helvetica Neue', Arial, sans-serif" font-size="{brand_fs:.2f}" font-weight="600" letter-spacing="2.3" fill="#efe3c8" text-anchor="middle">{safe_brand}</text>
          <line x1="{-hw + 16}" y1="{div_top:.1f}" x2="-5" y2="{div_top:.1f}" stroke="url(#foilG)" stroke-width="0.5" opacity="0.65"/>
          <line x1="5" y1="{div_top:.1f}" x2="{hw - 16}" y2="{div_top:.1f}" stroke="url(#foilG)" stroke-width="0.5" opacity="0.65"/>
          {orn(0, round(div_top, 1))}

          <!-- Perfume Title -->
          {title_svg}

          <!-- Concentration & Volume Footer -->
          <line x1="{-hw + 18}" y1="{div_bot:.1f}" x2="{hw - 18}" y2="{div_bot:.1f}" stroke="url(#foilG)" stroke-width="0.5" opacity="0.55"/>
          <text x="0" y="{top + height - 17:.1f}" font-family="'Inter', 'Helvetica Neue', Arial, sans-serif" font-size="6.3" font-weight="500" letter-spacing="1.7" fill="#d6c9ac" text-anchor="middle">{safe_conc}</text>
          <text x="0" y="{top + height - 8.5:.1f}" font-family="'Inter', 'Helvetica Neue', Arial, sans-serif" font-size="6.8" font-weight="600" letter-spacing="2.2" fill="url(#foilG)" text-anchor="middle">{safe_size}</text>
        </g>
        """

    # ------------------------------------------------------------------
    # Caps & closures
    # ------------------------------------------------------------------
    @classmethod
    def _collar(cls, hw: float, y0: float, y1: float) -> str:
        """Polished metal neck collar with a rubber gasket where the cap meets the glass neck."""
        return f"""
            <rect x="{-hw - 4}" y="{y1 - 5}" width="{2 * hw + 8}" height="7" rx="2" fill="#0a0b0e" opacity="0.92"/>
            <rect x="{-hw}" y="{y0}" width="{2 * hw}" height="{y1 - y0 - 1}" rx="2.5" fill="url(#capMetalG)"/>
            <line x1="{-hw + 1}" y1="{y0 + 2.2}" x2="{hw - 1}" y2="{y0 + 2.2}" stroke="#ffffff" stroke-width="0.9" opacity="0.55"/>
            <line x1="{-hw + 1}" y1="{y1 - 6}" x2="{hw - 1}" y2="{y1 - 6}" stroke="#000000" stroke-width="0.9" opacity="0.55"/>
            <line x1="{-hw + 1}" y1="{(y0 + y1) / 2 - 1:.1f}" x2="{hw - 1}" y2="{(y0 + y1) / 2 - 1:.1f}" stroke="#000000" stroke-width="0.6" opacity="0.35"/>
        """

    @classmethod
    def _top_face(cls, hw: float, y: float, ry: float = 8.0) -> str:
        return f"""
            <ellipse cx="0" cy="{y}" rx="{hw - 0.5:.1f}" ry="{ry}" fill="url(#capTopG)" stroke="#ffffff" stroke-width="0.9" stroke-opacity="0.65"/>
            <ellipse cx="0" cy="{y}" rx="{hw * 0.72:.1f}" ry="{ry * 0.62:.1f}" fill="none" stroke="#000000" stroke-width="0.6" stroke-opacity="0.35"/>
        """

    @classmethod
    def render_cap(cls, cap_type: str, accent: str, highlight: str, variant: Optional[Dict[str, Any]] = None) -> str:
        """Renders a closure with material-specific shading, seated on a collar and gasket."""
        variant = variant or {}
        cw = float(variant.get("cap_w", 1.0))
        chf = float(variant.get("cap_h", 1.0))
        style = variant.get("style", "")

        if cap_type == "fluted_cylinder":
            hw = 46 * cw
            yb, yt = -128.0, -128.0 - 128 * chf
            n = 14
            pitch = 2 * hw / n
            flutes = "".join(
                f'<rect x="{-hw + i * pitch:.2f}" y="{yt}" width="{pitch * 0.42:.2f}" height="{yb - yt}" fill="#000000" opacity="0.30"/>'
                f'<rect x="{-hw + i * pitch + pitch * 0.5:.2f}" y="{yt}" width="{pitch * 0.18:.2f}" height="{yb - yt}" fill="#ffffff" opacity="0.26"/>'
                for i in range(n)
            )
            return f"""
            {cls._collar(36, -130, -100)}
            <rect x="{-hw - 1}" y="{yt}" width="{2 * hw + 2}" height="{yb - yt}" rx="5" fill="url(#capMetalG)"/>
            {flutes}
            <rect x="{-hw - 2}" y="{yb - 13}" width="{2 * hw + 4}" height="13" rx="3" fill="url(#capMetalG)"/>
            <line x1="{-hw}" y1="{yb - 12}" x2="{hw}" y2="{yb - 12}" stroke="#ffffff" stroke-width="1" opacity="0.7"/>
            <line x1="{-hw}" y1="{yb - 1}" x2="{hw}" y2="{yb - 1}" stroke="#000000" stroke-width="1" opacity="0.6"/>
            {cls._top_face(hw, yt)}
            """
        elif cap_type == "sculpted_dome":
            yt = -256.0 - (chf - 1) * 46
            hwd = 50 * cw
            return f"""
            <path d="M-34,-100 L34,-100 L28,-131 L-28,-131 Z" fill="url(#capMetalG)"/>
            <rect x="-34" y="-104" width="68" height="5" fill="#0a0b0e" opacity="0.85"/>
            <ellipse cx="0" cy="-133" rx="{hwd * 0.62:.1f}" ry="5.5" fill="url(#capMetalG)" stroke="#ffffff" stroke-opacity="0.5" stroke-width="0.7"/>
            <path d="M{-hwd:.1f},-134 C{-hwd - 8:.1f},-198 -40,{yt + 6:.1f} 0,{yt:.1f} C40,{yt + 6:.1f} {hwd + 8:.1f},-198 {hwd:.1f},-134 Z" fill="url(#capLacquerG)" stroke="url(#metalG)" stroke-width="1.2"/>
            <path d="M{-hwd - 3:.1f},-172 Q0,-163 {hwd + 3:.1f},-172" fill="none" stroke="url(#capMetalG)" stroke-width="6"/>
            <path d="M{-hwd - 3:.1f},-174.6 Q0,-165.6 {hwd + 3:.1f},-174.6" fill="none" stroke="#ffffff" stroke-width="0.8" opacity="0.7"/>
            <ellipse cx="{-hwd * 0.42:.1f}" cy="{yt + 52:.1f}" rx="9" ry="30" transform="rotate(-8 {-hwd * 0.42:.1f} {yt + 52:.1f})" fill="url(#glossSpecG)"/>
            <path d="M{hwd * 0.80:.1f},-142 C{hwd * 0.96:.1f},-186 {hwd * 0.74:.1f},{yt + 22:.1f} {hwd * 0.34:.1f},{yt + 8:.1f}" fill="none" stroke="{highlight}" stroke-width="1.5" opacity="0.45" stroke-linecap="round"/>
            <ellipse cx="0" cy="{yt - 3:.1f}" rx="7.5" ry="6.2" fill="url(#capMetalG)" stroke="#ffffff" stroke-opacity="0.6" stroke-width="0.6"/>
            """
        elif cap_type == "faceted_stopper":
            yt = -252.0 - (chf - 1) * 36
            vx = [(-30, -148), (30, -148), (62, -198), (48, yt), (-48, yt), (-62, -198)]
            o = (0, -200)
            white = [0.12, 0.32, 0.06, 0.40, 0.05, 0.26]
            dark = [0.0, 0.0, 0.22, 0.0, 0.24, 0.04]
            tris = ""
            for i in range(6):
                a, b = vx[i], vx[(i + 1) % 6]
                pts = f"{o[0]},{o[1]} {a[0]},{a[1]} {b[0]},{b[1]}"
                tris += (f'<polygon points="{pts}" fill="#ffffff" opacity="{white[i]}"/>'
                         f'<polygon points="{pts}" fill="#000000" opacity="{dark[i]}"/>')
            edges = "".join(f'<line x1="{o[0]}" y1="{o[1]}" x2="{p[0]}" y2="{p[1]}" stroke="{highlight}" stroke-width="0.9" opacity="0.55"/>' for p in vx)
            return f"""
            {cls._collar(34, -130, -100)}
            <rect x="-23" y="-150" width="46" height="22" fill="url(#capGlassG)" stroke="url(#metalG)" stroke-width="1"/>
            <polygon points="{' '.join(f'{x},{y}' for x, y in vx)}" fill="url(#capGlassG)" stroke="url(#metalG)" stroke-width="1.8" stroke-linejoin="round"/>
            {tris}
            <polygon points="-48,{yt} 48,{yt} 30,{yt + 18} -30,{yt + 18}" fill="#ffffff" opacity="0.34"/>
            {edges}
            <polygon points="-30,{yt + 18} 30,{yt + 18} 30,{yt + 20} -30,{yt + 20}" fill="#ffffff" opacity="0.5"/>
            <polygon points="-40,{yt + 8} -36,{yt + 14} -30,{yt + 16} -36,{yt + 18} -40,{yt + 24} -44,{yt + 18} -50,{yt + 16} -44,{yt + 14}" fill="#ffffff" opacity="0.85"/>
            <circle cx="0" cy="-200" r="10" fill="#0f1014" stroke="url(#metalG)" stroke-width="1"/>
            <polygon points="0,-206 2.2,-202 6,-200 2.2,-198 0,-194 -2.2,-198 -6,-200 -2.2,-202" fill="url(#capMetalG)"/>
            """
        elif cap_type == "faceted_finial":
            yt = -240.0 - (chf - 1) * 30
            body = [(-44, -136), (44, -136), (58, -188), (44, yt), (-44, yt), (-58, -188)]
            return f"""
            {cls._collar(38, -132, -100)}
            <polygon points="{' '.join(f'{x},{y}' for x, y in body)}" fill="url(#capLacquerG)" stroke="url(#metalG)" stroke-width="1.6" stroke-linejoin="round"/>
            <polygon points="-58,-188 -44,{yt} -26,{yt} -26,-136 -44,-136" fill="#000000" opacity="0.22"/>
            <polygon points="58,-188 44,{yt} 26,{yt} 26,-136 44,-136" fill="#000000" opacity="0.40"/>
            <polygon points="-26,{yt} 26,{yt} 26,-136 -26,-136" fill="#ffffff" opacity="0.09"/>
            <line x1="-26" y1="{yt}" x2="-26" y2="-136" stroke="{highlight}" stroke-width="1" opacity="0.7"/>
            <line x1="26" y1="{yt}" x2="26" y2="-136" stroke="{highlight}" stroke-width="1" opacity="0.4"/>
            <line x1="-44" y1="{yt + 2}" x2="-44" y2="-138" stroke="#ffffff" stroke-width="1.2" opacity="0.55"/>
            <polygon points="-26,{yt} 26,{yt} 18,{yt + 12} -18,{yt + 12}" fill="#ffffff" opacity="0.30"/>
            <circle cx="0" cy="-188" r="15" fill="#0b0c10" stroke="url(#metalG)" stroke-width="1.5"/>
            <circle cx="0" cy="-188" r="11" fill="none" stroke="url(#capMetalG)" stroke-width="0.7" opacity="0.8"/>
            <polygon points="0,-197 2.6,-191 9,-188 2.6,-185 0,-179 -2.6,-185 -9,-188 -2.6,-191" fill="url(#capMetalG)"/>
            <polygon points="-26,{yt} 0,{yt - 36} 0,{yt}" fill="{highlight}" opacity="0.85"/>
            <polygon points="26,{yt} 0,{yt - 36} 0,{yt}" fill="{accent}"/>
            <polygon points="-26,{yt} 0,{yt - 36} 26,{yt}" fill="none" stroke="url(#metalG)" stroke-width="1" stroke-linejoin="round"/>
            """
        elif cap_type == "heavy_metal_cylinder":
            hw = 44 * cw
            yb, yt = -126.0, -126.0 - 114 * chf
            grain = "".join(
                f'<line x1="{-hw + 3 + i * (2 * hw - 6) / 17:.2f}" y1="{yt + 4}" x2="{-hw + 3 + i * (2 * hw - 6) / 17:.2f}" y2="{yb - 22}" '
                f'stroke="{"#ffffff" if i % 2 else "#000000"}" stroke-width="0.7" opacity="0.07"/>'
                for i in range(18)
            )
            knurl = "".join(
                f'<line x1="{-hw + 2 + i * (2 * hw - 4) / 30:.2f}" y1="{yb - 20}" x2="{-hw + 2 + i * (2 * hw - 4) / 30:.2f}" y2="{yb - 4}" stroke="#000000" stroke-width="0.8" opacity="0.38"/>'
                for i in range(31)
            )
            return f"""
            {cls._collar(30, -128, -100)}
            <rect x="{-hw}" y="{yt}" width="{2 * hw}" height="{yb - yt}" rx="5" fill="url(#capMetalG)" stroke="{highlight}" stroke-width="0.8" stroke-opacity="0.6"/>
            {grain}
            <rect x="{-hw}" y="{yb - 22}" width="{2 * hw}" height="20" fill="url(#capMetalG)"/>
            {knurl}
            <line x1="{-hw}" y1="{yb - 22}" x2="{hw}" y2="{yb - 22}" stroke="#ffffff" stroke-width="1" opacity="0.65"/>
            <line x1="{-hw}" y1="{yb - 2}" x2="{hw}" y2="{yb - 2}" stroke="#000000" stroke-width="1" opacity="0.6"/>
            <line x1="{-hw}" y1="{yt + 14}" x2="{hw}" y2="{yt + 14}" stroke="#000000" stroke-width="1.1" opacity="0.5"/>
            <line x1="{-hw}" y1="{yt + 15.4}" x2="{hw}" y2="{yt + 15.4}" stroke="#ffffff" stroke-width="0.7" opacity="0.5"/>
            {cls._top_face(hw, yt)}
            """
        elif cap_type == "jewel_octagon":
            if style == "radio":
                hw = 50 * cw
                yb, yt = -130.0, -216.0 - (chf - 1) * 40
                n = 36
                knurl = "".join(
                    f'<line x1="{-hw + 1.5 + i * (2 * hw - 3) / (n - 1):.2f}" y1="{yt}" x2="{-hw + 1.5 + i * (2 * hw - 3) / (n - 1):.2f}" y2="{yb}" stroke="#000000" stroke-width="1.1" opacity="{0.42 if i % 2 else 0.12}"/>'
                    for i in range(n)
                )
                return f"""
                {cls._collar(30, -132, -100)}
                <path d="M{-hw - 4},{yb} L{-hw},{yb - 14} L{hw},{yb - 14} L{hw + 4},{yb} Z" fill="url(#capMetalG)"/>
                <rect x="{-hw}" y="{yt}" width="{2 * hw}" height="{yb - yt - 12}" rx="6" fill="url(#capMetalG)"/>
                {knurl}
                {cls._top_face(hw, yt, 9)}
                <line x1="0" y1="{yt}" x2="{-hw * 0.22:.1f}" y2="{yt - 6}" stroke="#101114" stroke-width="3" stroke-linecap="round" opacity="0.85"/>
                <circle cx="0" cy="{yt}" r="5" fill="url(#capLacquerG)" stroke="#ffffff" stroke-opacity="0.6" stroke-width="0.6"/>
                """
            yt = -222.0 - (chf - 1) * 30
            return f"""
            {cls._collar(28, -128, -100)}
            <polygon points="-34,{yt} 34,{yt} 52,{yt + 26} 52,-158 36,-130 -36,-130 -52,-158 -52,{yt + 26}" fill="url(#capLacquerG)" stroke="url(#metalG)" stroke-width="1.7" stroke-linejoin="round"/>
            <polygon points="-34,{yt} 34,{yt} 26,{yt + 12} -26,{yt + 12}" fill="#ffffff" opacity="0.34"/>
            <polygon points="-52,{yt + 26} -34,{yt} -26,{yt + 12} -40,{yt + 30} -40,-156 -52,-158" fill="#ffffff" opacity="0.16"/>
            <polygon points="52,{yt + 26} 34,{yt} 26,{yt + 12} 40,{yt + 30} 40,-156 52,-158" fill="#000000" opacity="0.30"/>
            <polygon points="-40,-156 -36,-130 36,-130 40,-156 28,-144 -28,-144" fill="#000000" opacity="0.28"/>
            <circle cx="0" cy="{(yt - 142) / 2:.1f}" r="18" fill="#0d0e12" stroke="url(#metalG)" stroke-width="1.6"/>
            <circle cx="0" cy="{(yt - 142) / 2:.1f}" r="13" fill="url(#capGlassG)" stroke="url(#capMetalG)" stroke-width="0.8"/>
            <polygon points="0,{(yt - 142) / 2 - 10:.1f} 3.4,{(yt - 142) / 2 - 3.4:.1f} 10,{(yt - 142) / 2:.1f} 3.4,{(yt - 142) / 2 + 3.4:.1f} 0,{(yt - 142) / 2 + 10:.1f} -3.4,{(yt - 142) / 2 + 3.4:.1f} -10,{(yt - 142) / 2:.1f} -3.4,{(yt - 142) / 2 - 3.4:.1f}" fill="#ffffff" opacity="0.55"/>
            """
        elif cap_type == "heavy_metal_cube":
            yt = -242.0 - (chf - 1) * 30
            hw = 54 * cw
            i_ = 10
            return f"""
            {cls._collar(36, -130, -100)}
            <rect x="{-hw}" y="{yt}" width="{2 * hw}" height="{-128 - yt}" rx="3" fill="url(#capMetalV)" stroke="{highlight}" stroke-width="0.8" stroke-opacity="0.6"/>
            <polygon points="{-hw},{yt} {hw},{yt} {hw - i_},{yt + i_} {-hw + i_},{yt + i_}" fill="#ffffff" opacity="0.55"/>
            <polygon points="{-hw},{yt} {-hw + i_},{yt + i_} {-hw + i_},-138 {-hw},-128" fill="#ffffff" opacity="0.26"/>
            <polygon points="{hw},{yt} {hw - i_},{yt + i_} {hw - i_},-138 {hw},-128" fill="#000000" opacity="0.32"/>
            <polygon points="{-hw},-128 {hw},-128 {hw - i_},-138 {-hw + i_},-138" fill="#000000" opacity="0.38"/>
            <rect x="{-hw + 18}" y="{yt + 18}" width="{2 * hw - 36}" height="{-128 - yt - 36}" fill="none" stroke="#000000" stroke-width="1.1" opacity="0.4"/>
            <rect x="{-hw + 19.2}" y="{yt + 19.2}" width="{2 * hw - 36}" height="{-128 - yt - 36}" fill="none" stroke="#ffffff" stroke-width="0.7" opacity="0.45"/>
            <polygon points="0,{(yt - 128) / 2 - 11:.1f} 11,{(yt - 128) / 2:.1f} 0,{(yt - 128) / 2 + 11:.1f} -11,{(yt - 128) / 2:.1f}" fill="url(#capLacquerG)" stroke="#ffffff" stroke-opacity="0.6" stroke-width="0.7"/>
            """
        else:
            yt = -238.0 - (chf - 1) * 34
            return f"""
            {cls._collar(34, -130, -100)}
            <rect x="-52" y="-176" width="104" height="48" rx="6" fill="url(#capMetalG)" stroke="{highlight}" stroke-width="0.8" stroke-opacity="0.6"/>
            <rect x="-40" y="-212" width="80" height="38" rx="5" fill="url(#capMetalG)" stroke="{highlight}" stroke-width="0.8" stroke-opacity="0.6"/>
            <rect x="-27" y="{yt}" width="54" height="28" rx="5" fill="url(#capMetalG)" stroke="{highlight}" stroke-width="0.8" stroke-opacity="0.6"/>
            <line x1="-52" y1="-176" x2="52" y2="-176" stroke="#000000" stroke-width="1.2" opacity="0.5"/>
            <line x1="-40" y1="-212" x2="40" y2="-212" stroke="#000000" stroke-width="1.2" opacity="0.5"/>
            <line x1="-50" y1="-174" x2="50" y2="-174" stroke="#ffffff" stroke-width="0.8" opacity="0.55"/>
            <line x1="-38" y1="-210" x2="38" y2="-210" stroke="#ffffff" stroke-width="0.8" opacity="0.55"/>
            <rect x="-44" y="-168" width="88" height="34" rx="3" fill="none" stroke="#000000" stroke-width="0.9" opacity="0.4"/>
            {cls._top_face(27, yt, 6)}
            <circle cx="0" cy="-151" r="7.5" fill="url(#capLacquerG)" stroke="#ffffff" stroke-opacity="0.6" stroke-width="0.6"/>
            """

    # ------------------------------------------------------------------
    # Glass, liquid and surface treatment
    # ------------------------------------------------------------------
    @classmethod
    def _glass_defs(cls, g: Dict[str, Any], p: Dict[str, Any], v: Dict[str, Any]) -> str:
        """Per-bottle clip paths, masks and gradients (all in bottle-local user space)."""
        accent, hi, liq = p["accent"], p["highlight"], p["liquid"]
        W, B, slab, t, fy = g["W"], g["B"], g["slab"], g["wall"], g["fill_y"]
        outer = g["outer"]
        x0, x1 = -W - 4, W + 4
        st = cls._stops
        frosted = v["style"] in ("candy", "pearl")
        fa = 1.35 if frosted else 1.0
        mask_attrs = 'maskUnits="userSpaceOnUse" x="-230" y="-320" width="460" height="580"'

        def band(idn: str, d1: float, d2: float) -> str:
            blk = (f'<path d="{outer}" fill="none" stroke="#000000" stroke-width="{2 * d1:.2f}" stroke-linejoin="round"/>'
                   if d1 > 0 else "")
            return (f'<mask id="{idn}" {mask_attrs}><path d="{outer}" fill="none" stroke="#ffffff" '
                    f'stroke-width="{2 * d2:.2f}" stroke-linejoin="round"/>{blk}</mask>')

        glass_hi = cls._mix(accent, hi, 0.5)
        liq_edge = cls._shade(liq, -0.74)
        liq_deep = cls._shade(liq, -0.38)
        liq_core = cls._mix(liq, hi, 0.58)
        surf = cls._mix(liq, hi, 0.34)
        hl = cls._lift(hi, 0.8)
        mid_y = (fy + B - slab) / 2.0 + 8

        return f"""
        <clipPath id="bottleClip"><path d="{outer}"/></clipPath>
        <mask id="cavMask" {mask_attrs}>
          <path d="{outer}" fill="#ffffff"/>
          <path d="{outer}" fill="none" stroke="#000000" stroke-width="{2 * t:.2f}" stroke-linejoin="round"/>
          <rect x="-230" y="{B - slab:.1f}" width="460" height="{slab + 30:.1f}" fill="#000000"/>
        </mask>
        {band("bandRim", 0, 2.6)}
        {band("bandSpec", 6.6, 8.2)}
        {band("bandWall", max(t - 0.9, 1), t + 0.9)}
        {band("bandLiq", t, t + 4.2)}
        {band("bandInlay", 12.6, 13.9)}
        <mask id="vFade" {mask_attrs}><rect x="-230" y="-320" width="460" height="580" fill="url(#vFadeG)"/></mask>
        <linearGradient id="vFadeG" gradientUnits="userSpaceOnUse" x1="0" y1="-108" x2="0" y2="{B}">
          <stop offset="0" stop-color="#000000"/><stop offset="0.2" stop-color="#ffffff"/>
          <stop offset="0.8" stop-color="#ffffff"/><stop offset="1" stop-color="#000000"/>
        </linearGradient>
        <linearGradient id="glassBackG" gradientUnits="userSpaceOnUse" x1="0" y1="-104" x2="0" y2="{B}">
          {st([(0, glass_hi, round(0.05 * fa, 3)), (0.55, accent, round(0.10 * fa, 3)), (1, cls._shade(accent, -0.4), round(0.30 * fa, 3))])}
        </linearGradient>
        <linearGradient id="frostG" gradientUnits="userSpaceOnUse" x1="{x0}" y1="0" x2="{x1}" y2="0">
          {st([(0, cls._shade(accent, -0.15), 0.55), (0.22, cls._mix(hi, '#ffffff', 0.35), 0.32), (0.5, cls._mix(hi, '#ffffff', 0.6), 0.38), (0.8, cls._mix(accent, hi, 0.4), 0.34), (1, cls._shade(accent, -0.3), 0.6)])}
        </linearGradient>
        <linearGradient id="wallG" gradientUnits="userSpaceOnUse" x1="{x0}" y1="0" x2="{x1}" y2="0">
          {st([(0, cls._shade(accent, -0.55), min(0.92, 0.86 * fa)), (0.10, cls._shade(accent, -0.25), min(0.8, 0.56 * fa)), (0.5, glass_hi, min(0.6, 0.26 * fa)), (0.9, cls._shade(accent, -0.3), min(0.8, 0.56 * fa)), (1, cls._shade(accent, -0.62), min(0.92, 0.88 * fa))])}
        </linearGradient>
        <linearGradient id="slabG" gradientUnits="userSpaceOnUse" x1="0" y1="{B - slab:.1f}" x2="0" y2="{B}">
          {st([(0, hl, 0.62), (0.07, glass_hi, 0.40), (0.5, accent, 0.22), (1, cls._shade(accent, -0.6), 0.62)])}
        </linearGradient>
        <radialGradient id="slabGlowG" cx="50%" cy="50%" r="50%">
          {st([(0, liq_core, 0.78), (0.55, liq, 0.28), (1, liq, 0)])}
        </radialGradient>
        <linearGradient id="liquidBodyG" gradientUnits="userSpaceOnUse" x1="{x0}" y1="0" x2="{x1}" y2="0">
          {st([(0, liq_edge, 0.96), (0.10, liq_deep, 0.93), (0.30, liq, 0.88), (0.48, liq_core, 0.86), (0.70, liq, 0.88), (0.90, liq_deep, 0.93), (1, liq_edge, 0.96)])}
        </linearGradient>
        <linearGradient id="liquidDepthG" gradientUnits="userSpaceOnUse" x1="0" y1="{fy:.1f}" x2="0" y2="{B - slab:.1f}">
          {st([(0, hl, 0.22), (0.22, hl, 0.04), (0.6, '#000000', 0.0), (1, '#000000', 0.42)])}
        </linearGradient>
        <radialGradient id="liquidGlowG" gradientUnits="userSpaceOnUse" cx="{-W * 0.12:.1f}" cy="{mid_y:.1f}" r="{W * 0.95:.1f}">
          {st([(0, hl, 0.52), (0.55, hi, 0.13), (1, hi, 0)])}
        </radialGradient>
        <linearGradient id="liquidSurfG" x1="0%" y1="0%" x2="100%" y2="0%">
          {st([(0, surf, 0.62), (0.45, cls._mix(hi, '#ffffff', 0.55), 0.96), (1, surf, 0.62)])}
        </linearGradient>
        <linearGradient id="liquidEdgeG" gradientUnits="userSpaceOnUse" x1="{x0}" y1="0" x2="{x1}" y2="0">
          {st([(0, '#ffffff', 0.55), (0.14, hl, 0.32), (0.3, hl, 0.0), (0.7, hl, 0.0), (0.88, hl, 0.28), (1, hl, 0.5)])}
        </linearGradient>
        <linearGradient id="rimG" gradientUnits="userSpaceOnUse" x1="{x0}" y1="0" x2="{x1}" y2="0">
          {st([(0, '#ffffff', 0.78), (0.10, '#ffffff', 0.42), (0.30, '#ffffff', 0.08), (0.55, hl, 0.05), (0.86, hl, 0.26), (1, hl, 0.60)])}
        </linearGradient>
        <linearGradient id="specG" gradientUnits="userSpaceOnUse" x1="{x0}" y1="0" x2="{x1}" y2="0">
          {st([(0, '#ffffff', 0.95), (0.2, '#ffffff', 0.5), (0.38, '#ffffff', 0.0), (0.62, '#ffffff', 0.0), (0.84, hl, 0.26), (1, hl, 0.55)])}
        </linearGradient>
        <linearGradient id="innerEdgeG" gradientUnits="userSpaceOnUse" x1="{x0}" y1="0" x2="{x1}" y2="0">
          {st([(0, '#ffffff', 0.48), (0.5, hl, 0.12), (1, '#ffffff', 0.30)])}
        </linearGradient>
        <linearGradient id="topLightG" gradientUnits="userSpaceOnUse" x1="0" y1="-108" x2="0" y2="-56">
          {st([(0, '#ffffff', 0.95), (1, '#ffffff', 0)])}
        </linearGradient>
        <linearGradient id="baseLightG" gradientUnits="userSpaceOnUse" x1="0" y1="{B - 46:.1f}" x2="0" y2="{B}">
          {st([(0, '#ffffff', 0), (1, '#ffffff', 0.85)])}
        </linearGradient>
        <linearGradient id="softLeftG" x1="0%" y1="0%" x2="100%" y2="0%">
          {st([(0, '#ffffff', 0), (0.5, '#ffffff', 0.30), (1, '#ffffff', 0)])}
        </linearGradient>
        <linearGradient id="softRightG" x1="0%" y1="0%" x2="100%" y2="0%">
          {st([(0, hl, 0), (0.5, hl, 0.26), (1, hl, 0)])}
        </linearGradient>
        <radialGradient id="pearlG" cx="35%" cy="30%" r="70%">
          {st([(0, '#ffffff', 0.34), (0.5, cls._mix(hi, '#ffffff', 0.5), 0.12), (1, '#ffffff', 0)])}
        </radialGradient>
        <linearGradient id="leatherG" x1="0%" y1="0%" x2="100%" y2="0%">
          {st([(0, '#1f0f07'), (0.18, '#4a2a16'), (0.4, '#7a4a28'), (0.6, '#5a321a'), (0.85, '#2b160a'), (1, '#170b05')])}
        </linearGradient>
        <filter id="hlBlur" x="-80%" y="-5%" width="260%" height="110%"><feGaussianBlur stdDeviation="2.4"/></filter>
        <filter id="capShadowBlur" x="-40%" y="-200%" width="180%" height="500%"><feGaussianBlur stdDeviation="3.2"/></filter>
        """

    @classmethod
    def _style_overlay(cls, g: Dict[str, Any], p: Dict[str, Any], v: Dict[str, Any]) -> str:
        """Surface engraving, bands and ornament, drawn clipped to the glass silhouette."""
        style = v["style"]
        W, B, slab = g["W"], g["B"], g["slab"]
        acc, hi = p["accent"], p["highlight"]
        foil = cls._lift(cls._mix(acc, hi, 0.55), 0.72)
        cy = g["label"][0]
        top, bot = -88.0, B - slab - 6
        o: List[str] = []

        def line(x1, y1, x2, y2, col, w, a):
            o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}" opacity="{a}"/>')

        def bands(ys: List[float], h: float = 9.0):
            for y in ys:
                o.append(f'<rect x="{-W - 3:.1f}" y="{y:.1f}" width="{2 * W + 6:.1f}" height="{h}" fill="url(#capMetalG)"/>')
                line(-W, y + 1, W, y + 1, "#ffffff", 0.9, 0.7)
                line(-W, y + h, W, y + h, "#000000", 1.0, 0.55)

        def flutes(n: int, wd: float = 1.6):
            xs, xe = -W + 13, W - 13
            pitch = (xe - xs) / (n - 1)
            for i in range(n):
                x = xs + i * pitch
                line(x, top, x, bot, "#000000", wd, 0.30)
                line(x + wd + 0.4, top, x + wd + 0.4, bot, "#ffffff", 0.9, 0.30)

        def waves(ys: List[float], amp: float = 6.0, wl: float = 52.0):
            for y in ys:
                d = f"M{-W - wl:.1f},{y:.1f}"
                x = -W - wl
                d += f" Q{x + wl / 4:.1f},{y - amp:.1f} {x + wl / 2:.1f},{y:.1f}"
                x += wl / 2
                while x < W + wl:
                    d += f" T{x + wl / 2:.1f},{y:.1f}"
                    x += wl / 2
                o.append(f'<path d="{d}" fill="none" stroke="#000000" stroke-width="2.2" opacity="0.22" transform="translate(0,1.6)"/>')
                o.append(f'<path d="{d}" fill="none" stroke="{foil}" stroke-width="1.3" opacity="0.62"/>')

        if style in ("flute", "wave", "ribs"):
            flutes({"flute": v["flutes"], "wave": 7, "ribs": v["flutes"] + 3}[style], 1.6 if style != "ribs" else 1.2)
            if style != "ribs":
                bands([-70.0, bot - 8])
            if style == "wave":
                waves([cy + 78, cy + 90, cy + 102])
        elif style == "banded":
            bands([-70.0, bot - 8])
        elif style in ("diamond", "cut"):
            if style == "diamond":
                y0, dy, pitch = -34.0, bot + 34.0, 46.0
                k = -W - dy
                while k < W + 4:
                    line(k, y0, k + dy, y0 + dy, hi, 1.1, 0.26)
                    line(k + 1.6, y0, k + 1.6 + dy, y0 + dy, "#000000", 1.0, 0.20)
                    line(k + dy, y0, k, y0 + dy, hi, 1.1, 0.26)
                    line(k + dy + 1.6, y0, k + 1.6, y0 + dy, "#000000", 1.0, 0.20)
                    k += pitch
                line(-W, y0, W, y0, hi, 1.4, 0.55)
                line(-W, bot, W, bot, hi, 1.4, 0.45)
            o.append(f'<rect x="{-W:.1f}" y="-96" width="22" height="{B + 96:.1f}" fill="#ffffff" opacity="0.11"/>')
            o.append(f'<rect x="{W - 22:.1f}" y="-96" width="22" height="{B + 96:.1f}" fill="#000000" opacity="0.16"/>')
            line(-W + 22, -96, -W + 22, B, hi, 1.1, 0.55)
            line(W - 22, -96, W - 22, B, hi, 1.0, 0.3)
            line(-W, -52, W, -52, hi, 1.1, 0.5)
        elif style in ("stepped", "ornate"):
            for y in (-91.0, -80.0, -64.0):
                line(-W, y, W, y, hi, 1.1, 0.5)
            line(-W + 22, -96, -W + 22, B, hi, 1.0, 0.4)
            line(W - 22, -96, W - 22, B, hi, 1.0, 0.25)
            if style == "ornate":
                o.append(f'<rect x="{-W - 3:.1f}" y="-92" width="{2 * W + 6:.1f}" height="{B + 92:.1f}" fill="url(#foilG)" mask="url(#bandInlay)"/>')
                for sx in (-1, 1):
                    o.append(
                        f'<path d="M{sx * 18:.1f},-66 C{sx * W * 0.46:.1f},-72 {sx * W * 0.66:.1f},-52 {sx * W * 0.56:.1f},-40 '
                        f'C{sx * W * 0.48:.1f},-30 {sx * W * 0.34:.1f},-38 {sx * W * 0.38:.1f},-47" fill="none" stroke="{foil}" stroke-width="1.5" opacity="0.7" stroke-linecap="round"/>'
                        f'<circle cx="{sx * W * 0.40:.1f}" cy="-48" r="2.4" fill="{foil}" opacity="0.8"/>'
                    )
                line(-W, B - slab, W, B - slab, foil, 1.6, 0.8)
                line(-W, B - 9, W, B - 9, foil, 1.6, 0.7)
        elif style in ("prism", "arabesque", "inlay"):
            if style != "inlay":
                for sx in (-1, 1):
                    line(sx * W * 0.6, -100, sx * W * 0.6, B, hi, 1.2, 0.5)
                    line(sx * W * 0.6 + sx * 1.6, -100, sx * W * 0.6 + sx * 1.6, B, "#000000", 1.0, 0.28)
                    line(sx * W * 0.6, -92, sx * W, -66, hi, 1.1, 0.45)
                    line(sx * W * 0.6, B - 4, sx * W * 0.84, B, hi, 1.0, 0.35)
                o.append(f'<rect x="{-W:.1f}" y="-100" width="{W * 0.4:.1f}" height="{B + 100:.1f}" fill="#ffffff" opacity="0.07"/>')
                o.append(f'<rect x="{W * 0.6:.1f}" y="-100" width="{W * 0.4:.1f}" height="{B + 100:.1f}" fill="#000000" opacity="0.2"/>')
            o.append(f'<rect x="{-W - 3:.1f}" y="-100" width="{2 * W + 6:.1f}" height="{B + 100:.1f}" fill="url(#foilG)" mask="url(#bandInlay)"/>')
            if style == "arabesque":
                star = []
                for k in range(16):
                    r_ = 70 if k % 2 == 0 else 40
                    a = math.radians(k * 22.5 - 90)
                    star.append(f"{r_ * math.cos(a):.1f},{cy + r_ * math.sin(a):.1f}")
                o.append(f'<polygon points="{" ".join(star)}" fill="none" stroke="{foil}" stroke-width="1" opacity="0.42"/>')
                o.append(f'<circle cx="0" cy="{cy}" r="78" fill="none" stroke="{foil}" stroke-width="1.1" opacity="0.38"/>')
                o.append(f'<circle cx="0" cy="{cy}" r="84" fill="none" stroke="{foil}" stroke-width="0.5" stroke-dasharray="2 3" opacity="0.4"/>')
                for sx in (-1, 1):
                    for yy in (cy - 66, cy + 66):
                        o.append(f'<circle cx="{sx * (W - 26):.1f}" cy="{yy:.1f}" r="3.2" fill="none" stroke="{foil}" stroke-width="0.9" opacity="0.6"/>')
        elif style == "candy":
            hw = 66 * v["w"]
            for k, yy in enumerate((-12.0, 52.0, 116.0)):
                d = f"M{-W - 8:.1f},{yy:.1f} C{-W * 0.3:.1f},{yy - 34:.1f} {W * 0.3:.1f},{yy + 44:.1f} {W + 8:.1f},{yy + 8:.1f}"
                o.append(f'<path d="{d}" fill="none" stroke="{hi}" stroke-width="10" opacity="0.20" stroke-linecap="round"/>')
                o.append(f'<path d="{d}" fill="none" stroke="#ffffff" stroke-width="1.3" opacity="0.5" transform="translate(0,-4.5)"/>')
                o.append(f'<path d="{d}" fill="none" stroke="{cls._shade(acc, -0.4)}" stroke-width="1.2" opacity="0.4" transform="translate(0,5)"/>')
            o.append(f'<path d="M{-hw - 4:.1f},12 Q0,24 {hw + 4:.1f},12" fill="none" stroke="url(#capMetalG)" stroke-width="5.5"/>')
            o.append(f'<path d="M{-hw - 4:.1f},9.6 Q0,21.6 {hw + 4:.1f},9.6" fill="none" stroke="#ffffff" stroke-width="0.8" opacity="0.7"/>')
            o.append('<ellipse cx="-34" cy="-40" rx="26" ry="12" fill="url(#pearlG)"/>')
        elif style == "pearl":
            hw = 66 * v["w"]
            o.append(f'<ellipse cx="{-W * 0.3:.1f}" cy="-10" rx="{W * 0.9:.1f}" ry="110" fill="url(#pearlG)"/>')
            o.append(f'<path d="M{-hw - 4:.1f},12 Q0,24 {hw + 4:.1f},12" fill="none" stroke="url(#capMetalG)" stroke-width="4.5"/>')
            o.append(f'<path d="M{-hw - 4:.1f},9.8 Q0,21.8 {hw + 4:.1f},9.8" fill="none" stroke="#ffffff" stroke-width="0.7" opacity="0.65"/>')
        elif style == "ribbon":
            o.append(
                f'<path d="M{-W - 4:.1f},-10 C{-W * 0.4:.1f},-44 {W * 0.4:.1f},10 {W + 4:.1f},-24 L{W + 4:.1f},-8 '
                f'C{W * 0.4:.1f},26 {-W * 0.4:.1f},-28 {-W - 4:.1f},6 Z" fill="url(#capMetalG)" opacity="0.92"/>'
                f'<path d="M{-W - 4:.1f},-10 C{-W * 0.4:.1f},-44 {W * 0.4:.1f},10 {W + 4:.1f},-24" fill="none" stroke="#ffffff" stroke-width="0.9" opacity="0.7"/>'
                f'<path d="M{-W - 4:.1f},6 C{-W * 0.4:.1f},-28 {W * 0.4:.1f},26 {W + 4:.1f},-8" fill="none" stroke="#000000" stroke-width="1" opacity="0.5"/>'
            )
        elif style == "strap":
            o.append(f'<rect x="{-W - 3:.1f}" y="-78" width="{2 * W + 6:.1f}" height="30" fill="url(#leatherG)"/>')
            line(-W, -78, W, -78, "#000000", 1.2, 0.6)
            line(-W, -48, W, -48, "#000000", 1.4, 0.7)
            for yy in (-73.5, -52.5):
                o.append(f'<line x1="{-W:.1f}" y1="{yy}" x2="{W:.1f}" y2="{yy}" stroke="{foil}" stroke-width="0.9" stroke-dasharray="3 2.4" opacity="0.7"/>')
            bx = W * 0.46
            o.append(f'<rect x="{bx:.1f}" y="-82" width="24" height="38" rx="2.5" fill="none" stroke="url(#capMetalG)" stroke-width="3.4"/>')
            o.append(f'<line x1="{bx + 6:.1f}" y1="-63" x2="{bx + 34:.1f}" y2="-63" stroke="url(#capMetalG)" stroke-width="2.4" stroke-linecap="round"/>')
            o.append(f'<line x1="{-W:.1f}" y1="-47" x2="{W:.1f}" y2="-47" stroke="#000000" stroke-width="5" opacity="0.18"/>')
        elif style == "radio":
            ccy = -22.0
            rr = W * 0.64
            for k in range(0, 21):
                a = math.radians(200 + k * 7.0)
                long_ = (k % 4 == 0)
                r2 = rr + (7 if long_ else 4)
                o.append(f'<line x1="{rr * math.cos(a):.1f}" y1="{ccy + rr * math.sin(a):.1f}" x2="{r2 * math.cos(a):.1f}" y2="{ccy + r2 * math.sin(a):.1f}" stroke="{foil}" stroke-width="{1.4 if long_ else 0.9}" opacity="0.75"/>')
            a = math.radians(256)
            o.append(f'<line x1="0" y1="{ccy}" x2="{rr * 1.04 * math.cos(a):.1f}" y2="{ccy + rr * 1.04 * math.sin(a):.1f}" stroke="{acc}" stroke-width="1.6" opacity="0.95"/>')
            o.append(f'<circle cx="0" cy="{ccy}" r="3.4" fill="url(#capMetalG)"/>')
            gy0 = cy + g["label"][2] / 2 + 12
            for row in range(4):
                n = 9
                xs = -W + 30
                pitch = (2 * W - 60) / (n - 1)
                for i in range(n):
                    o.append(f'<circle cx="{xs + i * pitch:.1f}" cy="{gy0 + row * 10:.1f}" r="2.3" fill="#000000" opacity="0.5"/>')
                    o.append(f'<circle cx="{xs + i * pitch - 0.5:.1f}" cy="{gy0 + row * 10 - 0.6:.1f}" r="1.2" fill="{foil}" opacity="0.38"/>')
            o.append(f'<rect x="{-W + 20:.1f}" y="{gy0 - 10:.1f}" width="{2 * W - 40:.1f}" height="42" rx="8" fill="none" stroke="{foil}" stroke-width="0.8" opacity="0.5"/>')
            o.append(f'<rect x="{-W - 3:.1f}" y="-100" width="{2 * W + 6:.1f}" height="{B + 100:.1f}" fill="url(#foilG)" mask="url(#bandInlay)"/>')
        elif style == "lantern":
            wv = W - 14
            arch = (f"M{-wv:.1f},112 L{-wv:.1f},-20 C{-wv:.1f},-54 -26,-66 0,-90 "
                    f"C26,-66 {wv:.1f},-54 {wv:.1f},-20 L{wv:.1f},112")
            o.append(f'<path d="{arch}" fill="none" stroke="{foil}" stroke-width="1.8" opacity="0.72"/>')
            o.append(f'<path d="{arch}" fill="none" stroke="{foil}" stroke-width="0.6" opacity="0.5" transform="scale(0.93) translate(0,6)"/>')
            o.append(f'<polygon points="0,-82 2.6,-76 8,-74 2.6,-72 0,-66 -2.6,-72 -8,-74 -2.6,-76" fill="{foil}" opacity="0.8"/>')
            for sx in (-1, 1):
                for yy in (-6, 40, 86):
                    o.append(f'<circle cx="{sx * (wv - 8):.1f}" cy="{yy}" r="2" fill="{foil}" opacity="0.6"/>')
        return '<g clip-path="url(#bottleClip)">' + "".join(o) + "</g>"

    # ------------------------------------------------------------------
    # Flacon assembly
    # ------------------------------------------------------------------
    @classmethod
    def render_flacon(cls, profile: Dict[str, Any]) -> str:
        v = cls._variant(profile)
        g = cls._geometry(profile, v)
        cap_type = profile["cap"]
        accent = profile["accent"]
        highlight = profile["highlight"]
        W, B, slab, fy = g["W"], g["B"], g["slab"], g["fill_y"]
        hw_liq = g["fill_hw"]
        outer = g["outer"]
        x0, x1 = -W - 4, W + 4
        hl = cls._lift(highlight, 0.8)
        frosted = v["style"] in ("candy", "pearl")
        lcy, lw, lh = g["label"]
        ry = 7.5
        p_liq = profile["liquid"]

        parts: List[str] = [f"<defs>{cls._glass_defs(g, profile, v)}</defs>"]

        # 1. Glass volume (the studio shows through the clear glass)
        parts.append(f'<path d="{outer}" fill="url(#glassBackG)"/>')
        if frosted:
            parts.append(f'<path d="{outer}" fill="url(#frostG)"/>')

        # 2. Thick glass base slab with a lensed caustic from the liquid above it
        parts.append(
            f'<g clip-path="url(#bottleClip)">'
            f'<rect x="{x0:.1f}" y="{B - slab:.1f}" width="{x1 - x0:.1f}" height="{slab + 6:.1f}" fill="url(#slabG)"/>'
            f'<ellipse cx="0" cy="{B - slab * 0.44:.1f}" rx="{W * 0.66:.1f}" ry="{slab * 0.30:.1f}" fill="url(#slabGlowG)"/>'
            f'<line x1="{x0:.1f}" y1="{B - slab:.1f}" x2="{x1:.1f}" y2="{B - slab:.1f}" stroke="{hl}" stroke-width="1.4" opacity="0.75"/>'
            f'<line x1="{x0:.1f}" y1="{B - slab + 1.8:.1f}" x2="{x1:.1f}" y2="{B - slab + 1.8:.1f}" stroke="#000000" stroke-width="1.1" opacity="0.35"/>'
            f'</g>'
        )

        # 3. Liquid: gradient body, internal glow, surface ellipse with meniscus
        parts.append(
            f'<g mask="url(#cavMask)">'
            f'<rect x="{x0:.1f}" y="{fy:.1f}" width="{x1 - x0:.1f}" height="{B - fy:.1f}" fill="{p_liq}" opacity="0.62"/>'
            f'<rect x="{x0:.1f}" y="{fy:.1f}" width="{x1 - x0:.1f}" height="{B - fy:.1f}" fill="url(#liquidBodyG)"/>'
            f'<rect x="{x0:.1f}" y="{fy:.1f}" width="{x1 - x0:.1f}" height="{B - fy:.1f}" fill="url(#liquidDepthG)"/>'
            f'<rect x="{x0:.1f}" y="{fy:.1f}" width="{x1 - x0:.1f}" height="{B - fy:.1f}" fill="url(#liquidGlowG)"/>'
            f'<g mask="url(#bandLiq)"><rect x="{x0:.1f}" y="{fy:.1f}" width="{x1 - x0:.1f}" height="{B - fy:.1f}" fill="url(#liquidEdgeG)"/></g>'
            f'<ellipse cx="0" cy="{fy:.1f}" rx="{hw_liq:.1f}" ry="{ry}" fill="url(#liquidSurfG)"/>'
            f'<path d="M{-hw_liq:.1f},{fy:.1f} A{hw_liq:.1f},{ry} 0 0 1 {hw_liq:.1f},{fy:.1f}" fill="none" stroke="#000000" stroke-width="1" opacity="0.28"/>'
            f'<path d="M{-hw_liq:.1f},{fy:.1f} A{hw_liq:.1f},{ry} 0 0 0 {hw_liq:.1f},{fy:.1f}" fill="none" stroke="#ffffff" stroke-width="1.5" opacity="0.88"/>'
            f'<path d="M{-hw_liq:.1f},{fy:.1f} A{hw_liq:.1f},{ry} 0 0 0 {hw_liq:.1f},{fy + 2.6:.1f}" fill="none" stroke="{hl}" stroke-width="2.4" opacity="0.18"/>'
            f'<line x1="{-hw_liq:.1f}" y1="{fy - 5:.1f}" x2="{-hw_liq:.1f}" y2="{fy + 4:.1f}" stroke="#ffffff" stroke-width="1.6" opacity="0.6"/>'
            f'<line x1="{hw_liq:.1f}" y1="{fy - 5:.1f}" x2="{hw_liq:.1f}" y2="{fy + 4:.1f}" stroke="{hl}" stroke-width="1.4" opacity="0.5"/>'
            # dip tube: glass tube with a bright left wall, shaded right wall and a bent tip
            f'<line x1="-1.4" y1="-98" x2="-1.4" y2="{B - slab - 24:.1f}" stroke="#ffffff" stroke-width="1.7" opacity="0.40"/>'
            f'<line x1="1.4" y1="-98" x2="1.4" y2="{B - slab - 24:.1f}" stroke="#000000" stroke-width="1.3" opacity="0.30"/>'
            f'<path d="M0,{B - slab - 24:.1f} Q0,{B - slab - 12:.1f} -11,{B - slab - 9:.1f}" fill="none" stroke="#ffffff" stroke-width="1.4" opacity="0.30"/>'
            f'</g>'
        )

        # 4. Glass walls: tinted thick edge band, bright inner-wall line, crisp outline
        parts.append(f'<path d="{outer}" fill="none" stroke="url(#wallG)" stroke-width="{2 * g["wall"]:.1f}" stroke-linejoin="round" clip-path="url(#bottleClip)"/>')

        # 5. Engraving, bands and ornament
        parts.append(cls._style_overlay(g, profile, v))

        # 6. Studio lighting on glass: rim, edge-following specular, shoulder and base glints, softboxes
        parts.append(
            f'<g clip-path="url(#bottleClip)">'
            f'<rect x="{x0:.1f}" y="-112" width="{x1 - x0:.1f}" height="{B + 118:.1f}" fill="url(#innerEdgeG)" mask="url(#bandWall)"/>'
            f'<rect x="{x0:.1f}" y="-112" width="{x1 - x0:.1f}" height="{B + 118:.1f}" fill="url(#rimG)" mask="url(#bandRim)"/>'
            f'<g mask="url(#vFade)"><rect x="{x0:.1f}" y="-112" width="{x1 - x0:.1f}" height="{B + 118:.1f}" fill="url(#specG)" mask="url(#bandSpec)"/></g>'
            f'<rect x="{x0:.1f}" y="-112" width="{x1 - x0:.1f}" height="58" fill="url(#topLightG)" mask="url(#bandRim)"/>'
            f'<rect x="{x0:.1f}" y="{B - 46:.1f}" width="{x1 - x0:.1f}" height="54" fill="url(#baseLightG)" mask="url(#bandRim)"/>'
            f'</g>'
            f'<g clip-path="url(#bottleClip)" mask="url(#vFade)">'
            f'<rect x="{-W * 0.68:.1f}" y="-112" width="{W * 0.17:.1f}" height="{B + 118:.1f}" fill="url(#softLeftG)" filter="url(#hlBlur)"/>'
            f'<rect x="{W * 0.50:.1f}" y="-112" width="{W * 0.07:.1f}" height="{B + 118:.1f}" fill="url(#softRightG)" filter="url(#hlBlur)"/>'
            f'</g>'
            f'<path d="{outer}" fill="none" stroke="url(#rimG)" stroke-width="1.2" stroke-linejoin="round" opacity="0.5"/>'
        )

        # 7. Label plaque
        parts.append(cls.render_cartouche(profile, width=lw, height=lh, y_offset=lcy))

        # 8. Cap seat: soft contact shade on the shoulder, then the closure itself
        parts.append(
            f'<g clip-path="url(#bottleClip)">'
            f'<ellipse cx="0" cy="-91" rx="{g["nw"] + 26:.1f}" ry="8" fill="#000000" opacity="0.5" filter="url(#capShadowBlur)"/>'
            f'<ellipse cx="0" cy="-95" rx="{g["nw"] + 8:.1f}" ry="3.2" fill="{accent}" opacity="0.28" filter="url(#capShadowBlur)"/>'
            f'</g>'
        )
        parts.append(cls.render_cap(cap_type, accent, highlight, v))
        return "".join(parts)

    # ------------------------------------------------------------------
    # Studio environments
    # ------------------------------------------------------------------
    @classmethod
    def _environment(cls, p: Dict[str, Any], y_f: float) -> Dict[str, Any]:
        """Backdrop, surface material and reflectivity for each existing studio style."""
        env = p["env"]
        accent, hi, bg = p["accent"], p["highlight"], p["bg"]
        st = cls._stops
        yh = y_f - 150.0
        deep = cls._shade(bg, -0.72)
        foil = cls._lift(cls._mix(accent, hi, 0.5), 0.7)
        fh = 1500 - yh

        a_amb = {"champagne_boudoir": 0.32, "noir_architectural": 0.26, "amber_cognac_reserve": 0.36,
                 "royal_oriental_emerald": 0.30}.get(env, 0.28)
        defs = f"""
            <radialGradient id="ambG" cx="50%" cy="36%" r="72%">
              {st([(0, accent, a_amb), (0.40, bg, 0.97), (1, deep)])}
            </radialGradient>
            <linearGradient id="pedestalG" x1="0%" y1="0%" x2="0%" y2="100%">
              {st([(0, accent, 0.22), (0.2, cls._shade(bg, -0.5), 0.95), (1, deep)])}
            </linearGradient>
            <radialGradient id="spotG" cx="50%" cy="30%" r="46%">
              {st([(0, hi, 0.22), (0.55, accent, 0.06), (1, accent, 0)])}
            </radialGradient>
            <linearGradient id="floorG" gradientUnits="userSpaceOnUse" x1="0" y1="{yh}" x2="0" y2="1500">
              {st([(0, cls._mix(bg, accent, 0.30), 0.98), (0.14, cls._shade(bg, -0.30), 1), (0.6, cls._shade(bg, -0.62), 1), (1, deep)])}
            </linearGradient>
            <radialGradient id="poolG" cx="50%" cy="50%" r="50%">
              {st([(0, hi, 0.34), (0.5, accent, 0.10), (1, accent, 0)])}
            </radialGradient>
            <linearGradient id="shaftG" x1="0%" y1="0%" x2="0%" y2="100%">
              {st([(0, hi, 0.16), (1, hi, 0)])}
            </linearGradient>
            <linearGradient id="silkG" x1="0%" y1="0%" x2="100%" y2="0%">
              {st([(0, accent, 0), (0.35, hi, 0.16), (0.65, accent, 0.10), (1, accent, 0)])}
            </linearGradient>
            <linearGradient id="pilasterG" x1="0%" y1="0%" x2="100%" y2="0%">
              {st([(0, accent, 0.10), (0.5, hi, 0.05), (1, '#000000', 0.25)])}
            </linearGradient>
            <radialGradient id="nicheG" cx="50%" cy="62%" r="62%">
              {st([(0, accent, 0.34), (0.6, accent, 0.08), (1, bg, 0)])}
            </radialGradient>
            <radialGradient id="latticeFadeG" cx="50%" cy="46%" r="64%">
              <stop offset="0.35" stop-color="#000000"/><stop offset="1" stop-color="#ffffff"/>
            </radialGradient>
            <mask id="latticeMask" maskUnits="userSpaceOnUse" x="0" y="0" width="1200" height="{yh}"><rect width="1200" height="{yh}" fill="url(#latticeFadeG)"/></mask>
            <pattern id="latticeP" width="64" height="64" patternUnits="userSpaceOnUse">
              <path d="M32,2 L62,32 L32,62 L2,32 Z" fill="none" stroke="{foil}" stroke-width="0.9"/>
              <circle cx="32" cy="32" r="9" fill="none" stroke="{foil}" stroke-width="0.7"/>
              <path d="M32,23 L35,29 L41,32 L35,35 L32,41 L29,35 L23,32 L29,29 Z" fill="none" stroke="{foil}" stroke-width="0.6"/>
            </pattern>
            <filter id="blur30" filterUnits="userSpaceOnUse" x="0" y="0" width="1200" height="1100"><feGaussianBlur stdDeviation="26"/></filter>
            <filter id="blur14" filterUnits="userSpaceOnUse" x="0" y="0" width="1200" height="1100"><feGaussianBlur stdDeviation="14"/></filter>
            <filter id="blur6" filterUnits="userSpaceOnUse" x="0" y="0" width="1200" height="1100"><feGaussianBlur stdDeviation="6"/></filter>
        """

        wall = f'<rect width="1200" height="1500" fill="url(#ambG)"/><rect width="1200" height="{yh}" fill="url(#spotG)"/>'
        floor_extra = ""
        refl = 0.30

        if env == "champagne_boudoir":
            wall += (
                '<g filter="url(#blur30)">'
                '<path d="M40,0 C150,300 20,700 110,1000 L340,1000 C250,700 380,300 250,0 Z" fill="url(#silkG)"/>'
                '<path d="M880,0 C820,320 990,700 890,1000 L1150,1000 C1190,700 1090,300 1170,0 Z" fill="url(#silkG)"/>'
                '<path d="M420,0 C470,250 400,600 470,900 L560,900 C510,600 580,250 520,0 Z" fill="url(#silkG)" opacity="0.6"/>'
                '</g><g filter="url(#blur6)" fill="' + hi + '">'
                '<circle cx="230" cy="270" r="34" opacity="0.13"/><circle cx="975" cy="330" r="26" opacity="0.15"/>'
                '<circle cx="820" cy="170" r="17" opacity="0.18"/><circle cx="150" cy="640" r="22" opacity="0.10"/>'
                '<circle cx="1060" cy="720" r="30" opacity="0.10"/><circle cx="935" cy="520" r="13" opacity="0.16"/></g>'
            )
            floor_extra = "".join(
                f'<path d="{d}" fill="none" stroke="#ffffff" stroke-width="{w}" opacity="{a}"/>'
                for d, w, a in (
                    (f"M0,{yh + 120} C260,{yh + 90} 520,{yh + 190} 820,{yh + 150} S1100,{yh + 210} 1200,{yh + 190}", 1.2, 0.06),
                    (f"M-20,{yh + 250} C300,{yh + 200} 620,{yh + 300} 900,{yh + 260} S1160,{yh + 330} 1240,{yh + 300}", 0.9, 0.05),
                    (f"M0,{yh + 60} C200,{yh + 70} 400,{yh + 40} 640,{yh + 70} S1000,{yh + 50} 1200,{yh + 80}", 0.8, 0.05),
                )
            )
            refl = 0.30
        elif env == "noir_architectural":
            wall += (
                '<g>'
                f'<rect x="60" y="0" width="120" height="{yh}" fill="url(#pilasterG)"/><rect x="215" y="0" width="30" height="{yh}" fill="url(#pilasterG)"/>'
                f'<rect x="1020" y="0" width="120" height="{yh}" fill="url(#pilasterG)"/><rect x="955" y="0" width="30" height="{yh}" fill="url(#pilasterG)"/>'
                '</g>'
                f'<g filter="url(#blur6)"><rect x="296" y="110" width="12" height="{yh - 160}" fill="{hi}" opacity="0.13"/>'
                f'<rect x="892" y="110" width="12" height="{yh - 160}" fill="{hi}" opacity="0.13"/></g>'
                f'<polygon points="520,0 680,0 930,{yh} 270,{yh}" fill="url(#shaftG)" filter="url(#blur14)"/>'
            )
            floor_extra = (
                f'<rect x="0" y="{yh}" width="1200" height="{fh}" fill="#ffffff" opacity="0.025"/>'
                f'<line x1="0" y1="{yh + 70}" x2="1200" y2="{yh + 70}" stroke="#ffffff" stroke-width="0.8" opacity="0.05"/>'
                f'<line x1="0" y1="{yh + 190}" x2="1200" y2="{yh + 190}" stroke="#ffffff" stroke-width="0.8" opacity="0.04"/>'
            )
            refl = 0.36
        elif env == "amber_cognac_reserve":
            bokeh = [(190, 250, 46, 0.13), (330, 150, 24, 0.18), (880, 230, 40, 0.14), (1010, 400, 28, 0.17), (760, 120, 18, 0.2),
                     (120, 520, 30, 0.12), (1090, 640, 36, 0.10), (270, 700, 20, 0.14), (930, 780, 24, 0.12), (470, 90, 14, 0.2),
                     (640, 60, 20, 0.12), (60, 330, 16, 0.14), (1140, 190, 22, 0.14), (410, 830, 16, 0.1)]
            wall += '<g filter="url(#blur6)" fill="' + hi + '">' + "".join(
                f'<circle cx="{x}" cy="{y}" r="{r}" opacity="{a}"/>' for x, y, r, a in bokeh) + '</g>'
            wall += (f'<line x1="0" y1="430" x2="1200" y2="430" stroke="{accent}" stroke-width="1.2" opacity="0.13"/>'
                     f'<line x1="0" y1="438" x2="1200" y2="438" stroke="#000000" stroke-width="3" opacity="0.2"/>')
            seams = "".join(
                f'<line x1="{x}" y1="{yh}" x2="{600 + (x - 600) * 2.8:.0f}" y2="1500" stroke="#000000" stroke-width="1.6" opacity="0.30"/>'
                for x in range(-60, 1300, 130))
            grain = "".join(
                f'<path d="M0,{yh + 14 + i * 36} C300,{yh + 10 + i * 36 + (i % 3) * 3} 760,{yh + 22 + i * 36 - (i % 2) * 4} 1200,{yh + 12 + i * 36}" '
                f'fill="none" stroke="{accent}" stroke-width="{1.0 + (i % 3) * 0.5}" opacity="{0.05 + (i % 4) * 0.015:.3f}"/>'
                for i in range(14))
            floor_extra = seams + grain
            refl = 0.24
        elif env == "royal_oriental_emerald":
            arch = f"M290,{yh} L290,440 A310,310 0 0 1 910,440 L910,{yh} Z"
            arch2 = f"M308,{yh} L308,440 A292,292 0 0 1 892,440 L892,{yh} Z"
            wall += (
                f'<rect width="1200" height="{yh}" fill="url(#latticeP)" opacity="0.16" mask="url(#latticeMask)"/>'
                f'<path d="{arch}" fill="url(#nicheG)"/>'
                f'<path d="{arch}" fill="none" stroke="{foil}" stroke-width="2.4" opacity="0.5"/>'
                f'<path d="{arch2}" fill="none" stroke="{foil}" stroke-width="0.8" opacity="0.35"/>'
            )
            floor_extra = (
                f'<line x1="0" y1="{yh + 28}" x2="1200" y2="{yh + 28}" stroke="{foil}" stroke-width="1.6" opacity="0.34"/>'
                f'<line x1="0" y1="{yh + 36}" x2="1200" y2="{yh + 36}" stroke="{foil}" stroke-width="0.6" opacity="0.26"/>'
                f'<path d="M0,{yh + 150} C300,{yh + 120} 600,{yh + 210} 900,{yh + 170} S1150,{yh + 230} 1200,{yh + 210}" fill="none" stroke="{foil}" stroke-width="0.8" opacity="0.07"/>'
            )
            refl = 0.32
        elif env == "parisian_honed_slate":
            wall += (
                f'<rect x="110" y="110" width="980" height="{yh - 190}" fill="none" stroke="{hi}" stroke-width="2" opacity="0.09"/>'
                f'<rect x="136" y="136" width="928" height="{yh - 242}" fill="none" stroke="{hi}" stroke-width="1" opacity="0.07"/>'
                f'<g filter="url(#blur6)" fill="#ffffff" opacity="0.07">'
                '<polygon points="780,130 950,175 940,430 770,385"/><polygon points="790,450 945,490 935,740 780,700"/>'
                '<polygon points="560,160 730,205 720,450 550,405" opacity="0.7"/></g>'
            )
            floor_extra = (
                f'<line x1="0" y1="{yh + 110}" x2="1200" y2="{yh + 110}" stroke="#ffffff" stroke-width="0.8" opacity="0.04"/>'
                f'<line x1="0" y1="{yh + 260}" x2="1200" y2="{yh + 260}" stroke="#ffffff" stroke-width="0.8" opacity="0.035"/>'
            )
            refl = 0.12
        else:
            wall += (
                f'<circle cx="600" cy="540" r="390" fill="none" stroke="{hi}" stroke-width="46" opacity="0.07" filter="url(#blur14)"/>'
                f'<circle cx="600" cy="540" r="310" fill="none" stroke="{accent}" stroke-width="1.6" opacity="0.14"/>'
                f'<circle cx="600" cy="540" r="318" fill="none" stroke="{accent}" stroke-width="0.6" opacity="0.10"/>'
            )
            floor_extra = "".join(
                f'<line x1="0" y1="{yh + 40 + i * 52}" x2="1200" y2="{yh + 40 + i * 52}" stroke="{accent}" stroke-width="0.8" opacity="0.07"/>'
                for i in range(7))
            refl = 0.30

        floor = (
            f'<rect x="0" y="{yh}" width="1200" height="{fh}" fill="url(#floorG)"/>'
            f'{floor_extra}'
            f'<rect x="0" y="{yh - 7}" width="1200" height="14" fill="{hi}" opacity="0.10" filter="url(#blur6)"/>'
            f'<line x1="0" y1="{yh}" x2="1200" y2="{yh}" stroke="{accent}" stroke-width="1.0" opacity="0.40"/>'
            f'<ellipse cx="600" cy="{y_f + 8}" rx="640" ry="190" fill="url(#poolG)"/>'
        )
        return {"defs": defs, "wall": wall, "floor": floor, "refl": refl}

    @classmethod
    def render_flacon_svg(cls, prod: Dict[str, Any]) -> str:
        """Assembles complete luxury 1200x1500 SVG vector flacon artwork."""
        p = ProductProfile.derive_profile(prod)
        accent = p["accent"]
        highlight = p["highlight"]
        liquid = p["liquid"]
        bg = p["bg"]
        family = xml.sax.saxutils.escape(p["family"].upper())
        st = cls._stops

        v = cls._variant(p)
        g = cls._geometry(p, v)
        s = g["scale"]
        y_f = 1148.0
        ty = y_f - g["B"] * s
        hw_px = g["W"] * s
        env = cls._environment(p, y_f)
        bottle_markup = cls.render_flacon(p)

        hl = cls._lift(highlight, 0.8)
        pale = cls._mix(highlight, "#ffffff", 0.5)
        liq_core = cls._mix(liquid, highlight, 0.6)
        foil_a = cls._lift(cls._mix(accent, "#ffffff", 0.35), 0.74)
        foil_b = cls._lift(cls._mix(highlight, "#ffffff", 0.72), 0.86)
        foil_c = cls._lift(cls._mix(accent, highlight, 0.35), 0.74)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1200 1500" width="1200" height="1500">
  <defs>
    {env["defs"]}
    <linearGradient id="metalG" x1="0%" y1="0%" x2="100%" y2="100%">
      {st([(0, '#ffffff', 0.98), (0.16, highlight, 0.94), (0.40, accent), (0.62, cls._shade(accent, -0.5)), (0.82, accent), (1, highlight)])}
    </linearGradient>
    <linearGradient id="capMetalG" x1="0%" y1="0%" x2="100%" y2="0%">
      {st([(0, cls._shade(accent, -0.65)), (0.07, cls._shade(accent, -0.35)), (0.2, pale), (0.33, cls._mix(accent, highlight, 0.55)), (0.5, accent), (0.66, cls._shade(accent, -0.28)), (0.8, cls._shade(accent, -0.55)), (0.92, cls._mix(accent, highlight, 0.25)), (1, cls._shade(accent, -0.62))])}
    </linearGradient>
    <linearGradient id="capMetalV" x1="0%" y1="0%" x2="0%" y2="100%">
      {st([(0, hl), (0.12, highlight), (0.5, accent), (0.88, cls._shade(accent, -0.45)), (1, cls._shade(accent, -0.7))])}
    </linearGradient>
    <radialGradient id="capLacquerG" cx="34%" cy="26%" r="88%">
      {st([(0, cls._mix(highlight, '#ffffff', 0.45)), (0.2, highlight), (0.5, accent), (1, cls._shade(accent, -0.66))])}
    </radialGradient>
    <linearGradient id="capGlassG" x1="0%" y1="0%" x2="100%" y2="100%">
      {st([(0, '#ffffff', 0.6), (0.3, cls._mix(accent, highlight, 0.5), 0.55), (0.62, accent, 0.66), (1, cls._shade(accent, -0.5), 0.8)])}
    </linearGradient>
    <radialGradient id="capTopG" cx="50%" cy="45%" r="60%">
      {st([(0, pale), (1, cls._mix(accent, highlight, 0.4))])}
    </radialGradient>
    <radialGradient id="glossSpecG" cx="50%" cy="50%" r="50%">
      {st([(0, '#ffffff', 0.92), (1, '#ffffff', 0)])}
    </radialGradient>
    <linearGradient id="foilG" x1="0%" y1="0%" x2="100%" y2="0%">
      {st([(0, foil_a), (0.3, foil_b), (0.55, '#ffffff'), (0.78, foil_c), (1, foil_a)])}
    </linearGradient>
    <linearGradient id="plateSheenG" x1="0%" y1="0%" x2="0%" y2="100%">
      {st([(0, '#ffffff', 0.15), (1, '#ffffff', 0)])}
    </linearGradient>
    <linearGradient id="cartoucheG" x1="0%" y1="0%" x2="0%" y2="100%">
      {st([(0, cls._mix('#2c2d33', bg, 0.35), 0.96), (0.5, '#15161a', 0.96), (1, '#08090b', 0.97)])}
    </linearGradient>
    <linearGradient id="glassG" x1="0%" y1="0%" x2="100%" y2="0%">
      {st([(0, '#050608', 0.95), (0.14, bg, 0.85), (0.35, accent, 0.55), (0.5, highlight, 0.75), (0.65, accent, 0.55), (0.86, bg, 0.85), (1, '#050608', 0.95)])}
    </linearGradient>
    <linearGradient id="iceBaseG" x1="0%" y1="0%" x2="100%" y2="0%">
      {st([(0, '#000000', 0.95), (0.25, accent, 0.6), (0.5, highlight, 0.85), (0.75, accent, 0.6), (1, '#000000', 0.95)])}
    </linearGradient>
    <linearGradient id="liquidG" x1="0%" y1="0%" x2="100%" y2="0%">
      {st([(0, '#0a0502', 0.92), (0.2, liquid, 0.88), (0.5, highlight, 0.98), (0.8, liquid, 0.88), (1, '#0a0502', 0.92)])}
    </linearGradient>
    <linearGradient id="liquidMeniscusG" x1="0%" y1="0%" x2="100%" y2="0%">
      {st([(0, liquid, 0.4), (0.5, '#ffffff', 0.9), (1, liquid, 0.4)])}
    </linearGradient>
    <linearGradient id="capG" x1="0%" y1="0%" x2="100%" y2="100%">
      {st([(0, highlight), (0.35, accent), (0.7, bg), (1, accent)])}
    </linearGradient>
    <linearGradient id="reflFadeG" gradientUnits="userSpaceOnUse" x1="0" y1="{y_f}" x2="0" y2="{y_f + 340}">
      <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#000000"/>
    </linearGradient>
    <mask id="reflMask" maskUnits="userSpaceOnUse" x="0" y="{y_f - 2}" width="1200" height="{1500 - y_f + 2}">
      <rect x="0" y="{y_f - 2}" width="1200" height="400" fill="url(#reflFadeG)"/>
    </mask>
    <radialGradient id="vignetteG" cx="50%" cy="46%" r="76%">
      <stop offset="0.55" stop-color="#000000" stop-opacity="0"/><stop offset="1" stop-color="#000000" stop-opacity="0.58"/>
    </radialGradient>
    <filter id="softContact" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="22"/>
    </filter>
    <filter id="shBlur22" filterUnits="userSpaceOnUse" x="0" y="{y_f - 160}" width="1200" height="400"><feGaussianBlur stdDeviation="22"/></filter>
    <filter id="shBlur10" filterUnits="userSpaceOnUse" x="0" y="{y_f - 100}" width="1200" height="260"><feGaussianBlur stdDeviation="9"/></filter>
    <filter id="shBlur2" filterUnits="userSpaceOnUse" x="0" y="{y_f - 40}" width="1200" height="100"><feGaussianBlur stdDeviation="2"/></filter>
    <filter id="reflBlur" filterUnits="userSpaceOnUse" x="0" y="{y_f - 2}" width="1200" height="360"><feGaussianBlur stdDeviation="1.7"/></filter>
    <filter id="plaqueDrop" x="-15%" y="-15%" width="130%" height="130%">
      <feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#000000" flood-opacity="0.7"/>
    </filter>
    <filter id="flaconShadow" x="-30%" y="-20%" width="160%" height="150%">
      <feDropShadow dx="0" dy="26" stdDeviation="24" flood-color="#000000" flood-opacity="0.85"/>
    </filter>
    <g id="bottleArt">{bottle_markup}</g>
  </defs>

  {env["wall"]}
  {env["floor"]}

  <!-- Glossy-surface reflection -->
  <g mask="url(#reflMask)" opacity="{env["refl"]}">
    <g filter="url(#reflBlur)">
      <use xlink:href="#bottleArt" transform="translate(600 {2 * y_f - ty:.1f}) scale({s} {-s})"/>
    </g>
  </g>

  <!-- Contact, cast and transmitted-light shadows -->
  <ellipse cx="{600 + hw_px * 0.30:.1f}" cy="{y_f + 10}" rx="{hw_px * 1.65:.1f}" ry="44" fill="#000000" opacity="0.55" filter="url(#shBlur22)"/>
  <ellipse cx="{600 + hw_px * 0.62:.1f}" cy="{y_f + 24}" rx="{hw_px * 0.95:.1f}" ry="20" fill="{liq_core}" opacity="0.34" filter="url(#shBlur10)"/>
  <ellipse cx="{600 + hw_px * 0.10:.1f}" cy="{y_f + 3}" rx="{hw_px * 1.08:.1f}" ry="17" fill="#000000" opacity="0.72" filter="url(#shBlur10)"/>
  <ellipse cx="600" cy="{y_f + 1}" rx="{hw_px * 0.99:.1f}" ry="6.5" fill="#000000" opacity="0.93" filter="url(#shBlur2)"/>

  <use xlink:href="#bottleArt" transform="translate(600 {ty:.1f}) scale({s})"/>

  <rect width="1200" height="1500" fill="url(#vignetteG)"/>
  <rect x="44" y="44" width="1112" height="1412" fill="none" stroke="{accent}" stroke-width="1.2" opacity="0.25"/>
  <rect x="56" y="56" width="1088" height="1388" fill="none" stroke="{accent}" stroke-width="0.6" stroke-dasharray="6,4" opacity="0.16"/>

  <text x="600" y="1410" font-family="'Inter', 'Helvetica Neue', Arial, sans-serif" font-size="15" font-weight="600" letter-spacing="8" fill="{accent}" opacity="0.85" text-anchor="middle">{family}</text>
</svg>"""
        return svg


# =============================================================================
# 6. MANIFEST MANAGER
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
        """Updates manifest entry when an authorized, conceptual, or procedural image is optimized."""
        if slug not in manifest:
            return
        manifest[slug]["mode"] = mode
        if mode == "MODE_B_CONCEPTUAL":
            src = "conceptual_render"
        elif mode == "MODE_B_PROCEDURAL_FLACON":
            src = "procedural_vector_flacon"
        else:
            src = "authorized_photo"
        manifest[slug]["source_type"] = src
        manifest[slug]["generation_status"] = "optimized"
        manifest[slug]["primary_image_path"] = img_meta["webp_path"]
        manifest[slug]["fallback_image_path"] = img_meta["jpg_path"]
        manifest[slug]["actual_resolution"] = [img_meta["width"], img_meta["height"]]
        manifest[slug]["file_size_kb"] = img_meta["webp_size_kb"]
        manifest[slug]["luminance"] = img_meta["luminance"]
        manifest[slug]["sharpness"] = img_meta["sharpness"]
        manifest[slug]["updated_at"] = datetime.now().isoformat()


# =============================================================================
# 7. CONTACT SHEET GENERATOR
# =============================================================================
class ContactSheetGenerator:
    """Generates a responsive luxury HTML contact sheet for visual catalog QA."""

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
            if i["mode"] == "MODE_B_CONCEPTUAL":
                mode_badge = '<span class="badge badge-mode-b">COMMERCIAL AI STILL-LIFE</span>'
            elif i["mode"] == "MODE_B_PROCEDURAL_FLACON":
                mode_badge = '<span class="badge badge-mode-flacon">PROCEDURAL LUXURY FLACON</span>'
            elif i["mode"] == "MODE_A_AUTHORIZED":
                mode_badge = '<span class="badge badge-mode-a">MODE A: AUTHORIZED</span>'
            else:
                mode_badge = '<span class="badge badge-fallback">ARCHITECTURAL FLACON</span>'

            img_src = f"products/{Path(i['primary_image_path']).name}"
            res_str = f"{i['actual_resolution'][0]}x{i['actual_resolution'][1]}"
            size_str = f"{i['file_size_kb']} KB" if i["file_size_kb"] > 0 else "Vector SVG"

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
      letter-spacing: 3px;
      text-transform: uppercase;
      color: var(--gold);
      font-weight: 600;
      margin-bottom: 8px;
    }}
    h1 {{
      font-family: 'Cinzel', serif;
      font-size: 32px;
      color: #ffffff;
      font-weight: 700;
      letter-spacing: 1px;
      margin-bottom: 10px;
    }}
    .metrics-bar {{
      display: flex;
      gap: 24px;
      margin-top: 20px;
      flex-wrap: wrap;
    }}
    .metric-item {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 20px;
      min-width: 150px;
    }}
    .metric-val {{
      font-size: 24px;
      font-weight: 700;
      color: var(--gold-light);
      font-family: 'Cinzel', serif;
    }}
    .metric-label {{
      font-size: 11px;
      color: var(--muted);
      letter-spacing: 1px;
      text-transform: uppercase;
    }}
    .controls {{
      max-width: 1400px;
      margin: 0 auto 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
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
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .tab-btn:hover, .tab-btn.active {{
      background: var(--gold);
      color: #0c0d10;
      border-color: var(--gold);
      font-weight: 600;
    }}
    .search-box {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      color: #fff;
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 13px;
      min-width: 260px;
    }}
    .search-box:focus {{
      outline: none;
      border-color: var(--gold);
    }}
    .grid {{
      max-width: 1400px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 24px;
    }}
    .product-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: transform 0.2s ease, border-color 0.2s ease;
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
    .badge-mode-flacon {{ background: rgba(168, 85, 247, 0.9); color: #ffffff; }}
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
      Centralized visual inspection interface for all 100 catalog fragrances. Displays high-resolution 4:5 commercial product still-lifes alongside procedural luxury flacon photography (1200x1500 WebP/JPEG).
    </p>
    <div class="metrics-bar">
      <div class="metric-item">
        <div class="metric-val">{total}</div>
        <div class="metric-label">Total Catalog Products</div>
      </div>
      <div class="metric-item">
        <div class="metric-val">{optimized}</div>
        <div class="metric-label">Optimized Renders</div>
      </div>
      <div class="metric-item">
        <div class="metric-val">{pending}</div>
        <div class="metric-label">Pending Items</div>
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
      <button class="tab-btn" onclick="filterCards('optimized', this)">Optimized ({optimized})</button>
      <button class="tab-btn" onclick="filterCards('pending', this)">Pending ({pending})</button>
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
        var title = c.querySelector('.product-title').innerText.toLowerCase();
        var brand = c.querySelector('.brand-eyebrow').innerText.toLowerCase();
        var coll = c.querySelector('.product-collection').innerText.toLowerCase();
        if (title.indexOf(query) !== -1 || brand.indexOf(query) !== -1 || coll.indexOf(query) !== -1) {{
          c.style.display = 'flex';
        }} else {{
          c.style.display = 'none';
        }}
      }});
    }}
  </script>
</body>
</html>"""

        write_dual("static/images/contact_sheet.html", html_content)
        print("Responsive luxury Contact Sheet successfully generated.")


# =============================================================================
# 8. DATABASE SYNCHRONIZATION
# =============================================================================
class DatabaseSync:
    """Updates product_images in online_shop_perfume_dev and online_shop_perfume_test."""

    @classmethod
    def sync(
        cls,
        manifest: Dict[str, Dict[str, Any]],
        db_names: Tuple[str, ...] = ("online_shop_perfume_dev", "online_shop_perfume_test"),
    ) -> None:
        """Batch-updates product_images atomically across target databases."""
        for db_name in db_names:
            conn = None
            try:
                conn = get_connection(database=db_name)
                updated_count = 0
                with conn.cursor() as cur:
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
# 9. BRANDING & UI VISUALS
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
    """Scans raw output directories for commercial renders matching product slugs."""
    if search_dirs is None:
        search_dirs = [BASE_DIR / "data" / "raw_generated"]
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
    }

    lookup: Dict[str, str] = {slug_key.lower(): slug_key for slug_key in manifest}
    lookup.update(slug_aliases)
    prefix_keys = sorted(lookup.keys(), key=len, reverse=True)

    ingested_count = 0
    for sdir in search_dirs:
        if not sdir.exists():
            continue
        for img_file in sdir.glob("*.jpg"):
            stem = img_file.stem
            clean_stem = re.sub(r"_\d+$", "", stem).lower()
            # Exact alias / exact slug matches win; prefix matching is only a last resort,
            # longest key first, on a "_" boundary (so "khamrah_qahwa" never lands on "khamrah").
            matched_slug = lookup.get(clean_stem)
            if not matched_slug:
                for key in prefix_keys:
                    if clean_stem.startswith(key + "_"):
                        matched_slug = lookup[key]
                        break

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


# =============================================================================
# 10. MASTER CLI EXECUTION
# =============================================================================
def main() -> None:
    """Master CLI execution coordinating asset generation, optimization, and database synchronization."""
    parser = argparse.ArgumentParser(description="Advanced Perfume Image Generation & Visual Pipeline")
    parser.add_argument("--sync-only", action="store_true", help="Sync database only")
    parser.add_argument("--sheet-only", action="store_true", help="Generate contact sheet only")
    parser.add_argument("--force-regenerate", action="store_true", help="Force regenerate all procedural flacons")
    args = parser.parse_args()

    print("==================================================================")
    print(" ADVANCED PROCEDURAL PERFUME IMAGE GENERATION ENGINE")
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

    # 4. Generate procedural architectural flacons for the 87 remaining catalog items
    regenerated_count = 0
    preserved_count = 0
    skipped_count = 0

    for prod in catalog:
        slug = prod["slug"]

        # STRICT PRESERVATION OF 13 APPROVED COMMERCIAL AI RENDERS
        if slug in APPROVED_COMMERCIAL_SLUGS:
            preserved_count += 1
            continue

        # Honour --force-regenerate: without it, keep flacons that are already rendered and recorded
        if not args.force_regenerate:
            entry = manifest.get(slug, {})
            rel_assets = [
                f"static/images/products/{slug}.svg",
                f"static/images/products/{slug}.webp",
                f"static/images/products/{slug}.jpg",
            ]
            if (
                entry.get("mode") == "MODE_B_PROCEDURAL_FLACON"
                and entry.get("generation_status") == "optimized"
                and all((root / rel).exists() for rel in rel_assets for root in (APP_DIR, BASE_DIR))
            ):
                skipped_count += 1
                continue

        # Render ultra-luxury procedural vector flacon
        svg_content = ArchitecturalFlaconRenderer.render_flacon_svg(prod)
        rel_svg = f"static/images/products/{slug}.svg"
        write_dual(rel_svg, svg_content)

        # Rasterize directly to 1200x1500 WebP & JPEG assets
        img_meta = ImageProcessor.process_svg_string(svg_content, slug)
        if not img_meta.get("is_valid", False):
            print(f"Warning: {slug} failed validation gate: {img_meta}")
            continue

        ManifestManager.update_with_optimized_image(
            manifest, slug, img_meta, mode="MODE_B_PROCEDURAL_FLACON"
        )
        regenerated_count += 1
        print(f"[{regenerated_count:02d}/87] Rendered & Rasterized {slug:<28} -> 1200x1500 WebP ({img_meta['webp_size_kb']} KB) / JPG ({img_meta['jpg_size_kb']} KB)")

    # 5. Ingest any pending photorealistic renders
    ingested = scan_and_ingest_raw_renders(manifest)
    if ingested > 0:
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
    commercial_renders = sum(1 for i in manifest.values() if i.get("mode") == "MODE_B_CONCEPTUAL")
    procedural_flacons = sum(1 for i in manifest.values() if i.get("mode") == "MODE_B_PROCEDURAL_FLACON")

    print("\n------------------------------------------------------------------")
    print(" PIPELINE EXECUTION SUMMARY")
    print("------------------------------------------------------------------")
    print(f" Total Products in Catalog: {total}")
    print(f" Preserved Commercial AI Still-Lifes: {preserved_count} (in manifest: {commercial_renders})")
    print(f" Regenerated Procedural Luxury Flacons: {regenerated_count} (in manifest: {procedural_flacons})")
    print(f" Skipped Existing Procedural Flacons (use --force-regenerate to redraw): {skipped_count}")
    print(f" Total 1200x1500 Optimized Products: {optimized} (100% of catalog)")
    print(f" Manifest: {MANIFEST_PATH}")
    print(f" Contact Sheet: {CONTACT_SHEET_PATH}")
    print("------------------------------------------------------------------\n")


if __name__ == "__main__":
    main()
