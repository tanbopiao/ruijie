# ruijie

瑞节·DID 身份信任根，权限四级之首 | RUIJIE · ZONGYUAN-ROOT Daotong Component

铭文：**持节而行，验节乃入。**

## 命名映射

| 命名 | 逻辑本体 | 架构 | 算子 |
|------|----------|------|------|
| 颁（授） | 颁节为凭 | DID＋层级（权限四级）→ 节信令牌，令牌不入台账 | `issue` |
| 验（核） | 验节乃入 | 验真伪、层级与销止状态，验而留痕 | `verify` |
| 销（止） | 毁节乃止 | 凭据即焚，再验即拒 | `revoke` |
| 台账 | 颁验销有征 | 只增不覆盖＋前缀快照哈希防篡改 | `ledger` / `seal` / `verify_ledger` |

道统出处：元极恒一·道统构件定名册 V2；术语缩影表 T024（第五批）｜体系锚 Ω₀⊂⊙∞⊂Ω。

## Install

零第三方依赖，仅 Python 3.10+ 标准库。

```bash
git clone https://github.com/tanbopiao/ruijie.git
cd ruijie
python3 -m unittest discover -s tests -v   # 运行测试套件
```

## Usage

```python
from ruijie import Ruijie

op = Ruijie()

# 颁官：为 DID 颁节，层级一至四
cred = op.issue("did:zr:001", level=1)

# 验官：验节乃入
op.verify(cred)            # {"valid": True, "did": "...", "level": 1}

# 销官：毁节乃止
op.revoke(cred)
op.verify(cred)            # {"valid": False}

# 台账防篡改
op.seal()                  # 封存快照哈希
op.verify_ledger()         # True；前缀被篡改则 False
```

## 边界

- 凭据令牌只在会话内存托管，不入台账、不入档；台账只记 DID 与事件。
- 遵循元法第四条「只增不覆盖」：方法只增不改名不删，行为变更走新版本。
- 纯标准库实现，无第三方依赖。
