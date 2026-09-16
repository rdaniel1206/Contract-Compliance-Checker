"""Evaluator Agent for synthesizing risk assessments, red flags, and executive reports."""

from typing import Dict, Any, List
from core.context_engineering import build_evaluator_context
from core.observability import log_event
from tools.tools import format_markdown_report

class Evaluator:
    """Evaluator agent that synthesizes clause findings, calculates composite risk, and generates actionable advice."""
    NAME = "evaluator"

    def evaluate(self, contract_text: str, plan: Dict[str, Any], work: Dict[str, Any], sid: str) -> Dict[str, Any]:
        """Synthesizes analysis from Worker into a comprehensive final evaluation."""
        _ = build_evaluator_context(contract_text, plan, work)
        report = work.get("report", {})
        overall = report.get("overall_risk", {})
        clauses: List[Dict[str, Any]] = report.get("clauses", [])

        score = overall.get("score", 0.0)
        level = overall.get("level", "LOW")
        contract_type = report.get("contract_type", plan.get("contract_type", "GENERIC_CONTRACT"))

        # Collect critical red flags
        all_red_flags = []
        for c in clauses:
            for rf in c.get("red_flags", []):
                all_red_flags.append(f"[{c['clause_type'].replace('_', ' ').title()}] {rf}")

        # Summary construction
        summary_lines = [
            f"=== CONTRACT COMPLIANCE AUDIT ===",
            f"Contract Type: {contract_type}",
            f"Overall Risk Level: {level} (Score: {score}/1.0)",
            f"Total Red Flags: {len(all_red_flags)}",
            f"Clauses Inspected: {len(clauses)}",
            ""
        ]

        if all_red_flags:
            summary_lines.append("Top Identified Risks:")
            for flag in all_red_flags[:5]:
                summary_lines.append(f"  - {flag}")
            summary_lines.append("")

        summary_lines.append("Clause Breakdown:")
        for c in clauses:
            badge = "[OK]" if c["risk_level"] == "LOW" else "[!]" if c["risk_level"] == "MEDIUM" else "[X]"
            summary_lines.append(f"  {badge} {c['clause_type'].replace('_', ' ').title()}: {c['risk_level']} Risk ({c['status']})")

        summary_lines.append("\nRecommendation:")
        if level in ["HIGH", "CRITICAL"]:
            summary_lines.append("  ATTENTION REQUIRED: Multiple non-standard or high-risk provisions detected. Legal renegotiation recommended.")
        elif level == "MEDIUM":
            summary_lines.append("  MODERATE RISK: Review highlighted clauses before signing.")
        else:
            summary_lines.append("  FAVORABLE: Standard commercial terms detected with low identified legal risk.")

        summary_lines.append("\nNote: Automated analysis by Multi-Agent Contract Compliance Checker. Not formal legal advice.")

        final_text = "\n".join(summary_lines)
        markdown_report = format_markdown_report(report)

        result = {
            "session_id": sid,
            "contract_type": contract_type,
            "final_response": final_text,
            "markdown_report": markdown_report,
            "report_data": report,
            "score": score,
            "level": level,
            "red_flags": all_red_flags
        }

        log_event(self.NAME, "EVAL_COMPLETED", {
            "session_id": sid,
            "score": score,
            "level": level,
            "red_flags_count": len(all_red_flags)
        }, session_id=sid)
        return result

    def handle_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """A2A protocol handler."""
        payload = message.get("payload", {})
        sid = message.get("session_id") or payload.get("session_id", "")
        plan = payload.get("plan", {})
        work = payload.get("work_result", {})
        text = payload.get("contract_text", "")
        eval_result = self.evaluate(text, plan, work, sid)
        
        from core.a2a_protocol import make_eval_response
        return make_eval_response(sid, eval_result)

