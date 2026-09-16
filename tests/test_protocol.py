"""Unit tests for A2A communication protocol."""

import unittest
from core.a2a_protocol import (
    create_message,
    make_plan_request,
    make_plan_response,
    make_work_request,
    make_work_response,
    make_eval_request,
    make_eval_response
)

class TestA2AProtocol(unittest.TestCase):
    def test_create_message(self):
        msg = create_message("main_agent", "planner", "TEST_TYPE", {"hello": "world"}, "test-sid")
        self.assertEqual(msg["sender"], "main_agent")
        self.assertEqual(msg["receiver"], "planner")
        self.assertEqual(msg["message_type"], "TEST_TYPE")
        self.assertEqual(msg["session_id"], "test-sid")
        self.assertIn("timestamp", msg)
        self.assertIn("message_id", msg)

    def test_plan_lifecycle_messages(self):
        req = make_plan_request("sid-1", "Contract text here")
        self.assertEqual(req["message_type"], "PLAN_REQUEST")
        self.assertEqual(req["receiver"], "planner")

        res = make_plan_response("sid-1", {"contract_type": "NDA", "checks": []})
        self.assertEqual(res["message_type"], "PLAN_RESPONSE")
        self.assertEqual(res["sender"], "planner")

    def test_work_and_eval_messages(self):
        work_req = make_work_request("sid-2", {"checks": []}, "Contract text")
        self.assertEqual(work_req["message_type"], "WORK_REQUEST")

        eval_req = make_eval_request("sid-2", {}, {}, "Contract text")
        self.assertEqual(eval_req["message_type"], "EVAL_REQUEST")

if __name__ == "__main__":
    unittest.main()
