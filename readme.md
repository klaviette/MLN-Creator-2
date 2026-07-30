# MLN Layer Creator

A desktop GUI tool for constructing **Multi-Layer Networks (MLNs)** from CSV data. It provides two workflows:

1. **Intra-layer Network Creator** — generate individual network layers from a CSV file by selecting node identifiers, a feature column, a similarity metric, and a feature type.
2. **Inter-layer Network Creator with Set Operations** — combine two or more existing `.net` layer files using AND (intersection), OR (union), or NOT (difference) set operations.

Generated layers are stored in a local workspace at `~/MLNCreator/`.

---

## Requirements

- **OS:** macOS or Windows
- **Python:** 3.x
- **Tkinter:** included with most Python distributions (standard library)
- Additional Python dependencies are checked and installed automatically on first launch.

---

## Setup & Running

```bash
git clone <repo-url>
cd MLN-Creator-2
cd tkinter
python3 main.py
```

A splash screen will appear while dependencies are verified. Once ready, the main window opens at `1040×820`.

---

## Intra-layer Creator (Tab 1)

**Step 1 — Data Source**  
Browse for a CSV file. If the file is outside the workspace, it is copied into `~/MLNCreator/datasets/<dataset>/data_files/`.

**Step 2 — Feature Extraction**  
Select from the CSV columns:
- **Primary Key** — one or more columns that identify nodes (multi-select)
- **Feature Column** — the column whose values define edges
- **Similarity Metric** — `EQUALITY`, `EUCLIDEAN`, `HAVERSINE`, `JACCARD`, or `COSINE`
- **Feature Type** — `NOMINAL`, `NUMERIC`, `GEOGRAPHIC`, `TIME`, `DATE`, `SET`, or `TEXT`

**Step 3 — Additional Options**  
Context-sensitive fields appear based on the selected feature type:
- `THRESHOLD` — similarity cutoff for connecting nodes
- `RANGE` / `MULTI_RANGE` / `NUMBER_OF_EQUI_SIZED_SEGMENTS` — for numeric data
- `LONGITUDE_FEATURE_COLUMN` / `LATITUDE_FEATURE_COLUMN` — for geographic data
- `DATE_FORMAT` / `DATE_METRIC` — for date data
- `TIME_FORMAT` — for time data

**Step 4 — Config Preview & Generate**  
Click **Create Network Layer** to generate a `.gen` config file and invoke the layer-generation engine. The generated `.net` file is saved to `~/MLNCreator/datasets/<dataset>/layers_generated/`.

---

## Inter-layer Creator (Tab 2)

**Step 1** — Add two or more `.net` files produced by the Intra-layer Creator.  
**Step 2** — Choose a set operation:
- **AND** — edges present in *all* selected layers (intersection)
- **OR** — edges present in *any* selected layer (union)
- **NOT** — edges in the first layer but not the second (requires exactly 2 files)

**Step 3** — Set an output file name and directory (defaults to `~/MLNCreator/inter_layers/`).  
**Step 4** — Preview and save the resulting network layer.

---

## Attribution

This tool is based on concepts and source code from the following dissertation:

> Irany, F. A. (2024). *Large scale data analysis with application to computational epidemiology and network science* (Doctoral dissertation). University of North Texas.

---

## Project Structure

```
tkinter/          # GUI entry point (main.py) and UI helpers (utils.py)
scripts/          # confgen.py (config file generator), import_manager.py
main/             # Layer-generation engine (HOMLN/) and example datasets
  HOMLN/          # Core MLN logic: parsing, rules, similarity metrics, layer generation
  datasets/       # Sample datasets (Chocolate, DBLP, UKAccident, USCensus)
```

