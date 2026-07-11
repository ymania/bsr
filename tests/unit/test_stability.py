"""BSR 测试 — History 三件套 + Transaction + Constraint + Rollback"""

import os, json, sys, tempfile, shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.history.change import HistoryStore, Change
from core.constraint.engine import ConstraintEngine
from core.constraint.geometric import DepthRangeRule, GeometryExistsRule
from core.constraint.topological import ElementHasParentRule


# ── Helpers ──

_TMP = None
_IFC_PATH = None


def setup_module():
    global _TMP, _IFC_PATH
    _TMP = tempfile.mkdtemp()
    # 复制一个真实 IFC 用于集成测试
    src = os.path.join(os.path.dirname(__file__), "..", "..",
                       "examples/ifc/building/wall-with-opening-and-window.ifc")
    _IFC_PATH = os.path.join(_TMP, "test.ifc")
    if os.path.isfile(src):
        shutil.copy2(src, _IFC_PATH)


def teardown_module():
    if _TMP and os.path.isdir(_TMP):
        shutil.rmtree(_TMP)


def _db_path(ifc_path=None):
    p = ifc_path or _IFC_PATH
    return p.replace(".ifc", ".bsr.db")


# ── Test 1: History 三件套 ──


def test_history_write_and_read():
    """bsr history 能写入并读取记录"""
    db = _db_path()
    if os.path.isfile(db):
        os.remove(db)
    store = HistoryStore(db)

    store.record_change(Change(
        element_id="#37", property_name="Depth",
        before="3.0", after="4.0",
        operation="ModifyProperty",
    ))

    rows = store.get_history(10)
    assert len(rows) >= 1
    assert rows[0][1] == "#37"     # element_id
    assert rows[0][2] == "Depth"    # property
    assert rows[0][3] == "3.0"      # before
    assert rows[0][4] == "4.0"      # after


def test_history_persists_across_sessions():
    """同一个 .bsr.db 跨 session 读取数据不变"""
    db = _db_path()
    if not os.path.isfile(db):
        # 前一个测试如果没跑，手动建
        store = HistoryStore(db)
        store.record_change(Change(element_id="#1", property_name="Name",
                                   before="old", after="new"))
    count1 = len(HistoryStore(db).get_history(100))
    count2 = len(HistoryStore(db).get_history(100))
    assert count1 == count2, f"count mismatch: {count1} vs {count2}"
    assert count1 > 0


# ── Test 2: Transaction ──


def test_transaction_commit():
    """Transaction commit 后 change 可见"""
    db = _db_path() + ".tx"
    if os.path.isfile(db):
        os.remove(db)
    store = HistoryStore(db)

    tx_id = store.begin_tx("test tx")
    store.record_change(Change(element_id="#10", property_name="Name",
                               before="A", after="B", transaction_id=tx_id))
    store.commit_tx(tx_id)

    status = store.get_tx_status(tx_id)
    assert status["status"] == "committed"
    changes = store.get_tx_changes(tx_id)
    assert len(changes) == 1


def test_transaction_abort():
    """Transaction abort 后 change 不可见"""
    db = _db_path() + ".tx"
    if os.path.isfile(db):
        os.remove(db)
    store = HistoryStore(db)

    tx_id = store.begin_tx("abort test")
    store.record_change(Change(element_id="#20", property_name="Name",
                               before="X", after="Y", transaction_id=tx_id))
    store.abort_tx(tx_id)

    status = store.get_tx_status(tx_id)
    assert status["status"] == "aborted"
    changes = store.get_tx_changes(tx_id)
    assert len(changes) == 0


def test_transaction_context_manager_commits():
    """with transaction(): 成功时自动 commit"""
    db = _db_path() + ".ctx"
    if os.path.isfile(db):
        os.remove(db)
    store = HistoryStore(db)

    with store.transaction(description="ctx commit") as tx_id:
        store.record_change(Change(element_id="#30", property_name="Name",
                                   before="C", after="D", transaction_id=tx_id))

    status = store.get_tx_status(tx_id)
    assert status["status"] == "committed"


def test_transaction_context_manager_aborts_on_error():
    """with transaction(): 异常时自动 abort"""
    db = _db_path() + ".ctx2"
    if os.path.isfile(db):
        os.remove(db)
    store = HistoryStore(db)

    try:
        with store.transaction(description="ctx abort") as tx_id:
            store.record_change(Change(element_id="#40", property_name="Name",
                                       before="E", after="F", transaction_id=tx_id))
            raise ValueError("constraint fail")
    except ValueError:
        pass

    # tx 状态应为 aborted
    status = store.get_tx_status(tx_id)
    assert status["status"] == "aborted"


# ── Test 3: Constraint ──


def test_constraint_engine_summary():
    """ConstraintEngine 能正确汇总结果"""
    eng = ConstraintEngine()
    eng.register(DepthRangeRule())
    eng.register(GeometryExistsRule())
    eng.register(ElementHasParentRule())

    import ifcopenshell
    model = ifcopenshell.open(_IFC_PATH)
    results = eng.check_all(model)
    summary = eng.summary(results)

    assert summary["total"] > 0
    assert summary["passed"] + summary["failed"] == summary["total"]


def test_constraint_depth_range_expected_fail():
    """wall-with-opening: Depth=2000m 应在 DepthRangeRule 上 FAIL"""
    import ifcopenshell
    eng = ConstraintEngine()
    eng.register(DepthRangeRule())
    model = ifcopenshell.open(_IFC_PATH)
    results = eng.check_all(model)
    depth_results = [r for r in results if r.rule == "DepthRangeRule"]
    fails = [r for r in depth_results if not r.passed]
    # 这个文件 Wall Depth=2000.0m > 20.0
    assert len(fails) >= 1, "Expected DepthRangeRule FAIL for unrealistically thick wall"


# ── Test 4: Snapshot + Rollback ──


def test_snapshot_creation():
    """create_snapshot 生成备份文件并记录 hash"""
    db = _db_path() + ".snap"
    if os.path.isfile(db):
        os.remove(db)
    store = HistoryStore(db)

    snap = store.create_snapshot(_IFC_PATH, "test snapshot")
    assert snap.snapshot_id.startswith("snap-")
    assert os.path.isfile(snap.ifc_path)
    assert len(snap.ifc_hash) == 12

    # 验证能从 store 读回
    loaded = store.get_snapshot_by_id(snap.snapshot_id)
    assert loaded is not None
    assert loaded.ifc_hash == snap.ifc_hash


def test_rollback_restores_file():
    """rollback_to_snapshot 能恢复 IFC 文件内容"""
    db = _db_path() + ".rb"
    if os.path.isfile(db):
        os.remove(db)
    store = HistoryStore(db)

    import ifcopenshell

    # 1. 读原始 Name
    model_orig = ifcopenshell.open(_IFC_PATH)
    orig_entity_count = len(list(model_orig))

    # 2. snapshot
    snap = store.create_snapshot(_IFC_PATH, "pre-edit")

    # 3. 修改 IFC
    model = ifcopenshell.open(_IFC_PATH)
    walls = list(model.by_type("IfcWall"))
    if walls:
        walls[0].Name = "MODIFIED_BY_TEST"
    model.write(_IFC_PATH)

    # 4. rollback
    store.rollback_to_snapshot(snap, _IFC_PATH)

    # 5. 验证恢复
    model_restored = ifcopenshell.open(_IFC_PATH)
    restored_walls = list(model_restored.by_type("IfcWall"))
    if restored_walls:
        assert restored_walls[0].Name != "MODIFIED_BY_TEST", "Rollback did not revert Name"


def test_rollback_tx():
    """rollback_tx 回退事务并标记 aborted"""
    db = _db_path() + ".rtx"
    if os.path.isfile(db):
        os.remove(db)
    store = HistoryStore(db)

    # 1. snapshot 前
    snap = store.create_snapshot(_IFC_PATH, "before-tx")

    # 2. 开事务、做修改
    tx_id = store.begin_tx("test rollback tx")
    store.record_change(Change(element_id="#999", property_name="Name",
                               before="ORIG", after="EDITED", transaction_id=tx_id))
    store.commit_tx(tx_id)

    # 3. rollback 该事务
    store.rollback_tx(tx_id, _IFC_PATH)

    # 4. 事务状态
    status = store.get_tx_status(tx_id)
    assert status["status"] == "aborted"


# ── Test 5: Diff ──


def test_diff_same_file():
    """diff 相同文件应返回空差异"""
    from core.history.change import ifc_diff
    d = ifc_diff(_IFC_PATH, _IFC_PATH)
    assert d["summary"]["total_delta"] == 0


def test_diff_after_modification():
    """diff 修改后应检测到差异"""
    from core.history.change import ifc_diff
    import ifcopenshell

    tmp2 = os.path.join(_TMP, "test_modified.ifc")
    shutil.copy2(_IFC_PATH, tmp2)

    # 修改副本
    model = ifcopenshell.open(tmp2)
    for w in model.by_type("IfcWall"):
        w.Name = "DIFF_TEST"
        break
    model.write(tmp2)

    d = ifc_diff(_IFC_PATH, tmp2)
    assert d["summary"]["total_delta"] > 0, "Modified file should show diff"
