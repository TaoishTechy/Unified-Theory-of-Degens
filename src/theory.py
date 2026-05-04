#!/usr/bin/env python3
"""
theory.py
=========

Mathematical helper layer for the Triadic Archetype Atlas.

Axes:
    P = Precision
    B = Boundary
    T = Temporal horizon

Healthy origin:
    x0 = (0, 0, 0)

Severity:
    ||x|| = sqrt(P^2 + B^2 + T^2)

Similarity / comorbidity heuristic:
    overlap = exp(-distance / sigma)

Treatment response heuristic:
    response = exp(-||needed_vector - treatment_vector||^2 / (2*sigma^2))
"""

from __future__ import annotations

import math
from typing import Dict, Tuple


Coord = Dict[str, float]


def severity(p: float, b: float, t: float) -> float:
    """Distance from balanced origin."""
    return math.sqrt(p * p + b * b + t * t)


def distance(a: Coord, b: Coord) -> float:
    """Euclidean distance between two triadic coordinates."""
    return math.sqrt(
        (a["P"] - b["P"]) ** 2 +
        (a["B"] - b["B"]) ** 2 +
        (a["T"] - b["T"]) ** 2
    )


def overlap_score(distance_value: float, sigma: float = 1.5) -> float:
    """
    Geometric overlap/comorbidity heuristic.

    Higher when two conditions are close in theory-space.
    """
    return math.exp(-distance_value / sigma)


def needed_treatment_vector(coord: Coord) -> Coord:
    """
    The simplest treatment target is the negative of the disorder coordinate:
        needed = origin - coordinate
    """
    return {
        "P": -coord["P"],
        "B": -coord["B"],
        "T": -coord["T"],
    }


def vector_distance(a: Coord, b: Coord) -> float:
    """Distance between two vectors."""
    return math.sqrt(
        (a["P"] - b["P"]) ** 2 +
        (a["B"] - b["B"]) ** 2 +
        (a["T"] - b["T"]) ** 2
    )


def treatment_response_score(
    disorder_coord: Coord,
    treatment_vector: Coord,
    sigma: float = 2.0,
) -> float:
    """
    Scores how well a treatment vector matches what the coordinate needs.

    response ≈ exp(-||needed - treatment||^2 / 2σ²)
    """
    needed = needed_treatment_vector(disorder_coord)
    d = vector_distance(needed, treatment_vector)
    return math.exp(-(d * d) / (2 * sigma * sigma))


def axis_interpretation(p: float, b: float, t: float) -> Tuple[str, str, str]:
    """Human-readable interpretation of the three axes."""

    if p > 1.25:
        p_note = "high precision / high salience"
    elif p < -1.25:
        p_note = "low precision / signal loss"
    else:
        p_note = "balanced or oscillatory precision"

    if b > 1.25:
        b_note = "rigid boundary"
    elif b < -1.25:
        b_note = "porous or dissolved boundary"
    else:
        b_note = "moderate boundary"

    if t > 1.25:
        t_note = "future-locked or future-expanded"
    elif t < -1.25:
        t_note = "past-locked"
    else:
        t_note = "present-centered / neutral horizon"

    return p_note, b_note, t_note


def dysregulation_score(value: str) -> float:
    """
    Converts symbolic neurochemical notation into rough visual weight.

    Not a medical score. Visualization only.
    """
    if value is None:
        return 0.0

    value = str(value).strip().lower()

    if value in ("", "normal", "nan"):
        return 0.0

    score = 0.0

    if "+" in value:
        score += 1.0

    if "-" in value:
        score += 1.0

    if "mania" in value:
        score += 0.5

    if "depression" in value:
        score += 0.5

    if "depending" in value or "some" in value or "+/-" in value:
        score += 0.5

    return max(score, 1.0)


def is_dysregulated(value: str) -> bool:
    if value is None:
        return False

    value = str(value).strip().lower()
    return value not in ("", "normal", "nan")
