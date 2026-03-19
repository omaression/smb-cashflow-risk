#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

API_ROOT = Path(__file__).resolve().parents[1] / "apps" / "api"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.ml.config import RunConfig
from app.ml.pipelines.ibm import run_ibm_pipeline
from app.ml.pipelines.skywalker import run_skywalker_pipeline
from app.ml.reporting.contracts import write_comparison_report

IBM_PATH = PROJECT_ROOT.parents[1] / "uploads" / "20260319_091134_AgADHAcAArMx4EU.csv"
SKYWALKER_URL = "https://raw.githubusercontent.com/SkywalkerHub/Payment-Date-Prediction/main/Dataset.csv"


def main() -> int:
    config = RunConfig()
    ibm_dir = PROJECT_ROOT / "artifacts" / "ml" / "external" / "ibm"
    sky_dir = PROJECT_ROOT / "artifacts" / "ml" / "external" / "skywalker"
    comparison_dir = PROJECT_ROOT / "artifacts" / "ml" / "comparisons"

    ibm = run_ibm_pipeline(IBM_PATH, ibm_dir, config)
    sky = run_skywalker_pipeline(SKYWALKER_URL, sky_dir, config)
    comparison = write_comparison_report(comparison_dir, ibm, sky)

    print(f"ibm: {ibm.metrics_path}")
    print(f"skywalker: {sky.metrics_path}")
    print(f"comparison: {comparison.report_md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
