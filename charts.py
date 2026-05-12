import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def build_gantt_chart(
    df: pd.DataFrame,
    df_all: pd.DataFrame,
    color_by: str = "project_name",
) -> go.Figure:
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No slots match the current filters.",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="#888"),
        )
        fig.update_layout(height=400, plot_bgcolor="white", paper_bgcolor="white")
        return fig

    # Stable color ordering across filter changes — derive from full dataset
    category_orders = {color_by: sorted(df_all[color_by].unique().tolist())}

    n_resources = df["resource_name"].nunique()

    fig = px.timeline(
        df,
        x_start="start_datetime",
        x_end="end_datetime",
        y="resource_name",
        color=color_by,
        hover_name="resource_name",
        hover_data={
            "project_name": True,
            "role_name": True,
            "allocated_hours": ":.1f",
            "allocated_percentage": ":.0f",
            "state": True,
            "start_datetime": "|%b %d, %Y",
            "end_datetime": "|%b %d, %Y",
        },
        color_discrete_sequence=px.colors.qualitative.Set2,
        category_orders=category_orders,
        title="Resource Allocation Timeline",
    )

    # First resource at the top
    fig.update_yaxes(autorange="reversed")

    fig.update_layout(
        height=max(400, n_resources * 55 + 120),
        xaxis_title="",
        yaxis_title="",
        legend_title=color_by.replace("_name", "").title(),
        margin=dict(l=160, r=20, t=70, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(
            showgrid=True,
            gridcolor="#EBEBEB",
            tickformat="%b %d",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        bargap=0.25,
        bargroupgap=0.1,
    )

    # Draft slots: reduced opacity per bar
    for trace in fig.data:
        group_val = trace.name
        mask = df[color_by] == group_val
        opacities = [
            0.4 if s == "draft" else 1.0
            for s in df.loc[mask, "state"].values
        ]
        trace.marker.opacity = opacities

    return fig


def build_utilization_bar(resources_df: pd.DataFrame) -> go.Figure:
    if resources_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available.",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="#888"),
        )
        fig.update_layout(height=300, plot_bgcolor="white", paper_bgcolor="white")
        return fig

    df_sorted = resources_df.sort_values("total_allocated_hours", ascending=True)

    fig = px.bar(
        df_sorted,
        x="total_allocated_hours",
        y="resource_name",
        color="department",
        orientation="h",
        text="total_allocated_hours",
        title="Total Allocated Hours by Resource",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hover_data={"avg_allocation_pct": ":.1f", "total_slots": True},
    )
    fig.update_traces(texttemplate="%{text:.0f}h", textposition="outside")
    fig.update_layout(
        height=max(300, len(df_sorted) * 40 + 100),
        showlegend=True,
        margin=dict(l=150, r=80, t=60, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_title="Hours",
        yaxis_title="",
        legend_title="Department",
    )
    return fig
