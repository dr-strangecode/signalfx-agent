import string
from functools import partial as p
from pathlib import Path

import pytest

from tests.helpers.agent import Agent
from tests.helpers.assertions import has_datapoint_with_dim, has_datapoint_with_metric_name, tcp_socket_open
from tests.helpers.kubernetes.utils import get_discovery_rule, run_k8s_monitors_test
from tests.helpers.util import (
    container_ip,
    get_monitor_dims_from_selfdescribe,
    get_monitor_metrics_from_selfdescribe,
    run_container,
    wait_for,
)

pytestmark = [pytest.mark.collectd, pytest.mark.postgresql, pytest.mark.monitor_with_endpoints]

DIR = Path(__file__).parent

CONFIG_TEMP = string.Template(
    """
monitors:
  - type: collectd/postgresql
    host: $host
    port: 5432
    username: "username1"
    password: "password1"
    queries:
    - name: "exampleQuery"
      minVersion: 60203
      maxVersion: 200203
      statement: |
        SELECT coalesce(sum(n_live_tup), 0) AS live, coalesce(sum(n_dead_tup), 0) AS dead FROM pg_stat_user_tables;
      results:
      - type: gauge
        instancePrefix: live
        valuesFrom:
        - live
    databases:
    - name: test
      username: "test_user"
      password: "test_pwd"
      interval: 5
      expireDelay: 10
      sslMode: disable
"""
)

ENV = ["POSTGRES_USER=test_user", "POSTGRES_PASSWORD=test_pwd", "POSTGRES_DB=test"]


def test_postgresql():
    with run_container("postgres:10", environment=ENV) as cont:
        host = container_ip(cont)
        config = CONFIG_TEMP.substitute(host=host)
        assert wait_for(p(tcp_socket_open, host, 5432), 60), "service didn't start"

        with Agent.run(config) as agent:
            assert wait_for(
                p(has_datapoint_with_dim, agent.fake_services, "plugin", "postgresql")
            ), "Didn't get postgresql datapoints"
            assert wait_for(p(has_datapoint_with_metric_name, agent.fake_services, "pg_blks.toast_hit"))


@pytest.mark.kubernetes
def test_postgresql_in_k8s(agent_image, minikube, k8s_observer, k8s_test_timeout, k8s_namespace):
    yaml = DIR / "postgresql-k8s.yaml"
    monitors = [
        {
            "type": "collectd/postgresql",
            "discoveryRule": get_discovery_rule(yaml, k8s_observer, namespace=k8s_namespace),
            "databases": [{"name": "test", "username": "test_user", "password": "test_pwd"}],
            "username": "test_user",
            "password": "test_pwd",
        }
    ]
    run_k8s_monitors_test(
        agent_image,
        minikube,
        monitors,
        namespace=k8s_namespace,
        yamls=[yaml],
        observer=k8s_observer,
        expected_metrics=get_monitor_metrics_from_selfdescribe(monitors[0]["type"]),
        expected_dims=get_monitor_dims_from_selfdescribe(monitors[0]["type"]),
        test_timeout=k8s_test_timeout,
        passwords=["test_pwd"],
    )
