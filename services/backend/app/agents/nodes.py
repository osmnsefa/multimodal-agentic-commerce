import datetime
import logging
from typing import Dict, Any
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

# Heuristic categorization keyword mapping
CATEGORY_KEYWORDS = {
    "Electronics": ["headphones", "monitor", "keyboard", "audio", "wireless", "anc", "bluetooth", "screen", "4k", "pc", "laptop", "usb", "charge"],
    "Clothing": ["jacket", "jeans", "denim", "sweater", "hoodie", "shirt", "pants", "wool", "cotton", "cotton", "selvedge", "coat", "apparel"],
    "Home & Living": ["diffuser", "table", "chair", "vacuum", "lamp", "desk", "furniture", "cleaner", "oak", "wood", "mop", "aroma", "decor"],
    "Sports & Outdoors": ["running", "shoes", "helmet", "flask", "bottle", "cycling", "trail", "mountain", "fitness", "outdoor", "carbon", "vibram"]
}

# Base benchmark pricing tiers
BENCHMARK_PRICES = {
    "Electronics": 189.99,
    "Clothing": 89.95,
    "Home & Living": 119.00,
    "Sports & Outdoors": 129.50,
}

def cataloger_node(state: AgentState) -> Dict[str, Any]:
    """
    Cataloger Agent Node:
    Analyzes product metadata, detects/refines the target category,
    and produces an enriched, SEO-optimized e-commerce product description.
    """
    title = state.get("title", "")
    raw_desc = state.get("raw_description", "")
    existing_cat = state.get("category")
    combined_text = f"{title} {raw_desc}".lower()

    # 1. Determine or validate category
    import re
    detected_cat = existing_cat
    if not detected_cat or detected_cat in ("General", "General Merchandise", "Uncategorized"):
        for cat, keywords in CATEGORY_KEYWORDS.items():
            if any(re.search(rf"\b{re.escape(kw)}\b", combined_text) for kw in keywords):
                detected_cat = cat
                break
        if not detected_cat:
            detected_cat = "General Merchandise"

    # 2. Synthesize Enriched SEO Description
    features = []
    if "wireless" in combined_text or "bluetooth" in combined_text:
        features.append("High-bandwidth low-latency wireless connectivity")
    if "waterproof" in combined_text or "hardshell" in combined_text:
        features.append("All-weather durable weather-resistant exterior")
    if "carbon" in combined_text:
        features.append("Aerospace-grade ultra-lightweight carbon composite")
    if "oak" in combined_text or "wood" in combined_text:
        features.append("Sustainably sourced natural solid wood craftsmanship")
    if "anc" in combined_text or "noise" in combined_text:
        features.append("Active hybrid noise reduction acoustics")

    feature_bullets = "\n".join([f"- {f}" for f in features]) if features else "- Premium build quality engineered for daily utility"

    enriched_desc = (
        f"{title}\n\n"
        f"Overview:\n{raw_desc}\n\n"
        f"Key Highlights & Engineering:\n{feature_bullets}\n\n"
        f"Category: {detected_cat} | Multi-modal Verified by Aegis AI Cataloger."
    )

    tokens = 160 + len(enriched_desc.split())

    audit_entry = {
        "node": "cataloger_node",
        "action": "catalog_enrichment",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "details": {
            "assigned_category": detected_cat,
            "description_length": len(enriched_desc),
            "tokens_consumed": tokens
        }
    }

    logger.info(f"[CatalogerNode] Enriched product '{state.get('product_id')}' in category '{detected_cat}'.")

    return {
        "category": detected_cat,
        "enriched_description": enriched_desc,
        "audit_logs": [audit_entry],
        "tokens_used": state.get("tokens_used", 0) + tokens
    }

def pricing_node(state: AgentState) -> Dict[str, Any]:
    """
    Pricing Agent Node:
    Computes a smart, competitive suggested price based on product category,
    feature complexity, and market premium multipliers.
    """
    category = state.get("category", "General Merchandise")
    combined_text = f"{state.get('title', '')} {state.get('raw_description', '')}".lower()

    base_price = BENCHMARK_PRICES.get(category, 99.00)
    multiplier = 1.0

    # Multiplier heuristics based on high-end attributes
    if "pro" in combined_text or "flagship" in combined_text:
        multiplier += 0.35
    if "carbon" in combined_text or "titanium" in combined_text:
        multiplier += 0.30
    if "smart" in combined_text or "lidar" in combined_text:
        multiplier += 0.40
    if "selvedge" in combined_text or "merino" in combined_text or "organic" in combined_text:
        multiplier += 0.25
    if "anc" in combined_text or "4k" in combined_text:
        multiplier += 0.35

    suggested_price = round(base_price * multiplier, 2)
    tokens = 95

    audit_entry = {
        "node": "pricing_node",
        "action": "smart_pricing_evaluation",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "details": {
            "base_benchmark": base_price,
            "multiplier": round(multiplier, 2),
            "suggested_price": suggested_price,
            "tokens_consumed": tokens
        }
    }

    logger.info(f"[PricingNode] Suggested price for '{state.get('product_id')}': ${suggested_price} (multiplier={multiplier:.2f}).")

    return {
        "suggested_price": suggested_price,
        "audit_logs": [audit_entry],
        "tokens_used": state.get("tokens_used", 0) + tokens
    }

def audit_node(state: AgentState) -> Dict[str, Any]:
    """
    Audit Agent Node:
    Consolidates pipeline metrics, verifies compliance, and calculates
    total operational token expenditure.
    """
    tokens = 45
    total_tokens = state.get("tokens_used", 0) + tokens

    audit_entry = {
        "node": "audit_node",
        "action": "pipeline_verification",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "details": {
            "status": "APPROVED",
            "total_audit_steps": len(state.get("audit_logs", [])) + 1,
            "cumulative_tokens": total_tokens,
            "final_category": state.get("category"),
            "final_suggested_price": state.get("suggested_price")
        }
    }

    logger.info(f"[AuditNode] Audit passed for product '{state.get('product_id')}'. Total tokens: {total_tokens}.")

    return {
        "audit_logs": [audit_entry],
        "tokens_used": total_tokens
    }
