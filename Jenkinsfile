pipeline {
    agent any

    environment {
        DOCKER_COMPOSE = 'docker compose'
        REPO_URL = 'https://github.com/kunaal-ai/para-bank-ui-automation.git'
        GITHUB_CREDENTIALS = credentials('github-credentials')
        PYTHONPATH = "${WORKSPACE}:${WORKSPACE}/src"
        RED = '\033[0;31m'
        GREEN = '\033[0;32m'
        YELLOW = '\033[1;33m'
        BLUE = '\033[0;34m'
        NC = '\033[0m'
    }

    stages {
        stage('Checkout') {
            steps {
                echo "${BLUE}=== Starting Checkout Stage ===${NC}"
                cleanWs()
                echo "${GREEN}✓ Workspace cleaned${NC}"
                
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        url: "${REPO_URL}",
                        credentialsId: 'github-credentials'
                    ]]
                ])
                echo "${GREEN}✓ Code checked out successfully${NC}"
            }
        }

        stage('Validate Environment') {
            steps {
                echo "${BLUE}=== Starting Environment Validation ===${NC}"
                sh '''
                    #!/bin/bash
                    set -e
                    
                    echo "Checking Python version..."
                    if ! python3 --version; then
                        echo "${RED}✗ Python not found or not working${NC}"
                        exit 1
                    fi
                    echo "${GREEN}✓ Python version verified${NC}"
                    
                    echo "Checking pip version..."
                    if ! pip --version; then
                        echo "${RED}✗ Pip not found or not working${NC}"
                        exit 1
                    fi
                    echo "${GREEN}✓ Pip version verified${NC}"
                    
                    echo "Checking Docker version..."
                    if ! docker --version; then
                        echo "${RED}✗ Docker not found or not working${NC}"
                        exit 1
                    fi
                    echo "${GREEN}✓ Docker version verified${NC}"
                    
                    echo "Checking Docker Compose version..."
                    if ! docker compose version; then
                        echo "${RED}✗ Docker Compose not found or not working${NC}"
                        exit 1
                    fi
                    echo "${GREEN}✓ Docker Compose version verified${NC}"
                '''
            }
        }

        stage('Setup Environment') {
            steps {
                echo "${BLUE}=== Starting Environment Setup ===${NC}"
                sh '''
                    #!/bin/bash
                    set -e
                    
                    echo "Creating test results directory..."
                    if ! mkdir -p test-results; then
                        echo "${RED}✗ Failed to create test results directory${NC}"
                        exit 1
                    fi
                    chmod -R 777 test-results
                    echo "${GREEN}✓ Test results directory created${NC}"
                    
                    echo "Setting up Python virtual environment..."
                    if ! python3 -m venv venv; then
                        echo "${RED}✗ Failed to create virtual environment${NC}"
                        exit 1
                    fi
                    . venv/bin/activate
                    echo "${GREEN}✓ Virtual environment created and activated${NC}"
                    
                    echo "Upgrading pip..."
                    if ! pip install --upgrade pip; then
                        echo "${RED}✗ Failed to upgrade pip${NC}"
                        exit 1
                    fi
                    echo "${GREEN}✓ Pip upgraded${NC}"
                    
                    echo "Installing project dependencies..."
                    if ! pip install -r requirements.txt; then
                        echo "${RED}✗ Failed to install project dependencies${NC}"
                        exit 1
                    fi
                    echo "${GREEN}✓ Project dependencies installed${NC}"
                    
                    echo "Installing project in development mode..."
                    if ! pip install -e .; then
                        echo "${RED}✗ Failed to install project in development mode${NC}"
                        exit 1
                    fi
                    echo "${GREEN}✓ Project installed in development mode${NC}"
                '''
            }
        }

        stage('Build Test Container') {
            steps {
                echo "${BLUE}=== Starting Test Container Build ===${NC}"
                sh '''
                    #!/bin/bash
                    set -e
                    
                    echo "Building test container..."
                    if ! ${DOCKER_COMPOSE} build test; then
                        echo "${RED}✗ Failed to build test container${NC}"
                        exit 1
                    fi
                    echo "${GREEN}✓ Test container built successfully${NC}"
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo "${BLUE}=== Starting Test Execution ===${NC}"
                sh '''
                    #!/bin/bash
                    set -e
                    
                    echo "Running test suite..."
                    if ! ${DOCKER_COMPOSE} run --rm test pytest \
                        -v \
                        --html=test-results/report.html \
                        --self-contained-html \
                        --junitxml=test-results/junit.xml \
                        tests/; then
                        echo "${RED}✗ Test execution failed${NC}"
                        echo "${YELLOW}Check test-results/report.html for detailed test results${NC}"
                        exit 1
                    fi
                    echo "${GREEN}✓ All tests passed successfully!${NC}"
                '''
            }
        }

        stage('Generate Reports') {
            steps {
                echo "${BLUE}=== Starting Report Generation ===${NC}"
                sh '''
                    #!/bin/bash
                    set -e
                    
                    echo "Checking test results directory..."
                    if ! ls -la test-results/; then
                        echo "${RED}✗ Test results directory not found${NC}"
                        exit 1
                    fi
                    echo "${GREEN}✓ Test results directory contents verified${NC}"
                    
                    echo "Verifying report files..."
                    if [ ! -f "test-results/report.html" ]; then
                        echo "${RED}✗ HTML report not found${NC}"
                        exit 1
                    fi
                    echo "${GREEN}✓ HTML report generated${NC}"
                    
                    if [ ! -f "test-results/junit.xml" ]; then
                        echo "${RED}✗ JUnit XML report not found${NC}"
                        exit 1
                    fi
                    echo "${GREEN}✓ JUnit XML report generated${NC}"
                '''
            }
        }
    }

    post {
        always {
            echo "${BLUE}=== Starting Post-Build Actions ===${NC}"
            
            echo "Archiving test results..."
            junit 'test-results/*.xml'
            archiveArtifacts artifacts: 'test-results/*.html', allowEmptyArchive: true
            echo "${GREEN}✓ Test results archived${NC}"
            
            echo "Cleaning up workspace..."
            cleanWs()
            echo "${GREEN}✓ Workspace cleaned${NC}"
            
            echo "${BLUE}=== Build Process Completed ===${NC}"
        }
        success {
            echo "${GREEN}=== Build Succeeded ===${NC}"
            echo "${GREEN}✓ All stages completed successfully${NC}"
            echo "${GREEN}✓ Test reports are available in the build artifacts${NC}"
        }
        failure {
            echo "${RED}=== Build Failed ===${NC}"
            echo "${RED}✗ One or more stages failed${NC}"
            echo "${YELLOW}Please check the build logs for details${NC}"
            echo "${YELLOW}Look for ${RED}✗${YELLOW} symbols to identify failures${NC}"
        }
    }
}