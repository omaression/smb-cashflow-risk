"""Shared ML configuration objects for external-data dual pipelines."""

from .pipeline import LeakagePolicy, RunConfig

__all__ = ["LeakagePolicy", "RunConfig"]
