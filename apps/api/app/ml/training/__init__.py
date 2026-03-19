"""Training scaffold for dual-dataset experiments."""

from .runner import ModelRunManifest, train_dataset_pipeline

__all__ = ["ModelRunManifest", "train_dataset_pipeline"]
