# config.py
from dataclasses import dataclass
from datetime import timedelta
import os


@dataclass
class BucketConfig:
    """Dataclass to hold bucket configuration."""

    template_bucket: str
    processing_bucket: str
    documented_bucket: str
    feedback_bucket: str
    extras_bucket: str
    lock_timeout: timedelta


prod_bucket_config = BucketConfig(
    template_bucket="prod-paycodehelper-templates",
    processing_bucket="prod-paycodehelper-processing",
    documented_bucket="prod-paycodehelper-documented",
    feedback_bucket="prod-paycodehelper-feedback",
    extras_bucket="prod-paycodehelper-extras",
    lock_timeout=timedelta(minutes=30),
)

test_bucket_config = BucketConfig(
    template_bucket="paycodehelper-templates",
    processing_bucket="paycodehelper-processing",
    documented_bucket="paycodehelper-documented",
    feedback_bucket="paycodehelper-feedback",
    extras_bucket="paycodehelper-extras",
    lock_timeout=timedelta(minutes=30),
)


def get_bucket_config() -> BucketConfig:
    """Returns the bucket configuration based on the environment."""
    if os.getenv("IS_PROD", "false").lower() == "true":
        return prod_bucket_config
    else:
        return test_bucket_config
