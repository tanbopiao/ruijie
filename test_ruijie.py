"""瑞节（RUIJIE）算子骨架单测：名帖完整、桩位齐整、只增不覆盖。"""
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

    def test_issue_stub(self):
        with self.assertRaises(NotImplementedError):
            self.op.issue(None)

    def test_verify_stub(self):
        with self.assertRaises(NotImplementedError):
            self.op.verify(None)


if __name__ == "__main__":
    unittest.main()
