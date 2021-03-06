import sys
from functools import partial as p

import pytest

from tests.helpers.agent import Agent
from tests.helpers.assertions import has_any_metric_or_dim, has_log_message
from tests.helpers.util import ensure_never, get_monitor_dims_from_selfdescribe, wait_for

pytestmark = [pytest.mark.windows, pytest.mark.filesystems, pytest.mark.monitor_without_endpoints]


def test_filesystems():
    # TODO: make the helper that fetches metrics from selfdescribe.json check for platform specificity
    expected_metrics = [
        "df_complex.free",
        "df_complex.used",
        "percent_bytes.free",
        "percent_bytes.used",
        "disk.summary_utilization",
        "disk.utilization",
    ]
    if sys.platform == "linux":
        expected_metrics.extend(["df_inodes.free", "df_inodes.used", "percent_inodes.free", "percent_inodes.used"])
    expected_dims = get_monitor_dims_from_selfdescribe("filesystems")
    with Agent.run(
        """
    monitors:
      - type: filesystems
    """
    ) as agent:
        assert wait_for(
            p(has_any_metric_or_dim, agent.fake_services, expected_metrics, expected_dims), timeout_seconds=60
        ), "timed out waiting for metrics and/or dimensions!"
        assert not has_log_message(agent.output.lower(), "error"), "error found in agent output!"


def test_filesystems_mountpoint_filter():
    expected_metrics = [
        "df_complex.free",
        "df_complex.used",
        "percent_bytes.free",
        "percent_bytes.used",
        "disk.utilization",
    ]
    if sys.platform == "linux":
        expected_metrics.extend(["df_inodes.free", "df_inodes.used", "percent_inodes.free", "percent_inodes.used"])

    with Agent.run(
        """
    procPath: /proc
    monitors:
      - type: filesystems
        mountPoints:
         - "!*"
    """
    ) as agent:
        assert wait_for(
            p(has_any_metric_or_dim, agent.fake_services, ["disk.summary_utilization"], []), timeout_seconds=60
        ), "timed out waiting for metrics and/or dimensions!"
        assert ensure_never(lambda: has_any_metric_or_dim(agent.fake_services, expected_metrics, []))
        assert not has_log_message(agent.output.lower(), "error"), "error found in agent output!"


def test_filesystems_fstype_filter():
    expected_metrics = [
        "df_complex.free",
        "df_complex.used",
        "percent_bytes.free",
        "percent_bytes.used",
        "disk.utilization",
    ]
    if sys.platform == "linux":
        expected_metrics.extend(["df_inodes.free", "df_inodes.used", "percent_inodes.free", "percent_inodes.used"])

    with Agent.run(
        """
    procPath: /proc
    monitors:
      - type: filesystems
        fsTypes:
         - "!*"
    """
    ) as agent:
        assert wait_for(
            p(has_any_metric_or_dim, agent.fake_services, ["disk.summary_utilization"], []), timeout_seconds=60
        ), "timed out waiting for metrics and/or dimensions!"
        assert ensure_never(lambda: has_any_metric_or_dim(agent.fake_services, expected_metrics, []))
        assert not has_log_message(agent.output.lower(), "error"), "error found in agent output!"
