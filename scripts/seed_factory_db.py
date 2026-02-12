from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from persistence.db import create_sqlite_engine, session_factory
from persistence.models import (
    AlarmHistory,
    CompressorEvent,
    Equipment,
    FactoryBase,
    MaintenanceLog,
    Sop,
)

DB_PATH = "factory.db"


def main() -> None:
    engine = create_sqlite_engine(DB_PATH)
    SessionLocal = session_factory(engine)

    FactoryBase.metadata.drop_all(engine)
    FactoryBase.metadata.create_all(engine)

    with SessionLocal() as session:
        session.add_all(
            [
                Equipment(
                    id=1,
                    tag="COMP-01",
                    equipment_type="compressor",
                    area="Utilities",
                    line="Line-A",
                    status="running",
                    installed_at="2024-02-10",
                ),
                Equipment(
                    id=2,
                    tag="COMP-02",
                    equipment_type="compressor",
                    area="Utilities",
                    line="Line-B",
                    status="running",
                    installed_at="2024-03-20",
                ),
                Equipment(
                    id=3,
                    tag="CHILL-01",
                    equipment_type="chiller",
                    area="Utilities",
                    line="Line-A",
                    status="running",
                    installed_at="2023-10-02",
                ),
                Equipment(
                    id=4,
                    tag="PACK-03",
                    equipment_type="packaging_machine",
                    area="Packaging",
                    line="Line-C",
                    status="maintenance",
                    installed_at="2022-06-15",
                ),
            ]
        )
        session.flush()

        session.add_all(
            [
                Sop(
                    id=1,
                    code="SOP-COMP-001",
                    title="Compressor startup checklist",
                    area="Utilities",
                    version="v2.1",
                    content=(
                        "Verify oil level, open discharge valve, start in local mode, "
                        "monitor pressure and vibration for 10 minutes."
                    ),
                ),
                Sop(
                    id=2,
                    code="SOP-COMP-002",
                    title="Compressor shutdown procedure",
                    area="Utilities",
                    version="v1.8",
                    content=(
                        "Unload compressor, isolate power, close valves, apply "
                        "lockout-tagout, register reason in maintenance log."
                    ),
                ),
                Sop(
                    id=3,
                    code="SOP-MNT-014",
                    title="Preventive maintenance for rotary compressor",
                    area="Maintenance",
                    version="v3.0",
                    content=(
                        "Inspect belts, clean intake filter, check coupling alignment, "
                        "inspect drain trap, record findings with timestamp."
                    ),
                ),
                Sop(
                    id=4,
                    code="SOP-QA-020",
                    title="Batch release checklist",
                    area="Quality",
                    version="v1.3",
                    content=(
                        "Confirm line clearance, verify calibration status, attach "
                        "sampling report and approve by QA supervisor."
                    ),
                ),
                Sop(
                    id=5,
                    code="SOP-PACK-009",
                    title="Packaging line setup",
                    area="Packaging",
                    version="v2.0",
                    content=(
                        "Load recipe, run empty cycle, verify label alignment, release "
                        "first-piece inspection before full run."
                    ),
                ),
                Sop(
                    id=6,
                    code="SOP-SAFE-003",
                    title="Lockout-tagout standard",
                    area="Safety",
                    version="v4.2",
                    content=(
                        "Identify all energy sources, isolate and lock devices, verify "
                        "zero energy, execute service, remove locks with sign-off."
                    ),
                ),
            ]
        )

        session.add_all(
            [
                CompressorEvent(
                    id=1,
                    equipment_id=1,
                    event_ts="2026-01-10T08:10:00",
                    event_type="startup",
                    severity="info",
                    value=None,
                    unit=None,
                    description="Compressor started after morning inspection.",
                ),
                CompressorEvent(
                    id=2,
                    equipment_id=1,
                    event_ts="2026-01-10T10:20:00",
                    event_type="vibration",
                    severity="warning",
                    value=5.2,
                    unit="mm/s",
                    description="Vibration above control limit for 2 minutes.",
                ),
                CompressorEvent(
                    id=3,
                    equipment_id=1,
                    event_ts="2026-01-10T10:24:00",
                    event_type="vibration",
                    severity="info",
                    value=3.1,
                    unit="mm/s",
                    description="Vibration returned to normal range.",
                ),
                CompressorEvent(
                    id=4,
                    equipment_id=2,
                    event_ts="2026-01-10T11:05:00",
                    event_type="pressure",
                    severity="warning",
                    value=6.4,
                    unit="bar",
                    description="Discharge pressure below expected baseline.",
                ),
                CompressorEvent(
                    id=5,
                    equipment_id=2,
                    event_ts="2026-01-10T11:15:00",
                    event_type="pressure",
                    severity="info",
                    value=7.1,
                    unit="bar",
                    description="Pressure stabilized after valve adjustment.",
                ),
                CompressorEvent(
                    id=6,
                    equipment_id=1,
                    event_ts="2026-01-11T14:40:00",
                    event_type="temperature",
                    severity="critical",
                    value=98.5,
                    unit="C",
                    description="High discharge temperature alarm.",
                ),
                CompressorEvent(
                    id=7,
                    equipment_id=1,
                    event_ts="2026-01-11T14:47:00",
                    event_type="shutdown",
                    severity="critical",
                    value=None,
                    unit=None,
                    description="Automatic shutdown due to overtemperature.",
                ),
                CompressorEvent(
                    id=8,
                    equipment_id=1,
                    event_ts="2026-01-11T16:20:00",
                    event_type="startup",
                    severity="info",
                    value=None,
                    unit=None,
                    description="Restart after corrective maintenance.",
                ),
                CompressorEvent(
                    id=9,
                    equipment_id=2,
                    event_ts="2026-01-12T09:30:00",
                    event_type="vibration",
                    severity="warning",
                    value=4.9,
                    unit="mm/s",
                    description="Vibration trend increasing during peak load.",
                ),
                CompressorEvent(
                    id=10,
                    equipment_id=2,
                    event_ts="2026-01-12T09:50:00",
                    event_type="inspection",
                    severity="info",
                    value=None,
                    unit=None,
                    description="Operator confirmed no abnormal noise.",
                ),
                CompressorEvent(
                    id=11,
                    equipment_id=1,
                    event_ts="2026-01-12T15:05:00",
                    event_type="runtime",
                    severity="info",
                    value=14.0,
                    unit="h",
                    description="Continuous runtime recorded for shift.",
                ),
                CompressorEvent(
                    id=12,
                    equipment_id=2,
                    event_ts="2026-01-13T07:15:00",
                    event_type="startup",
                    severity="info",
                    value=None,
                    unit=None,
                    description="Compressor started for first shift.",
                ),
            ]
        )

        session.add_all(
            [
                MaintenanceLog(
                    id=1,
                    equipment_id=1,
                    work_order="WO-260110-01",
                    event_ts="2026-01-10T10:30:00",
                    status="closed",
                    technician="M. Silva",
                    note="Tightened motor base bolts after vibration warning.",
                ),
                MaintenanceLog(
                    id=2,
                    equipment_id=2,
                    work_order="WO-260110-04",
                    event_ts="2026-01-10T11:20:00",
                    status="closed",
                    technician="R. Lima",
                    note="Adjusted discharge control valve and rechecked pressure.",
                ),
                MaintenanceLog(
                    id=3,
                    equipment_id=1,
                    work_order="WO-260111-02",
                    event_ts="2026-01-11T15:00:00",
                    status="closed",
                    technician="M. Silva",
                    note="Replaced clogged oil separator and cleaned cooler fins.",
                ),
                MaintenanceLog(
                    id=4,
                    equipment_id=1,
                    work_order="WO-260111-03",
                    event_ts="2026-01-11T16:10:00",
                    status="closed",
                    technician="A. Souza",
                    note="Performed restart verification with thermal camera.",
                ),
                MaintenanceLog(
                    id=5,
                    equipment_id=2,
                    work_order="WO-260112-02",
                    event_ts="2026-01-12T10:00:00",
                    status="open",
                    technician="R. Lima",
                    note="Monitor vibration trend in next 3 shifts.",
                ),
                MaintenanceLog(
                    id=6,
                    equipment_id=4,
                    work_order="WO-260112-07",
                    event_ts="2026-01-12T13:30:00",
                    status="in_progress",
                    technician="C. Rocha",
                    note="Packaging machine alignment and sensor recalibration.",
                ),
            ]
        )

        session.add_all(
            [
                AlarmHistory(
                    id=1,
                    equipment_id=1,
                    alarm_code="ALM-COMP-HOT",
                    severity="critical",
                    started_at="2026-01-11T14:39:20",
                    ended_at="2026-01-11T14:48:10",
                    acknowledged_by="op.jcarvalho",
                    note="Overtemperature trip acknowledged in SCADA.",
                ),
                AlarmHistory(
                    id=2,
                    equipment_id=2,
                    alarm_code="ALM-COMP-LOWP",
                    severity="warning",
                    started_at="2026-01-10T11:03:10",
                    ended_at="2026-01-10T11:14:00",
                    acknowledged_by="op.lmota",
                    note="Low pressure during line transition.",
                ),
                AlarmHistory(
                    id=3,
                    equipment_id=2,
                    alarm_code="ALM-COMP-VIB",
                    severity="warning",
                    started_at="2026-01-12T09:28:55",
                    ended_at="2026-01-12T09:46:02",
                    acknowledged_by="op.lmota",
                    note="Transient vibration above threshold.",
                ),
                AlarmHistory(
                    id=4,
                    equipment_id=3,
                    alarm_code="ALM-CHILL-FLOW",
                    severity="warning",
                    started_at="2026-01-09T16:20:10",
                    ended_at="2026-01-09T16:42:33",
                    acknowledged_by="op.jcarvalho",
                    note="Cooling water flow oscillation.",
                ),
            ]
        )

        session.commit()

    print(f"Database seeded at: {DB_PATH}")


if __name__ == "__main__":
    main()
