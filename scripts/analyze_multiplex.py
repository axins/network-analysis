"""
analyze_multiplex.py — Standalone entry point for multiplex network analysis.
Orchestrates the full pipeline: preprocessing → metrics → reports.

USAGE:
  # Full pipeline from raw data (all steps):
  python analyze_multiplex.py --full

  # Quick report from existing processed data:
  python analyze_multiplex.py --report

  # Compute only core multiplex metrics:
  python analyze_multiplex.py --core

  # Compute embedding + participation coefficient:
  python analyze_multiplex.py --embedding

REQUIRED: Run from the project root directory where the .xlsx files are located,
or set PROJECT_ROOT environment variable.
"""

import os
import sys
import subprocess
from pathlib import Path

# === Configuration ===
PROJECT_ROOT = os.environ.get(
    'PROJECT_ROOT',
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

SRC_DIR = os.path.join(PROJECT_ROOT, 'multi_network_analysis', 'src')
DATA_DIR = os.path.join(PROJECT_ROOT, 'multi_network_analysis', 'data', 'processed')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'multi_network_analysis', 'output')

# Ensure script directory exists
if not os.path.isdir(SRC_DIR):
    print(f"ERROR: Source directory not found: {SRC_DIR}")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print("Set PROJECT_ROOT environment variable to the correct path.")
    sys.exit(1)

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, 'tables'), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, 'figures'), exist_ok=True)


def run_script(script_name, description=""):
    """Run a Python script from the src directory."""
    script_path = os.path.join(SRC_DIR, script_name)
    if not os.path.isfile(script_path):
        print(f"  [SKIP] {script_name} not found — {description}")
        return False

    print(f"\n{'='*60}")
    print(f"  Running: {script_name}")
    if description:
        print(f"  {description}")
    print(f"{'='*60}")

    result = subprocess.run(
        [sys.executable, script_path],
        cwd=os.path.join(PROJECT_ROOT, 'multi_network_analysis'),
        capture_output=False
    )

    if result.returncode != 0:
        print(f"  [ERROR] {script_name} failed with code {result.returncode}")
        return False

    print(f"  [OK] {script_name} completed")
    return True


def step_preprocessing():
    """Stage 1: Name normalization + ID encoding"""
    return run_script('01_fuzzy_matching.py', 'Entity name normalization and ID encoding')


def step_single_layer_metrics():
    """Stage 2a: Single-layer network metrics"""
    return run_script('02_network_metrics.py', 'Per-network metrics (density, clustering, GCC, etc.)')


def step_core_multiplex():
    """Stage 2b: Core multiplex analysis"""
    return run_script('05_multiplex_analysis.py', 'Node/edge overlap, degree correlation, aggregated stats')


def step_embedding():
    """Stage 2c: Enterprise embedding analysis"""
    return run_script('07b_embedding_metrics.py', 'Layer participation, embedding scores')


def step_visualization():
    """Stage 3a: Single-layer visualization (optional, slow)"""
    return run_script('03_network_viz.py', 'Annual network layout figures (Top-300 nodes)')


def step_merged_viz():
    """Stage 3b: Merged network visualization"""
    return run_script('09_merged_unified_network.py', '4-color merged network visualization')


def step_report():
    """Stage 3c: Comprehensive academic report"""
    return run_script(
        '11_multiplex_comprehensive_report.py',
        'Academic report with publication-formatted tables (HTML + MD)'
    )


def print_usage():
    print(__doc__)


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    mode = sys.argv[1]

    if mode == '--full':
        print("Starting FULL multiplex network analysis pipeline...")
        print(f"Project root: {PROJECT_ROOT}")
        print(f"Source dir:   {SRC_DIR}")

        steps = [
            ("Preprocessing", step_preprocessing),
            ("Single-layer metrics", step_single_layer_metrics),
            ("Core multiplex analysis", step_core_multiplex),
            ("Enterprise embedding", step_embedding),
            ("Visualization", step_visualization),      # optional: slow
            ("Merged network visualization", step_merged_viz),
            ("Academic report generation", step_report),
        ]

        for name, step_fn in steps:
            print(f"\n>>> Stage: {name}")
            success = step_fn()
            if not success:
                print(f"\n[WARNING] Stage '{name}' failed or skipped. Continuing...")

        print(f"\n{'='*60}")
        print("  FULL PIPELINE COMPLETE")
        print(f"{'='*60}")
        print(f"  Report: {os.path.join(OUTPUT_DIR, 'multiplex_comprehensive_report.html')}")
        print(f"  Data:   {os.path.join(OUTPUT_DIR, 'tables')}/")

    elif mode == '--core':
        print("Running core multiplex analysis...")
        step_preprocessing()
        step_single_layer_metrics()
        step_core_multiplex()

    elif mode == '--embedding':
        print("Running embedding analysis...")
        step_embedding()

    elif mode == '--report':
        print("Generating comprehensive academic report...")
        step_report()

    elif mode == '--status':
        print("Checking pipeline status...")
        print(f"\nProject root: {PROJECT_ROOT}")

        checks = [
            ("Preprocessing", os.path.join(DATA_DIR, 'cpall_encoded.csv')),
            ("Single-layer metrics", os.path.join(OUTPUT_DIR, 'tables', 'metrics_all.csv')),
            ("Node overlap", os.path.join(OUTPUT_DIR, 'tables', 'multiplex_node_overlap.csv')),
            ("Edge overlap", os.path.join(OUTPUT_DIR, 'tables', 'multiplex_edge_overlap_ts.csv')),
            ("Degree correlation", os.path.join(OUTPUT_DIR, 'tables', 'multiplex_degree_correlation.csv')),
            ("Aggregated stats", os.path.join(OUTPUT_DIR, 'tables', 'multiplex_aggregated.csv')),
            ("Embedding analysis", os.path.join(OUTPUT_DIR, 'tables', 'enterprise_layer_distribution.csv')),
            ("Academic report (HTML)", os.path.join(OUTPUT_DIR, 'multiplex_comprehensive_report.html')),
            ("Academic report (MD)", os.path.join(OUTPUT_DIR, 'multiplex_comprehensive_report.md')),
        ]

        all_ok = True
        for name, path in checks:
            exists = os.path.isfile(path)
            status = "✓ DONE" if exists else "✗ MISSING"
            if not exists:
                all_ok = False
            print(f"  [{status}] {name}")

        if all_ok:
            print("\n  All pipeline stages complete.")
        else:
            print("\n  Some stages are incomplete. Run with --full to execute complete pipeline.")

    else:
        print(f"Unknown mode: {mode}")
        print_usage()


if __name__ == '__main__':
    main()
