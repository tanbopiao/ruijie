"""瑞节（RUIJIE）· DID 身份信任根，权限四级之首

道统出处：元极恒一·道统构件定名册 V2；术语缩影表 T024 ｜ 第五批
体系锚：Ω₀⊂⊙∞⊂Ω｜DID-BR-000002

工程映射：DID 身份信任根，权限四级之首。

命名映射：颁（授）→ issue 颁节为凭；验（核）→ verify 验节乃入；
销（止）→ revoke 毁节乃止；启闭台账只增不覆盖，seal/verify 前缀快照哈希防篡改。

边界：本件为算子 v0.1——三官齐备；遵循元法第四条「只增不覆盖」，
方法只增不改名不删，行为变更走新版本；凭据令牌仅会话内存，不入档不入日志，宣称与事实分离。
纯标准库，Python 3.10+。
"""

import copy
import hashlib
import json


class Ruijie:
    """瑞节（RUIJIE）算子 v0.1：颁官授、验官核、销官止。"""

    ANCHOR = "Ω₀⊂⊙∞⊂Ω｜DID-BR-000002"
    CODE = "RUIJIE"

    def __init__(self, config=None):
        self.config = dict(config or {})
        self.events = []  # 只增不覆盖：颁验销台账
        self.credentials = {}  # token → 凭据（仅会话内存）
        self._seq = 0
        self._snapshots = []  # 已封存的台账前缀快照 (长度, 哈希)

    # ---------- 名帖 ----------

    def describe(self):
        """构件名帖：名、代号、职责、铭文、体系锚。"""
        return {
            "repo": "ruijie",
            "cn": "瑞节",
            "code": self.CODE,
            "duty": "DID 身份信任根，权限四级之首",
            "mingwen": "持节而行，验节乃入",
            "anchor": self.ANCHOR,
        }

    # ---------- 颁官：持节而行 ----------

    def issue(self, did, level=1):
        """颁节为凭：为 DID 颁节，节有层级（权限四级之首）。"""
        if not did or not isinstance(did, str):
            raise ValueError("DID 不备，节不颁")
        if not isinstance(level, int) or not 1 <= level <= 4:
            raise ValueError("层级越四级之外，节不颁")
        self._seq += 1
        token = hashlib.sha256(
            ("%s|%d" % (did, self._seq)).encode("utf-8")).hexdigest()[:32]
        cred = {"did": did, "level": level, "token": token}
        self.credentials[token] = cred
        self.events.append({"event": "issue", "did": did, "level": level})
        return dict(cred)

    # ---------- 验官：验节乃入 ----------

    def verify(self, credential):
        """验节乃入：验凭据真伪、层级与销止状态。"""
        token = (credential or {}).get("token")
        cred = self.credentials.get(token)
        if cred is None:
            return {"valid": False}
        self.events.append({"event": "verify", "did": cred["did"]})
        return {"valid": True, "did": cred["did"], "level": cred["level"]}

    # ---------- 销官：毁节乃止 ----------

    def revoke(self, credential):
        """毁节乃止：凭据即焚，再验即拒。"""
        token = (credential or {}).get("token")
        cred = self.credentials.pop(token, None)
        if cred is None:
            raise KeyError("无此节，无从销")
        self.events.append({"event": "revoke", "did": cred["did"]})
        return {"revoked": True, "did": cred["did"], "level": cred["level"]}

    # ---------- 台账防篡改 ----------

    def ledger(self):
        """颁验销台账：只增不覆盖，返回深拷贝防外改。"""
        return copy.deepcopy(self.events)

    def seal(self):
        """封台账：取前缀快照哈希存证（封存动作本身不入台账），返回哈希值。"""
        digest = self._hash_prefix(len(self.events))
        self._snapshots.append((len(self.events), digest))
        return digest

    def verify_ledger(self, expect=None):
        """验台账：前缀内篡改现形返回 False；封存后新增长的合法条目不算篡改。
        expect 给定时按全量哈希比对。"""
        if expect is not None:
            return self._ledger_hash() == expect
        if not self._snapshots:
            return True  # 尚无封存，无可篡之征
        n, digest = self._snapshots[-1]
        return self._hash_prefix(n) == digest

    # ---------- 内部 ----------

    def _ledger_hash(self):
        return self._hash_prefix(len(self.events))

    def _hash_prefix(self, n):
        canonical = json.dumps(self.events[:n], ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
