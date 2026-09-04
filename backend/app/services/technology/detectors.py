import re
from typing import Dict, List, Any
from app.schemas.lookup import TechnologyDetection
from app.services.technology.signatures import TECHNOLOGY_SIGNATURES

# Weights per signal type — higher = stronger evidence
SIGNAL_WEIGHTS = {
    "headers": 0.85,
    "cookies": 0.80,
    "scripts": 0.70,
    "meta": 0.65,
    "inline_js": 0.60,
    "html": 0.50,
    "js_bundle": 0.55,
}


def _evidence_label(signal_type: str, detail: str) -> str:
    labels = {
        "html": f"HTML pattern: {detail}",
        "inline_js": f"Inline script: {detail}",
        "js_bundle": f"JS bundle content: {detail}",
        "headers": f"HTTP header: {detail}",
        "cookies": f"Cookie: {detail}",
        "scripts": f"Script URL: {detail}",
        "meta": f"Meta tag: {detail}",
    }
    return labels.get(signal_type, detail)


def check_rules(
    signature: Dict[str, Any],
    html: str,
    headers: Dict[str, str],
    cookies: Dict[str, str],
    scripts: List[str],
    meta: Dict[str, str],
    inline_scripts: List[str] = None,
    js_bundle_content: str = "",
) -> tuple[bool, float, List[str]]:
    rules = signature.get("rules", {})
    weights = signature.get("confidence_weight", SIGNAL_WEIGHTS)

    score = 0.0
    evidence = []
    inline_combined = "\n".join(inline_scripts or [])

    # --- HTML ---
    for pattern in rules.get("html", []):
        if html and re.search(pattern, html, re.IGNORECASE):
            score += weights.get("html", SIGNAL_WEIGHTS["html"])
            evidence.append(_evidence_label("html", pattern))

    # --- Inline JS (inside <script> tags, NOT external) ---
    for pattern in rules.get("inline_js", []):
        if inline_combined and re.search(pattern, inline_combined, re.IGNORECASE):
            score += weights.get("inline_js", SIGNAL_WEIGHTS["inline_js"])
            evidence.append(_evidence_label("inline_js", pattern))

    # --- JS Bundle content (fetched external bundles) ---
    for pattern in rules.get("js_bundle", []):
        if js_bundle_content and re.search(pattern, js_bundle_content, re.IGNORECASE):
            score += weights.get("js_bundle", SIGNAL_WEIGHTS["js_bundle"])
            evidence.append(_evidence_label("js_bundle", pattern))

    # --- HTTP Headers ---
    for header_name, pattern in rules.get("headers", []):
        for h_key, h_val in headers.items():
            if h_key.lower() == header_name.lower():
                if re.search(pattern, h_val, re.IGNORECASE):
                    score += weights.get("headers", SIGNAL_WEIGHTS["headers"])
                    evidence.append(_evidence_label("headers", f"{header_name}: {h_val}"))

    # --- Cookies ---
    for pattern in rules.get("cookies", []):
        for cookie_name in cookies.keys():
            if re.search(pattern, cookie_name, re.IGNORECASE):
                score += weights.get("cookies", SIGNAL_WEIGHTS["cookies"])
                evidence.append(_evidence_label("cookies", cookie_name))

    # --- Script src URLs ---
    for pattern in rules.get("scripts", []):
        for script in scripts:
            if re.search(pattern, script, re.IGNORECASE):
                score += weights.get("scripts", SIGNAL_WEIGHTS["scripts"])
                evidence.append(_evidence_label("scripts", script))
                break  # avoid duplicate for same pattern

    # --- Meta tags ---
    for meta_name, pattern in rules.get("meta", []):
        for m_key, m_val in meta.items():
            if m_key.lower() == meta_name.lower():
                if re.search(pattern, m_val, re.IGNORECASE):
                    score += weights.get("meta", SIGNAL_WEIGHTS["meta"])
                    evidence.append(_evidence_label("meta", f"{meta_name}={m_val}"))

    # Cap confidence at 0.99 and deduplicate evidence
    confidence = min(score, 0.99) if score > 0 else 0.0
    unique_evidence = list(dict.fromkeys(evidence))  # preserve order, remove dups

    return confidence > 0, confidence, unique_evidence


def _get_status(confidence: float) -> str:
    if confidence >= 0.85:
        return "confirmed"
    elif confidence >= 0.65:
        return "high confidence"
    elif confidence > 0:
        return "possible"
    return "no evidence"


def detect_technologies(
    category: str,
    html: str,
    headers: Dict[str, str],
    cookies: Dict[str, str],
    scripts: List[str],
    meta: Dict[str, str],
    inline_scripts: List[str] = None,
    js_bundle_content: str = "",
) -> List[TechnologyDetection]:
    detections = []
    signatures = TECHNOLOGY_SIGNATURES.get(category, [])

    for sig in signatures:
        found, confidence, evidence = check_rules(
            sig, html, headers, cookies, scripts, meta,
            inline_scripts=inline_scripts,
            js_bundle_content=js_bundle_content,
        )
        if found:
            detections.append(TechnologyDetection(
                name=sig["name"],
                category=category,
                status=_get_status(confidence),
                confidence=round(confidence, 2),
                evidence=evidence,
            ))

    return detections


def analyze_all(
    html: str,
    headers: Dict[str, str],
    cookies: Dict[str, str],
    scripts: List[str],
    meta: Dict[str, str],
    inline_scripts: List[str] = None,
    js_bundle_content: str = "",
) -> Dict[str, List[TechnologyDetection]]:
    results = {}
    for category in TECHNOLOGY_SIGNATURES.keys():
        results[category] = detect_technologies(
            category, html, headers, cookies, scripts, meta,
            inline_scripts=inline_scripts,
            js_bundle_content=js_bundle_content,
        )
    return results
