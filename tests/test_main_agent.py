"""End-to-end integration tests for MainAgent and full pipeline."""

import os
import unittest
from main_agent import MainAgent, run_agent

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestMainAgent(unittest.TestCase):
    def setUp(self):
        self.agent = MainAgent()

    def test_handle_message_raw_text(self):
        raw_text = """MUTUAL NON-DISCLOSURE AGREEMENT
        1. Confidentiality: Each party shall maintain proprietary information confidential with reasonable care.
        2. Termination: Either party may terminate with 30 days notice.
        3. Governing Law: State of New York.
        """
        result = self.agent.handle_message(raw_text)
        
        self.assertIsNotNone(result.get("session_id"))
        self.assertEqual(result["contract_type"], "NDA")
        self.assertIn("response", result)
        self.assertIn("markdown_report", result)
        self.assertIn("score", result["meta"])

    def test_analyze_file_nda(self):
        sample_path = os.path.join(BASE_DIR, "sample_contracts", "sample_nda_standard.txt")
        if os.path.exists(sample_path):
            result = self.agent.analyze_file(sample_path)
            self.assertEqual(result["contract_type"], "NDA")
            self.assertIn("Contract Type: NDA", result["response"])

    def test_analyze_file_risky_msa(self):
        sample_path = os.path.join(BASE_DIR, "sample_contracts", "sample_vendor_msa_risky.txt")
        if os.path.exists(sample_path):
            result = self.agent.analyze_file(sample_path)
            self.assertEqual(result["contract_type"], "MSA")
            self.assertIn(result["meta"]["level"], ["HIGH", "CRITICAL"])
            self.assertTrue(len(result["meta"]["red_flags"]) > 0)

    def test_run_agent_convenience_function(self):
        output = run_agent("MUTUAL NON-DISCLOSURE AGREEMENT\n1. Confidentiality: Party shall protect trade secrets.")
        self.assertIsInstance(output, str)
        self.assertIn("CONTRACT COMPLIANCE AUDIT", output)

if __name__ == "__main__":
    unittest.main()
