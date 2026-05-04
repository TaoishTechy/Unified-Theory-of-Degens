#!/usr/bin/env python3
"""
atlas.py
========

Builds an interactive Plotly 3D atlas from:

    data/archetypes.csv
    data/triadic_coordinates.csv
    data/treatment_vectors.csv

Output:
    index.html

Run:
    python3 src/atlas.py
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from theory import (
    severity,
    distance,
    overlap_score,
    treatment_response_score,
    axis_interpretation,
    dysregulation_score,
    is_dysregulated,
)


ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data"
ARCHETYPES_CSV = DATA_DIR / "archetypes.csv"
COORDINATES_CSV = DATA_DIR / "triadic_coordinates.csv"
TREATMENTS_CSV = DATA_DIR / "treatment_vectors.csv"
OUTPUT_HTML = ROOT / "index.html"

TRANSMITTER_COLS = [
    "Dopamine",
    "Serotonin",
    "Norepinephrine",
    "Glutamate",
    "GABA",
]

HORMONE_COLS = [
    "Oxytocin",
    "Vasopressin",
]

ALL_NH_COLS = TRANSMITTER_COLS + HORMONE_COLS

ARCHETYPE_COLORS = {
    "Witches": "#ff4d4d",
    "Androids": "#38d46b",
    "Mystics": "#4d7dff",
    "Clinical": "#d9d9d9",
}

NH_COLORS = {
    "Dopamine": "#b14cff",
    "Serotonin": "#ffb347",
    "Norepinephrine": "#00bcd4",
    "Glutamate": "#ff66cc",
    "GABA": "#9acd32",
    "Oxytocin": "#ffe66d",
    "Vasopressin": "#ffd000",
}


@dataclass
class Node:
    node_id: str
    label: str
    node_type: str
    x: float
    y: float
    z: float
    color: str
    size: float
    hover: str


@dataclass
class Edge:
    source: str
    target: str
    label: str
    color: str
    width: float
    edge_type: str


def clean(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def load_data():
    for path in [ARCHETYPES_CSV, COORDINATES_CSV, TREATMENTS_CSV]:
        if not path.exists():
            raise FileNotFoundError(f"Missing file: {path}")

    archetypes = pd.read_csv(ARCHETYPES_CSV)
    coords = pd.read_csv(COORDINATES_CSV)
    treatments = pd.read_csv(TREATMENTS_CSV)

    archetypes.columns = archetypes.columns.str.strip()
    coords.columns = coords.columns.str.strip()
    treatments.columns = treatments.columns.str.strip()

    return archetypes, coords, treatments


def build_coordinate_lookup(coords: pd.DataFrame) -> Dict[str, Dict]:
    lookup = {}

    for _, row in coords.iterrows():
        subtype = clean(row["Subtype"])

        lookup[subtype] = {
            "P": float(row["P"]),
            "B": float(row["B"]),
            "T": float(row["T"]),
            "Mode": clean(row["Mode"]),
            "AxisNote": clean(row["AxisNote"]),
        }

    return lookup


def build_treatment_lookup(treatments: pd.DataFrame) -> Dict[str, Dict]:
    lookup = {}

    for _, row in treatments.iterrows():
        treatment = clean(row["Treatment"])

        lookup[treatment] = {
            "P": float(row["DeltaP"]),
            "B": float(row["DeltaB"]),
            "T": float(row["DeltaT"]),
            "Mechanism": clean(row["Mechanism"]),
            "PrimaryTargets": clean(row["PrimaryTargets"]),
        }

    return lookup


def best_treatments_for_subtype(coord: Dict, treatment_lookup: Dict, limit: int = 3):
    scored = []

    for name, vector in treatment_lookup.items():
        score = treatment_response_score(coord, vector)
        scored.append((name, score, vector))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:limit]


def make_archetype_hover(row, coord, treatment_lookup):
    archetype = clean(row["Archetype"])
    subtype = clean(row["Subtype"])

    p = coord["P"]
    b = coord["B"]
    t = coord["T"]

    sev = severity(p, b, t)
    p_note, b_note, t_note = axis_interpretation(p, b, t)

    nh_lines = []
    load = 0.0

    for col in ALL_NH_COLS:
        value = clean(row.get(col, ""))
        if value:
            nh_lines.append(f"{col}: {value}")
            load += dysregulation_score(value)

    frequency = clean(row.get("FrequencyHz", ""))
    band = clean(row.get("BrainwaveBand", ""))
    function = clean(row.get("ArchetypeFunction", ""))

    best = best_treatments_for_subtype(coord, treatment_lookup, limit=3)
    treatment_lines = [
        f"{name}: match {score:.2f}<br><i>{vector['Mechanism']}</i>"
        for name, score, vector in best
    ]

    return (
        f"<b>{archetype} — {subtype}</b>"
        f"<br><br><b>Triadic Coordinates</b>"
        f"<br>𝒫 Precision: {p:+.2f} — {p_note}"
        f"<br>ℬ Boundary: {b:+.2f} — {b_note}"
        f"<br>𝒯 Temporal: {t:+.2f} — {t_note}"
        f"<br>Severity distance: {sev:.2f}"
        f"<br><br><b>Mode</b><br>{coord['Mode']}"
        f"<br><br><b>Axis Note</b><br>{coord['AxisNote']}"
        f"<br><br><b>Neurochemical Layer</b><br>{'<br>'.join(nh_lines)}"
        f"<br>Total dysregulation load: {load:.2f}"
        f"<br><br><b>Archetype Frequency</b>"
        f"<br>{frequency} Hz — {band}"
        f"<br>{function}"
        f"<br><br><b>Best-Matching Treatment Vectors</b><br>"
        f"{'<br><br>'.join(treatment_lines)}"
    )


def build_nodes_and_edges(archetypes, coords, treatments):
    coordinate_lookup = build_coordinate_lookup(coords)
    treatment_lookup = build_treatment_lookup(treatments)

    nodes: List[Node] = []
    edges: List[Edge] = []
    node_lookup: Dict[str, Node] = {}

    # --------------------------------------------------------
    # 1. Archetype subtype nodes
    # --------------------------------------------------------
    for _, row in archetypes.iterrows():
        archetype = clean(row["Archetype"])
        subtype = clean(row["Subtype"])

        if subtype not in coordinate_lookup:
            print(f"[WARN] No coordinate found for subtype: {subtype}")
            continue

        coord = coordinate_lookup[subtype]

        p = coord["P"]
        b = coord["B"]
        t = coord["T"]

        sev = severity(p, b, t)
        color = ARCHETYPE_COLORS.get(archetype, "#999999")
        size = 12 + sev * 4

        node_id = f"AS::{archetype}::{subtype}"

        node = Node(
            node_id=node_id,
            label=subtype,
            node_type="archetype",
            x=p,
            y=b,
            z=t,
            color=color,
            size=size,
            hover=make_archetype_hover(row, coord, treatment_lookup),
        )

        nodes.append(node)
        node_lookup[node_id] = node

    # --------------------------------------------------------
    # 2. Extra coordinate-only clinical nodes
    # --------------------------------------------------------
    existing_subtypes = set(archetypes["Subtype"].astype(str).str.strip())

    for _, row in coords.iterrows():
        subtype = clean(row["Subtype"])

        if subtype in existing_subtypes:
            continue

        p = float(row["P"])
        b = float(row["B"])
        t = float(row["T"])
        sev = severity(p, b, t)

        coord = {
            "P": p,
            "B": b,
            "T": t,
            "Mode": clean(row["Mode"]),
            "AxisNote": clean(row["AxisNote"]),
        }

        p_note, b_note, t_note = axis_interpretation(p, b, t)

        best = best_treatments_for_subtype(coord, treatment_lookup, limit=3)
        treatment_lines = [
            f"{name}: match {score:.2f}<br><i>{vector['Mechanism']}</i>"
            for name, score, vector in best
        ]

        hover = (
            f"<b>Clinical Coordinate — {subtype}</b>"
            f"<br><br>𝒫 Precision: {p:+.2f} — {p_note}"
            f"<br>ℬ Boundary: {b:+.2f} — {b_note}"
            f"<br>𝒯 Temporal: {t:+.2f} — {t_note}"
            f"<br>Severity distance: {sev:.2f}"
            f"<br><br><b>Mode</b><br>{coord['Mode']}"
            f"<br><br><b>Axis Note</b><br>{coord['AxisNote']}"
            f"<br><br><b>Best-Matching Treatment Vectors</b><br>"
            f"{'<br><br>'.join(treatment_lines)}"
        )

        node_id = f"CLINICAL::{subtype}"

        node = Node(
            node_id=node_id,
            label=subtype,
            node_type="clinical",
            x=p,
            y=b,
            z=t,
            color=ARCHETYPE_COLORS["Clinical"],
            size=9 + sev * 3,
            hover=hover,
        )

        nodes.append(node)
        node_lookup[node_id] = node

    # --------------------------------------------------------
    # 3. Neurotransmitter/hormone satellite nodes
    # --------------------------------------------------------
    angle_step = 2 * math.pi / len(ALL_NH_COLS)
    radius = 4.8

    for i, col in enumerate(ALL_NH_COLS):
        if col not in archetypes.columns:
            continue

        appears = any(is_dysregulated(v) for v in archetypes[col].values)

        if not appears:
            continue

        angle = i * angle_step
        z = -3.6 if col in TRANSMITTER_COLS else 3.6

        node_id = f"NH::{col}"

        node = Node(
            node_id=node_id,
            label=col,
            node_type="neurochemical",
            x=radius * math.cos(angle),
            y=radius * math.sin(angle),
            z=z,
            color=NH_COLORS.get(col, "#cccccc"),
            size=10,
            hover=(
                f"<b>{col}</b>"
                f"<br>Layer: neurotransmitter/hormone"
                f"<br>Connected when non-normal dysregulation appears."
            ),
        )

        nodes.append(node)
        node_lookup[node_id] = node

    # --------------------------------------------------------
    # 4. Treatment vector nodes
    # --------------------------------------------------------
    for treatment, vector in treatment_lookup.items():
        node_id = f"TX::{treatment}"

        node = Node(
            node_id=node_id,
            label=treatment,
            node_type="treatment",
            x=vector["P"],
            y=vector["B"],
            z=vector["T"],
            color="#00ffff",
            size=8,
            hover=(
                f"<b>Treatment Vector — {treatment}</b>"
                f"<br>Δ𝒫: {vector['P']:+.2f}"
                f"<br>Δℬ: {vector['B']:+.2f}"
                f"<br>Δ𝒯: {vector['T']:+.2f}"
                f"<br><br><b>Mechanism</b><br>{vector['Mechanism']}"
                f"<br><br><b>Targets</b><br>{vector['PrimaryTargets']}"
            ),
        )

        nodes.append(node)
        node_lookup[node_id] = node

    # --------------------------------------------------------
    # 5. Neurochemical edges
    # --------------------------------------------------------
    for _, row in archetypes.iterrows():
        archetype = clean(row["Archetype"])
        subtype = clean(row["Subtype"])
        source_id = f"AS::{archetype}::{subtype}"

        if source_id not in node_lookup:
            continue

        for col in ALL_NH_COLS:
            value = clean(row.get(col, ""))

            if not is_dysregulated(value):
                continue

            target_id = f"NH::{col}"

            if target_id not in node_lookup:
                continue

            strength = dysregulation_score(value)

            edges.append(
                Edge(
                    source=source_id,
                    target=target_id,
                    label=f"{subtype} → {col}: {value}",
                    color="rgba(170,170,170,0.32)",
                    width=1.0 + strength,
                    edge_type="neurochemical",
                )
            )

    # --------------------------------------------------------
    # 6. Similarity edges between archetype/clinical nodes
    # --------------------------------------------------------
    theory_nodes = [
        n for n in nodes
        if n.node_type in ("archetype", "clinical")
    ]

    for i in range(len(theory_nodes)):
        for j in range(i + 1, len(theory_nodes)):
            n1 = theory_nodes[i]
            n2 = theory_nodes[j]

            c1 = {"P": n1.x, "B": n1.y, "T": n1.z}
            c2 = {"P": n2.x, "B": n2.y, "T": n2.z}

            d = distance(c1, c2)
            overlap = overlap_score(d)

            if overlap < 0.12:
                continue

            edges.append(
                Edge(
                    source=n1.node_id,
                    target=n2.node_id,
                    label=(
                        f"<b>Theory-space proximity</b>"
                        f"<br>{n1.label} ↔ {n2.label}"
                        f"<br>Distance: {d:.2f}"
                        f"<br>Overlap score: {overlap:.2f}"
                    ),
                    color="rgba(255,255,255,0.25)",
                    width=1.0 + overlap * 5,
                    edge_type="similarity",
                )
            )

    # --------------------------------------------------------
    # 7. Treatment recommendation edges
    # --------------------------------------------------------
    for node in theory_nodes:
        coord = {"P": node.x, "B": node.y, "T": node.z}
        best = best_treatments_for_subtype(coord, treatment_lookup, limit=2)

        for treatment, score, vector in best:
            target_id = f"TX::{treatment}"

            if target_id not in node_lookup:
                continue

            edges.append(
                Edge(
                    source=node.node_id,
                    target=target_id,
                    label=(
                        f"<b>Treatment vector match</b>"
                        f"<br>{node.label} → {treatment}"
                        f"<br>Match score: {score:.2f}"
                        f"<br>{vector['Mechanism']}"
                    ),
                    color="rgba(0,255,255,0.35)",
                    width=1.0 + score * 4,
                    edge_type="treatment",
                )
            )

    return nodes, edges, node_lookup


def make_edge_trace(edge: Edge, node_lookup: Dict[str, Node]):
    source = node_lookup[edge.source]
    target = node_lookup[edge.target]

    return go.Scatter3d(
        x=[source.x, target.x, None],
        y=[source.y, target.y, None],
        z=[source.z, target.z, None],
        mode="lines",
        hoverinfo="text",
        text=[edge.label, edge.label, None],
        line=dict(
            width=edge.width,
            color=edge.color,
        ),
        showlegend=False,
    )


def make_node_trace(nodes: List[Node], node_type: str, name: str):
    selected = [n for n in nodes if n.node_type == node_type]

    if not selected:
        return None

    return go.Scatter3d(
        x=[n.x for n in selected],
        y=[n.y for n in selected],
        z=[n.z for n in selected],
        mode="markers+text",
        text=[n.label for n in selected],
        hovertext=[n.hover for n in selected],
        hoverinfo="text",
        textposition="top center",
        marker=dict(
            size=[n.size for n in selected],
            color=[n.color for n in selected],
            opacity=0.92,
            line=dict(width=1, color="white"),
        ),
        name=name,
    )


def make_origin_trace():
    return go.Scatter3d(
        x=[0],
        y=[0],
        z=[0],
        mode="markers+text",
        text=["Origin"],
        hovertext=[
            "<b>Healthy Origin</b>"
            "<br>𝒫 = 0"
            "<br>ℬ = 0"
            "<br>𝒯 = 0"
            "<br>Balanced precision, boundary, and temporal integration."
        ],
        hoverinfo="text",
        textposition="bottom center",
        marker=dict(
            size=9,
            color="white",
            symbol="diamond",
            line=dict(width=2, color="black"),
        ),
        name="Healthy Origin",
    )


def make_severity_shell(radius=3.0, points=48):
    u = np.linspace(0, 2 * np.pi, points)
    v = np.linspace(0, np.pi, points)

    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v))

    return go.Surface(
        x=x,
        y=y,
        z=z,
        opacity=0.06,
        colorscale="Greys",
        showscale=False,
        hoverinfo="skip",
        name="Severity Shell",
    )


def build_figure(nodes, edges, node_lookup):
    fig = go.Figure()

    fig.add_trace(make_severity_shell(radius=3.0))

    for edge in edges:
        fig.add_trace(make_edge_trace(edge, node_lookup))

    traces = [
        make_node_trace(nodes, "archetype", "Archetypes"),
        make_node_trace(nodes, "clinical", "Clinical Coordinates"),
        make_node_trace(nodes, "neurochemical", "Neurochemistry"),
        make_node_trace(nodes, "treatment", "Treatment Vectors"),
        make_origin_trace(),
    ]

    for trace in traces:
        if trace is not None:
            fig.add_trace(trace)

    fig.update_layout(
        title=(
            "Triadic Neurochemical Archetype Atlas"
            "<br><sup>𝒫 Precision × ℬ Boundary × 𝒯 Temporal Horizon</sup>"
        ),
        scene=dict(
            xaxis=dict(
                title="𝒫 Precision",
                range=[-4.0, 5.0],
                backgroundcolor="rgb(16,16,24)",
                gridcolor="rgba(255,255,255,0.15)",
                zerolinecolor="white",
            ),
            yaxis=dict(
                title="ℬ Boundary",
                range=[-4.0, 5.0],
                backgroundcolor="rgb(16,16,24)",
                gridcolor="rgba(255,255,255,0.15)",
                zerolinecolor="white",
            ),
            zaxis=dict(
                title="𝒯 Temporal",
                range=[-4.0, 4.0],
                backgroundcolor="rgb(16,16,24)",
                gridcolor="rgba(255,255,255,0.15)",
                zerolinecolor="white",
            ),
            bgcolor="rgb(8,8,12)",
        ),
        paper_bgcolor="rgb(8,8,12)",
        plot_bgcolor="rgb(8,8,12)",
        font=dict(color="white"),
        margin=dict(l=0, r=0, b=0, t=75),
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor="rgba(0,0,0,0.35)",
        ),
        showlegend=True,
    )

    return fig


def build_atlas(output_html: Path = OUTPUT_HTML):
    archetypes, coords, treatments = load_data()
    nodes, edges, node_lookup = build_nodes_and_edges(archetypes, coords, treatments)
    fig = build_figure(nodes, edges, node_lookup)

    fig.write_html(output_html, auto_open=False)

    print(f"[INFO] Saved atlas: {output_html}")
    print(f"[INFO] Nodes: {len(nodes)}")
    print(f"[INFO] Edges: {len(edges)}")


if __name__ == "__main__":
    build_atlas()
