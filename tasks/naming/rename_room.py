"""
BSR Task — rename-room

工程语言: "把 1 楼所有房间的名称改成 R-XXX 格式"

从自然语言接收：
- floor: 目标楼层
- prefix: 名称前缀
- elements: 可选，指定具体元素 ID

不会 Plan。只会执行。
"""

from dataclasses import dataclass, field
from typing import Optional
from core.operation.executor import BSRExecutor, Operation, OperationResult
from core.constraint.engine import ConstraintEngine
from core.constraint.geometric import DepthRangeRule, GeometryExistsRule
from core.constraint.topological import ElementHasParentRule
from core.history.change import HistoryStore


@dataclass
class TaskInput:
    floor: str = ""        # "1F" / "GroundFloor"
    prefix: str = "R-"     # 名称前缀
    elements: list = field(default_factory=list)  # 具体 ID 列表（可选）
    ifc_path: str = ""
    protected: bool = False


@dataclass
class TaskReport:
    task: str = "rename-room"
    status: str = ""   # success / rejected
    operations: int = 0
    modified: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    tx_id: str = ""


def run(inp: TaskInput) -> TaskReport:
    import ifcopenshell
    report = TaskReport()

    model = ifcopenshell.open(inp.ifc_path)

    # 1. 找到目标元素
    targets = []
    if inp.elements:
        for eid in inp.elements:
            el = model.by_id(int(eid.lstrip("#"))) if eid.startswith("#") else model.by_guid(eid)
            if el:
                targets.append(el)
    elif inp.floor:
        # 按楼层查找
        for storey in model.by_type("IfcBuildingStorey"):
            if inp.floor.lower() in (storey.Name or "").lower():
                for rel in model.by_type("IfcRelContainedInSpatialStructure"):
                    if rel.RelatingStructure.id() == storey.id():
                        targets.extend(rel.RelatedElements or [])
    else:
        # 全部 building elements
        targets = list(model.by_type("IfcBuildingElementProxy")) + list(model.by_type("IfcWall"))

    if not targets:
        report.status = "rejected"
        report.errors.append("No elements found for the given floor/ID")
        return report

    # 2. 事务执行——只改建筑构件，跳过环境元素
    SKIP_KEYWORDS = ["grass", "plant", "tree", "vegetation", "sculpture", "sidewalk"]
    targets = [el for el in targets if not any(kw in (el.Name or "").lower() for kw in SKIP_KEYWORDS)]
    store = HistoryStore(HistoryStore.db_path_for(inp.ifc_path))
    exe = BSRExecutor(protected=inp.protected)
    def eng():
        e = ConstraintEngine()
        e.register(DepthRangeRule()); e.register(GeometryExistsRule()); e.register(ElementHasParentRule())
        return e
    exe.register_engine(eng)
    exe.register_history(lambda: store)

    # 执行前 snapshot（保障回滚能力）
    store.create_snapshot(inp.ifc_path, f"before rename-room {inp.floor}")

    tx_id = store.begin_tx(f"rename-room {inp.floor} prefix={inp.prefix}")

    idx = 0
    modified = []
    for el in targets:
        idx += 1
        old_name = el.Name or f"#{el.id()}"
        new_name = f"{inp.prefix}{idx}"
        op = Operation(
            name="ModifyProperty",
            params={"element_id": f"#{el.id()}", "property": "Name", "value": new_name},
            protection_level=1,
            agent_prompt=f"rename {old_name} → {new_name}",
        )
        r = exe.execute(op, inp.ifc_path, inp.ifc_path, transaction_id=tx_id)
        if r.status == "success":
            modified.append({"element": f"#{el.id()}", "old": old_name, "new": new_name})
        else:
            report.errors.append(f"#{el.id()} {old_name}: {r.errors}")

    if report.errors:
        store.abort_tx(tx_id)
        report.status = "rejected"
        report.tx_id = tx_id
        return report

    store.commit_tx(tx_id)
    report.status = "success"
    report.operations = len(modified)
    report.modified = modified
    report.tx_id = tx_id
    return report
