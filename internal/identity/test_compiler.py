"""Deterministic guardrail tests. No real personal data required."""
import unittest

from internal.identity.compiler import MAX_ATOMS, compile_identity_overlay


class IdentityCompilerTests(unittest.TestCase):
    def setUp(self):
        self.atom = {"id": "s1", "kind": "TrustBoundary",
                     "label": "Ask before publishing", "source_ref": "local:note:3",
                     "reviewed_by_user": True}

    def test_default_is_private_and_retains_nothing(self):
        overlay = compile_identity_overlay([self.atom])
        self.assertEqual(overlay.accepted, ())
        self.assertEqual(overlay.abstentions, ())

    def test_explicit_review_and_source_required(self):
        overlay = compile_identity_overlay([self.atom], user_opt_in=True)
        self.assertEqual(overlay.display()[0]["label"], "Ask before publishing")
        self.assertEqual(overlay.scope, "user_reviewed_non_diagnostic")

    def test_abstain_without_review(self):
        a = dict(self.atom, reviewed_by_user=False)
        x = compile_identity_overlay([a], user_opt_in=True)
        self.assertEqual(x.accepted, ())
        self.assertEqual(x.abstentions[0].reason, "awaiting_user_review")

    def test_reject_unanchored_or_unknown_kind(self):
        x = compile_identity_overlay([dict(self.atom, source_ref=""),
                                      dict(self.atom, id="s2", kind="Diagnosis")], user_opt_in=True)
        self.assertEqual(x.accepted, ())
        self.assertEqual([a.reason for a in x.abstentions], ["missing_source_ref", "unknown_kind"])

    def test_no_duplicate_identity_candidates(self):
        x = compile_identity_overlay([self.atom, self.atom], user_opt_in=True)
        self.assertEqual(len(x.accepted), 1)
        self.assertEqual(x.abstentions[0].reason, "invalid_or_duplicate_id")

    def test_limit_is_fail_closed(self):
        with self.assertRaises(ValueError):
            compile_identity_overlay([self.atom] * (MAX_ATOMS + 1), user_opt_in=True)

    def test_revoke_removes_output_and_source(self):
        x = compile_identity_overlay([self.atom], user_opt_in=True)
        self.assertEqual(x.revoke("s1").display(), ())
        self.assertEqual(x.revoke("s1").abstentions, ())

    def test_input_is_unchanged_and_no_narrative_diagnosis(self):
        atom = dict(self.atom)
        x = compile_identity_overlay([atom], user_opt_in=True)
        self.assertEqual(atom, self.atom)
        self.assertEqual(x.accepted[0].kind, "TrustBoundary")
        self.assertNotIn("diagnosis", repr(x).lower())


if __name__ == "__main__":
    unittest.main()
