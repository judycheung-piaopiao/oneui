#!/bin/bash
set -e

echo "Current directory: $PWD"
echo "Deploying backend for branch $BITBUCKET_BRANCH"

if [ "$BITBUCKET_BRANCH" = "uat" ]; then
    cd $PROJECT_UAT_PATH/ag-tools-catalogue/backend

    echo "Syncing UAT backend to 1.65"
    rsync -a --delete $PROJECT_UAT_PATH/ag-tools-catalogue/backend infra@10.40.1.65:/home/infra/prod/gui/installers/services/uat/gui-services/ag-tools-catalogue/
    ssh 10.40.1.65 "source ~/.bashrc && app ag-tools-catalogue-backend-uat restart"

    echo "Backend deployment to UAT done"
elif [ "$BITBUCKET_BRANCH" = "master" ]; then
    cd $PROJECT_PATH/ag-tools-catalogue/backend

    echo "Syncing PROD backend to 1.144"
    rsync -a --delete $PROJECT_PATH/ag-tools-catalogue/backend infra@10.40.1.144:/home/infra/prod/gui/installers/services/prod/gui-services/ag-tools-catalogue/
    ssh 10.40.1.144 "source ~/.bashrc && app ag-tools-catalogue-backend restart"

    echo "Backend deployment to PROD done"
else
    echo "Unknown branch $BITBUCKET_BRANCH"
    exit 1
fi
