"""Entrypoints for each independent dataset pipeline."""

from .ibm import run_ibm_pipeline
from .skywalker import run_skywalker_pipeline

__all__ = ["run_ibm_pipeline", "run_skywalker_pipeline"]
