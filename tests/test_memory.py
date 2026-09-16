"""Unit tests for SessionMemory."""

import unittest
from memory.session_memory import SessionMemory

class TestSessionMemory(unittest.TestCase):
    def setUp(self):
        SessionMemory.clear()

    def test_create_and_get_session(self):
        sid = SessionMemory.create_session(metadata={"source": "test"})
        self.assertIsNotNone(sid)
        
        session = SessionMemory.get_session(sid)
        self.assertIsNotNone(session)
        self.assertEqual(session["metadata"]["source"], "test")

    def test_set_and_get_data(self):
        sid = SessionMemory.create_session()
        SessionMemory.set(sid, "score", 0.85)
        SessionMemory.set(sid, "contract_type", "MSA")

        self.assertEqual(SessionMemory.get(sid, "score"), 0.85)
        self.assertEqual(SessionMemory.get(sid, "contract_type"), "MSA")
        self.assertIsNone(SessionMemory.get(sid, "non_existent"))

    def test_history_logging(self):
        sid = SessionMemory.create_session()
        SessionMemory.append_history(sid, {"event": "PLAN_SENT"})
        SessionMemory.append_history(sid, {"event": "WORK_RECEIVED"})

        hist = SessionMemory.get_history(sid)
        self.assertEqual(len(hist), 2)
        self.assertEqual(hist[0]["event"], "PLAN_SENT")
        self.assertIn("timestamp", hist[0])

if __name__ == "__main__":
    unittest.main()
