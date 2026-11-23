"""瑞节（RUIJIE）算子单测：名帖完整、行为达标、只增不覆盖。"""
import unittest

from ruijie import Ruijie


class TestRuijie(unittest.TestCase):
    def setUp(self):
        self.op = Ruijie()

    def test_describe(self):
        d = self.op.describe()
        self.assertEqual(d["repo"], "ruijie")
        self.assertEqual(d["code"], "RUIJIE")
        self.assertTrue(d["anchor"].startswith("Ω₀⊂⊙∞⊂Ω"))
        self.assertTrue(d["mingwen"])

    def test_issue_verify(self):
        cred = self.op.issue("did:zr:001")
        self.assertTrue(self.op.verify(cred)["valid"])
        self.assertEqual(self.op.verify(cred)["did"], "did:zr:001")
        self.assertFalse(self.op.verify({"token": "伪节"})["valid"])


if __name__ == "__main__":
    unittest.main()
