"""
import_manager.py — MLN Creator dependency manager.

Checks every required third-party package and installs any that are missing.
Also downloads the NLTK corpora / tokenizer data needed by similarityMetric.py.

Usage
-----
Stand-alone:   python scripts/import_manager.py
From code:     from import_manager import ensure_dependencies
               failed = ensure_dependencies(log=print)   # returns [] when all OK
"""
import sys
import subprocess
import importlib

# ── Required packages ─────────────────────────────────────────────────────────
# (human-readable label,  import name,  pip install name)
PACKAGES = [
    ("NumPy",        "numpy",     "numpy"),
    ("Pandas",       "pandas",    "pandas"),
    ("NLTK",         "nltk",      "nltk"),
    ("scikit-learn", "sklearn",   "scikit-learn"),
    ("Haversine",    "haversine", "haversine"),
    ("Colorama",     "colorama",  "colorama"),
    ("Tabulate",     "tabulate",  "tabulate"),
    ("NetworkX",     "networkx",  "networkx"),
    ("Pillow",       "PIL",       "Pillow"),
]

# NLTK data items needed by similarityMetric.py
# (nltk.data.find path,        download name)
NLTK_DATA = [
    ("tokenizers/punkt_tab", "punkt_tab"),
    ("tokenizers/punkt",     "punkt"),
    ("corpora/stopwords",    "stopwords"),
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _installed(import_name: str) -> bool:
    """Return True if the package can be imported."""
    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False


def _pip_install(pip_name: str) -> tuple:
    """Run pip install <pip_name>. Returns (success: bool, stderr: str)."""
    result = subprocess.run(
        [
            sys.executable, "-m", "pip", "install", pip_name,
            "--quiet", "--disable-pip-version-check",
        ],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, result.stderr.strip()


def _ensure_nltk_data(log=print) -> None:
    """Download any missing NLTK corpora / tokenizer data."""
    try:
        import nltk
    except ImportError:
        return  # nltk itself might have just been installed; caller re-imports

    for find_path, download_name in NLTK_DATA:
        try:
            nltk.data.find(find_path)
        except LookupError:
            log(f"Downloading NLTK data: {download_name}…")
            nltk.download(download_name, quiet=True)


# ── Public API ────────────────────────────────────────────────────────────────

def ensure_dependencies(log=print) -> list:
    """
    Check every package in PACKAGES and install any that are missing.

    Parameters
    ----------
    log : callable
        Receives human-readable status strings.  Defaults to print.

    Returns
    -------
    list of str
        pip names of packages that could *not* be installed (empty = all OK).
    """
    missing = [(d, i, p) for d, i, p in PACKAGES if not _installed(i)]

    if not missing:
        log("All dependencies are already satisfied.")
        _ensure_nltk_data(log)
        return []

    log(f"Installing {len(missing)} missing package(s)…")
    failed = []

    for display, _import_name, pip_name in missing:
        log(f"Installing {display}…")
        ok, err = _pip_install(pip_name)
        if ok:
            log(f"✓  {display} installed.")
        else:
            log(f"✗  Failed to install {display}" + (f": {err}" if err else "."))
            failed.append(pip_name)

    _ensure_nltk_data(log)
    return failed


# ── CLI entry-point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    SEP = "=" * 52
    print(SEP)
    print("  MLN Creator — Dependency Manager")
    print(SEP)
    failed = ensure_dependencies()
    print(SEP)
    if failed:
        print(f"WARNING: could not install: {', '.join(failed)}")
        print("Try manually:")
        print(f"  pip install {' '.join(failed)}")
        sys.exit(1)
    else:
        print("All dependencies satisfied. Ready to run.")
    print(SEP)
