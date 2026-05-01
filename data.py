import random
import pandas as pd
from datetime import datetime, timedelta

EMPLOYEES = [
    {"id": 1,  "name": "Alice Martin",   "department": "Engineering"},
    {"id": 2,  "name": "Bob Chen",        "department": "Engineering"},
    {"id": 3,  "name": "Carol Davis",     "department": "Design"},
    {"id": 4,  "name": "Dan Kim",         "department": "Engineering"},
    {"id": 5,  "name": "Eva Rodriguez",   "department": "Design"},
    {"id": 6,  "name": "Frank Schmidt",   "department": "Management"},
    {"id": 7,  "name": "Grace Nguyen",    "department": "Engineering"},
    {"id": 8,  "name": "Hugo Petrov",     "department": "QA"},
    {"id": 9,  "name": "Iris Tanaka",     "department": "Management"},
    {"id": 10, "name": "Jake Osei",       "department": "QA"},
]

PROJECTS = [
    {"id": 1, "name": "ERP Migration"},
    {"id": 2, "name": "Mobile App"},
    {"id": 3, "name": "Data Warehouse"},
    {"id": 4, "name": "CRM Revamp"},
    {"id": 5, "name": "Security Audit"},
]

ROLES = [
    {"id": 1, "name": "Developer"},
    {"id": 2, "name": "Designer"},
    {"id": 3, "name": "Manager"},
    {"id": 4, "name": "QA Engineer"},
]

STATES = ["draft", "published"]

_BASE_DATE = datetime(2025, 4, 1)


def generate_slots(n: int = 80, seed: int = 42) -> pd.DataFrame:
    rng = random.Random(seed)
    rows = []
    for i in range(1, n + 1):
        emp = rng.choice(EMPLOYEES)
        proj = rng.choice(PROJECTS)
        role = rng.choice(ROLES)
        state = rng.choices(STATES, weights=[30, 70])[0]

        duration_days = rng.choices([1, 2, 3, 5, 10], weights=[30, 30, 20, 15, 5])[0]
        start_offset = rng.randint(0, 55)

        start_dt = _BASE_DATE + timedelta(days=start_offset)
        end_dt = start_dt + timedelta(days=duration_days)

        rows.append({
            "id": i,
            "resource_name": emp["name"],
            "department": emp["department"],
            "role_name": role["name"],
            "project_name": proj["name"],
            "start_datetime": start_dt,
            "end_datetime": end_dt,
            "allocated_hours": float(duration_days * 8),
            "allocated_percentage": float(rng.choice([25, 50, 75, 100])),
            "state": state,
        })

    df = pd.DataFrame(rows)
    df["start_datetime"] = pd.to_datetime(df["start_datetime"])
    df["end_datetime"] = pd.to_datetime(df["end_datetime"])
    return df


def get_resources_df(slots_df: pd.DataFrame) -> pd.DataFrame:
    if slots_df.empty:
        return pd.DataFrame(columns=[
            "resource_name", "department", "total_slots",
            "total_allocated_hours", "avg_allocation_pct", "projects",
        ])

    agg = (
        slots_df.groupby("resource_name", sort=False)
        .agg(
            department=("department", "first"),
            total_slots=("id", "count"),
            total_allocated_hours=("allocated_hours", "sum"),
            avg_allocation_pct=("allocated_percentage", "mean"),
            projects=("project_name", "nunique"),
        )
        .reset_index()
        .sort_values("total_allocated_hours", ascending=False)
    )
    return agg
