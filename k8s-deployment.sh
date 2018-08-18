#!/bin/sh

K8S_CONFIG="$HOME/.kube/config.local"

TRAEFIK_URL="http://traefik.localhost"
KUBE_DASH_URL="https://kubernetes.localhost"
AIRFLOW_URL="http://airflow.localhost"
OPENFAAS_URL="http://openfaas.localhost"
PROMETHEUS_OPENFAAS_URL="http://prometheus.openfaas.localhost"
ALERTMANAGER_OPENFAAS_USL="http://alertmanager.openfaas.localhost"
REDIS_URL=""
JENKIS_URL="http://jenkins.localhost"

function main() {

    # Identify Operating System
    case "$(uname -s)" in
        Linux*)     execute_linux_dependencies;;
        Darwin*)    execute_mac_dependencies;;
        *)          echo "Operating System not support, app terminated!" && exit 1;;
    esac

    # Check if config.local file exists
    if [ -e "${K8S_CONFIG}" ]
    then
        break
    else
        dialog --backtitle "Kubernetes Services Deployment" \
        --title "Kubernetes Services Deployment" \
        --msgbox "File ${K8S_CONFIG} was not found!\n\nMake sure to read the README file and execute 'cp $HOME/.kube/config ${K8S_CONFIG}'" 20 50

        clear
        exit 1
    fi

    export KUBECONFIG=${K8S_CONFIG}

    ### Install tiller on k8s cluster ###
    kubectl get serviceaccount tiller --namespace kube-system
    if [ "$?" != "0" ]; then
        kubectl create serviceaccount tiller --namespace kube-system
    fi

    kubectl get clusterrolebinding tiller
    if [ "$?" != "0" ]; then
        kubectl create clusterrolebinding tiller \
            --clusterrole cluster-admin \
            --serviceaccount=kube-system:tiller
    fi

    action_selections=(dialog --title "Kubernetes Services Deployment" --backtitle "Kubernetes Services Deployment" --radiolist "What would like to do?" 20 50 0)
    action_options=("Install" "" on
                    "Delete" "" off)
    res_action_selections+=$("${action_selections[@]}" "${action_options[@]}" 2>&1 > /dev/tty)

    # Return status of non-zero indicates cancel
    if [ "$?" != "0" ]; then
        terminate_process
    fi

    if [ ${res_action_selections} == "Install" ]; then
        deploy_kubernetes_services
    else
        delete_kubernetes_services
    fi

    exit 0
}

function delete_kubernetes_services() {
    delete_selections=(dialog --backtitle "Kubernetes Services Delete" --separate-output --checklist "Select applications to delete:" 20 50 0)
    delete_options=("kubernetes-dashboard" "" off
                    "jenkins" "" off
                    "airflow" "" off
                    "openfaas" "" off
                    "redis" "" off)
    res_delete_selections+=$("${delete_selections[@]}" "${delete_options[@]}" 2>&1 > /dev/tty)

    # Return status of non-zero indicates cancel
    if [ "$?" != "0" ]; then
        terminate_process
    fi

    # selections are now: { app1 app2 app3... }
    # Cast selections into an Array delimiter is space
    deployments_array=(${res_delete_selections// / })
    num_of_deployments=${#deployments_array[@]}

    # Check if selections made
    if [ ${num_of_deployments} -gt 0 ]; then
        step=$((100/num_of_deployments))  # progress bar step
        cur_file_idx=0
        counter=0
        (
        for index in ${deployments_array[@]}
        do
            (( counter+=step ))

            echo "XXX"
            echo "$counter"
            echo "$counter% Deleted"
            echo "Please wait"

            echo "Deleting: $index"
            echo "XXX"
            processed=$((processed+1))

            (( cur_file_idx+=1 )) # increase counter

            [ ${counter} -gt 100 ] && break  # break when reach the 100% (or greater
                                       # since Bash only does integer arithmetic)
            # Main execution part
            helm delete --purge ${index}
        done
        ) | dialog --backtitle "Kubernetes Services Delete" --title "Kubernetes Services Delete" --gauge "Wait please..." 20 50 0

        message="Kubernetes Services Deletion Completed!\n"
    else
        message="You did not selected any applications to delete.\nKubernetes Services Delete Completed!\n"
    fi

    dialog --backtitle "Kubernetes Services Delete" \
        --title "Kubernetes Services Delete" \
        --no-cancel \
        --msgbox "${message}" 20 50

    clear
    echo $(kubectl cluster-info)
    echo "\n${message}"
    return 0
}

function deploy_kubernetes_services() {

    dialog --backtitle "Kubernetes Services Deployment" \
        --title "Kubernetes Services Deployment" \
        --msgbox "This app will deploy various containers upon your selection.\nMake sure internet connection is available.\nPress <Enter> to continue, or <Esc> to cancel." 20 50

    # Return status of non-zero indicates cancel
    if [ "$?" != "0" ]; then
        terminate_process
    else
        # Check internet connection
        wget -q --spider http://google.com
        # Return status of non-zero indicates no internet connection
        if [ $? -eq 1 ]; then
            dialog --backtitle "Kubernetes Services Deployment" \
                --title "Kubernetes Services Deployment" \
                --yesno "Internet connection test Failed!\nContinue only if you already have downloaded all images!" 20 50
            # Return status of 0 indicates Yes selected
            # Return status of 1 indicates No selected
            # Return status of 255 indicates <Esc> pressed
            case $? in
                1) terminate_process;;
                255) terminate_process;;
            esac
        fi
    fi

    deploy_selections=(dialog --backtitle "Kubernetes Services Deployment" --separate-output --checklist "Select applications to install:" 20 50 0)
    deploy_options=(
             "kubernetes_dashboard" "" on
             "jenkins" "" off
             "openfaas" "" off
             "airflow" "" off
             "redis" "" off)
    res_deploy_selections+=$("${deploy_selections[@]}" "${deploy_options[@]}" 2>&1 > /dev/tty)

    # Return status of non-zero indicates cancel
    if [ "$?" != "0" ]; then
        terminate_process
    fi

    # Add traefik_ingress to the array
    res_deploy_selections+=' traefik_ingress'

    # selections are now: { app1 app2 app3... ... traefik_ingress }
    # Cast selections into an Array
    deployments_array=(${res_deploy_selections// / })
    num_of_deployments=${#deployments_array[@]}

    urls_string="\n"
    step=$((100/num_of_deployments))  # progress bar step
    cur_file_idx=0
    counter=0
    (
    for index in ${deployments_array[@]}
    do
        (( counter+=step ))

        echo "XXX"
        echo "$counter"
        echo "$counter% Deployed"
        echo "Please wait"

        echo "Deploying: $index"
        echo "XXX"
        processed=$((processed+1))

        (( cur_file_idx+=1 )) # increase counter

        [ ${counter} -gt 100 ] && break  # break when reach the 100% (or greater
                                   # since Bash only does integer arithmetic)
        # Main execution part
        deploy_${index}

    done
    ) | dialog --backtitle "Kubernetes Services Deployment" --title "Kubernetes Services Deployment" --gauge "Wait please..." 20 50 0

    # Build urls list based on selections
    for index in ${deployments_array[@]}
    do
        # Append to url string the return from relevant function
        urls_string="${urls_string}$(get_url_${index}) \n"
    done

    dialog --backtitle "Kubernetes Services Deployment" \
        --title "Kubernetes Services Deployment" \
        --no-cancel \
        --msgbox "Kubernetes Services Deployment Completed!\nVisit: ${urls_string}" 20 50

    clear
    echo $(kubectl cluster-info)
    echo "\nKubernetes Services Deployment Completed!\nVisit: ${urls_string}"

    return 0
}

function deploy_traefik_ingress() {

#    mkdir $HOME/.kube/certificates &> /dev/null
#
#    # Generate self signed certificate for TLS use
#    openssl req -subj "/C=/L=/O=*.localhost/CN=*.localhost" \
#        -x509 \
#        -nodes \
#        -days 3650 \
#        -newkey rsa:2048 \
#        -keyout $HOME/.kube/certificates/tls.key \
#        -out $HOME/.kube/certificates/tls.crt &> /dev/null
#
#    tls_key=$(cat ${HOME}/.kube/certificates/tls.key | base64)
#    tls_crt=$(cat ${HOME}/.kube/certificates/tls.crt | base64)
#
#    sed -i -e "s/  defaultCert:.*/  defaultCert: ${tls_crt}/g" ./traefik/values.local.yml
#    sed -i -e "s/  defaultKey:.*/  defaultKey: ${tls_key}/g" ./traefik/values.local.yml

    helm upgrade ingress-traefik --install stable/traefik \
        --namespace ingress-traefik \
        -f deployments/ingress-traefik/values.local.yml
    return 0
}

function get_url_traefik_ingress() {
    echo ${TRAEFIK_URL}
}

function deploy_kubernetes_dashboard() {
    update_config_file
    helm upgrade kubernetes-dashboard --install stable/kubernetes-dashboard \
        --namespace kube-system \
        -f deployments/kubernetes-dashboard/values.local.yml
    return 0
}

function get_url_kubernetes_dashboard() {
    echo ${KUBE_DASH_URL}
}

function deploy_airflow() {
    mkdir /tmp/airflow-dags &> /dev/null

    helm upgrade airflow --install ./airflow \
        --namespace airflow \
        -f deployments/airflow/values.local.yaml
    return 0
}

function get_url_airflow() {
    echo "${AIRFLOW_URL} - Use /tmp/airflow-dags as persistent DAG files directory."
}

function deploy_openfaas() {
    kubectl apply -f https://raw.githubusercontent.com/openfaas/faas-netes/master/namespaces.yml

    # Wait until namespace created
    until kubectl get namespaces|grep openfaas
    do
        sleep 0.5
    done

    # Wait until namespace created
    until kubectl get namespaces|grep openfaas-fn
    do
        sleep 0.5
    done

    helm upgrade openfaas --install openfaas/openfaas \
        --namespace openfaas \
        -f deployments/openfaas/values.local.yml
    return 0
}

function get_url_openfaas() {
    echo "${OPENFAAS_URL}\n${PROMETHEUS_OPENFAAS_URL}\n${ALERTMANAGER_OPENFAAS_USL}"
}

function deploy_redis() {
    helm upgrade redis --install stable/redis \
        --namespace redis \
        -f deployments/redis/values.local.yml
    return 0
}

function get_url_redis() {
    echo ${REDIS_URL}
}

function deploy_jenkins() {
    helm upgrade jenkins --install stable/jenkins \
        --namespace jenkins \
        -f deployments/jenkins/values.local.yml
    return 0
}

function get_url_jenkins() {
    JENKINS_PASS="$(printf $(kubectl get secret --namespace jenkins jenkins -o jsonpath="{.data.jenkins-admin-password}" | base64 --decode);echo)"
    echo "${JENKIS_URL} - Username: admin, password: ${JENKINS_PASS}"
}

function update_config_file() {
    # Adds 'token' to $HOME/.kube/config.local file to allow k8s dashboard connection
    grep "token:    " $HOME/.kube/config.local
    if [ "$?" != "0" ]; then # If not found

        # Get admin token name
        admin_token_name=$(kubectl get secrets --namespace kube-system | grep admin-token | awk '{print $1}')

        # Describe the admin token secret
        admin_token_data=$(kubectl describe secrets ${admin_token_name} --namespace kube-system)

        # Get the token
        admin_token=$(echo "${admin_token_data}" | awk '/token:/,0')

        # Append token to config.local
		echo "    ${admin_token}" | tee -a $HOME/.kube/config.local
	fi
}

function execute_linux_dependencies() {
    case "$(awk -F= '/^NAME/{print $2}' /etc/os-release)" in
        "Ubuntu"*)          echo "Ubuntu not yet supported" && exit 1;; #sudo apt-get install -y dialog;;
        "CentOS Linux"*)    echo "CentOS not yet supported" && exit 1;; #sudo yum install -y dialog;;
        *)                  echo "Linux version not support, app terminated!" && exit 1;;
    esac
}

function execute_mac_dependencies() {
    # Check if dialog already installed
    brew ls --versions dialog
    if [ "$?" != "0" ]; then
        brew install dialog
    fi
    # Check if kubernetes-helm already installed
    brew install kubernetes-helm
    if [ "$?" != "0" ]; then
        brew install kubernetes-helm
    fi
}

function unexpected_process_termination() {
    dialog --title "Kubernetes Services Deployment" \
        --infobox "Something went wrong, application had to be terminated" 20 50
    clear
    echo "Kubernetes Services Deployment Terminated for some reason (no logs for now sorry)"
    exit 1
}

function terminate_process() {
    clear
    echo "Kubernetes Services Deployment Terminated"
    exit 1
}

main
