"""
خط أنابيب التسعير الكامل — دمج مطابقة ذكية + بيانات المنافس من الكاشط + محرك التسعير.
"""
from __future__ import annotations

import logging
import os

import pandas as pd

from engines.ai_engine_enhanced import EnhancedAIPricingEngine
from utils.matcher import SmartMatcher

logger = logging.getLogger(__name__)


def _normalize_competitor_csv(df_comp: pd.DataFrame) -> pd.DataFrame:
    """يُوحّد أسماء الأعمدة بعد قراءة competitors_latest.csv من المكشطة."""
    import hashlib

    d = df_comp.copy()
    if "comp_sku" not in d.columns and "sku" in d.columns:
        d["comp_sku"] = d["sku"].fillna("").astype(str)
    elif "comp_sku" in d.columns:
        d["comp_sku"] = d["comp_sku"].fillna("").astype(str)
    elif "comp_url" in d.columns:
        d["comp_sku"] = d["comp_url"].apply(
            lambda u: hashlib.sha256(str(u).encode("utf-8")).hexdigest()[:16]
            if pd.notna(u) and str(u).strip()
            else ""
        )
    if "comp_price" not in d.columns and "price" in d.columns:
        d["comp_price"] = d["price"]
    if "comp_name" not in d.columns and "name" in d.columns:
        d["comp_name"] = d["name"]
    if "sku" not in d.columns and "comp_sku" in d.columns:
        d["sku"] = d["comp_sku"].astype(str)
    return d


def run_full_pricing_pipeline(df_mine: pd.DataFrame) -> pd.DataFrame:
    """
    هذا هو القلب النابض للنظام (Data Fusion).
    يقوم بربط بياناتك مع بيانات المنافسين المحدثة، يطابقها بذكاء، ثم يسعرها عبر الـ AI.
    """
    comp_file = "data/competitors_latest.csv"
    if not os.path.exists(comp_file):
        raise FileNotFoundError(
            "لم يتم العثور على بيانات المنافسين. الرجاء تشغيل الكاشط أولاً."
        )

    df_comp = pd.read_csv(comp_file)
    df_comp = _normalize_competitor_csv(df_comp)

    required_mine = ["sku", "name", "price", "cost"]
    for col in required_mine:
        if col not in df_mine.columns:
            df_mine[col] = 0 if col in ["price", "cost"] else ""

    if "image_url" not in df_mine.columns:
        df_mine["image_url"] = ""

    df_mine = df_mine.copy()
    df_mine["sku"] = df_mine["sku"].fillna("").astype(str)

    logger.info("جاري بدء عملية المطابقة الذكية...")
    matcher = SmartMatcher(fuzzy_threshold=88)
    matched_pairs = matcher.match_products(df_mine, df_comp)

    if matched_pairs.empty:
        raise ValueError(
            "لم يتم العثور على أي تطابق بين منتجاتك ومنتجات المنافسين."
        )

    logger.info("جاري دمج البيانات (Data Fusion)...")
    mp = matched_pairs.copy()
    mp["sku_mine"] = mp["sku_mine"].fillna("").astype(str)

    final_df = pd.merge(
        mp,
        df_mine,
        left_on="sku_mine",
        right_on="sku",
        how="left",
    )

    need_cols = ["comp_sku", "comp_price", "comp_url"]
    for c in need_cols:
        if c not in df_comp.columns:
            raise ValueError(
                f"ملف المنافسين يفتقد العمود المطلوب '{c}' بعد التطبيع. "
                "تأكد من تشغيل المكشطة الأحدث (عمود sku و price و comp_url)."
            )

    subset = df_comp[
        ["comp_sku", "comp_price", "comp_url"]
        + (["comp_name"] if "comp_name" in df_comp.columns else [])
    ].drop_duplicates(subset=["comp_sku"])

    final_df["sku_comp"] = final_df["sku_comp"].fillna("").astype(str)
    subset["comp_sku"] = subset["comp_sku"].astype(str)

    final_df = pd.merge(
        final_df,
        subset,
        left_on="sku_comp",
        right_on="comp_sku",
        how="left",
    )

    if "comp_name" not in final_df.columns and "name_comp" in final_df.columns:
        final_df["comp_name"] = final_df["name_comp"].astype(str)

    if "comp_name" not in final_df.columns:
        final_df["comp_name"] = (
            final_df["name_comp"].astype(str)
            if "name_comp" in final_df.columns
            else ""
        )

    final_df["price"] = pd.to_numeric(final_df["price"], errors="coerce").fillna(0)
    final_df["cost"] = pd.to_numeric(final_df["cost"], errors="coerce").fillna(0)
    final_df["comp_price"] = pd.to_numeric(final_df["comp_price"], errors="coerce").fillna(
        0
    )

    logger.info("جاري تشغيل محرك التسعير (VSP)...")
    ai_engine = EnhancedAIPricingEngine()
    priced_df = ai_engine.process_pricing_strategy(final_df, target_margin=0.35)

    columns_to_keep = [
        "sku",
        "name",
        "image_url",
        "cost",
        "price",
        "comp_price",
        "comp_name",
        "comp_url",
        "match_type",
        "match_score",
        "suggested_price",
        "action_required",
        "ai_luxury_factor",
        "ai_scarcity_factor",
    ]

    existing_columns_to_keep = [col for col in columns_to_keep if col in priced_df.columns]
    return priced_df[existing_columns_to_keep]
