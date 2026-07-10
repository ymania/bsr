# BSR — Building State Runtime

> IFC 数据的运行时层。像 Aider 操作代码一样操作 IFC 数据。
> *The runtime layer for IFC data. Manipulate IFC models the way Aider manipulates code.*

---

## 一句话 / In One Sentence

**中文**：不卖 Agent，不卖 UI，卖一个 IFC 数据的操作规范 + 约束引擎 + 版本管理基础设施。Agent 只是这个基础设施的调用者。

**English**: We don't sell an Agent or a UI. We sell an IFC data runtime — operation spec, constraint engine, and version management. The Agent is just the caller.

产品目标：**一个真实工程人员，一句话能完成过去需要半天到一天的工作。**
*Product goal: **One sentence from an engineer replaces half a day to a full day of manual work.** *

---

## 安装 / Install

```bash
pip install ifcopenshell click
git clone git@github.com:ymania/bsr.git
cd bsr && chmod +x bsr
```

---

## 快速开始 / Quick Start

```bash
# Inspect an IFC file / 查看 IFC 文件
./bsr inspect building.ifc

# Compliance check / 合规检查
./bsr check building.ifc

# Natural language modification / 自然语言修改
./bsr set building.ifc "把 #37 的 Depth 改成 4.0"

# Parametric modification / 参数化修改
./bsr set building.ifc element=#37 depth=4.0

# Engineering task / 工程任务
./bsr task rename-room building.ifc --prefix Room-

# View change log / 查看修改记录
./bsr log building.ifc

# Diff two IFC files / 对比两个 IFC
./bsr diff building.ifc building_modified.ifc

# Project status / 项目状态
./bsr status building.ifc
```

---

## 项目结构 / Project Structure

```
bsr/
├── CONSTITUTION.md              # 项目宪法（16条） / Constitution (16 articles)
├── core/                        # Runtime
│   ├── constraint/              # 约束引擎（36条规则） / Constraint engine
│   ├── history/                 # 状态记录 / History (Transaction, Snapshot, Rollback, Diff)
│   └── operation/               # 操作执行器 / Operation executor
├── tasks/                       # Task Library（工程任务）
│   ├── naming/rename_room.py    # 房间重命名 / Rename rooms
│   └── fire/fix_guid.py         # GUID 修复 / Fix duplicate GUIDs
├── planner/router.py            # 任务路由 / Task router
├── cli/main.py                  # 终端入口 / CLI entry
├── spec/                        # 四份协议文档 / 4 protocol specs
├── docs/studies/                # 标杆产品学习笔记 / Product study notes
├── plugins/                     # Revit/Rhino/Blender 入口（占位）
├── examples/                    # 真实 IFC 测试文件
└── pyproject.toml
```

---

## 五阶段成熟度 / 5-Stage Maturity

| Stage | Name | BSR Status |
|-------|------|------------|
| 1 | Tool（工具） | ✅ `bsr exec / diff / inspect` |
| 2 | Assistant（助手） | ✅ `bsr set "把 building 改成 4m"` |
| 3 | Consultant（顾问） | ⬜ Tasks: check-fire, check-lod |
| 4 | Planner（规划者） | ⬜ Automatic task decomposition |
| 5 | Partner（真正的 Agent） | ⬜ One-sentence engineering completion |

当前处于 Stage 2→3 过渡。核心 Runtime 已就绪，重心是 Task Library。
*Currently transitioning from Stage 2→3. Core Runtime is solid. Focus is now on the Task Library.*

---

## 长期架构 / Long-Term Architecture

```
User Goal ("让这个模型满足消防规范" / "Make this model fire-code compliant")
        ↓
Goal Interpreter
        ↓
Task Planner
        ↓
Building State Runtime (BSR)  ← 核心壁垒 / Core moat
    ┌────────┬────────┬────────┐
    ▼        ▼        ▼
Operation  Constraint  History
    │        │        │
    └────────┴────────┘
            ▼
           IFC
```

---

## 设计原则 / Design Principles

1. **Runtime 不依赖 LLM** — LLM 可换、Planner 可升级，但状态管理、约束验证、历史追踪必须扎实
   *Runtime does not depend on an LLM. LLMs and Planners are replaceable; state management, constraint validation, and history are not.*
2. **Task 不是 Operation** — 单位是工程任务（消防整改），不是 ModifyProperty
   *Units are engineering tasks (fire-code remediation), not ModifyProperty.*
3. **Desired State** — 用户描述最终状态，系统自己收敛（如 Kubernetes）
   *Users describe the desired state; the system converges on it (like Kubernetes).*
4. **可追踪、可验证、可恢复** — 企业放心使用
   *Traceable, verifiable, recoverable — enterprise-ready.*

---

## 学习对象 / Study References

| Product | What to Learn |
|---------|---------------|
| **GitHub Copilot** | Always aware of current Context |
| **Aider** | Diff + History + knows which files |
| **Cursor** | It's a Project, not a chat |
| **Kubernetes / Terraform** | Desired State — describe the end state, the system converges |

学习笔记在 `docs/studies/`。*Study notes live in `docs/studies/`.*

---

## 当前状态 / Current Status (2026-07-10)

- [x] Core Runtime: Operation + Constraint(36) + History(Transaction/Snapshot/Rollback/Diff)
- [x] CLI: inspect / check / set / log / diff / task
- [x] Protocol: Natural language → Operation parser
- [x] Tasks: rename-room, fix-guid
- [x] Task Planner: Router table
- [x] Spec: 4 protocol documents
- [x] Constitution: 16 articles
- [ ] Daily Task: 每天一个新 Task / Ship one new Task per day
- [ ] Real IFC test cases collection
