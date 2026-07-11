"""
BSR Task — fix-guid

工程语言: "修复 IFC 文件中重复的 GUID"

找所有 IfcGloballyUniqueId 重复 → 生成新 GUID → 替换 → 约束检查 → 报告。

不需要 Plan。只执行。
"""

import uuid
from collections import Counter
from dataclasses import dataclass, field
from core.operation.executor import BSRExecutor, Operation
from core.constraint.engine import ConstraintEngine
from core.constraint.geometric import DepthRangeRule, GeometryExistsRule
from core.constraint.topological import ElementHasParentRule
from core.history.change import HistoryStore


@dataclass
class TaskInput:
    ifc_path: str = ""
    protected: bool = False


@dataclass
class TaskReport:
    task: str = "fix-guid"
    status: str = ""
    operations: int = 0
    fixed: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    tx_id: str = ""


def run(inp: TaskInput) -> TaskReport:
    import ifcopenshell
    report = TaskReport()
    model = ifcopenshell.open(inp.ifc_path)

    # 1. 找重复 GUID
    guid_counter = Counter()
    guid_map = {}  # guid → [elements]
    for el in model:
        g = str(el.GlobalId)
        guid_counter[g] += 1
        guid_map.setdefault(g, []).append(el)

    duplicates = {g: els for g, els in guid_map.items() if len(els) > 1}
    if not duplicates:
        report.status = "success"
        report.operations = 0
        return report

    # 2. 事务修复
    store = HistoryStore(HistoryStore.db_path_for(inp.ifc_path))
    exe = BSRExecutor(protected=inp.protected)
    def eng():
        e = ConstraintEngine()
        e.register(DepthRangeRule()); e.register(GeometryExistsRule()); e.register(ElementHasParentRule())
        return e
    exe.register_engine(eng)
    exe.register_history(lambda: store)

    tx_id = store.begin_tx(f"fix-guid: {len(duplicates)} duplicates")

    fixed = []
    for g, els in duplicates.items():
        for i, el in enumerate(els):
            if i == 0:
                continue  # 保留第一个
            new_guid = str(uuid.uuid4())
            op = Operation(
                name="ModifyProperty",
                params={"element_id": f"#{el.id()}", "property": "GlobalId", "value": new_guid},
                protection_level=2,
            )
            r = exe.execute(op, inp.ifc_path, inp.ifc_path, transaction_id=tx_id)
            if r.status == "success":
                fixed.append({"element": f"#{el.id()}", "type": el.is_a(), "old": g[:8], "new": new_guid[:8]})
            else:
                report.errors.append(f"#{el.id()} {el.is_a()}: {r.errors}")

    if report.errors:
        store.abort_tx(tx_id)
        report.status = "rejected"
        report.tx_id = tx_id
        return report

    store.commit_tx(tx_id)
    report.status = "success"
    report.operations = len(fixed)
    report.fixed = fixed
    report.tx_id = tx_id
    return report
