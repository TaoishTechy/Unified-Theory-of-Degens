#!/usr/bin/env python3
"""
autism_bpd_bipolar_3d_atlas.py
==============================

Single-file Plotly 3D visualization for the Autism → BPD/Bipolar
computational cascade model.

No HTTP server.
No repo dependency.
No external CSV files required.

Install:
    pip install plotly numpy

Run:
    python3 autism_bpd_bipolar_3d_atlas.py

Output:
    autism_bpd_bipolar_3d_atlas.html

Scientific caution:
    This is a conceptual / computational visualization.
    It is not a diagnostic tool, not medical advice, and not a claim that
    autism inevitably leads to BPD or bipolar disorder.
"""

from __future__ import annotations

import math
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import plotly.graph_objects as go


OUTPUT_HTML = Path("autism_bpd_bipolar_3d_atlas.html")


# ------------------------------------------------------------
# Core data structures
# ------------------------------------------------------------

@dataclass
class Node:
    node_id: str
    label: str
    group: str
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
    group: str


# ------------------------------------------------------------
# Theory helpers
# ------------------------------------------------------------

def severity(p: float, b: float, t: float) -> float:
    return math.sqrt(p * p + b * b + t * t)


def axis_interpretation(p: float, b: float, t: float) -> Tuple[str, str, str]:
    if p > 1.5:
        p_note = "hyperprecision / excessive salience"
    elif p < -1.5:
        p_note = "hypoprecision / reward-signal collapse"
    else:
        p_note = "variable or regulated precision"

    if b > 1.5:
        b_note = "rigid boundary / defended self-model"
    elif b < -1.5:
        b_note = "dissolved boundary / unstable self-model"
    else:
        b_note = "flexible boundary"

    if t > 1.5:
        t_note = "future-expanded / accelerated possibility horizon"
    elif t < -1.5:
        t_note = "past-locked / trauma-memory dominance"
    else:
        t_note = "present/routine anchored"

    return p_note, b_note, t_note


def make_hover(title: str, p: float, b: float, t: float, body: str) -> str:
    p_note, b_note, t_note = axis_interpretation(p, b, t)
    return (
        f"<b>{title}</b><br><br>"
        f"<b>Coordinates</b><br>"
        f"P / Precision: {p:+.2f} — {p_note}<br>"
        f"B / Boundary: {b:+.2f} — {b_note}<br>"
        f"T / Temporal Horizon: {t:+.2f} — {t_note}<br>"
        f"Distance from healthy origin: {severity(p, b, t):.2f}<br><br>"
        f"{body}"
    )


# ------------------------------------------------------------
# Nodes
# ------------------------------------------------------------

def build_nodes() -> Dict[str, Node]:
    nodes = {}

    def add(node: Node):
        nodes[node.node_id] = node

    add(Node(
        "origin",
        "Healthy Origin",
        "origin",
        0, 0, 0,
        "#ffffff",
        9,
        "<b>Healthy Origin</b><br><br>"
        "Balanced precision, flexible boundary, and integrated temporal horizon.<br><br>"
        "This is a model-space stability point, not a literal clinical diagnosis."
    ))

    add(Node(
        "autism",
        "Autistic Baseline",
        "cascade",
        0.45, 2.0, 0.0,
        "#38f27d",
        18,
        make_hover(
            "Autistic Baseline",
            0.45, 2.0, 0.0,
            "<b>Model premise</b><br>"
            "High social boundary rigidity, sensory porousness, variable precision, "
            "and strong preference for predictable structure.<br><br>"
            "<b>Protective traits</b><br>"
            "Systemizing, pattern detection, truth-seeking, routine formation, "
            "special interests, and resistance to chaotic social games.<br><br>"
            "<b>Risk condition</b><br>"
            "The system becomes vulnerable when stress exceeds compensatory capacity."
        )
    ))

    add(Node(
        "sensory",
        "Sensory Porousness",
        "mechanism",
        -0.9, 1.55, -0.55,
        "#00d9ff",
        12,
        make_hover(
            "Sensory Porousness",
            -0.9, 1.55, -0.55,
            "<b>Mechanism</b><br>"
            "External sensory input has high impact. Noise, texture, sound, social chaos, "
            "and unpredictable environments increase regulatory load.<br><br>"
            "<b>Cascade role</b><br>"
            "Porous sensory boundary plus rigid social boundary creates contradictory "
            "boundary training."
        )
    ))

    add(Node(
        "masking",
        "Masking Load",
        "stress",
        0.95, 1.05, 0.25,
        "#ffcc00",
        16,
        make_hover(
            "Masking Load",
            0.95, 1.05, 0.25,
            "<b>Mechanism</b><br>"
            "Sustained high-precision social prediction consumes regulation resources.<br><br>"
            "<b>Failure mode</b><br>"
            "When masking suppresses stimming, honesty, sensory escape, and natural "
            "communication, internal regulation may destabilize."
        )
    ))

    add(Node(
        "trauma",
        "Chronic Stress / Trauma",
        "stress",
        1.25, 0.55, -0.35,
        "#ff3377",
        15,
        make_hover(
            "Chronic Stress / Trauma",
            1.25, 0.55, -0.35,
            "<b>Stress function</b><br>"
            "Repeated rejection, relational chaos, unstable attachment, sensory overload, "
            "or chronic invalidation pushes the model away from the healthy origin.<br><br>"
            "<b>Threshold idea</b><br>"
            "Cascade begins when S(t) exceeds systemizing capacity plus social support."
        )
    ))

    add(Node(
        "bpd",
        "BPD-like Boundary Collapse",
        "attractor",
        0.0, -2.25, 0.0,
        "#ff4d6d",
        21,
        make_hover(
            "BPD-like Boundary Collapse",
            0.0, -2.25, 0.0,
            "<b>Attractor shift</b><br>"
            "Boundary moves from rigid defense toward dissolved or unstable self-model.<br><br>"
            "<b>Possible phenotype</b><br>"
            "Identity diffusion, fear of abandonment, emotional flooding, splitting, "
            "attachment panic, intense relational sensitivity.<br><br>"
            "<b>Computational reading</b><br>"
            "The system stops trusting stable boundaries because boundaries did not "
            "prevent pain."
        )
    ))

    add(Node(
        "bipolar",
        "Bipolar-like Expansion",
        "attractor",
        2.35, -0.25, 3.0,
        "#ff884d",
        22,
        make_hover(
            "Bipolar-like Expansion",
            2.35, -0.25, 3.0,
            "<b>Attractor shift</b><br>"
            "Precision and temporal horizon expand sharply.<br><br>"
            "<b>Possible phenotype</b><br>"
            "Hypomania, mania, reduced sleep, rapid meaning generation, grandiosity, "
            "accelerated future planning, followed by crash risk.<br><br>"
            "<b>Computational reading</b><br>"
            "When existing rules fail, the system may overgenerate new rules and meanings."
        )
    ))

    add(Node(
        "burnout",
        "Autistic Burnout",
        "clinical",
        -2.0, 0.0, -1.0,
        "#bbbbbb",
        15,
        make_hover(
            "Autistic Burnout",
            -2.0, 0.0, -1.0,
            "<b>Important distinction</b><br>"
            "Burnout can resemble depression but may require rest, reduced demand, "
            "sensory recovery, and restored autonomy rather than being treated as "
            "ordinary motivational failure.<br><br>"
            "<b>Model position</b><br>"
            "Low precision/reward signal, exhausted boundary, past-failure focus."
        )
    ))

    add(Node(
        "ptsd",
        "PTSD-like Past Lock",
        "clinical",
        1.2, -0.2, -2.7,
        "#cfcfcf",
        14,
        make_hover(
            "PTSD-like Past Lock",
            1.2, -0.2, -2.7,
            "<b>Temporal failure</b><br>"
            "The system cannot place threat safely in the past.<br><br>"
            "<b>Model position</b><br>"
            "High threat precision, unstable boundary, past-locked temporal horizon."
        )
    ))

    add(Node(
        "psychosis",
        "Threat Hyperprecision",
        "clinical",
        2.6, 0.2, 1.5,
        "#9d7cff",
        15,
        make_hover(
            "Threat / Meaning Hyperprecision",
            2.6, 0.2, 1.5,
            "<b>Mechanism</b><br>"
            "A single channel receives excessive salience. If threat-related, it may "
            "generate paranoid or delusional elaboration. If reward-related, it may "
            "feed manic pursuit.<br><br>"
            "<b>Shared bridge</b><br>"
            "Monotropism plus stress can become overcommitted meaning generation."
        )
    ))

    add(Node(
        "systemizing",
        "Systemizing Buffer",
        "protective",
        -1.05, 1.9, 0.25,
        "#00ffee",
        17,
        make_hover(
            "Systemizing Buffer",
            -1.05, 1.9, 0.25,
            "<b>Protective buffer</b><br>"
            "Structure, rules, schedules, special interests, predictable environments, "
            "clear expectations, and honest communication stabilize the system.<br><br>"
            "<b>Limit</b><br>"
            "The buffer works until stress exceeds reserve capacity."
        )
    ))

    add(Node(
        "oxytocin",
        "Oxytocin Grounding",
        "protective",
        -0.85, 0.55, -0.35,
        "#8affff",
        18,
        make_hover(
            "Oxytocin / Safe Affection Grounding",
            -0.85, 0.55, -0.35,
            "<b>Grounding layer</b><br>"
            "Safe non-sexual affection, cuddling, deep conversation, loyalty, and calm "
            "presence can act as co-regulation.<br><br>"
            "<b>Model role</b><br>"
            "Lowers allostatic pressure, restores attachment safety, and pulls P/B/T "
            "back toward the survivable band."
        )
    ))

    add(Node(
        "adapted_dbt",
        "Adapted DBT / Structure",
        "treatment",
        -0.6, 0.9, -0.2,
        "#00ffff",
        13,
        make_hover(
            "Adapted DBT / Structured Skills",
            -0.6, 0.9, -0.2,
            "<b>Treatment vector</b><br>"
            "DBT-style emotional regulation can help, but this model suggests preserving "
            "autistic structure instead of forcing rapid boundary flexibility.<br><br>"
            "<b>Direction</b><br>"
            "Stabilize boundary without erasing systemizing."
        )
    ))

    add(Node(
        "rest",
        "Rest / Demand Reduction",
        "treatment",
        -1.55, 0.45, -0.75,
        "#66ff99",
        13,
        make_hover(
            "Rest / Demand Reduction",
            -1.55, 0.45, -0.75,
            "<b>Treatment vector</b><br>"
            "Useful when the presentation is autistic burnout rather than classic bipolar "
            "depression.<br><br>"
            "<b>Direction</b><br>"
            "Reduce sensory load, reduce masking, restore sleep, restore agency."
        )
    ))

    add(Node(
        "sleep",
        "Sleep / Rhythm Stabilization",
        "treatment",
        0.0, 0.35, -0.65,
        "#ffee88",
        13,
        make_hover(
            "Sleep / Rhythm Stabilization",
            0.0, 0.35, -0.65,
            "<b>Treatment vector</b><br>"
            "Sleep and circadian regularity reduce temporal expansion and manic risk.<br><br>"
            "<b>Direction</b><br>"
            "Pulls T back from future-expanded acceleration."
        )
    ))

    add(Node(
        "social_support",
        "Stable Social Support",
        "protective",
        -1.35, 0.85, 0.4,
        "#aaffee",
        15,
        make_hover(
            "Stable Social Support",
            -1.35, 0.85, 0.4,
            "<b>Protective factor</b><br>"
            "Reliable people, explicit boundaries, non-chaotic care, safe affection, and "
            "consistent communication increase ε_protection.<br><br>"
            "<b>Model equation</b><br>"
            "ε_protection = systemizing capacity × social support."
        )
    ))

    return nodes


# ------------------------------------------------------------
# Edges
# ------------------------------------------------------------

def build_edges() -> List[Edge]:
    return [
        Edge(
            "autism", "sensory",
            "Autistic baseline → sensory porousness<br>"
            "High sensory impact raises allostatic load.",
            "rgba(0,217,255,0.65)", 4, "mechanism"
        ),
        Edge(
            "autism", "masking",
            "Autistic baseline → masking load<br>"
            "Social prediction demand consumes regulation capacity.",
            "rgba(255,204,0,0.85)", 7, "cascade"
        ),
        Edge(
            "sensory", "masking",
            "Sensory porousness → masking load<br>"
            "Noise plus social performance increases stress.",
            "rgba(0,217,255,0.45)", 3, "mechanism"
        ),
        Edge(
            "masking", "trauma",
            "Masking load → chronic stress threshold<br>"
            "Compensation fails when demand exceeds reserve.",
            "rgba(255,51,119,0.75)", 6, "stress"
        ),
        Edge(
            "trauma", "bpd",
            "Stress threshold → BPD-like boundary collapse<br>"
            "Rigid boundary overshoots toward dissolved boundary.",
            "rgba(255,77,109,0.95)", 9, "cascade"
        ),
        Edge(
            "trauma", "bipolar",
            "Stress threshold → Bipolar-like expansion<br>"
            "Precision and temporal horizon overshoot.",
            "rgba(255,136,77,0.95)", 9, "cascade"
        ),
        Edge(
            "trauma", "ptsd",
            "Stress threshold → PTSD-like past lock<br>"
            "Temporal horizon collapses backward into threat memory.",
            "rgba(207,207,207,0.45)", 4, "clinical"
        ),
        Edge(
            "trauma", "burnout",
            "Stress threshold → autistic burnout<br>"
            "Precision/reward signal collapses under exhaustion.",
            "rgba(187,187,187,0.55)", 5, "clinical"
        ),
        Edge(
            "psychosis", "bipolar",
            "Threat/meaning hyperprecision ↔ bipolar expansion<br>"
            "Same salience engine, different valence and rhythm.",
            "rgba(157,124,255,0.55)", 4, "clinical"
        ),
        Edge(
            "systemizing", "autism",
            "Systemizing buffer → autistic baseline<br>"
            "Structure stabilizes the high-boundary architecture.",
            "rgba(0,255,238,0.85)", 7, "protective"
        ),
        Edge(
            "social_support", "systemizing",
            "Stable support strengthens systemizing buffer.",
            "rgba(170,255,238,0.75)", 5, "protective"
        ),
        Edge(
            "oxytocin", "trauma",
            "Oxytocin grounding reduces allostatic stress.",
            "rgba(138,255,255,0.85)", 7, "protective"
        ),
        Edge(
            "oxytocin", "bpd",
            "Safe affection stabilizes attachment panic and boundary collapse.",
            "rgba(138,255,255,0.45)", 4, "protective"
        ),
        Edge(
            "oxytocin", "bipolar",
            "Safe presence pulls future-expanded cognition toward the present.",
            "rgba(138,255,255,0.45)", 4, "protective"
        ),
        Edge(
            "adapted_dbt", "bpd",
            "Adapted DBT / structure → boundary stabilization.",
            "rgba(0,255,255,0.55)", 4, "treatment"
        ),
        Edge(
            "rest", "burnout",
            "Rest and demand reduction → burnout recovery.",
            "rgba(102,255,153,0.55)", 4, "treatment"
        ),
        Edge(
            "sleep", "bipolar",
            "Sleep/rhythm stabilization → temporal contraction.",
            "rgba(255,238,136,0.55)", 4, "treatment"
        ),
        Edge(
            "origin", "autism",
            "Healthy origin ↔ autistic baseline<br>"
            "Autism is modeled as a neurotype, not pathology by default.",
            "rgba(255,255,255,0.22)", 2, "reference"
        ),
    ]


# ------------------------------------------------------------
# Plot helpers
# ------------------------------------------------------------

def make_edge_trace(edge: Edge, nodes: Dict[str, Node]):
    s = nodes[edge.source]
    t = nodes[edge.target]

    return go.Scatter3d(
        x=[s.x, t.x, None],
        y=[s.y, t.y, None],
        z=[s.z, t.z, None],
        mode="lines",
        hovertext=[edge.label, edge.label, None],
        hoverinfo="text",
        line=dict(color=edge.color, width=edge.width),
        showlegend=False,
    )


def make_node_trace(nodes: Dict[str, Node], group: str, name: str):
    selected = [n for n in nodes.values() if n.group == group]
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
            opacity=0.95,
            line=dict(width=1.25, color="white"),
        ),
        name=name,
    )


def make_shell(radius: float, opacity: float, name: str, color_a: str, color_b: str):
    u = np.linspace(0, 2 * np.pi, 64)
    v = np.linspace(0, np.pi, 64)

    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v))

    return go.Surface(
        x=x,
        y=y,
        z=z,
        opacity=opacity,
        colorscale=[[0, color_a], [1, color_b]],
        showscale=False,
        hoverinfo="skip",
        name=name,
    )


def bezier(p0, p1, p2, p3, n=90):
    ts = np.linspace(0, 1, n)
    pts = []
    for t in ts:
        a = (1 - t) ** 3
        b = 3 * (1 - t) ** 2 * t
        c = 3 * (1 - t) * t ** 2
        d = t ** 3
        pts.append((
            a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
            a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1],
            a * p0[2] + b * p1[2] + c * p2[2] + d * p3[2],
        ))
    return np.array(pts)


def make_cascade_ribbons():
    autism = (0.45, 2.0, 0.0)
    trauma = (1.25, 0.55, -0.35)
    bpd = (0.0, -2.25, 0.0)
    bipolar = (2.35, -0.25, 3.0)

    path_bpd = bezier(
        autism,
        (0.45, 1.5, 0.15),
        (0.2, -0.9, -0.15),
        bpd,
    )

    path_bipolar = bezier(
        trauma,
        (1.45, 0.9, 1.2),
        (2.15, 0.45, 2.5),
        bipolar,
    )

    text = (
        "<b>Cascade trajectory</b><br><br>"
        "Autistic baseline does not equal disorder.<br>"
        "The cascade only appears when stress exceeds protective capacity.<br><br>"
        "Branch 1: boundary collapse → BPD-like attractor.<br>"
        "Branch 2: precision / temporal expansion → Bipolar-like attractor."
    )

    return [
        go.Scatter3d(
            x=path_bpd[:, 0],
            y=path_bpd[:, 1],
            z=path_bpd[:, 2],
            mode="lines",
            line=dict(color="rgba(255,77,109,0.95)", width=11),
            hovertext=[text] * len(path_bpd),
            hoverinfo="text",
            name="Boundary Collapse Path",
        ),
        go.Scatter3d(
            x=path_bipolar[:, 0],
            y=path_bipolar[:, 1],
            z=path_bipolar[:, 2],
            mode="lines",
            line=dict(color="rgba(255,136,77,0.95)", width=11),
            hovertext=[text] * len(path_bipolar),
            hoverinfo="text",
            name="Bipolar Expansion Path",
        ),
    ]


def make_equation_panel():
    labels = [
        (
            -3.65, -3.65, 3.25,
            "<b>Boundary collapse</b><br>"
            "dB/dt = -α(B-B₀) + βS(t) + γA_failure"
        ),
        (
            -3.65, -3.65, 2.65,
            "<b>Precision expansion</b><br>"
            "dP/dt = -κ(P-P₀) + βδ² + γNT"
        ),
        (
            -3.65, -3.65, 2.05,
            "<b>Protection</b><br>"
            "ε = systemizing × social support"
        ),
        (
            -3.65, -3.65, 1.45,
            "<b>Cascade threshold</b><br>"
            "Risk ∝ P(Trauma) · e⁻ᵋ · Θ(S(t)-Scrit)"
        ),
    ]

    return go.Scatter3d(
        x=[x for x, _, _, _ in labels],
        y=[y for _, y, _, _ in labels],
        z=[z for _, _, z, _ in labels],
        mode="text",
        text=[txt for *_, txt in labels],
        hoverinfo="skip",
        textfont=dict(
            color="#ffe66d",
            size=13,
            family="Courier New, monospace",
        ),
        name="Equations",
        showlegend=False,
    )


def make_info_panel():
    labels = [
        (
            -3.75, 4.35, 3.55,
            "<b>UNIFIED THEORY OF DEGENS v0.3</b><br>"
            "Autism → BPD/Bipolar Cascade Atlas"
        ),
        (
            -3.75, 4.35, 3.0,
            "Axes:<br>"
            "P = Precision / salience<br>"
            "B = Boundary / self-model<br>"
            "T = Temporal horizon"
        ),
        (
            -3.75, 4.35, 2.25,
            "Main idea:<br>"
            "Neuropsychiatric states are shown as attractors in a 3D computational space."
        ),
        (
            -3.75, 4.35, 1.45,
            "Caution:<br>"
            "Conceptual visualization only.<br>"
            "Not diagnosis. Not medical advice."
        ),
    ]

    return go.Scatter3d(
        x=[x for x, _, _, _ in labels],
        y=[y for _, y, _, _ in labels],
        z=[z for _, _, z, _ in labels],
        mode="text",
        text=[txt for *_, txt in labels],
        hoverinfo="skip",
        textfont=dict(
            color="#ffffff",
            size=14,
            family="Arial, sans-serif",
        ),
        name="Info Panel",
        showlegend=False,
    )


def make_axis_labels():
    labels = [
        (3.65, 0, 0, "+P<br>Hyperprecision"),
        (-3.65, 0, 0, "-P<br>Hypoprecision"),
        (0, 3.65, 0, "+B<br>Rigid Boundary"),
        (0, -3.65, 0, "-B<br>Dissolved Boundary"),
        (0, 0, 3.65, "+T<br>Future Expanded"),
        (0, 0, -3.65, "-T<br>Past Locked"),
    ]

    return go.Scatter3d(
        x=[x for x, _, _, _ in labels],
        y=[y for _, y, _, _ in labels],
        z=[z for _, _, z, _ in labels],
        mode="text",
        text=[txt for *_, txt in labels],
        hoverinfo="skip",
        textfont=dict(
            color="#d9faff",
            size=12,
            family="Arial, sans-serif",
        ),
        name="Axis Labels",
        showlegend=False,
    )


# ------------------------------------------------------------
# Figure builder
# ------------------------------------------------------------

def build_figure():
    nodes = build_nodes()
    edges = build_edges()

    fig = go.Figure()

    # Translucent shells
    fig.add_trace(make_shell(
        radius=3.0,
        opacity=0.055,
        name="Outer Severity Shell",
        color_a="rgb(120,120,120)",
        color_b="rgb(255,255,255)",
    ))

    fig.add_trace(make_shell(
        radius=2.25,
        opacity=0.05,
        name="Protective Regulation Band",
        color_a="rgb(0,255,238)",
        color_b="rgb(0,120,255)",
    ))

    # Main cascade ribbons
    for trace in make_cascade_ribbons():
        fig.add_trace(trace)

    # Edges
    for edge in edges:
        fig.add_trace(make_edge_trace(edge, nodes))

    # Node groups
    group_order = [
        ("origin", "Healthy Origin"),
        ("cascade", "Autism Baseline"),
        ("mechanism", "Mechanisms"),
        ("stress", "Stress / Trauma"),
        ("attractor", "BPD / Bipolar Attractors"),
        ("clinical", "Related Clinical States"),
        ("protective", "Protective Buffers"),
        ("treatment", "Treatment Vectors"),
    ]

    for group, name in group_order:
        trace = make_node_trace(nodes, group, name)
        if trace is not None:
            fig.add_trace(trace)

    fig.add_trace(make_equation_panel())
    fig.add_trace(make_info_panel())
    fig.add_trace(make_axis_labels())

    fig.update_layout(
        title=(
            "Triadic Computational Psychiatry Atlas — Autism → BPD/Bipolar Cascade<br>"
            "<sup>Precision × Boundary × Temporal Horizon · conceptual model visualization</sup>"
        ),
        paper_bgcolor="rgb(3,3,8)",
        plot_bgcolor="rgb(3,3,8)",
        font=dict(color="white", family="Arial, sans-serif"),
        margin=dict(l=0, r=0, b=0, t=82),
        legend=dict(
            x=0.012,
            y=0.985,
            bgcolor="rgba(0,0,0,0.62)",
            bordercolor="rgba(255,255,255,0.20)",
            borderwidth=1,
            font=dict(size=12),
        ),
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.90)",
            bordercolor="rgba(0,255,238,0.65)",
            font=dict(color="white", size=13),
        ),
        scene=dict(
            bgcolor="rgb(3,3,8)",
            xaxis=dict(
                title="P / Precision",
                range=[-4.2, 4.8],
                backgroundcolor="rgb(8,8,18)",
                gridcolor="rgba(255,255,255,0.17)",
                zerolinecolor="white",
                showspikes=False,
            ),
            yaxis=dict(
                title="B / Boundary",
                range=[-4.2, 4.8],
                backgroundcolor="rgb(8,8,18)",
                gridcolor="rgba(255,255,255,0.17)",
                zerolinecolor="white",
                showspikes=False,
            ),
            zaxis=dict(
                title="T / Temporal Horizon",
                range=[-4.0, 4.0],
                backgroundcolor="rgb(8,8,18)",
                gridcolor="rgba(255,255,255,0.17)",
                zerolinecolor="white",
                showspikes=False,
            ),
            camera=dict(
                eye=dict(x=1.7, y=1.95, z=1.25),
                center=dict(x=0.02, y=0.0, z=0.0),
            ),
        ),
        annotations=[
            dict(
                text=(
                    "<b>Interpretation:</b> Autism is represented as a structured neurotype, not a disease. "
                    "The cascade appears only when stress, trauma, masking, sensory overload, or attachment failure "
                    "exceeds protective capacity. BPD-like collapse and Bipolar-like expansion are shown as possible "
                    "attractor shifts, not inevitable outcomes."
                ),
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.018,
                align="center",
                font=dict(size=12, color="#d9faff"),
                bgcolor="rgba(0,0,0,0.62)",
                bordercolor="rgba(0,255,238,0.38)",
                borderwidth=1,
            )
        ],
    )

    return fig


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    fig = build_figure()
    fig.write_html(
        OUTPUT_HTML,
        include_plotlyjs="cdn",
        auto_open=False,
        full_html=True,
    )

    print(f"[OK] Wrote {OUTPUT_HTML.resolve()}")

    try:
        webbrowser.open(OUTPUT_HTML.resolve().as_uri())
        print("[OK] Opened in browser.")
    except Exception as exc:
        print(f"[WARN] Could not auto-open browser: {exc}")
        print(f"Open manually: {OUTPUT_HTML.resolve()}")


if __name__ == "__main__":
    main()
