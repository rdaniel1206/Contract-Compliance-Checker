"""Context Engineering module for structuring prompts and data payloads for agents."""

import re
from typing import Dict, Any, List

def clean_and_normalize_text(text: str) -> str:
    """Cleans up text, normalizes line breaks and whitespace."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Normalize multiple spaces while preserving paragraphs
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    return "\n".join(line for line in lines if line)

def extract_sections(text: str) -> List[Dict[str, str]]:
    """Splits contract into identifiable sections or numbered clauses."""
    cleaned = clean_and_normalize_text(text)
    paragraphs = cleaned.split("\n")
    
    sections = []
    current_title = "Preamble / General"
    current_body = []
    
    header_pattern = re.compile(
        r"^(?:section\s+\d+|clause\s+\d+|\d+\.|\barticle\s+[ivxlcdm\d]+|[A-Z\s]{4,}:|confidentiality|liability|indemnification|termination|governing law|data protection|payment|intellectual property|force majeure|warranties)",
        re.IGNORECASE
    )

    for p in paragraphs:
        if header_pattern.match(p) and len(p) < 100:
            if current_body:
                sections.append({
                    "title": current_title,
                    "content": " ".join(current_body)
                })
                current_body = []
            current_title = p
        else:
            current_body.append(p)

    if current_body:
        sections.append({
            "title": current_title,
            "content": " ".join(current_body)
        })

    return sections

def get_document_stats(text: str) -> Dict[str, Any]:
    cleaned = clean_and_normalize_text(text)
    words = cleaned.split()
    return {
        "char_count": len(cleaned),
        "word_count": len(words),
        "line_count": len(cleaned.splitlines()) if cleaned else 0
    }

def build_planner_context(text: str) -> Dict[str, Any]:
    """Prepares structured context for the Planner agent."""
    from tools.tools import summarize_text, detect_contract_type
    stats = get_document_stats(text)
    sections = extract_sections(text)
    contract_type = detect_contract_type(text)
    return {
        "raw_input": text,
        "summary": summarize_text(text, 350),
        "contract_type": contract_type,
        "stats": stats,
        "section_count": len(sections),
        "section_titles": [s["title"] for s in sections[:10]]
    }

def build_worker_context(text: str, plan: Dict[str, Any]) -> Dict[str, Any]:
    """Prepares structured context for the Worker agent."""
    sections = extract_sections(text)
    return {
        "raw_input": text,
        "plan": plan,
        "sections": sections,
        "checks_required": plan.get("checks", [])
    }

def build_evaluator_context(text: str, plan: Dict[str, Any], work_result: Dict[str, Any]) -> Dict[str, Any]:
    """Prepares structured context for the Evaluator agent."""
    return {
        "raw_input": text,
        "plan": plan,
        "work_result": work_result,
        "total_checks": len(plan.get("checks", [])),
        "clauses_analyzed": len(work_result.get("clauses", [])) if isinstance(work_result, dict) else 0
    }

