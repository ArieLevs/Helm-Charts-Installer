#!/bin/sh

function main() {
    #cp ~/.kube/config ~/.kube/config.local
    export KUBECONFIG=~/.kube/config.local

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

        deploy_kubernetes_services
    fi

    exit 0
}

function deploy_kubernetes_services() {

    service_selections=(dialog --backtitle "Kubernetes Services Deployment" --separate-output --checklist "Select applications to install:" 20 50 0)
    options=("kubernetes_dashboard" "" on
             "openfaas" "" off
             "airflow" "" off)
    selections+=$("${service_selections[@]}" "${options[@]}" 2>&1 > /dev/tty)

    # Return status of non-zero indicates cancel
    if [ "$?" != "0" ]; then
        terminate_process
    fi

    # Add traefik_ingress to the array
    selections+=' traefik_ingress'

    # selections is now: { app1 app2 app3... ... traefik_ingress }
    # Cast selections into an Array
    deployments_array=(${selections// / })
    num_of_deployments=${#deployments_array[@]}


    urls_string="\n"
    step=$((100/num_of_deployments))  # progress bar step
    cur_file_idx=0
    counter=0
    (
    for index in ${deployments_array[@]}
    do
        (( counter+=step ))

        #pct=$(( cur_file_idx * 100 / num_of_deployments ))
        echo "XXX"
        echo "$counter"
        echo "$counter% Deployed"

        echo "Deploying: $index"
        echo "XXX"
        #echo "$pct"
        processed=$((processed+1))

        (( cur_file_idx+=1 )) # increase counter

        [ ${counter} -gt 100 ] && break  # break when reach the 100% (or greater
                                   # since Bash only does integer arithmetic)
        # Main execution part
        deploy_${index}

    done
    ) | dialog --backtitle "Kubernetes Services Deployment" --title "Kubernetes Services Deployment" --gauge "Wait please..." 20 50 0


    for index in ${deployments_array[@]}
    do
        urls_string="${urls_string}$(get_utl_${index}) \n"
    done

    dialog --backtitle "Kubernetes Services Deployment" \
        --title "Kubernetes Services Deployment" \
        --no-cancel \
        --msgbox "Kubernetes Services Deployment Completed!\nVisit: ${urls_string}" 20 50

    clear
    echo "Kubernetes Services Deployment Completed!\nVisit: ${urls_string}"
    exit 0
}

function deploy_traefik_ingress() {
    kubectl apply -f traefik/traefik-namespace.yml
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
    kubectl apply -f airflow/airflow-ingress.yml
    kubectl apply -f airflow/airflow-deployment.yml

    return 0
}

function get_utl_airflow() {
    echo "http://airflow.localhost"
}

function deploy_openfaas() {
    kubectl apply -f openfaas/namespace.yml
    kubectl apply -f openfaas/

    return 0
}

function get_utl_openfaas() {
    echo "http://openfaas.localhost\nhttp://prometheus.openfaas.localhost"
}

function terminate_process() {
    dialog --title "Kubernetes Services Deployment" \
        --infobox "Deployment canceled." 20 50
    clear
    echo "Kubernetes Services Deployment Terminated"
    exit 1
}

function test_internet_connection() {
    wget -q --spider http://google.com
    return $?
}

main "$@"
