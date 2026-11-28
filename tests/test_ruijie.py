"""瑞节（RUIJIE）算子单测：名帖完整、三官行为达标、防篡改现形、回归重放。

命名映射：颁（授）→ issue；验（核）→ verify；销（止）→ revoke。
"""
import unittest

from ruijie import Ruijie


class TestMingtie(unittest.TestCase):
    """名帖：名、代号、职责、铭文、体系锚。"""

    def setUp(self):
        self.op = Ruijie()

    def test_describe_repo(self):
        self.assertEqual(self.op.describe()["repo"], "ruijie")

    def test_describe_code(self):
        self.assertEqual(self.op.describe()["code"], "RUIJIE")

    def test_describe_anchor(self):
        self.assertTrue(self.op.describe()["anchor"].startswith("Ω₀⊂⊙∞⊂Ω"))

    def test_describe_mingwen(self):
        self.assertTrue(self.op.describe()["mingwen"])


class TestBanGuan(unittest.TestCase):
    """颁官：持节而行，颁节为凭。"""

    def setUp(self):
        self.op = Ruijie()

    def test_issue_returns_cred(self):
        cred = self.op.issue("did:zr:001")
        self.assertEqual(cred["did"], "did:zr:001")
        self.assertEqual(cred["level"], 1)
        self.assertEqual(len(cred["token"]), 32)

    def test_issue_custom_level(self):
        self.assertEqual(self.op.issue("did:zr:002", level=3)["level"], 3)

    def test_issue_level_bounds(self):
        with self.assertRaises(ValueError):
            self.op.issue("did:zr:003", level=5)
        with self.assertRaises(ValueError):
            self.op.issue("did:zr:003", level=0)

    def test_issue_empty_did(self):
        with self.assertRaises(ValueError):
            self.op.issue("")
        with self.assertRaises(ValueError):
            self.op.issue(None)

    def test_issue_tokens_differ(self):
        c1 = self.op.issue("did:zr:001")
        c2 = self.op.issue("did:zr:001")
        self.assertNotEqual(c1["token"], c2["token"])

    def test_issue_no_token_in_ledger(self):
        """凭据令牌不入台账：台账里不得出现明文 token。"""
        cred = self.op.issue("did:zr:001")
        self.assertNotIn(cred["token"], str(self.op.ledger()))


class TestYanGuan(unittest.TestCase):
    """验官：验节乃入。"""

    def setUp(self):
        self.op = Ruijie()
        self.cred = self.op.issue("did:zr:001")

    def test_verify_valid(self):
        r = self.op.verify(self.cred)
        self.assertTrue(r["valid"])
        self.assertEqual(r["did"], "did:zr:001")
        self.assertEqual(r["level"], 1)

    def test_verify_none(self):
        self.assertFalse(self.op.verify(None)["valid"])

    def test_verify_forged(self):
        forged = dict(self.cred, token="0" * 32)
        self.assertFalse(self.op.verify(forged)["valid"])

    def test_verify_records_event(self):
        before = len(self.op.ledger())
        self.op.verify(self.cred)
        self.assertEqual(len(self.op.ledger()), before + 1)
        self.assertEqual(self.op.ledger()[-1]["event"], "verify")


class TestXiaoGuan(unittest.TestCase):
    """销官：毁节乃止。"""

    def setUp(self):
        self.op = Ruijie()
        self.cred = self.op.issue("did:zr:001")

    def test_revoke_then_verify_rejected(self):
        self.op.revoke(self.cred)
        self.assertFalse(self.op.verify(self.cred)["valid"])

    def test_revoke_unknown(self):
        with self.assertRaises(KeyError):
            self.op.revoke({"token": "无此节"})

    def test_revoke_records_event(self):
        self.op.revoke(self.cred)
        self.assertEqual(self.op.ledger()[-1]["event"], "revoke")


class TestTaizhang(unittest.TestCase):
    """台账防篡改：只增不覆盖＋前缀快照哈希。"""

    def setUp(self):
        self.op = Ruijie()

    def test_ledger_deep_copy(self):
        self.op.issue("did:zr:001")
        snapshot = self.op.ledger()
        snapshot.append({"event": "伪造"})
        self.assertEqual(len(self.op.ledger()), 1)

    def test_seal_returns_digest(self):
        self.op.issue("did:zr:001")
        self.assertEqual(len(self.op.seal()), 64)

    def test_verify_ledger_clean(self):
        self.op.issue("did:zr:001")
        self.op.verify(self.op.issue("did:zr:002"))
        self.op.seal()
        self.assertTrue(self.op.verify_ledger())

    def test_tamper_detected(self):
        """篡改现形：封存前缀内台账被改，验台账即 False。"""
        self.op.issue("did:zr:001")
        self.op.seal()
        self.op.events[0]["event"] = "越权伪造"
        self.assertFalse(self.op.verify_ledger())

    def test_append_after_seal_not_tamper(self):
        """封存后新增长的合法条目不算篡改。"""
        self.op.issue("did:zr:001")
        self.op.seal()
        self.op.issue("did:zr:002")
        self.assertTrue(self.op.verify_ledger())

    def test_verify_with_expect(self):
        self.op.issue("did:zr:001")
        digest = self.op.seal()
        self.assertTrue(self.op.verify_ledger(expect=digest))
        self.assertFalse(self.op.verify_ledger(expect="0" * 64))


class TestRegression(unittest.TestCase):
    """回归重放：v1 骨架既有行为不回退。"""

    def test_v1_flow_replay(self):
        op = Ruijie()
        cred = op.issue("did:zr:001")
        self.assertTrue(op.verify(cred)["valid"])
        d = op.describe()
        self.assertEqual(d["repo"], "ruijie")
        self.assertEqual(d["code"], "RUIJIE")


if __name__ == "__main__":
    unittest.main()
