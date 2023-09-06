from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from kubernetes.client.rest import ApiException

from main import main


def test_successful_deletion_of_namespace():
    mock_namespace = MagicMock()
    mock_namespace.metadata.name = "test-namespace"
    mock_namespace.metadata.creation_timestamp = datetime.now(
        timezone.utc
    ) - timedelta(seconds=3600)
    mock_namespace.metadata.labels = {"argocd-review-environment": "true"}
    mock_namespace_items = [mock_namespace]
    mock_pod_items = []
    with patch("main.client.CoreV1Api") as mock_api:
        mock_api_instance = mock_api.return_value
        mock_api_instance.list_namespace.return_value.items = (
            mock_namespace_items
        )
        mock_api_instance.list_namespaced_pod.return_value.items = (
            mock_pod_items
        )
        with patch(
            "main.config.load_incluster_config", side_effect=ApiException
        ):
            with patch("main.config.load_kube_config"):
                main()
        mock_api_instance.delete_namespace.assert_called_once_with(
            "test-namespace"
        )


def test_namespace_not_deleted_because_it_has_a_pod():
    mock_namespace = MagicMock()
    mock_namespace.metadata.name = "test-namespace-2"
    mock_namespace.metadata.creation_timestamp = datetime.now(
        timezone.utc
    ) - timedelta(seconds=3600)
    mock_namespace.metadata.labels = {"argocd-review-environment": "true"}
    mock_namespace_items = [mock_namespace]
    mock_pod = MagicMock()
    mock_pod_items = [mock_pod]
    with patch("main.client.CoreV1Api") as mock_api:
        mock_api_instance = mock_api.return_value
        mock_api_instance.list_namespace.return_value.items = (
            mock_namespace_items
        )
        mock_api_instance.list_namespaced_pod.return_value.items = (
            mock_pod_items
        )
        with patch(
            "main.config.load_incluster_config", side_effect=ApiException
        ):
            with patch("main.config.load_kube_config"):
                main()
        mock_api_instance.delete_namespace.assert_not_called()


def test_namespace_not_deleted_if_it_was_created_less_than_30_minutes_ago():
    mock_namespace = MagicMock()
    mock_namespace.metadata.name = "test-namespace-3"
    mock_namespace.metadata.creation_timestamp = datetime.now(timezone.utc)
    mock_namespace.metadata.labels = {"argocd-review-environment": "true"}
    mock_namespace_items = [mock_namespace]
    mock_pod_items = []
    with patch("main.client.CoreV1Api") as mock_api:
        mock_api_instance = mock_api.return_value
        mock_api_instance.list_namespace.return_value.items = (
            mock_namespace_items
        )
        mock_api_instance.list_namespaced_pod.return_value.items = (
            mock_pod_items
        )
        with patch(
            "main.config.load_incluster_config", side_effect=ApiException
        ):
            with patch("main.config.load_kube_config"):
                main()
        mock_api_instance.delete_namespace.assert_not_called()


def test_namespace_not_deleted_without_correct_label():
    mock_namespace = MagicMock()
    mock_namespace.metadata.name = "test-namespace-4"
    mock_namespace.metadata.creation_timestamp = datetime.now(
        timezone.utc
    ) - timedelta(seconds=3600)
    mock_namespace.metadata.labels = {"not-the-right-label": "true"}
    mock_namespace_items = [mock_namespace]
    mock_pod_items = []
    with patch("main.client.CoreV1Api") as mock_api:
        mock_api_instance = mock_api.return_value
        mock_api_instance.list_namespace.return_value.items = (
            mock_namespace_items
        )
        mock_api_instance.list_namespaced_pod.return_value.items = (
            mock_pod_items
        )
        with patch(
            "main.config.load_incluster_config", side_effect=ApiException
        ):
            with patch("main.config.load_kube_config"):
                main()
        mock_api_instance.delete_namespace.assert_not_called()


def test_value_error_when_label_is_not_in_the_correct_format():
    with patch("main.getenv", return_value="not-in-the-correct-format"):
        try:
            main()
        except ValueError as e:
            assert (
                str(e)
                == "ARGOCD_NAMESPACE_LABEL must be in the format of key=value"
            )
