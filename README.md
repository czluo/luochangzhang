# materialist-dev · 原则1.1

> 给 AI 编码助手的**疑难技术决策**把关 skill：先调查再发言、抓主要矛盾彻底解决、定位真身、把个案升为规律。
> 别称「原则1.1」。无需运行环境，纯文本即插即用。
> 📖 English: [README.en.md](README.en.md) · 英文版 skill：[SKILL.en.md](SKILL.en.md) + [references/01-principles.en.md](references/01-principles.en.md)

## 它治什么病

AI 写代码很少"写不出来"，更多是**判断错位**：

| 常见表现 | 本 skill 的定性 |
|---|---|
| 「我先给个初步看法，之后再核实」 | 违反 §2 没有调查就没有发言权 |
| 两案之间递给你「A 最小改法 / B 彻底方案」让你选 | 违反 §3 只给唯一彻底方案 |
| 残留 `deprecated` 参数、兼容壳、新旧并存 | 违反 §3 禁向后兼容 |
| 症状反复：加去重、加开关、加兜底 | 违反 §4 治现象未治矛盾 |
| `TIMEOUT = 实测最大值 * 2` 写进常量 | 违反 §4 把现象边界当普适常量 |
| 每加一个模块就多一条特例规则 | 违反 §5 抽象失败，维护点随规模增长 |

## 三条原则 + 一条抽查

| | 原则 | 一句话 |
|---|---|---|
| §2 | 前提 | 结论只能来自可复现的取证；犹豫要不要核实 ⇒ 查 |
| §3 | 原则① 抓主要矛盾 | 两案择一取最彻底者；同批旧形态必须消失，禁兼容壳 |
| §4 | 原则② 定位真身 | 先问"这个概念有几处在定义它"；规则必须说得出矛盾 + 定义域 |
| §5 | 原则③ 上升规律 | 个案提炼为不变式：新场景零新增规则、维护点不随规模增长 |
| §6 | 自查 | 经验主义 / 教条主义 / 唯理论三个变种 |
| §7 | 机械抽查 | 任取一个阈值：由什么矛盾推出？推导式？定义域？ |

## 安装

**CodeBuddy / Claude Code（skills 目录）**

```bash
git clone https://github.com/<you>/materialist-dev.git ~/.codebuddy/skills/materialist-dev
# Claude Code: ~/.claude/skills/materialist-dev
# 项目内共用: <repo>/.codebuddy/skills/materialist-dev
```

Windows（PowerShell）：

```powershell
git clone https://github.com/<you>/materialist-dev.git "$HOME\.codebuddy\skills\materialist-dev"
```

**其他工具（Cursor / Cline / 自建 Agent）**

- 把 `SKILL.md` 全文放进 rules 或系统提示；
- 需要完整判据时，让模型读 `references/01-principles.md`（约 150 行，一次读完不占上下文）；
- 只想要最小版：`SKILL.md` 前 9 行（心智锚 + 路线）即可生效。

## 触发方式

无需记命令，命中这些场景就会自动加载（见 `SKILL.md` 场景表）：

- 疑难 bug、症状反复、同一问题修了两次还在
- 两案择一、要不要"先兼容以后删"
- 定阈值 / 超时 / 上限 / 边界值 / 解析规则
- 审查方案或他人代码改动的根本性把关
- 怀疑自己在凭经验下结论

## 设计取舍（为什么这么短）

- `SKILL.md` ≈ 26 行 = **索引层**：心智锚 + 8 行场景表 + 无条件三动作，常驻上下文成本极低；
- `references/01-principles.md` = **真身**：三原则的完整判据，只在命中场景时读，读全不截断；
- 判据尽量写成**可机械验**的形式（能 grep、能数定义处、能比对同批旧形态是否消失），避免"看起来很对但没法验收"的原则话。

## 仓库结构

```
materialist-dev/
├── SKILL.md                     # 索引层（中文）：心智锚 + 场景→锚句 + 三项无条件动作
├── SKILL.en.md                  # 索引层（英文）
├── references/
│   ├── 01-principles.md         # 真身（中文）：§1 路线 · §2 前提 · §3-§5 三原则 · §6 变种 · §7 抽查
│   └── 01-principles.en.md      # 真身（英文）
├── README.md / README.en.md
└── LICENSE
```

**语言选择**：中文用 `SKILL.md` + `references/01-principles.md`；英文用 `SKILL.en.md` + `references/01-principles.en.md`。两者判据等价，按模型语种适应度装其一即可。

## 它不是什么

- 不是代码规范（命名 / 格式 / 目录结构另找规范）；
- 不是流程规范（评审流程、发布流程按团队自己的走）；
- 不提供"标准答案"，只强制你把**矛盾、推导式、定义域**三件事说出来——说不出来就必须标为假设。

## English summary

A decision-gating skill for AI coding agents facing hard technical choices. It enforces a materialist epistemology: investigate before asserting, resolve the *principal contradiction* (no compatibility shims), locate the single source of truth, and promote one-off fixes into invariants with explicit domains of validity. Every rule must state the contradiction it resolves, its derivation, and its domain — otherwise it must be labeled an assumption.

## License

MIT — see [LICENSE](LICENSE).
