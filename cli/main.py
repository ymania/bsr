"""
BSR CLI — Building State Runtime 终端工具

使用模式：
  bsr inspect <file>        查看 IFC 详情
  bsr check <file>          合规检查
  bsr set <file> <mods>     修改参数
  bsr log <file>            查看修改记录
  bsr diff <a> <b>          对比两个 IFC
  bsr history <file>        完整的修改历史列表
  bsr status <file>         项目状态摘要
  bsr task <name> <file> [options]  执行工程任务
"""

import sys, os, json
import click

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.constraint.engine import ConstraintEngine
from core.constraint.geometric import DepthRangeRule, GeometryExistsRule
from core.constraint.topological import ElementHasParentRule
from core.history.change import HistoryStore
from core.operation.executor import BSRExecutor, Operation
from core.protocol_handler import ProtocolHandler


_def_eng = lambda: (
    (e := ConstraintEngine(), e.register(DepthRangeRule()),
     e.register(GeometryExistsRule()), e.register(ElementHasParentRule()), e)[-1]
)


def _store(path):
    return HistoryStore(_db_path(path))



def _db_path(path):
    """统一 DB 文件路径（隐藏文件，IFC 同目录）"""
    return os.path.join(
        os.path.dirname(os.path.abspath(path)), ".bsr.db"
    )


# ============================================================
# bsr inspect — 看一眼文件就知道要不要动它
# ============================================================
@click.command("inspect")
@click.argument("ifc_path", type=click.Path(exists=True))
def cmd_inspect(ifc_path):
    """查看 IFC 详情"""
    import ifcopenshell
    m = ifcopenshell.open(ifc_path)
    click.echo(f"文件: {ifc_path}")
    click.echo(f"Schema: {m.schema}  |  实体: {len(list(m))}")

    for t in ["IfcWall","IfcSlab","IfcDoor","IfcWindow",
              "IfcBuildingElementProxy","IfcOpeningElement","IfcStair"]:
        els = list(m.by_type(t))
        if not els:
            continue
        click.echo(f"\n  {t} x{len(els)}:")
        for e in els[:6]:
            name = e.Name or f"#{e.id()}"
            extra = ""
            if e.Representation:
                for rep in (e.Representation.Representations or []):
                    for it in (rep.Items or []):
                        if hasattr(it, 'Depth'):
                            extra = f" Depth={float(it.Depth):.2f}"
            click.echo(f"    #{e.id()} {name}{extra}")
        if len(els) > 6:
            click.echo(f"    ... 还有 {len(els)-6} 个")


# ============================================================
# bsr check — 只说 FAIL，不说 PASS
# ============================================================
@click.command("check")
@click.argument("ifc_path", type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True, help="JSON 输出")
@click.option("--proto", is_flag=True, help="PROTECTED 模式")
def cmd_check(ifc_path, as_json, proto):
    """合规检查"""
    import ifcopenshell
    m = ifcopenshell.open(ifc_path)
    eng = _def_eng()
    results = eng.check_all(m)
    summary = eng.summary(results)

    if as_json:
        click.echo(json.dumps({
            "summary": summary,
            "fails": [{"rule": r.rule, "element": r.element_id, "msg": r.message}
                      for r in results if not r.passed]
        }, indent=2))
        return

    if summary["passed_all"]:
        click.echo("✅ 全部通过")
        return

    click.echo(f"❌ {summary['failed']} 项未通过:")
    for r in results:
        if not r.passed:
            click.echo(f"  {r.rule} @ {r.element_id} — {r.message}")

    if proto:
        raise SystemExit(1)


# ============================================================
# bsr set — 核心命令，支持自然语言和参数化两种输入
# ============================================================
@click.command("set")
@click.argument("ifc_path", type=click.Path(exists=True))
@click.argument("mods", nargs=-1, required=True)
@click.option("--out", default="", help="另存到（默认覆盖原文件）")
@click.option("--proto", is_flag=True, help="PROTECTED 模式")
def cmd_set(ifc_path, mods, out, proto):
    """修改 IFC 参数。支持两种模式：

    自然语言: bsr set file.ifc "把 building_0 改成 4m"

    参数化:   bsr set file.ifc --element #37 --depth 4.0

    批量:     bsr set file.ifc "#37.depth=4.0" "#37.Name=new"
    """
    import ifcopenshell

    text = " ".join(mods)
    store = _store(ifc_path)
    exe = BSRExecutor(protected=proto)
    exe.register_engine(_def_eng)
    exe.register_history(lambda: store)

    # 尝试自然语言解析
    h = ProtocolHandler()
    op = h.parse(text)
    if op:
        click.echo(f"→ {op.name}: {op.params}")
        r = exe.execute(op, ifc_path, out or ifc_path)
    else:
        # 参数化模式：key=value
        params = {"element_id": "", "property": "", "value": ""}
        for pair in mods:
            if "=" in pair:
                k, v = pair.split("=", 1)
                k = k.lower().strip()
                if k in ("element", "e", "id"):
                    params["element_id"] = v
                elif k in ("property", "p", "attr"):
                    params["property"] = v
                elif k in ("value", "v", "to", "深度", "高度", "depth", "name"):
                    params["property"] = params.get("property") or {
                        "深度": "Depth", "高度": "Depth", "depth": "Depth",
                        "name": "Name"
                    }.get(k, k)
                    params["value"] = v
        if not params["element_id"] or not params["property"]:
            click.echo("❌ 无法解析参数。示例: bsr set file.ifc element=#37 depth=4.0")
            raise SystemExit(1)
        op = Operation(name="ModifyProperty", params=params, protection_level=2,
                       agent_prompt=text)
        click.echo(f"→ {op.name}: {params}")
        r = exe.execute(op, ifc_path, out or ifc_path)

    if r.status == "success":
        click.echo(f"✅ 完成 | 影响: {r.affected_ids}")
    else:
        click.echo(f"❌ {r.errors}")
        raise SystemExit(1)


# ============================================================
# bsr log — 最近修改记录
# ============================================================
@click.command("log")
@click.argument("ifc_path", type=click.Path(exists=True))
@click.option("--limit", default=10)
def cmd_log(ifc_path, limit):
    """查看修改记录"""
    store = _store(ifc_path)
    rows = store.get_history(limit)
    if not rows:
        click.echo("无修改记录")
        return
    click.echo(f"最近 {len(rows)} 次修改:")
    for r in rows:
        click.echo(f"  #{r[0]} | {r[1]} | {r[2]}: {r[3][:20]} → {r[4][:20]} | {r[6][:40]}")


# ============================================================
# bsr history — 完整修改历史（含快照）
# ============================================================
@click.command("history")
@click.argument("ifc_path", type=click.Path(exists=True))
@click.option("--all", "all_flag", is_flag=True, help="显示所有记录")
def cmd_history(ifc_path, all_flag):
    """完整修改历史"""
    store = _store(ifc_path)
    limit = 100 if all_flag else 20
    rows = store.get_history(limit)
    snaps = store.conn.execute("SELECT * FROM snapshots ORDER BY timestamp DESC LIMIT 5").fetchall()
    if not rows:
        click.echo("无修改记录")
        return
    click.echo(f"修改 {len(rows)} 条:")
    for r in rows[:limit]:
        click.echo(f"  #{r[0]} [{r[6][:6]}] {r[1]}.{r[2]}: {r[3][:15]} → {r[4][:15]}  ({r[5]})")
    if snaps:
        click.echo(f"\n快照 {len(snaps)} 个:")
        for s in snaps[:3]:
            click.echo(f"  {s[0]} | {s[2][:12]} | {s[3][:19]}")


# ============================================================
# bsr diff — IFC 对比
# ============================================================
@click.command("diff")
@click.argument("a_path", type=click.Path(exists=True))
@click.argument("b_path", type=click.Path(exists=True))
def cmd_diff(a_path, b_path):
    """对比两个 IFC"""
    from core.history.change import ifc_diff
    d = ifc_diff(a_path, b_path)
    click.echo(json.dumps(d, indent=2, ensure_ascii=False))


# ============================================================
# bsr rollback — 回滚 IFC 文件到指定 snapshot
# ============================================================
@click.command("rollback")
@click.argument("ifc_path", type=click.Path(exists=True))
@click.option("--snapshot", default="", help="快照 ID（默认回退最近一个事务）")
@click.option("--list", "list_snaps", is_flag=True, help="列出可用快照")
def cmd_rollback(ifc_path, snapshot, list_snaps):
    """回滚 IFC 到指定快照"""
    store = _store(ifc_path)

    if list_snaps:
        snaps = store.get_snapshots(10)
        if not snaps:
            click.echo("无可用快照")
            return
        click.echo("可用快照:")
        for s in snaps:
            click.echo(f"  {s[0]} | {s[2][:12]} | {s[3][:19]} | {s[5]}")
        return

    if snapshot:
        snap = store.get_snapshot_by_id(snapshot)
        if not snap:
            click.echo(f"❌ 快照不存在: {snapshot}")
            raise SystemExit(1)
        store.rollback_to_snapshot(snap, ifc_path)
        click.echo(f"✅ 已回滚到 {snapshot}")
    else:
        # 找最后一个已提交事务
        tx = store.conn.execute(
            "SELECT id, description FROM transactions WHERE status='committed' ORDER BY committed_at DESC LIMIT 1"
        ).fetchone()
        if not tx:
            click.echo("❌ 无可回滚的已提交事务")
            raise SystemExit(1)
        store.rollback_tx(tx[0], ifc_path)
        click.echo(f"✅ 已回滚事务 {tx[0]} ({tx[1]})")


# ============================================================
# bsr constrain — 查看/解释约束规则
# ============================================================
@click.command("constrain")
@click.option("--explain", is_flag=True, help="输出规则详细信息")
@click.argument("ifc_path", type=click.Path(exists=True), required=False)
def cmd_constrain(explain, ifc_path):
    """查看约束引擎状态。--explain 输出规则详情"""
    if explain:
        rules = [
            {
                "rule": "DepthRangeRule",
                "reason": "ExtrudedAreaSolid 的 Depth 必须在合理范围",
                "location": "core/constraint/geometric.py:DepthRangeRule",
                "fix": "调整构件 Depth 到阈值内（building/wall: 0.1~20.0, vegetation: 0.01~5.0）",
            },
            {
                "rule": "GeometryExistsRule",
                "reason": "每个 BuildingElement 必须有几何表示",
                "location": "core/constraint/geometric.py:GeometryExistsRule",
                "fix": "为该构件添加 Representation（IfcExtrudedAreaSolid 或 IfcTessellation）",
            },
            {
                "rule": "ElementHasParentRule",
                "reason": "每个 BuildingElement 必须在 IfcBuildingStorey 下",
                "location": "core/constraint/topological.py:ElementHasParentRule",
                "fix": "添加 IfcRelContainedInSpatialStructure 关系将构件关联到楼层",
            },
        ]
        click.echo(json.dumps(rules, indent=2, ensure_ascii=False))
        return

    if not ifc_path:
        click.echo("用法: bsr constrain --explain (查看规则) | bsr constrain <file.ifc> (检查)")
        return


# ============================================================
# bsr task — 工程任务入口
# ============================================================
@click.command("task")
@click.argument("name", required=False)
@click.argument("ifc_path", type=click.Path(exists=True), required=False)
@click.option("--floor", default="", help="楼层（如 GroundFloor）")
@click.option("--prefix", default="R-", help="名称前缀")
@click.option("--element", multiple=True, help="指定元素 ID（可重复）")
@click.option("--proto", is_flag=True, help="PROTECTED 模式")
@click.option("--list", "list_tasks_flag", is_flag=True, help="列出所有可用任务")
def cmd_task(name, ifc_path, floor, prefix, element, proto, list_tasks_flag):
    """执行工程任务（如 rename-room）"""
    # 注册所有任务
    from tasks.naming.rename_room import run as run_rename, TaskInput as RenameInput
    from planner.router import register, run_task, list_tasks

    register("rename-room", run_rename)

    if list_tasks_flag:
        click.echo("可用任务:")
        for t in list_tasks():
            click.echo(f"  bsr task {t} <file.ifc> [options]")
        return

    if not name or not ifc_path:
        click.echo("指定任务名和 IFC 文件。bsr task --list 查看可用任务")
        raise SystemExit(1)

    # 构造输入
    if name == "rename-room":
        inp = RenameInput(floor=floor, prefix=prefix, elements=list(element) if element else [],
                          ifc_path=ifc_path, protected=proto)
    else:
        click.echo(f"unknown task: {name}. available: {list_tasks()}")
        raise SystemExit(1)

    result = run_task(name, inp)
    if not result:
        click.echo(f"task failed: {name}")
        raise SystemExit(1)

    click.echo(f"Task: {name}")
    click.echo(f"Status: {result['status']}")
    click.echo(f"Operations: {result['operations']}")
    for m in result.get("modified", [])[:5]:
        click.echo(f"  {m['element']} {m['old']} → {m['new']}")
    for e in result.get("errors", []):
        click.echo(f"  Error: {e}")
    if result["status"] != "success":
        raise SystemExit(1)


# ============================================================
# bsr status — 项目整体状态（修改次数 + 合规 + 快照）
# ============================================================
@click.command("status")
@click.argument("ifc_path", type=click.Path(exists=True))
def cmd_status(ifc_path):
    """项目状态摘要"""
    import ifcopenshell
    m = ifcopenshell.open(ifc_path)
    eng = _def_eng()
    results = eng.check_all(m)
    summary = eng.summary(results)
    store = _store(ifc_path)
    changes = store.get_history(100)
    snaps = store.conn.execute("SELECT count(*) FROM snapshots").fetchone()[0]
    c_today = sum(1 for r in changes if r[6] and "T" in r[6] and r[6].startswith(__import__('datetime').datetime.now().strftime("%Y-%m-%d")))

    click.echo(f"文件:   {ifc_path}")
    click.echo(f"实体:   {len(list(m))}")
    click.echo(f"合规:   {summary['passed']}/{summary['total']} ✅" if summary['passed_all'] else f"{summary['failed']} FAIL ❌")
    click.echo(f"修改:   {len(changes)} 次 (今日 {c_today})")
    click.echo(f"快照:   {snaps} 个")


# ============================================================
# 组装
# ============================================================
class BSRGroup(click.Group):
    def get_help(self, ctx):
        return """BSR — Building State Runtime

使用方式:
  bsr inspect file.ifc         查看 IFC 信息
  bsr check file.ifc           运行合规检查
  bsr set file.ifc <指令>      修改参数
  bsr log file.ifc             查看修改记录
  bsr history file.ifc         完整修改历史
  bsr diff a.ifc b.ifc         对比两个 IFC
  bsr rollback file.ifc        回滚到上一次快照
  bsr rollback --snapshot <id> 回滚到指定快照
  bsr constrain --explain      查看约束规则详情
  bsr status file.ifc          查看项目状态

示例:
  bsr inspect building.ifc
  bsr check building.ifc
  bsr set building.ifc "把 #37 的 Depth 改成 4.0"
  bsr set building.ifc element=#37 depth=4.0
  bsr log building.ifc
  bsr status building.ifc
"""


@click.group(cls=BSRGroup)
def cli():
    pass


cli.add_command(cmd_inspect)
cli.add_command(cmd_check)
cli.add_command(cmd_set)
cli.add_command(cmd_log)
cli.add_command(cmd_history)
cli.add_command(cmd_diff)
cli.add_command(cmd_rollback)
cli.add_command(cmd_constrain)
cli.add_command(cmd_task)
cli.add_command(cmd_status)

if __name__ == "__main__":
    cli()
