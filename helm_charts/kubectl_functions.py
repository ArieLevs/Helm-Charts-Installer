
import subprocess


def get_cluster_info():
    """
    Get cluster information

    :return: return value from command execution as string
    """
    cluster_info_completed_process = subprocess.run(["kubectl", "cluster-info"],
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE)

    if cluster_info_completed_process.returncode == 0:
        return cluster_info_completed_process.stdout.decode('utf-8').strip()
    else:
        return cluster_info_completed_process.stderr.decode('utf-8').strip()


def create_registry_secret(secret_name, docker_registry, docker_username, docker_password, namespace):
    """
    Create a new docker-registry secret

    :param secret_name: String
    :param docker_registry: String
    :param docker_username: String
    :param docker_password: String
    :param namespace: String
    :return: return code and value from command execution as dictionary
    """
    add_registry_completed = subprocess.run(["kubectl", "create", "secret", "docker-registry", secret_name,
                                             "--docker-server=%s" % docker_registry,
                                             "--docker-username=%s" % docker_username,
                                             "--docker-password=%s" % docker_password,
                                             "--namespace=%s" % namespace],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
    if add_registry_completed.returncode == 0:
        value = add_registry_completed.stdout.decode('utf-8').strip()
    else:
        value = add_registry_completed.stderr.decode('utf-8').strip()

    return {'returncode': add_registry_completed.returncode, 'value': value}
