"""Unit tests for individual agents (Planner, Worker, Evaluator)."""

import unittest
from agents.planner import Planner
from agents.worker import Worker
from agents.evaluator import Evaluator
from memory.session_memory import SessionMemory

class TestAgents(unittest.TestCase):
    def setUp(self):
        self.sid = SessionMemory.create_session()
        self.planner = Planner()
        self.worker = Worker()
        self.evaluator = Evaluator()

    def test_planner_create_plan(self):
        contract_text = "MUTUAL NON-DISCLOSURE AGREEMENT\nBetween Party A and Party B."
        plan = self.planner.create_plan(contract_text, self.sid)
        
        self.assertEqual(plan["session_id"], self.sid)
        self.assertEqual(plan["contract_type"], "NDA")
        self.assertIn("confidentiality_clause", plan["checks"])

    def test_worker_execute_plan(self):
        contract_text = "MUTUAL NON-DISCLOSURE AGREEMENT\n1. Confidentiality: Each party shall protect proprietary information with reasonable care."
        plan = self.planner.create_plan(contract_text, self.sid)
        work = self.worker.execute_plan(contract_text, plan, self.sid)

        self.assertIn("report", work)
        self.assertEqual(work["session_id"], self.sid)
        self.assertTrue(len(work["report"]["clauses"]) > 0)

    def test_evaluator_evaluate(self):
        contract_text = "MUTUAL NON-DISCLOSURE AGREEMENT\n1. Confidentiality: Each party shall protect proprietary information with reasonable care."
        plan = self.planner.create_plan(contract_text, self.sid)
        work = self.worker.execute_plan(contract_text, plan, self.sid)
        eval_result = self.evaluator.evaluate(contract_text, plan, work, self.sid)

        self.assertEqual(eval_result["session_id"], self.sid)
        self.assertIn("final_response", eval_result)
        self.assertIn("markdown_report", eval_result)
        self.assertIn(eval_result["level"], ["LOW", "MEDIUM", "HIGH", "CRITICAL"])

if __name__ == "__main__":
    unittest.main()
