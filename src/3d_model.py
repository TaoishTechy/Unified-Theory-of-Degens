#!/usr/bin/env python3
"""
Triadic Archetype Neurochemical Atlas
=====================================

Enhanced version of the original Plotly network.

Core upgrade:
- Replaces random coordinates with theory-driven coordinates:
    X = Precision axis 𝒫
    Y = Boundary axis ℬ
    Z = Temporal axis 𝒯

- Uses neurotransmitter/hormone dysregulation as biological metadata.
- Computes severity as Euclidean distance from healthy origin.
- Computes comorbidity/overlap proximity from distance in 𝒫-ℬ-𝒯 space.
- Builds two edge layers:
    1. Neurochemical edges: disorder/archetype -> neurotransmitter/hormone
    2. Similarity edges: disorder/archetype -> disorder/archetype

Run:
    python3 triadic_archetype_atlas.py

Requires:
    pip install pandas numpy plotly
"""

import os
import math
import http.server
import socketserver
from dataclasses import dataclass

import numpy as np
import pandas as pd
import plotly.graph_objects as go


# ============================================================
# 1. CONFIG
# ============================================================

DEFAULT_CSV = "Neurotransmitter_Dysregulation_in_Archetypes.csv"
DEFAULT_OUTPUT = "index.html"

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

# 𝒫, ℬ, 𝒯 coordinates from the imported triadic theory.
# These are theory coordinates, not clinical diagnoses.
TRIADIC_COORDINATES = {
    "Bipolar Disorder": {
        "P": 2.0,
        "B": -1.0,
        "T": 3.0,
        "mode": "Mania-weighted bipolar state",
        "axis_note": "High precision/reward salience, porous boundary, expanded future horizon.",
    },
    "Borderline Personality Disorder (BPD)": {
        "P": 0.0,
        "B": -2.0,
        "T": 0.0,
        "mode": "Chaotic precision / porous boundary",
        "axis_note": "Precision oscillates rapidly; boundary becomes porous under emotional intensity.",
    },
    "High-Functioning Autism": {
        "P": 1.0,
        "B": 2.0,
        "T": 0.0,
        "mode": "Rigid social boundary / high local precision",
        "axis_note": "Local-detail precision and strong self/world boundary; sensory boundary may vary.",
    },
    "ADHD / ADD": {
        "P": -2.0,
        "B": 0.0,
        "T": 0.0,
        "mode": "Low precision / present-locked salience",
        "axis_note": "Attention precision drops; immediate salience dominates planning horizon.",
    },
    "OCD": {
        "P": 1.5,
        "B": 1.0,
        "T": 2.0,
        "mode": "Doubt precision / future threat loop",
        "axis_note": "High precision assigned to doubt, contamination, error, or future harm.",
    },
    "High-Functioning Schizophrenia": {
        "P": 2.0,
        "B": -2.0,
        "T": 0.0,
        "mode": "Aberrant precision / dissolved boundary",
        "axis_note": "Noise becomes signal; self/world boundary can become unstable.",
    },
}


# Optional archetype frequency layer from your existing README.
ARCHETYPE_FREQUENCIES = {
    "Witches": {
        "frequency_hz": 7.83,
        "band": "Alpha/Theta",
        "description": "Grounding, emotional rhythm, intuitive integration.",
    },
    "Androids": {
        "frequency_hz": 14.3,
        "band": "Low Beta",
        "description": "Focus, structure, problem-solving, executive control.",
    },
    "Mystics": {
        "frequency_hz": 33.8,
        "band": "Gamma",
        "description": "Abstraction, symbolic synthesis, high-order cognition.",
    },
}


TREATMENT_HINTS = {
    "Bipolar Disorder": [
        "Stabilize oscillation before pushing cognition harder.",
        "Protect sleep/circadian rhythm.",
        "Mood-stability vector should dampen precision spikes.",
    ],
    "Borderline Personality Disorder (BPD)": [
        "Boundary-strengthening is the primary axis target.",
        "DBT-style skills map well to ℬ stabilization.",
        "Mindfulness helps stabilize chaotic 𝒫 oscillation.",
    ],
    "High-Functioning Autism": [
        "Reduce sensory overload and improve translation across boundaries.",
        "Support structure rather than forcing social permeability.",
        "Use predictable routines as boundary-safe scaffolding.",
    ],
    "ADHD / ADD": [
        "Increase useful precision without overloading the system.",
        "Externalize time: reminders, timers, task boards.",
        "Reward shaping can extend temporal horizon.",
    ],
    "OCD": [
        "Reduce overprecision of threat/doubt loops.",
        "Exposure/response prevention maps to precision recalibration.",
        "Future-threat loops need uncertainty tolerance training.",
    ],
    "High-Functioning Schizophrenia": [
        "Reduce aberrant salience and protect boundaries.",
        "Reality-testing should be gentle, structured, and non-shaming.",
        "Stress reduction reduces boundary permeability collapse.",
    ],
}


# ============================================================
# 2. HELPERS
# ============================================================

def clean_value(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def is_dysregulated(value):
    value = clean_value(value).lower()
    return value not in ("", "normal", "nan")


def dysregulation_score(value):
    """
    Converts symbolic dysregulation text into a rough strength score.

    This is not clinical measurement.
    It is a visualization heuristic.

    Examples:
        "(+)" -> 1
        "(-)" -> 1
        "(+ during mania, - during depression)" -> 2
        "(+/- depending on symptoms)" -> 2
    """
    value = clean_value(value).lower()

    if not value or value == "normal":
        return 0.0

    score = 0.0

    if "+" in value:
        score += 1.0
    if "-" in value:
        score += 1.0
    if "mania" in value or "depression" in value:
        score += 0.5
    if "depending" in value or "some" in value or "+/-" in value:
        score += 0.5

    return max(score, 1.0)


def severity_from_coord(p, b, t):
    return math.sqrt(p * p + b * b + t * t)


def euclidean_distance(a, b):
    return math.sqrt(
        (a["P"] - b["P"]) ** 2 +
        (a["B"] - b["B"]) ** 2 +
        (a["T"] - b["T"]) ** 2
    )


def comorbidity_probability(distance, sigma=1.5):
    """
    Geometric overlap model:
        P_overlap ≈ exp(-d / sigma)

    This is a visualization heuristic.
    """
    return math.exp(-distance / sigma)


def axis_interpretation(p, b, t):
    p_note = (
        "high precision / salience" if p > 1
        else "low precision / signal loss" if p < -1
        else "balanced or oscillatory precision"
    )

    b_note = (
        "rigid boundary" if b > 1
        else "porous/dissolved boundary" if b < -1
        else "moderate boundary"
    )

    t_note = (
        "future-locked" if t > 1
        else "past-locked" if t < -1
        else "present-centered / neutral horizon"
    )

    return p_note, b_note, t_note


def make_hover_text(row, coord):
    archetype = clean_value(row["Archetype"])
    subtype = clean_value(row["Subtype"])

    p, b, t = coord["P"], coord["B"], coord["T"]
    severity = severity_from_coord(p, b, t)

    p_note, b_note, t_note = axis_interpretation(p, b, t)

    nh_lines = []
    nh_score_total = 0.0

    for col in ALL_NH_COLS:
        value = clean_value(row.get(col, ""))
        if value:
            nh_lines.append(f"{col}: {value}")
            nh_score_total += dysregulation_score(value)

    freq = ARCHETYPE_FREQUENCIES.get(archetype, {})
    freq_line = ""
    if freq:
        freq_line = (
            f"<br><br><b>Archetype Frequency Layer</b>"
            f"<br>{freq['frequency_hz']} Hz — {freq['band']}"
            f"<br>{freq['description']}"
        )

    hints = TREATMENT_HINTS.get(subtype, [])
    hint_html = ""
    if hints:
        hint_html = "<br>".join([f"• {h}" for h in hints])

    return (
        f"<b>{archetype} — {subtype}</b>"
        f"<br><br><b>Triadic Coordinates</b>"
        f"<br>𝒫 Precision: {p:+.2f} — {p_note}"
        f"<br>ℬ Boundary: {b:+.2f} — {b_note}"
        f"<br>𝒯 Temporal: {t:+.2f} — {t_note}"
        f"<br>Severity distance from origin: {severity:.2f}"
        f"<br><br><b>Mode</b><br>{coord.get('mode', '')}"
        f"<br><br><b>Axis Note</b><br>{coord.get('axis_note', '')}"
        f"<br><br><b>Neurochemical Layer</b><br>" +
        "<br>".join(nh_lines) +
        f"<br>Total dysregulation load: {nh_score_total:.2f}"
        f"{freq_line}"
        f"<br><br><b>Computational Treatment Hints</b><br>{hint_html}"
    )


# ============================================================
# 3. DATA MODEL
# ============================================================

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


# ============================================================
# 4. BUILD GRAPH
# ============================================================

def build_nodes_and_edges(df):
    df.columns = df.columns.str.strip()

    nodes = []
    edges = []
    node_lookup = {}

    # --------------------------------------------------------
    # A) Archetype / subtype nodes in 𝒫-ℬ-𝒯 space
    # --------------------------------------------------------
    for _, row in df.iterrows():
        archetype = clean_value(row["Archetype"])
        subtype = clean_value(row["Subtype"])
        node_id = f"AS::{archetype}::{subtype}"

        if subtype not in TRIADIC_COORDINATES:
            print(f"[WARN] No triadic coordinate for subtype: {subtype}")
            continue

        coord = TRIADIC_COORDINATES[subtype]

        p, b, t = coord["P"], coord["B"], coord["T"]
        severity = severity_from_coord(p, b, t)

        color = ARCHETYPE_COLORS.get(archetype, "#999999")
        size = 12 + severity * 4

        hover = make_hover_text(row, coord)

        node = Node(
            node_id=node_id,
            label=subtype,
            node_type="archetype_subtype",
            x=p,
            y=b,
            z=t,
            color=color,
            size=size,
            hover=hover,
        )

        nodes.append(node)
        node_lookup[node_id] = node

    # --------------------------------------------------------
    # B) Neurotransmitter/hormone nodes
    # Place these outside the disorder atlas as satellites.
    # --------------------------------------------------------
    nh_angle_step = 2 * math.pi / len(ALL_NH_COLS)
    nh_radius = 4.5

    for i, col in enumerate(ALL_NH_COLS):
        if col not in df.columns:
            continue

        appears = any(is_dysregulated(v) for v in df[col].values)
        if not appears:
            continue

        angle = i * nh_angle_step

        # Neurochemical nodes form a ring around the theory-space.
        x = nh_radius * math.cos(angle)
        y = nh_radius * math.sin(angle)
        z = -3.5 if col in TRANSMITTER_COLS else 3.5

        node_type = "neurotransmitter" if col in TRANSMITTER_COLS else "hormone"
        node_id = f"NH::{col}"

        node = Node(
            node_id=node_id,
            label=col,
            node_type=node_type,
            x=x,
            y=y,
            z=z,
            color=NH_COLORS.get(col, "#cccccc"),
            size=10 if node_type == "neurotransmitter" else 12,
            hover=(
                f"<b>{col}</b>"
                f"<br>Type: {node_type}"
                f"<br>Connected when subtype has non-normal dysregulation."
            ),
        )

        nodes.append(node)
        node_lookup[node_id] = node

    # --------------------------------------------------------
    # C) AS -> NH edges
    # --------------------------------------------------------
    for _, row in df.iterrows():
        archetype = clean_value(row["Archetype"])
        subtype = clean_value(row["Subtype"])
        source_id = f"AS::{archetype}::{subtype}"

        if source_id not in node_lookup:
            continue

        for col in ALL_NH_COLS:
            value = clean_value(row.get(col, ""))
            if not is_dysregulated(value):
                continue

            target_id = f"NH::{col}"
            if target_id not in node_lookup:
                continue

            strength = dysregulation_score(value)

            edges.append(Edge(
                source=source_id,
                target=target_id,
                label=f"{subtype} → {col}: {value}",
                color="rgba(160,160,160,0.35)",
                width=1.0 + strength,
                edge_type="neurochemical",
            ))

    # --------------------------------------------------------
    # D) AS -> AS similarity/comorbidity edges
    # --------------------------------------------------------
    as_nodes = [n for n in nodes if n.node_type == "archetype_subtype"]

    for i in range(len(as_nodes)):
        for j in range(i + 1, len(as_nodes)):
            n1 = as_nodes[i]
            n2 = as_nodes[j]

            c1 = {"P": n1.x, "B": n1.y, "T": n1.z}
            c2 = {"P": n2.x, "B": n2.y, "T": n2.z}

            d = euclidean_distance(c1, c2)
            overlap = comorbidity_probability(d)

            # Only draw meaningful overlaps.
            if overlap < 0.12:
                continue

            edges.append(Edge(
                source=n1.node_id,
                target=n2.node_id,
                label=(
                    f"Theory-space proximity"
                    f"<br>{n1.label} ↔ {n2.label}"
                    f"<br>Distance: {d:.2f}"
                    f"<br>Overlap score: {overlap:.2f}"
                ),
                color="rgba(255,255,255,0.35)",
                width=1.0 + overlap * 5.0,
                edge_type="triadic_similarity",
            ))

    return nodes, edges, node_lookup


# ============================================================
# 5. PLOTLY RENDERING
# ============================================================

def edge_trace(edge, node_lookup):
    s = node_lookup[edge.source]
    t = node_lookup[edge.target]

    return go.Scatter3d(
        x=[s.x, t.x, None],
        y=[s.y, t.y, None],
        z=[s.z, t.z, None],
        mode="lines",
        hoverinfo="text",
        text=[edge.label, edge.label, None],
        line=dict(
            width=edge.width,
            color=edge.color,
        ),
        showlegend=False,
    )


def node_trace(nodes, node_type, name):
    selected = [n for n in nodes if n.node_type == node_type]

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


def origin_trace():
    return go.Scatter3d(
        x=[0],
        y=[0],
        z=[0],
        mode="markers+text",
        text=["Healthy Origin"],
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
            size=8,
            color="white",
            symbol="diamond",
            line=dict(width=2, color="black"),
        ),
        name="Healthy Origin",
    )


def axis_shell_trace(radius=3.0, points=40):
    """
    Draws a faint sphere around the healthy/pathological zone.
    This makes distance-from-origin visually meaningful.
    """
    u = np.linspace(0, 2 * np.pi, points)
    v = np.linspace(0, np.pi, points)

    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v))

    return go.Surface(
        x=x,
        y=y,
        z=z,
        opacity=0.08,
        colorscale="Greys",
        showscale=False,
        hoverinfo="skip",
        name="Severity Shell",
    )


def build_figure(nodes, edges, node_lookup):
    fig = go.Figure()

    # Draw shell first.
    fig.add_trace(axis_shell_trace(radius=3.0))

    # Draw edges before nodes.
    for edge in edges:
        fig.add_trace(edge_trace(edge, node_lookup))

    # Draw node layers.
    fig.add_trace(node_trace(nodes, "archetype_subtype", "Archetype Subtypes"))
    fig.add_trace(node_trace(nodes, "neurotransmitter", "Neurotransmitters"))
    fig.add_trace(node_trace(nodes, "hormone", "Hormones"))
    fig.add_trace(origin_trace())

    fig.update_layout(
        title=(
            "Triadic Neurochemical Archetype Atlas "
            "<br><sup>𝒫 Precision × ℬ Boundary × 𝒯 Temporal Horizon</sup>"
        ),
        scene=dict(
            xaxis=dict(
                title="𝒫 Precision — signal/noise weighting",
                range=[-3.5, 5.0],
                backgroundcolor="rgb(18,18,24)",
                gridcolor="rgba(255,255,255,0.15)",
                zerolinecolor="white",
            ),
            yaxis=dict(
                title="ℬ Boundary — self/world demarcation",
                range=[-3.5, 5.0],
                backgroundcolor="rgb(18,18,24)",
                gridcolor="rgba(255,255,255,0.15)",
                zerolinecolor="white",
            ),
            zaxis=dict(
                title="𝒯 Temporal — past/present/future horizon",
                range=[-4.0, 4.0],
                backgroundcolor="rgb(18,18,24)",
                gridcolor="rgba(255,255,255,0.15)",
                zerolinecolor="white",
            ),
            bgcolor="rgb(8,8,12)",
        ),
        paper_bgcolor="rgb(8,8,12)",
        plot_bgcolor="rgb(8,8,12)",
        font=dict(color="white"),
        margin=dict(l=0, r=0, b=0, t=70),
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor="rgba(0,0,0,0.35)",
        ),
        showlegend=True,
    )

    return fig


# ============================================================
# 6. MAIN BUILD FUNCTION
# ============================================================

def build_3d_network(
    csv_path=DEFAULT_CSV,
    output_html=DEFAULT_OUTPUT,
):
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    required = ["Archetype", "Subtype"] + ALL_NH_COLS
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    nodes, edges, node_lookup = build_nodes_and_edges(df)
    fig = build_figure(nodes, edges, node_lookup)

    fig.write_html(output_html, auto_open=False)

    print(f"[INFO] Saved enhanced triadic atlas to: {output_html}")
    print(f"[INFO] Nodes: {len(nodes)}")
    print(f"[INFO] Edges: {len(edges)}")
    print("[INFO] Coordinate system:")
    print("       X = 𝒫 Precision")
    print("       Y = ℬ Boundary")
    print("       Z = 𝒯 Temporal")


# ============================================================
# 7. SERVER
# ============================================================

def run_http_server(port=8000):
    handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"[INFO] Serving HTTP on 0.0.0.0:{port}")
        print(f"[INFO] Open: http://localhost:{port}/index.html")
        httpd.serve_forever()


# ============================================================
# 8. ENTRYPOINT
# ============================================================

if __name__ == "__main__":
    csv_file = DEFAULT_CSV
    output_html = DEFAULT_OUTPUT

    try:
        build_3d_network(csv_file, output_html)
    except Exception as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(1)

    run_http_server(port=8000)
