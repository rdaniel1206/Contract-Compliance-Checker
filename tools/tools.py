"""Comprehensive Contract Intelligence & Compliance Analysis Tools."""

import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple

# ==========================================
# 1. Text Processing & Contract Detection
# ==========================================

def summarize_text(text: str, max_length: int = 250) -> str:
    """Summarizes text cleanly without cutting words abruptly."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_length:
        return text
    truncated = text[:max_length]
    if " " in truncated:
        truncated = truncated.rsplit(" ", 1)[0]
    return truncated + "..."

def detect_contract_type(text: str) -> str:
    """Detects the specific contract type based on legal keywords, title patterns, and clauses."""
    t = text.lower()
    first_few_lines = "\n".join(t.splitlines()[:5])
    
    scores = {
        "EMPLOYMENT": 0,
        "DPA": 0,
        "SLA": 0,
        "MSA": 0,
        "SAAS_AGREEMENT": 0,
        "NDA": 0,
        "CONSULTING": 0,
        "VENDOR_AGREEMENT": 0,
        "LEASE_AGREEMENT": 0
    }

    # High-priority document header/title detection
    if re.search(r"\b(employment\s+agreement|offer\s+letter|executive\s+employment)\b", first_few_lines):
        scores["EMPLOYMENT"] += 30
    if re.search(r"\b(data\s+processing\s+(?:agreement|addendum)|dpa|gdpr\s+data\s+processing)\b", first_few_lines):
        scores["DPA"] += 30
    if re.search(r"\b(service\s+level\s+agreement|sla)\b", first_few_lines):
        scores["SLA"] += 30
    if re.search(r"\b(master\s+services?\s+agreement|msa|master\s+agreement)\b", first_few_lines):
        scores["MSA"] += 30
    if re.search(r"\b(software\s+as\s+a\s+service|saas\s+agreement|subscription\s+agreement)\b", first_few_lines):
        scores["SAAS_AGREEMENT"] += 30
    if re.search(r"\b(non-disclosure|nondisclosure|confidentiality\s+agreement|mutual\s+nda)\b", first_few_lines):
        scores["NDA"] += 30
    if re.search(r"\b(consulting\s+agreement|independent\s+contractor\s+agreement)\b", first_few_lines):
        scores["CONSULTING"] += 30

    # Keyword frequency in body
    if re.search(r"\b(employment|employee|employer|base\s+salary|job\s+title|severance|probationary)\b", t):
        scores["EMPLOYMENT"] += 8
    if re.search(r"\b(data\s+processing|gdpr|personal\s+data|sub-processor|data\s+controller)\b", t):
        scores["DPA"] += 8
    if re.search(r"\b(uptime|service\s+credits|scheduled\s+downtime|availability\s+guarantee)\b", t):
        scores["SLA"] += 8
    if re.search(r"\b(master\s+services|statement\s+of\s+work|sow|deliverables)\b", t):
        scores["MSA"] += 8
    if re.search(r"\b(receiving\s+party|disclosing\s+party|confidential\s+information)\b", t):
        scores["NDA"] += 6
    if re.search(r"\b(cloud\s+service|authorized\s+users|license\s+grant)\b", t):
        scores["SAAS_AGREEMENT"] += 6

    # Consulting patterns
    if re.search(r"\b(consulting\s+agreement|independent\s+contractor|consultant|client)\b", t):
        scores["CONSULTING"] += 10

    # Vendor patterns
    if re.search(r"\b(vendor\s+agreement|supplier\s+agreement|procurement\s+contract|purchase\s+order)\b", t):
        scores["VENDOR_AGREEMENT"] += 10

    # Lease patterns
    if re.search(r"\b(lease\s+agreement|tenancy\s+agreement|landlord|tenant|demised\s+premises)\b", t):
        scores["LEASE_AGREEMENT"] += 10

    best_type, highest_score = max(scores.items(), key=lambda item: item[1])
    return best_type if highest_score >= 3 else "GENERIC_CONTRACT"

# ==========================================
# 2. Clause Extractors & Rule Database
# ==========================================

CLAUSE_PATTERNS = {
    "confidentiality_clause": [
        r"(?i)\b(?:confidential(?:ity)?|non-disclosure|proprietary\s+information|trade\s+secrets?)\b[^\.\n]*?(?:shall\s+keep|maintain|not\s+disclose|protect|standard\s+of\s+care|return\s+or\s+destroy|exclusions?)[^\.\n]*\.",
        r"(?i)(?:section|clause|\d+\.)?[^\n]*?(?:confidentiality|non-disclosure)[\s\S]*?(?=(?:section|clause|\d+\.|$|\n\n[A-Z]))"
    ],
    "liability_clause": [
        r"(?i)\b(?:limitation\s+of\s+liability|aggregate\s+liability|consequential\s+damages|maximum\s+liability|liability\s+cap|indirect\s+damages|punitive\s+damages)\b[^\.\n]*\.",
        r"(?i)(?:section|clause|\d+\.)?[^\n]*?(?:limitation\s+of\s+liability|liability\s+cap)[\s\S]*?(?=(?:section|clause|\d+\.|$|\n\n[A-Z]))"
    ],
    "indemnification_clause": [
        r"(?i)\b(?:indemnif(?:y|ication|ied)|hold\s+harmless|defend\s+and\s+hold\s+harmless|third-party\s+claims?)\b[^\.\n]*\.",
        r"(?i)(?:section|clause|\d+\.)?[^\n]*?(?:indemnification|indemnity)[\s\S]*?(?=(?:section|clause|\d+\.|$|\n\n[A-Z]))"
    ],
    "termination_clause": [
        r"(?i)\b(?:term\s+and\s+termination|terminate\s+for\s+convenience|terminate\s+for\s+cause|written\s+notice\s+of\s+(?:\d+|thirty|sixty|ninety)\s+days|cure\s+period|upon\s+breach)\b[^\.\n]*\.",
        r"(?i)(?:section|clause|\d+\.)?[^\n]*?(?:term\s+and\s+termination|termination\s+notice)[\s\S]*?(?=(?:section|clause|\d+\.|$|\n\n[A-Z]))"
    ],
    "governing_law_clause": [
        r"(?i)\b(?:governing\s+law|jurisdiction|applicable\s+law|dispute\s+resolution|exclusive\s+jurisdiction|arbitration|courts\s+of)\b[^\.\n]*\.",
        r"(?i)(?:section|clause|\d+\.)?[^\n]*?(?:governing\s+law|jurisdiction|dispute\s+resolution)[\s\S]*?(?=(?:section|clause|\d+\.|$|\n\n[A-Z]))"
    ],
    "data_protection_clause": [
        r"(?i)\b(?:data\s+protection|data\s+privacy|gdpr|ccpa|personal\s+data|security\s+measures|breach\s+notification|subprocessor)\b[^\.\n]*\.",
        r"(?i)(?:section|clause|\d+\.)?[^\n]*?(?:data\s+protection|privacy\s+and\s+security)[\s\S]*?(?=(?:section|clause|\d+\.|$|\n\n[A-Z]))"
    ],
    "intellectual_property_clause": [
        r"(?i)\b(?:intellectual\s+property|ip\s+rights|work\s+made\s+for\s+hire|patent|copyright|trademarks?|ownership\s+of\s+deliverables|license\s+grant)\b[^\.\n]*\.",
        r"(?i)(?:section|clause|\d+\.)?[^\n]*?(?:intellectual\s+property|ownership)[\s\S]*?(?=(?:section|clause|\d+\.|$|\n\n[A-Z]))"
    ],
    "payment_terms_clause": [
        r"(?i)\b(?:payment\s+terms|invoic(?:e|ing)|fees|net\s+\d+|due\s+within|late\s+payment\s+interest|taxes|currency)\b[^\.\n]*\.",
        r"(?i)(?:section|clause|\d+\.)?[^\n]*?(?:fees\s+and\s+payment|payment\s+terms)[\s\S]*?(?=(?:section|clause|\d+\.|$|\n\n[A-Z]))"
    ],
    "non_compete_clause": [
        r"(?i)\b(?:non-compete|non-solicitation|restrictive\s+covenant|solicit\s+employees|compete\s+with)\b[^\.\n]*\.",
        r"(?i)(?:section|clause|\d+\.)?[^\n]*?(?:non-compete|non-solicitation)[\s\S]*?(?=(?:section|clause|\d+\.|$|\n\n[A-Z]))"
    ],
    "force_majeure_clause": [
        r"(?i)\b(?:force\s+majeure|acts\s+of\s+god|unforeseeable\s+circumstances|natural\s+disasters|war|pandemic|epidemic)\b[^\.\n]*\.",
        r"(?i)(?:section|clause|\d+\.)?[^\n]*?(?:force\s+majeure)[\s\S]*?(?=(?:section|clause|\d+\.|$|\n\n[A-Z]))"
    ],
    "warranties_disclaimers_clause": [
        r"(?i)\b(?:warranties|disclaimer\s+of\s+warranties|as\s+is|merchantability|fitness\s+for\s+a\s+particular\s+purpose)\b[^\.\n]*\.",
        r"(?i)(?:section|clause|\d+\.)?[^\n]*?(?:warranties|warranty\s+disclaimer)[\s\S]*?(?=(?:section|clause|\d+\.|$|\n\n[A-Z]))"
    ]
}

def extract_clause_text(full_text: str, clause_type: str) -> Optional[str]:
    """Finds and extracts the matching clause excerpt from full text."""
    patterns = CLAUSE_PATTERNS.get(clause_type, [])
    for pattern in patterns:
        match = re.search(pattern, full_text)
        if match:
            excerpt = match.group(0).strip()
            # Clean up excerpt length
            if len(excerpt) > 600:
                excerpt = excerpt[:600].rsplit(" ", 1)[0] + "..."
            return excerpt
    return None

# ==========================================
# 3. Deep Clause Risk & Compliance Analysis
# ==========================================

def analyze_clause_compliance(clause_type: str, excerpt: Optional[str], contract_type: str) -> Dict[str, Any]:
    """Evaluates an individual clause for compliance, legal risks, and red flags."""
    if not excerpt:
        # Clause is missing in contract
        critical_clauses = ["liability_clause", "termination_clause", "governing_law_clause", "confidentiality_clause"]
        if contract_type == "DPA":
            critical_clauses.append("data_protection_clause")
            
        if clause_type in critical_clauses:
            return {
                "clause_type": clause_type,
                "found": False,
                "risk_level": "HIGH",
                "risk_score": 0.85,
                "status": "MISSING_CRITICAL",
                "reason": f"Critical clause '{clause_type.replace('_', ' ').title()}' is completely missing from the agreement.",
                "red_flags": [f"No standard '{clause_type}' terms defined."],
                "recommendation": f"Add a standard, balanced {clause_type.replace('_', ' ').title()} section to protect your rights.",
                "excerpt": ""
            }
        else:
            return {
                "clause_type": clause_type,
                "found": False,
                "risk_level": "LOW",
                "risk_score": 0.20,
                "status": "NOT_PRESENT_OPTIONAL",
                "reason": f"Optional clause '{clause_type.replace('_', ' ').title()}' is not present in this contract.",
                "red_flags": [],
                "recommendation": f"Verify if {clause_type.replace('_', ' ')} is required for this engagement.",
                "excerpt": ""
            }

    t = excerpt.lower()
    red_flags = []
    positives = []
    score = 0.2
    level = "LOW"

    # Deep rules per clause type
    if clause_type == "liability_clause":
        if re.search(r"\b(unlimited\s+liability|no\s+limitation\s+of\s+liability|without\s+limitation|shall\s+be\s+fully\s+liable)\b", t):
            red_flags.append("Unlimited liability exposure detected.")
            score += 0.65
        if not re.search(r"\b(aggregate\s+liability|cap|total\s+amount\s+paid|fees\s+paid\s+in\s+the\s+preceding)\b", t):
            red_flags.append("No explicit monetary liability cap found.")
            score += 0.35
        if re.search(r"\b(consequential|punitive|indirect|lost\s+profits)\b", t) and not re.search(r"\b(in\s+no\s+event|neither\s+party|shall\s+not\s+be\s+liable\s+for)\b", t):
            red_flags.append("Exposure to indirect or consequential damages.")
            score += 0.30
        if re.search(r"\b(aggregate\s+liability\s+shall\s+not\s+exceed|capped\s+at)\b", t):
            positives.append("Contains monetary liability cap.")

    elif clause_type == "indemnification_clause":
        if re.search(r"\b(solely\s+indemnif|unilaterally\s+indemnif|contractor\s+shall\s+indemnify\s+client\s+against\s+all)\b", t) and not re.search(r"\b(mutual|each\s+party\s+shall\s+indemnif)\b", t):
            red_flags.append("One-sided unilateral indemnification obligation.")
            score += 0.50
        if re.search(r"\b(gross\s+negligence|willful\s+misconduct)\b", t):
            positives.append("Appropriate carve-outs for willful misconduct or negligence.")
        if not re.search(r"\b(prompt\s+written\s+notice|sole\s+control\s+of\s+defense)\b", t):
            red_flags.append("Missing defense control and prompt notice procedures.")
            score += 0.25

    elif clause_type == "termination_clause":
        if re.search(r"\b(terminate\s+immediately\s+without\s+cause|at\s+any\s+time\s+without\s+notice)\b", t):
            red_flags.append("Immediate unilateral termination without cause or notice.")
            score += 0.60
        if re.search(r"\b(cure\s+period\s+of\s+(?:10|15|30)\s+days|written\s+notice\s+of\s+(?:30|60)\s+days)\b", t):
            positives.append("Includes standard notice period and cure window.")
        elif not re.search(r"\b(notice|cure|remedy)\b", t):
            red_flags.append("No cure period provided for material breach.")
            score += 0.30

    elif clause_type == "governing_law_clause":
        if re.search(r"\b(foreign|offshore|arbitration\s+in\s+unknown|non-exclusive)\b", t):
            red_flags.append("Potentially disadvantageous or foreign dispute venue.")
            score += 0.40
        if re.search(r"\b(arbitration|binding\s+arbitration|rules\s+of\s+the\s+aaa|icc)\b", t):
            positives.append("Structured arbitration mechanism specified.")

    elif clause_type == "data_protection_clause":
        if re.search(r"\b(72\s+hours|without\s+undue\s+delay|immediate\s+notification)\b", t):
            positives.append("Complies with rapid breach notification requirements.")
        else:
            red_flags.append("Missing explicit rapid breach notification timeline (e.g. 72 hours).")
            score += 0.40
        if not re.search(r"\b(technical\s+and\s+organizational\s+measures|toms|encryption|access\s+controls)\b", t):
            red_flags.append("Lack of specific security and technical safeguards.")
            score += 0.30

    elif clause_type == "confidentiality_clause":
        if re.search(r"\b(perpetual\s+obligation|indefinitely)\b", t) and not re.search(r"\b(trade\s+secrets?)\b", t):
            red_flags.append("Perpetual confidentiality duration without trade secret distinction.")
            score += 0.35
        if not re.search(r"\b(publicly\s+known|prior\s+knowledge|required\s+by\s+law|legal\s+process)\b", t):
            red_flags.append("Missing standard confidentiality exclusions (e.g., legally compelled disclosure).")
            score += 0.40
        if re.search(r"\b(exclusions?|standard\s+of\s+care|reasonable\s+care)\b", t):
            positives.append("Standard reasonable care and exclusions included.")

    elif clause_type == "non_compete_clause":
        if re.search(r"\b(worldwide|global|unlimited\s+geography|(?:3|4|5)\s+years|perpetual)\b", t):
            red_flags.append("Overly broad geographic or temporal non-compete restraint.")
            score += 0.65
        else:
            score += 0.15

    # Clamp score
    score = min(1.0, max(0.05, round(score, 2)))
    if score >= 0.70:
        level = "HIGH"
    elif score >= 0.40:
        level = "MEDIUM"
    else:
        level = "LOW"

    # Build recommendations
    rec = "Clause terms appear standard and balanced."
    if red_flags:
        rec = f"Address identified risks: {'; '.join(red_flags[:2])}"

    return {
        "clause_type": clause_type,
        "found": True,
        "risk_level": level,
        "risk_score": score,
        "status": "FOUND",
        "reason": f"Clause evaluated with {len(red_flags)} red flags and {len(positives)} positive provisions.",
        "red_flags": red_flags,
        "positives": positives,
        "recommendation": rec,
        "excerpt": excerpt
    }

def analyze_full_contract(plan: Dict[str, Any], contract_text: str) -> Dict[str, Any]:
    """Runs all checks specified in plan across the contract text."""
    contract_type = plan.get("contract_type", "GENERIC_CONTRACT")
    checks = plan.get("checks", [])
    
    analyzed_clauses = []
    total_score = 0.0
    red_flag_count = 0

    for check in checks:
        excerpt = extract_clause_text(contract_text, check)
        result = analyze_clause_compliance(check, excerpt, contract_type)
        analyzed_clauses.append(result)
        total_score += result["risk_score"]
        red_flag_count += len(result.get("red_flags", []))

    avg_score = round(total_score / max(len(checks), 1), 2)
    
    # Scale overall risk level
    if avg_score >= 0.60 or red_flag_count >= 3:
        overall_level = "CRITICAL" if avg_score >= 0.75 else "HIGH"
    elif avg_score >= 0.35 or red_flag_count >= 1:
        overall_level = "MEDIUM"
    else:
        overall_level = "LOW"

    overall_risk = {
        "score": avg_score,
        "level": overall_level,
        "total_checks": len(checks),
        "total_red_flags": red_flag_count,
        "reason": f"Analyzed {len(checks)} clauses across '{contract_type}' with {red_flag_count} red flags."
    }

    return {
        "contract_type": contract_type,
        "overall_risk": overall_risk,
        "clauses": analyzed_clauses
    }

# ==========================================
# 4. File Ingestion & Report Formatting
# ==========================================

def load_contract_file(file_path: str) -> Tuple[str, Optional[str]]:
    """Loads contract content from a local file path (.txt, .md, .json, .pdf, .docx)."""
    if not os.path.exists(file_path):
        return "", f"File does not exist: {file_path}"
    
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext in [".txt", ".md", ".log", ""]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(), None
        elif ext == ".json":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data.get("text") or data.get("content") or json.dumps(data, indent=2), None
                return str(data), None
        elif ext == ".pdf":
            # Attempt pdf extraction
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                text = "\n".join([page.extract_text() or "" for page in reader.pages])
                return text, None
            except ImportError:
                # Fallback binary text extractor for zero-dependency
                with open(file_path, "rb") as f:
                    content = f.read()
                # Extract printable strings
                strings = re.findall(rb"[A-Za-z0-9\s.,;:()'\"]{6,}", content)
                decoded = "\n".join([s.decode("latin1", errors="ignore") for s in strings])
                return decoded, "Note: Installed 'pypdf' recommended for perfect PDF parsing; fallback raw extraction used."
        elif ext == ".docx":
            try:
                import docx
                doc = docx.Document(file_path)
                text = "\n".join([p.text for p in doc.paragraphs])
                return text, None
            except ImportError:
                return "", "DOCX format requires python-docx library ('pip install python-docx')."
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(), None
    except Exception as e:
        return "", f"Error reading file {file_path}: {str(e)}"

def format_markdown_report(report_data: Dict[str, Any]) -> str:
    """Formats full compliance findings as a clean Markdown report."""
    contract_type = report_data.get("contract_type", "GENERIC_CONTRACT")
    overall = report_data.get("overall_risk", {})
    score = overall.get("score", 0.0)
    level = overall.get("level", "LOW")
    clauses = report_data.get("clauses", [])

    badge_color = "🟢" if level == "LOW" else "🟡" if level == "MEDIUM" else "🔴"
    
    md = []
    md.append(f"# Contract Compliance Audit Report")
    md.append(f"**Contract Classification**: `{contract_type}`  ")
    md.append(f"**Overall Risk Assessment**: {badge_color} **{level}** (Score: `{score}` / 1.0)  ")
    md.append(f"**Total Clauses Analyzed**: `{len(clauses)}`  ")
    md.append(f"**Total Red Flags Identified**: `{overall.get('total_red_flags', 0)}`  \n")
    md.append("---")
    md.append("## Executive Summary")
    md.append(f"> {overall.get('reason', 'Compliance audit completed successfully.')}\n")

    md.append("## Detailed Clause Analysis\n")
    md.append("| Clause Type | Status | Risk Level | Score | Red Flags | Recommendation |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

    for c in clauses:
        c_name = c["clause_type"].replace("_", " ").title()
        flags = "<br>".join([f"⚠️ {f}" for f in c.get("red_flags", [])]) if c.get("red_flags") else "None"
        md.append(f"| **{c_name}** | `{c['status']}` | `{c['risk_level']}` | `{c['risk_score']}` | {flags} | {c.get('recommendation', '')} |")

    md.append("\n## Clause Excerpts & Findings\n")
    for c in clauses:
        c_name = c["clause_type"].replace("_", " ").title()
        md.append(f"### {c_name} (`{c['risk_level']}` Risk)")
        if c.get("excerpt"):
            md.append(f"```text\n{c['excerpt']}\n```")
        else:
            md.append("*No corresponding text found in contract.*")
        if c.get("red_flags"):
            md.append("**Red Flags Identified:**")
            for flag in c["red_flags"]:
                md.append(f"- ❌ {flag}")
        if c.get("positives"):
            md.append("**Protective Terms Found:**")
            for pos in c["positives"]:
                md.append(f"- ✅ {pos}")
        md.append(f"**Actionable Advice**: {c.get('recommendation', '')}\n")

    md.append("\n---\n*Disclaimer: This automated audit report is generated by Contract Compliance Checker AI agents for evaluation purposes and does not constitute formal legal counsel.*")
    return "\n".join(md)

