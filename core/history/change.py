# BSR 历史记录——增量变更 + Transaction + Snapshot

"""
BSR 的状态记录层。

每次操作记录一条 Change。一组操作可以打包为一个 Transaction。
关键 checkpoint 做全量 Snapshot。

四个核心能力：
- Change：单次修改的 before/after
- Transaction：一组 change 的原子单元
- Snapshot：全量 IFC 快照，用于回滚
- Rollback：恢复到指定 snapshot 或回退 transaction
"""

from dataclasses import dataclass, field
from contextlib import contextmanager
from typing import Optional
import hashlib
import sqlite3
import shutil
import os
from datetime import datetime


@dataclass
class Change:
    element_id: str
    property_name: str
    before: str
    after: str
    operation: str = ""
    agent_prompt: str = ""
    timestamp: str = ""
    transaction_id: str = ""  # 归属的事务

    def to_dict(self):
        return {
            "element_id": self.element_id,
            "property": self.property_name,
            "before": str(self.before),
            "after": str(self.after),
            "operation": self.operation,
            "agent_prompt": self.agent_prompt,
            "timestamp": self.timestamp or datetime.now().isoformat(),
            "transaction_id": self.transaction_id,
        }


@dataclass
class Snapshot:
    snapshot_id: str
    ifc_path: str
    ifc_hash: str
    timestamp: str
    parent_id: str = ""
    description: str = ""


class HistoryStore:
    """
    SQLite-backed 状态存储。

    schema 兼容现有 .bsr.db 文件。
    新增 transaction 表和 transaction_id 字段。
    """

    @staticmethod
    def db_path_for(ifc_path: str) -> str:
        """统一 DB 路径：IFC 同目录隐藏文件"""
        import os
        return os.path.join(os.path.dirname(os.path.abspath(ifc_path)), ".bsr.db")

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                element_id TEXT,
                property_name TEXT,
                before_value TEXT,
                after_value TEXT,
                operation TEXT,
                agent_prompt TEXT,
                timestamp TEXT,
                transaction_id TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS snapshots (
                snapshot_id TEXT PRIMARY KEY,
                ifc_path TEXT,
                ifc_hash TEXT,
                timestamp TEXT,
                parent_id TEXT DEFAULT '',
                description TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                status TEXT DEFAULT 'active',
                created_at TEXT,
                committed_at TEXT,
                description TEXT DEFAULT ''
            );
        """)
        self.conn.commit()

    # ── Transaction ──

    @contextmanager
    def transaction(self, ifc_path: str = "", description: str = ""):
        """上下文管理器：全成功 or 全回滚
        
        Usage:
            with store.transaction(ifc_path) as tx:
                tx_id = tx
                # do operations...
                # if constraint fails, raise to auto-rollback
        """
        tx_id = self.begin_tx(description)
        try:
            yield tx_id
            self.commit_tx(tx_id)
        except Exception:
            # 如果有 IFC 文件路径且 snapshot 存在，恢复
            if ifc_path:
                try:
                    self.rollback_tx(tx_id, ifc_path)
                except Exception:
                    self.abort_tx(tx_id)
            else:
                self.abort_tx(tx_id)
            raise

    def begin_tx(self, description: str = "") -> str:
        tx_id = f"tx-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}"
        self.conn.execute(
            "INSERT INTO transactions (id, status, created_at, description) VALUES (?, 'active', ?, ?)",
            (tx_id, datetime.now().isoformat(), description)
        )
        self.conn.commit()
        return tx_id

    def commit_tx(self, tx_id: str):
        self.conn.execute(
            "UPDATE transactions SET status='committed', committed_at=? WHERE id=?",
            (datetime.now().isoformat(), tx_id)
        )
        self.conn.commit()

    def abort_tx(self, tx_id: str):
        """回滚事务：删除该事务下所有 change 记录"""
        self.conn.execute("DELETE FROM changes WHERE transaction_id=?", (tx_id,))
        self.conn.execute(
            "UPDATE transactions SET status='aborted' WHERE id=?",
            (tx_id,)
        )
        self.conn.commit()

    def get_tx_status(self, tx_id: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT id, status, created_at, committed_at, description FROM transactions WHERE id=?",
            (tx_id,)
        ).fetchone()
        if row:
            return {"id": row[0], "status": row[1], "created": row[2], "committed": row[3], "description": row[4]}
        return None

    # ── Change ──

    def record_change(self, change: Change):
        d = change.to_dict()
        self.conn.execute(
            """INSERT INTO changes
               (element_id, property_name, before_value, after_value, operation, agent_prompt, timestamp, transaction_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (d["element_id"], d["property"], d["before"], d["after"],
             d["operation"], d["agent_prompt"], d["timestamp"], d["transaction_id"])
        )
        self.conn.commit()

    def get_history(self, limit: int = 20) -> list:
        return self.conn.execute(
            "SELECT * FROM changes ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()

    def get_tx_changes(self, tx_id: str) -> list:
        return self.conn.execute(
            "SELECT * FROM changes WHERE transaction_id=? ORDER BY id", (tx_id,)
        ).fetchall()

    # ── Snapshot ──

    def create_snapshot(self, ifc_path: str, description: str = "") -> Snapshot:
        with open(ifc_path, "rb") as f:
            ifc_hash = hashlib.sha256(f.read()).hexdigest()[:12]
        # 备份 IFC 文件到 .bsr_snapshots/ 目录
        snap_dir = os.path.join(os.path.dirname(os.path.abspath(ifc_path)), ".bsr_snapshots")
        os.makedirs(snap_dir, exist_ok=True)
        snap_id = f"snap-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}"
        snap_file = os.path.join(snap_dir, f"{snap_id}.ifc")
        shutil.copy2(ifc_path, snap_file)
        snap = Snapshot(
            snapshot_id=snap_id,
            ifc_path=snap_file,  # 指向备份副本
            ifc_hash=ifc_hash,
            timestamp=datetime.now().isoformat(),
            description=description,
        )
        self.conn.execute(
            "INSERT INTO snapshots (snapshot_id, ifc_path, ifc_hash, timestamp, parent_id, description) VALUES (?, ?, ?, ?, ?, ?)",
            (snap.snapshot_id, snap.ifc_path, snap.ifc_hash, snap.timestamp, "", snap.description)
        )
        self.conn.commit()
        return snap

    def get_snapshots(self, limit: int = 10) -> list:
        return self.conn.execute(
            "SELECT * FROM snapshots ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()

    def get_snapshot_by_id(self, snap_id: str) -> Optional[Snapshot]:
        row = self.conn.execute(
            "SELECT snapshot_id, ifc_path, ifc_hash, timestamp, parent_id, description FROM snapshots WHERE snapshot_id=?",
            (snap_id,)
        ).fetchone()
        if row:
            return Snapshot(snapshot_id=row[0], ifc_path=row[1], ifc_hash=row[2],
                            timestamp=row[3], parent_id=row[4], description=row[5])
        return None

    # ── Rollback ──

    def rollback_to_snapshot(self, snap: Snapshot, current_ifc_path: str) -> str:
        """回滚到指定 snapshot。"""
        src = snap.ifc_path
        dst = current_ifc_path
        if not os.path.isfile(src):
            raise FileNotFoundError(f"Snapshot IFC file not found: {src}")
        # 通过临时文件避免 SameFileError
        tmp = dst + ".rollback_tmp"
        shutil.copy2(src, tmp)
        os.replace(tmp, dst)
        self.record_change(Change(
            element_id="__system__",
            property_name="rollback",
            before=f"rolled back to {snap.snapshot_id}",
            after="",
            operation="Rollback",
            agent_prompt=f"rollback to {snap.snapshot_id} ({snap.description})",
        ))
        return dst

    def rollback_tx(self, tx_id: str, ifc_path: str):
        """
        回退一个已提交事务：找到该事务前的最后一个 snapshot，恢复。
        如果该事务前无 snapshot，报错。
        """
        tx = self.get_tx_status(tx_id)
        if not tx:
            raise ValueError(f"Transaction not found: {tx_id}")
        # 找到该事务 timestamp 之前的最后一个 snapshot
        row = self.conn.execute(
            "SELECT * FROM snapshots WHERE timestamp < (SELECT created_at FROM transactions WHERE id=?) ORDER BY timestamp DESC LIMIT 1",
            (tx_id,)
        ).fetchone()
        if not row:
            raise ValueError(f"No snapshot found before transaction {tx_id}. Cannot rollback.")
        snap = Snapshot(snapshot_id=row[0], ifc_path=row[1], ifc_hash=row[2],
                        timestamp=row[3], parent_id=row[4], description=row[5])
        self.rollback_to_snapshot(snap, ifc_path)
        self.abort_tx(tx_id)

    # ── Diff ──

    def diff_between_snapshots(self, snap_a_id: str, snap_b_id: str) -> dict:
        """比较两个 snapshot 的 IFC 文件差异"""
        a = self.get_snapshot_by_id(snap_a_id)
        b = self.get_snapshot_by_id(snap_b_id)
        if not a or not b:
            raise ValueError("Snapshot not found")
        return ifc_diff(a.ifc_path, b.ifc_path)


def ifc_diff(a_path: str, b_path: str) -> dict:
    """
    全量 IFC 差异比较。

    返回结构化差异：
    - by_type: { 'IfcWall': { added:[], removed:[], modified:[...] }, ... }
    - summary: 总数
    """
    import ifcopenshell
    ma = ifcopenshell.open(a_path)
    mb = ifcopenshell.open(b_path)

    result = {}
    total_added = 0
    total_removed = 0
    total_modified = 0

    # 检查所有实体类型
    all_types = set()
    for m in (ma, mb):
        for el in m:
            all_types.add(el.is_a())

    for t in sorted(all_types):
        a_els = {e.id(): e for e in ma.by_type(t)}
        b_els = {e.id(): e for e in mb.by_type(t)}
        a_ids = set(a_els.keys())
        b_ids = set(b_els.keys())

        added = [f"#{eid}" for eid in (b_ids - a_ids)]
        removed = [f"#{eid}" for eid in (a_ids - b_ids)]
        modified = []

        for eid in sorted(a_ids & b_ids):
            ea, eb = a_els[eid], b_els[eid]
            for attr in ("Name", "Description", "GlobalId"):
                va = str(getattr(ea, attr, "") or "")
                vb = str(getattr(eb, attr, "") or "")
                if va != vb:
                    modified.append({"element": f"#{eid}", "attr": attr, "before": va[:30], "after": vb[:30]})
            # 几何（Depth），跳过无 Representation 的类型
            if hasattr(ea, 'Representation') and ea.Representation and hasattr(eb, 'Representation') and eb.Representation:
                items_a = [it for rep in ea.Representation.Representations or [] for it in rep.Items or []]
                items_b = [it for rep in eb.Representation.Representations or [] for it in rep.Items or []]
                for item_a, item_b in zip(items_a, items_b):
                    if hasattr(item_a, 'Depth') and hasattr(item_b, 'Depth'):
                        da, db = float(item_a.Depth), float(item_b.Depth)
                        if abs(da - db) > 0.001:
                            modified.append({"element": f"#{eid}", "attr": "Depth", "before": f"{da:.2f}", "after": f"{db:.2f}"})

        if added or removed or modified:
            result[t] = {
                "added": added,
                "removed": removed,
                "modified": modified,
            }
            total_added += len(added)
            total_removed += len(removed)
            total_modified += len(modified)

    return {
        "by_type": result,
        "summary": {
            "type_count": len(result),
            "added": total_added,
            "removed": total_removed,
            "modified": total_modified,
            "total_delta": total_added + total_removed + total_modified,
        }
    }
