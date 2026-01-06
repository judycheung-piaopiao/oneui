#!/bin/bash
set -e

export NVM_DIR=~/.nvm
source ~/.nvm/nvm.sh
source ~/.bashrc

nvm use 22

echo "Deploying frontend for branch $BITBUCKET_BRANCH"

if [ "$BITBUCKET_BRANCH" = "uat" ]; then
    cd $PROJECT_UAT_PATH/ag-tools-catalogue/frontend

    # Set UAT environment variables
    export VITE_API_BASE_URL="http://10.40.1.65:8889"
    export VITE_APP_ENV="uat"

    npm install
    npm run build
    
    echo "Syncing UAT frontend to 1.65"
    rsync -a --delete $PROJECT_UAT_PATH/ag-tools-catalogue/frontend infra@10.40.1.65:/home/infra/prod/gui/installers/apps/uat/gui-apps/ag-tools-catalogue/
    
    echo "Restarting uat frontend"
    ssh 10.40.1.65 "source ~/.bashrc && app ag-tools-catalogue-frontend-uat restart"
    
    echo "Frontend deployed to UAT successfully"
elif [ "$BITBUCKET_BRANCH" = "master" ]; then
    cd $PROJECT_PATH/ag-tools-catalogue/frontend

    # Set PROD environment variables
    export VITE_API_BASE_URL="https://one-api.alpha-grep.com"
    export VITE_APP_ENV="production"

    npm install
    npm run build
    
    echo "Syncing PROD frontend to 1.144"
    rsync -a --delete $PROJECT_PATH/ag-tools-catalogue/frontend infra@10.40.1.144:/home/infra/prod/gui/installers/apps/prod/gui-apps/ag-tools-catalogue/
    
    echo "Restarting prod frontend"
    ssh 10.40.1.144 "source ~/.bashrc && app ag-tools-catalogue-frontend restart"
    
    echo "Frontend deployed to PROD successfully"
else
    echo "Unknown branch $BITBUCKET_BRANCH"
    exit 1
fi
