import sqlite3

DB_PATH = "factory.db"


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    cur.executescript(
        """
        DROP TABLE IF EXISTS compressor_events;
        DROP TABLE IF EXISTS maintenance_log;
        DROP TABLE IF EXISTS alarm_history;
        DROP TABLE IF EXISTS sop;
        DROP TABLE IF EXISTS equipment;

        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY,
            tag TEXT NOT NULL UNIQUE,
            equipment_type TEXT NOT NULL,
            area TEXT NOT NULL,
            line TEXT NOT NULL,
            status TEXT NOT NULL,
            installed_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sop (
            id INTEGER PRIMARY KEY,
            code TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            area TEXT NOT NULL,
            version TEXT NOT NULL,
            content TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS compressor_events (
            id INTEGER PRIMARY KEY,
            equipment_id INTEGER NOT NULL,
            event_ts TEXT NOT NULL,
            event_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            value REAL,
            unit TEXT,
            description TEXT NOT NULL,
            FOREIGN KEY (equipment_id) REFERENCES equipment(id)
        );

        CREATE TABLE IF NOT EXISTS maintenance_log (
            id INTEGER PRIMARY KEY,
            equipment_id INTEGER NOT NULL,
            work_order TEXT NOT NULL,
            event_ts TEXT NOT NULL,
            status TEXT NOT NULL,
            technician TEXT NOT NULL,
            note TEXT,
            FOREIGN KEY (equipment_id) REFERENCES equipment(id)
        );

        CREATE TABLE IF NOT EXISTS alarm_history (
            id INTEGER PRIMARY KEY,
            equipment_id INTEGER NOT NULL,
            alarm_code TEXT NOT NULL,
            severity TEXT NOT NULL,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            acknowledged_by TEXT,
            note TEXT,
            FOREIGN KEY (equipment_id) REFERENCES equipment(id)
        );

        CREATE INDEX IF NOT EXISTS idx_compressor_events_equipment_ts
            ON compressor_events (equipment_id, event_ts DESC);
        CREATE INDEX IF NOT EXISTS idx_maintenance_log_equipment_ts
            ON maintenance_log (equipment_id, event_ts DESC);
        CREATE INDEX IF NOT EXISTS idx_alarm_history_equipment_start
            ON alarm_history (equipment_id, started_at DESC);
        """
    )

    cur.execute("DELETE FROM compressor_events")
    cur.execute("DELETE FROM maintenance_log")
    cur.execute("DELETE FROM alarm_history")
    cur.execute("DELETE FROM sop")
    cur.execute("DELETE FROM equipment")

    cur.executemany(
        """
        INSERT INTO equipment (
            id, tag, equipment_type, area, line, status, installed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (1, "COMP-01", "compressor", "Utilities", "Line-A", "running", "2024-02-10"),
            (2, "COMP-02", "compressor", "Utilities", "Line-B", "running", "2024-03-20"),
            (3, "CHILL-01", "chiller", "Utilities", "Line-A", "running", "2023-10-02"),
            (4, "PACK-03", "packaging_machine", "Packaging", "Line-C", "maintenance", "2022-06-15"),
        ],
    )

    cur.executemany(
        """
        INSERT INTO sop (id, code, title, area, version, content)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                1,
                "SOP-COMP-001",
                "Compressor startup checklist",
                "Utilities",
                "v2.1",
                "Verify oil level, open discharge valve, start in local mode, monitor pressure and vibration for 10 minutes.",
            ),
            (
                2,
                "SOP-COMP-002",
                "Compressor shutdown procedure",
                "Utilities",
                "v1.8",
                "Unload compressor, isolate power, close valves, apply lockout-tagout, register reason in maintenance log.",
            ),
            (
                3,
                "SOP-MNT-014",
                "Preventive maintenance for rotary compressor",
                "Maintenance",
                "v3.0",
                "Inspect belts, clean intake filter, check coupling alignment, inspect drain trap, record findings with timestamp.",
            ),
            (
                4,
                "SOP-QA-020",
                "Batch release checklist",
                "Quality",
                "v1.3",
                "Confirm line clearance, verify calibration status, attach sampling report and approve by QA supervisor.",
            ),
            (
                5,
                "SOP-PACK-009",
                "Packaging line setup",
                "Packaging",
                "v2.0",
                "Load recipe, run empty cycle, verify label alignment, release first-piece inspection before full run.",
            ),
            (
                6,
                "SOP-SAFE-003",
                "Lockout-tagout standard",
                "Safety",
                "v4.2",
                "Identify all energy sources, isolate and lock devices, verify zero energy, execute service, remove locks with sign-off.",
            ),
        ],
    )

    cur.executemany(
        """
        INSERT INTO compressor_events (
            id, equipment_id, event_ts, event_type, severity, value, unit, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (1, 1, "2026-01-10T08:10:00", "startup", "info", None, None, "Compressor started after morning inspection."),
            (2, 1, "2026-01-10T10:20:00", "vibration", "warning", 5.2, "mm/s", "Vibration above control limit for 2 minutes."),
            (3, 1, "2026-01-10T10:24:00", "vibration", "info", 3.1, "mm/s", "Vibration returned to normal range."),
            (4, 2, "2026-01-10T11:05:00", "pressure", "warning", 6.4, "bar", "Discharge pressure below expected baseline."),
            (5, 2, "2026-01-10T11:15:00", "pressure", "info", 7.1, "bar", "Pressure stabilized after valve adjustment."),
            (6, 1, "2026-01-11T14:40:00", "temperature", "critical", 98.5, "C", "High discharge temperature alarm."),
            (7, 1, "2026-01-11T14:47:00", "shutdown", "critical", None, None, "Automatic shutdown due to overtemperature."),
            (8, 1, "2026-01-11T16:20:00", "startup", "info", None, None, "Restart after corrective maintenance."),
            (9, 2, "2026-01-12T09:30:00", "vibration", "warning", 4.9, "mm/s", "Vibration trend increasing during peak load."),
            (10, 2, "2026-01-12T09:50:00", "inspection", "info", None, None, "Operator confirmed no abnormal noise."),
            (11, 1, "2026-01-12T15:05:00", "runtime", "info", 14.0, "h", "Continuous runtime recorded for shift."),
            (12, 2, "2026-01-13T07:15:00", "startup", "info", None, None, "Compressor started for first shift."),
        ],
    )

    cur.executemany(
        """
        INSERT INTO maintenance_log (
            id, equipment_id, work_order, event_ts, status, technician, note
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (1, 1, "WO-260110-01", "2026-01-10T10:30:00", "closed", "M. Silva", "Tightened motor base bolts after vibration warning."),
            (2, 2, "WO-260110-04", "2026-01-10T11:20:00", "closed", "R. Lima", "Adjusted discharge control valve and rechecked pressure."),
            (3, 1, "WO-260111-02", "2026-01-11T15:00:00", "closed", "M. Silva", "Replaced clogged oil separator and cleaned cooler fins."),
            (4, 1, "WO-260111-03", "2026-01-11T16:10:00", "closed", "A. Souza", "Performed restart verification with thermal camera."),
            (5, 2, "WO-260112-02", "2026-01-12T10:00:00", "open", "R. Lima", "Monitor vibration trend in next 3 shifts."),
            (6, 4, "WO-260112-07", "2026-01-12T13:30:00", "in_progress", "C. Rocha", "Packaging machine alignment and sensor recalibration."),
        ],
    )

    cur.executemany(
        """
        INSERT INTO alarm_history (
            id, equipment_id, alarm_code, severity, started_at, ended_at, acknowledged_by, note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (1, 1, "ALM-COMP-HOT", "critical", "2026-01-11T14:39:20", "2026-01-11T14:48:10", "op.jcarvalho", "Overtemperature trip acknowledged in SCADA."),
            (2, 2, "ALM-COMP-LOWP", "warning", "2026-01-10T11:03:10", "2026-01-10T11:14:00", "op.lmota", "Low pressure during line transition."),
            (3, 2, "ALM-COMP-VIB", "warning", "2026-01-12T09:28:55", "2026-01-12T09:46:02", "op.lmota", "Transient vibration above threshold."),
            (4, 3, "ALM-CHILL-FLOW", "warning", "2026-01-09T16:20:10", "2026-01-09T16:42:33", "op.jcarvalho", "Cooling water flow oscillation."),
        ],
    )

    con.commit()
    con.close()
    print(f"Database seeded at: {DB_PATH}")


if __name__ == "__main__":
    main()
