from datetime import datetime, timezone
from os import getenv

from kubernetes import client, config


def main() -> None:
    try:
        key, value = getenv(
            "ARGOCD_NAMESPACE_LABEL", "argocd-review-environment=true"
        ).split("=")
    except ValueError:
        raise ValueError(
            "ARGOCD_NAMESPACE_LABEL must be in the format of key=value"
        )  # noqa: E501

    try:
        config.load_incluster_config()
    except:  # noqa: E722
        config.load_kube_config()

    api = client.CoreV1Api()

    namespaces = api.list_namespace().items

    for namespace in namespaces:
        if not api.list_namespaced_pod(namespace.metadata.name).items:
            if (
                namespace.metadata.labels
                and namespace.metadata.labels.get(key) == value
            ):
                creation_time = datetime.fromisoformat(
                    str(namespace.metadata.creation_timestamp)
                )
                current_time = datetime.now(timezone.utc)
                time_diff = current_time - creation_time
                if time_diff.total_seconds() > 1800:
                    print(
                        f"Deleting namespace {namespace.metadata.name}"
                    )  # noqa: E501
                    api.delete_namespace(
                        namespace.metadata.name,
                    )


if __name__ == "__main__":
    main()
