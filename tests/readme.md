# Tests

Run all tests from the repo root:

```bash
py -3.12 -m pytest tests/ -v
```

Requires `pytest` (`pip install pytest`) and the project's runtime dependencies (`python scripts/import_manager.py`).

---

## Test files

- **`test_confgen.py`** (11 tests) — `scripts/confgen.py`
  - `.gen` file is created and placed in the correct directory
  - `layers_generated/` sibling folder is created automatically
  - Required fields (layer name, feature column, similarity metric, etc.) are written correctly
  - Multiple primary keys are comma-separated
  - Optional parameters (geographic, date, time, range) are written when provided
  - `NULL` threshold is written as `NULL`

- **`test_utils.py`** (14 tests) — `tkinter/utils.py`
  - CSV headers are read correctly, including single-column and space-containing headers
  - Filename extraction works for posix, Windows, and extension-only paths
  - Similarity metric option list is non-empty and contains all expected values
  - Feature type option list is non-empty and contains all expected values

- **`test_similarity_metrics.py`** (31 tests) — `main/HOMLN/similarityMetric.py`
  - Nominal equality: edge returned only when values match exactly (case-sensitive)
  - Euclidean distance: single and multi-dimensional vectors, threshold comparisons
  - Jaccard similarity: identical, disjoint, and partially overlapping sets
  - Numeric range: inclusive `[]`, exclusive `()`, and half-open `(]` / `[)` intervals
  - Multi-range: values matched against multiple intervals
  - Date equality: DAY / MONTH / YEAR granularity for both `dd-mm-yyyy` and `mm-dd-yyyy` formats
  - Haversine: nearby points within threshold, distant points outside threshold, identical points

- **`test_set_operations.py`** (18 tests) — inter-layer set operations
  - `.net` file parsing: layer name, node list, edge set, empty line handling
  - AND: common edges kept, disjoint layers produce empty result, three-layer intersection
  - OR: union of disjoint edges, no duplicates on shared edges, three-layer union
  - NOT: shared edges removed, empty result when fully overlapping, non-commutativity

**74 tests total.**
