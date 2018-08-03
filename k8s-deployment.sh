#!/bin/sh

function main() {

    # Find Operating System
    case "$(uname -s)" in
        Linux*)     execute_linux_dependencies;;
        Darwin*)    execute_mac_dependencies;;
        *)          echo "Operating System not support, app terminated!" && exit 1;;
    esac

    # Check if config.local file exists
    k8s_config="$HOME/.kube/config.local"
    if [ -e "$k8s_config" ]
    then
        break
    else
        dialog --backtitle "Kubernetes Services Deployment" \
        --title "Kubernetes Services Deployment" \
        --msgbox "File ${k8s_config} was not found!\n\nMake sure to read the README file and execute 'cp $HOME/.kube/config $HOME/.kube/config.local'" 20 50

        clear
        exit 1
    fi

    export KUBECONFIG=~/.kube/config.local

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
    delete_options=("openfaas openfaas-fn" "" off
                    "airflow" "" off)
    res_delete_selections+=$("${delete_selections[@]}" "${delete_options[@]}" 2>&1 > /dev/tty)

    # Return status of non-zero indicates cancel
    if [ "$?" != "0" ]; then
        terminate_process
    fi

    # selections is now: { app1 app2 app3... ... traefik_ingress }
    # Cast selections into an Array
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
            # Grep exact match
            kubectl get namespaces|grep ${index}
            # Return status of non-zero indicates cancel
            if [ "$?" == "0" ]; then
                kubectl delete namespace ${index}
            fi
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
    deploy_options=("kubernetes_dashboard" "" on
             "openfaas" "" off
             "airflow" "" off)
    res_deploy_selections+=$("${deploy_selections[@]}" "${deploy_options[@]}" 2>&1 > /dev/tty)

    # Return status of non-zero indicates cancel
    if [ "$?" != "0" ]; then
        terminate_process
    fi

    # Add traefik_ingress to the array
    res_deploy_selections+=' traefik_ingress'

    # selections is now: { app1 app2 app3... ... traefik_ingress }
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
        urls_string="${urls_string}$(get_utl_${index}) \n"
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
    kubectl apply -f traefik/traefik-namespace.yml

    # Wait until namespace created
    until kubectl get namespaces|grep ingress-traefik
    do
        sleep 0.5
    done

    kubectl apply -f traefik/traefik-confgmap.yml
    kubectl apply -f traefik/traefik-rbac.yaml
    kubectl apply -f traefik/traefik-ds.yaml

    return 0
}

function get_utl_traefik_ingress() {
    echo "http://traefik.localhost"
}

function deploy_kubernetes_dashboard() {
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/master/src/deploy/recommended/kubernetes-dashboard.yaml
    kubectl apply -f kubernetes-dashboard/dashboard-ingress.yml

    return 0
}

function get_utl_kubernetes_dashboard() {
    echo "http://kubernetes.localhost"
}

function deploy_airflow() {
    kubectl apply -f airflow/airflow-namespace.yml

    # Wait until namespace created
    until kubectl get namespaces|grep airflow
    do
        sleep 0.5
    done

    kubectl apply -f airflow/airflow-ingress.yml
    kubectl apply -f airflow/airflow-deployment.yml

    return 0
}

function get_utl_airflow() {
    echo "http://airflow.localhost"
}

function deploy_openfaas() {
    kubectl apply -f openfaas/namespace.yml

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

    kubectl apply -f openfaas/

    return 0
}

function get_utl_openfaas() {
    echo "http://openfaas.localhost\nhttp://prometheus.openfaas.localhost"
}

function execute_linux_dependencies() {
    case "$(awk -F= '/^NAME/{print $2}' /etc/os-release)" in
        "Ubuntu"*)          sudo apt-get install -y dialog;;
        "CentOS Linux"*)    sudo yum install -y dialog;;
        *)                  echo "Linux version not support, app terminated!" && exit 1;;
    esac
}

function execute_mac_dependencies() {
    # Check if dialog already installed
    brew ls --versions dialog
    if [ "$?" != "0" ]; then
        brew install dialog
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

function test_internet_connection() {
    wget -q --spider http://google.com
    return $?
}

main "$@"
