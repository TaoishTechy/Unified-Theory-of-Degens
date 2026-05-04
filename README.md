# Triadic Neurochemical Archetype Atlas

An interactive 3D Plotly model mapping archetypes, neurochemical dysregulation, and computational psychiatry into a unified coordinate system.

The atlas uses three axes:

```text
𝒫 = Precision
ℬ = Boundary
𝒯 = Temporal Horizon
````

The healthy origin is:

```text
(𝒫, ℬ, 𝒯) = (0, 0, 0)
```

Each subtype is placed in this space as a theory-coordinate. Distance from the origin represents severity or deviation from balanced regulation.

---

## Core Idea

The system models mental and archetypal patterns as positions in a computational space:

| Axis         | Meaning                               | Too High                | Too Low                   |
| ------------ | ------------------------------------- | ----------------------- | ------------------------- |
| 𝒫 Precision | How strongly the mind weights signals | Noise becomes signal    | Signal becomes noise      |
| ℬ Boundary   | Self/world demarcation                | Rigid separation        | Porous/dissolved boundary |
| 𝒯 Temporal  | Past/present/future orientation       | Future lock / expansion | Past lock                 |

---

## Archetypes

### Witches

Associated with emotional rhythm, phase-shifting, attachment intensity, and affective volatility.

Examples:

* Bipolar Disorder
* Borderline Personality Disorder

### Androids

Associated with structure, systemization, executive regulation, sensory precision, and attention mechanics.

Examples:

* High-Functioning Autism
* ADHD / ADD
* OCD

### Mystics

Associated with symbolic abstraction, salience expansion, reality-model instability, and gamma-like integrative cognition.

Examples:

* High-Functioning Schizophrenia

---

## Data Files

```text
data/
  archetypes.csv
  triadic_coordinates.csv
  treatment_vectors.csv
```

### `archetypes.csv`

Stores archetype metadata and neurochemical dysregulation patterns.

### `triadic_coordinates.csv`

Stores the 𝒫-ℬ-𝒯 coordinates for each subtype or condition.

### `treatment_vectors.csv`

Stores intervention vectors that push coordinates toward balance.

---

## Source Files

```text
src/
  atlas.py
  theory.py
  server.py
```

### `src/theory.py`

Contains the mathematical helper functions:

```text
severity = sqrt(P² + B² + T²)
distance = Euclidean distance between disorders
overlap = exp(-distance / sigma)
treatment response = exp(-||needed - treatment||² / 2σ²)
```

### `src/atlas.py`

Builds the interactive 3D Plotly visualization.

### `src/server.py`

Builds the atlas and serves it locally.

---

## Install

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

---

## Run

```bash
python3 src/server.py
```

Then open:

```text
http://localhost:8000/index.html
```

---

## Visualization Layers

The atlas contains four node classes:

| Node Type            | Meaning                                                                     |
| -------------------- | --------------------------------------------------------------------------- |
| Archetypes           | Witches, Androids, Mystics                                                  |
| Clinical Coordinates | Extra disorders from the coordinate atlas                                   |
| Neurochemistry       | Dopamine, serotonin, norepinephrine, glutamate, GABA, oxytocin, vasopressin |
| Treatment Vectors    | Interventions represented as coordinate-shifting forces                     |

---

## Edge Types

| Edge               | Meaning                                                          |
| ------------------ | ---------------------------------------------------------------- |
| Neurochemical edge | A subtype has non-normal neurotransmitter/hormone dysregulation  |
| Similarity edge    | Two conditions are close in 𝒫-ℬ-𝒯 space                        |
| Treatment edge     | A treatment vector is theoretically well-matched to a coordinate |

---

## Mathematical Notes

### Severity

```text
severity = sqrt(P² + B² + T²)
```

The farther a point is from the origin, the more dysregulated that coordinate is in the model.

### Similarity

```text
overlap = exp(-distance / sigma)
```

Conditions closer together in theory-space are expected to share symptoms, misdiagnosis risk, or comorbidity patterns.

### Treatment Matching

```text
needed_vector = -coordinate
```

A treatment is scored by how closely its vector points back toward the origin.

---

## Disclaimer

This project is an educational and theoretical visualization tool.

It is not a diagnostic instrument, not medical advice, and not a replacement for professional psychiatric or psychological care.

The coordinates, treatment vectors, and neurochemical relationships are conceptual modeling assumptions intended for visualization and hypothesis-building.

---

## License

MIT License.

````

---

# 10. Run full test

```bash
python3 src/atlas.py
````

Expected:

```text
[INFO] Saved atlas: /path/to/project/index.html
[INFO] Nodes: ...
[INFO] Edges: ...
```

Then:

```bash
python3 src/server.py
```

Open:

```text
http://localhost:8000/index.html
```
