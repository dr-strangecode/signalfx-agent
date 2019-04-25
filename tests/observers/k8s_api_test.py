import os
from functools import partial as p

import pytest
from tests.helpers.assertions import has_datapoint
from tests.helpers.util import TEST_SERVICES_DIR, wait_for


@pytest.mark.k8s
@pytest.mark.kubernetes
def test_k8s_annotations_in_discovery(agent_image, minikube, k8s_namespace):
    nginx_yaml = os.path.join(TEST_SERVICES_DIR, "nginx/nginx-k8s.yaml")
    with minikube.create_resources([nginx_yaml], namespace=k8s_namespace):
        config = """
            observers:
            - type: k8s-api

            monitors:
            - type: collectd/nginx
              discoveryRule: 'Get(kubernetes_annotations, "allowScraping") == "true" && port == 80'
        """
        with minikube.run_agent(agent_image, config=config, namespace=k8s_namespace) as [_, fake_services]:
            assert wait_for(p(has_datapoint, fake_services, dimensions={"plugin": "nginx"}))
