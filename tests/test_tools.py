"""Unit tests for contract compliance tools."""

import os
import unittest
from tools.tools import (
    summarize_text,
    detect_contract_type,
    extract_clause_text,
    analyze_clause_compliance,
    analyze_full_contract,
    load_contract_file,
    format_markdown_report
)

class TestTools(unittest.TestCase):
    def test_summarize_text(self):
        text = "This is a simple contract clause text that needs to be truncated cleanly."
        summary = summarize_text(text, max_length=30)
        self.assertTrue(len(summary) <= 35)
        self.assertTrue(summary.endswith("..."))
        self.assertEqual(summarize_text(""), "")

    def test_detect_contract_type(self):
        nda_text = "MUTUAL NON-DISCLOSURE AGREEMENT\nThis agreement protects confidential information."
        msa_text = "MASTER SERVICES AGREEMENT\nBetween Client and Contractor for Deliverables."
        dpa_text = "DATA PROCESSING ADDENDUM\nIn compliance with GDPR and Personal Data Protection."
        emp_text = "EMPLOYMENT AGREEMENT\nEmployee base salary and position details."
        sla_text = "SERVICE LEVEL AGREEMENT\n99.9% uptime and service credits."

        self.assertEqual(detect_contract_type(nda_text), "NDA")
        self.assertEqual(detect_contract_type(msa_text), "MSA")
        self.assertEqual(detect_contract_type(dpa_text), "DPA")
        self.assertEqual(detect_contract_type(emp_text), "EMPLOYMENT")
        self.assertEqual(detect_contract_type(sla_text), "SLA")

    def test_extract_clause_text(self):
        text = "Section 1. Confidentiality: Each party shall not disclose proprietary information. Section 2. Governing Law: Governed by Delaware."
        conf = extract_clause_text(text, "confidentiality_clause")
        gov = extract_clause_text(text, "governing_law_clause")
        
        self.assertIsNotNone(conf)
        self.assertIsNotNone(gov)
        self.assertIn("disclose", conf.lower())

    def test_analyze_clause_compliance(self):
        risky_liability = "Contractor shall have unlimited liability for all direct and indirect damages without limitation."
        res = analyze_clause_compliance("liability_clause", risky_liability, "MSA")
        self.assertEqual(res["risk_level"], "HIGH")
        self.assertTrue(len(res["red_flags"]) > 0)

        missing_res = analyze_clause_compliance("liability_clause", None, "MSA")
        self.assertEqual(missing_res["status"], "MISSING_CRITICAL")
        self.assertEqual(missing_res["risk_level"], "HIGH")

    def test_analyze_full_contract(self):
        contract = """MUTUAL NON-DISCLOSURE AGREEMENT
        1. Confidentiality: Party shall protect proprietary information with reasonable care, excluding public knowledge or required by law.
        2. Term: Terminate upon thirty days notice.
        3. Governing Law: State of Delaware.
        """
        plan = {
            "contract_type": "NDA",
            "checks": ["confidentiality_clause", "termination_clause", "governing_law_clause"]
        }
        res = analyze_full_contract(plan, contract)
        self.assertIn("overall_risk", res)
        self.assertEqual(len(res["clauses"]), 3)

    def test_format_markdown_report(self):
        report_data = {
            "contract_type": "NDA",
            "overall_risk": {"score": 0.2, "level": "LOW", "total_red_flags": 0, "reason": "Passed"},
            "clauses": [
                {
                    "clause_type": "confidentiality_clause",
                    "status": "FOUND",
                    "risk_level": "LOW",
                    "risk_score": 0.2,
                    "red_flags": [],
                    "recommendation": "Standard terms."
                }
            ]
        }
        md = format_markdown_report(report_data)
        self.assertIn("# Contract Compliance Audit Report", md)
        self.assertIn("NDA", md)

if __name__ == "__main__":
    unittest.main()
