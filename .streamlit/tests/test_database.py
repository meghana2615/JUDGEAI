"""Small regression tests for account authentication and per-user data isolation."""
import os
import tempfile
import unittest

_DB_FILE = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_DB_FILE.close()
os.environ["JUDGEAI_DB_PATH"] = _DB_FILE.name

import database  # noqa: E402


class DatabaseSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.init_db()
        database.create_user("alpha_user", "alpha@example.com", "StrongPass123")
        database.create_user("beta_user", "beta@example.com", "StrongPass123")

    def test_login_accepts_username_and_email(self):
        self.assertIsNotNone(database.authenticate_user("alpha_user", "StrongPass123"))
        self.assertIsNotNone(database.authenticate_user("alpha@example.com", "StrongPass123"))

    def test_wrong_password_is_rejected(self):
        self.assertIsNone(database.authenticate_user("alpha_user", "incorrect"))

    def test_user_records_are_isolated(self):
        result = {
            "accuracy": 8, "relevance": 7, "clarity": 9, "completeness": 6,
            "overall_score": 7.5, "strengths": "s", "weaknesses": "w",
            "improvements": "i", "verdict": "v"
        }
        alpha = database.authenticate_user("alpha_user", "StrongPass123")
        beta = database.authenticate_user("beta_user", "StrongPass123")
        database.save_evaluation(alpha["id"], "Question A", "Answer A", result, "test")
        self.assertEqual(len(database.get_history(alpha["id"])), 1)
        self.assertEqual(len(database.get_history(beta["id"])), 0)
        database.delete_evaluation(beta["id"], 1)
        self.assertEqual(len(database.get_history(alpha["id"])), 1)


    def test_personal_workspace_preferences_persist(self):
        alpha = database.authenticate_user("alpha_user", "StrongPass123")
        ok, message = database.update_preferences(
            alpha["id"], "Alpha Analyst", "AI Researcher", "Testing answer quality.",
            "#36C8F4", 30, 40, 30, 20, 10
        )
        self.assertTrue(ok, message)
        saved = database.get_user(alpha["id"])
        self.assertEqual(saved["display_name"], "Alpha Analyst")
        self.assertEqual(saved["accent_color"], "#36C8F4")
        self.assertEqual(saved["weekly_goal"], 30)
        self.assertEqual(saved["accuracy_weight"], 40)

    def test_rubric_rejects_all_zero_weights(self):
        alpha = database.authenticate_user("alpha_user", "StrongPass123")
        ok, _ = database.update_preferences(
            alpha["id"], "Alpha", "Analyst", "", "#8B5CF6", 20, 0, 0, 0, 0
        )
        self.assertFalse(ok)

    def test_registration_validation(self):
        self.assertFalse(database.create_user("x", "bad-email", "short")[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
