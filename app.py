import pandas as pd
import streamlit as st

import charts
import data

st.set_page_config(
    page_title="Odoo Planning Dashboard",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data() -> pd.DataFrame:
    return data.generate_slots(n=80, seed=42)


df_all = load_data()

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📅 Odoo Planning")
    st.caption("Resource Allocation Dashboard")
    st.divider()
    st.header("Filters")

    min_date = df_all["start_datetime"].min().date()
    max_date = df_all["end_datetime"].max().date()

    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if len(date_range) != 2:
        st.info("Select an end date to continue.")
        st.stop()
    start_filter, end_filter = date_range

    all_resources = sorted(df_all["resource_name"].unique().tolist())
    selected_resources = st.multiselect(
        "Resources", all_resources, default=all_resources
    )

    all_projects = sorted(df_all["project_name"].unique().tolist())
    selected_projects = st.multiselect(
        "Projects", all_projects, default=all_projects
    )

    all_roles = sorted(df_all["role_name"].unique().tolist())
    selected_roles = st.multiselect("Roles", all_roles, default=all_roles)

    selected_states = st.multiselect(
        "State",
        options=data.STATES,
        default=data.STATES,
        format_func=str.title,
    )

    st.divider()
    color_by = st.radio(
        "Color Gantt by",
        options=["project_name", "role_name"],
        format_func=lambda x: x.replace("_name", "").title(),
    )

    st.divider()
    if st.button("Reset Filters", use_container_width=True):
        st.rerun()

# ── Apply filters ──────────────────────────────────────────────────────────────
start_dt = pd.Timestamp(start_filter)
end_dt = pd.Timestamp(end_filter) + pd.Timedelta(days=1)

resources_f = selected_resources if selected_resources else all_resources
projects_f  = selected_projects  if selected_projects  else all_projects
roles_f     = selected_roles     if selected_roles     else all_roles
states_f    = selected_states    if selected_states    else data.STATES

mask = (
    (df_all["start_datetime"] < end_dt)
    & (df_all["end_datetime"]  > start_dt)
    & (df_all["resource_name"].isin(resources_f))
    & (df_all["project_name"].isin(projects_f))
    & (df_all["role_name"].isin(roles_f))
    & (df_all["state"].isin(states_f))
)
df_filtered = df_all[mask].copy()

# ── Header + Metrics ───────────────────────────────────────────────────────────
st.title("Odoo Planning Dashboard")
st.caption("Visualizing resource allocation from the Odoo Planning module")

col1, col2, col3, col4 = st.columns(4)

total_slots = len(df_filtered)
total_resources = df_filtered["resource_name"].nunique()
avg_pct = df_filtered["allocated_percentage"].mean() if total_slots else 0.0

if total_slots:
    span_days = (df_filtered["end_datetime"].max() - df_filtered["start_datetime"].min()).days
    span_label = f"{span_days}d"
else:
    span_label = "—"

col1.metric("Total Slots", total_slots)
col2.metric("Resources", total_resources)
col3.metric("Avg Allocation %", f"{avg_pct:.1f}%")
col4.metric("Date Span", span_label)

st.divider()

# ── Gantt chart ────────────────────────────────────────────────────────────────
st.subheader("Resource Allocation Timeline")

draft_count = (df_filtered["state"] == "draft").sum() if total_slots else 0
if draft_count:
    st.caption(f"Faded bars = draft ({draft_count} slot{'s' if draft_count != 1 else ''})")

fig_gantt = charts.build_gantt_chart(df_filtered, df_all=df_all, color_by=color_by)
st.plotly_chart(fig_gantt, use_container_width=True)

st.divider()

# ── Resource utilization ───────────────────────────────────────────────────────
st.subheader("Resource Utilization")

resources_df = data.get_resources_df(df_filtered)

tab_chart, tab_table = st.tabs(["Chart", "Table"])

with tab_chart:
    fig_util = charts.build_utilization_bar(resources_df)
    st.plotly_chart(fig_util, use_container_width=True)

with tab_table:
    if resources_df.empty:
        st.info("No data matches the current filters.")
    else:
        display_df = resources_df.rename(columns={
            "resource_name": "Employee",
            "department": "Department",
            "total_slots": "Slots",
            "total_allocated_hours": "Total Hours",
            "avg_allocation_pct": "Avg %",
            "projects": "Projects",
        })
        st.dataframe(
            display_df.style.format({
                "Total Hours": "{:.1f}",
                "Avg %": "{:.1f}%",
            }),
            use_container_width=True,
            hide_index=True,
        )
