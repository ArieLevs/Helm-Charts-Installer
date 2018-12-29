
import subprocess


def get_cluster_info():
    cluster_info_completed_process = subprocess.run(["kubectl", "cluster-info"],
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE)

    if cluster_info_completed_process.returncode == 0:
        return cluster_info_completed_process.stdout.decode('utf-8').strip()
    else:
        return cluster_info_completed_process.stderr.decode('utf-8').strip()
