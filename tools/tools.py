from typing import Dict, Any

def summarize_text(text: str, max_length: int = 200) -> str:
    if not text:
        return ""
    text = text.strip().replace("\n", " ")
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."

def simple_risk_score(text: str) -> Dict[str, Any]:
    if not text:
        return {"score": 0.0, "level": "LOW", "reason": "No text provided."}

    length = len(text)
    if length < 50:
        level = "LOW"; score = 0.2
    elif length < 200:
        level = "MEDIUM"; score = 0.5
    else:
        level = "HIGH"; score = 0.8

    return {"score": score, "level": level, "reason": f"Length-based risk ({length})."}

def detect_contract_type(user_input: str) -> str:
    text = user_input.lower()
    if "nda" in text: return "NDA"
    if "msa" in text: return "MSA"
    if "sla" in text: return "SLA"
    return "GENERIC"

def generate_dummy_clause_report(plan: Dict[str, Any], user_input: str) -> Dict[str, Any]:
    clauses = []
    for check in plan.get("checks", []):
        snippet = summarize_text(user_input, max_length=120)
        risk = simple_risk_score(snippet)
        clauses.append({
            "clause_type": check,
            "found": True,
            "risk_level": risk["level"],
            "risk_score": risk["score"],
            "reason": risk["reason"],
            "excerpt": snippet,
        })

    overall = simple_risk_score(user_input)
    return {"overall_risk": overall, "clauses": clauses}
