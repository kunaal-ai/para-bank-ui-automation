#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting local pipeline test...${NC}"

# Get Jenkins container ID
JENKINS_CONTAINER=$(docker ps -q -f name=jenkins)

if [ -z "$JENKINS_CONTAINER" ]; then
    echo -e "${RED}Jenkins container is not running. Please start it first.${NC}"
    exit 1
fi

# Wait for Jenkins to be ready
echo -e "${YELLOW}Waiting for Jenkins to be ready...${NC}"
while ! docker exec ${JENKINS_CONTAINER} curl -s http://localhost:8080/ > /dev/null; do
    echo "Jenkins is not ready yet, waiting..."
    sleep 10
done

# Get the initial admin password
echo -e "${YELLOW}Getting Jenkins admin password...${NC}"
JENKINS_PASSWORD=$(docker exec ${JENKINS_CONTAINER} cat /var/jenkins_home/secrets/initialAdminPassword)

# Create the job if it doesn't exist
echo -e "${YELLOW}Creating Jenkins job if it doesn't exist...${NC}"
JOB_XML=$(cat <<EOF
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@1289.vd1c337fd5354">
  <description>Para Bank UI Automation Pipeline</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@3697.vb_470e4543a_d">
    <scm class="hudson.plugins.git.GitSCMSource" plugin="git@4.14.3">
      <id>para-bank-ui-automation</id>
      <remote>https://github.com/kt/para-bank-ui-automation.git</remote>
      <credentialsId>github-credentials</credentialsId>
    </scm>
    <scriptPath>Jenkinsfile</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>
EOF
)

# Create the job using curl
curl -X POST \
    -H "Content-Type: application/xml" \
    -d "${JOB_XML}" \
    --user admin:${JENKINS_PASSWORD} \
    http://localhost:8080/createItem?name=para-bank-ui-automation

# Copy the current Jenkinsfile to the container
echo -e "${GREEN}Copying Jenkinsfile to container...${NC}"
docker cp Jenkinsfile ${JENKINS_CONTAINER}:/var/jenkins_home/workspace/para-bank-ui-automation/Jenkinsfile

# Run the pipeline using curl
echo -e "${GREEN}Running pipeline...${NC}"
BUILD_URL=$(curl -s -X POST \
    --user admin:${JENKINS_PASSWORD} \
    http://localhost:8080/job/para-bank-ui-automation/build)

# Extract build number from the response
BUILD_NUMBER=$(curl -s \
    --user admin:${JENKINS_PASSWORD} \
    http://localhost:8080/job/para-bank-ui-automation/lastBuild/api/json | grep -o '"number":[0-9]*' | cut -d':' -f2)

echo -e "${GREEN}Build started with number: ${BUILD_NUMBER}${NC}"
echo "You can check the build status at: http://localhost:8080/job/para-bank-ui-automation/${BUILD_NUMBER}/"

# Function to check build status
check_build_status() {
    local status=$(curl -s \
        --user admin:${JENKINS_PASSWORD} \
        http://localhost:8080/job/para-bank-ui-automation/${BUILD_NUMBER}/api/json | grep -o '"result":"[^"]*"' | cut -d'"' -f4)
    echo $status
}

# Wait for build to complete
echo "Waiting for build to complete..."
while true; do
    status=$(check_build_status)
    if [ "$status" = "SUCCESS" ]; then
        echo -e "${GREEN}Build completed successfully!${NC}"
        break
    elif [ "$status" = "FAILURE" ]; then
        echo -e "${RED}Build failed!${NC}"
        break
    elif [ "$status" = "ABORTED" ]; then
        echo -e "${RED}Build was aborted!${NC}"
        break
    fi
    sleep 10
done

# Show build console output
echo -e "${GREEN}Build console output:${NC}"
curl -s \
    --user admin:${JENKINS_PASSWORD} \
    http://localhost:8080/job/para-bank-ui-automation/${BUILD_NUMBER}/consoleText 