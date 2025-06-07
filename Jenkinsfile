pipeline {
    agent any

    options {
        timeout(time: 1, unit: 'HOURS')
    }

    environment {
        DOCKER_COMPOSE = 'docker compose'
        REPO_URL = 'https://github.com/kunaal-ai/para-bank-ui-automation.git'
        GITHUB_CREDENTIALS = credentials('github-credentials')
        PARA_BANK_PASSWORD = credentials('PARABANK_PASSWORD')
        PYTHONPATH = "${WORKSPACE}:${WORKSPACE}/src"
        TIMESTAMP = "${new Date().format('yyyyMMdd_HHmmss')}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "=== Starting Checkout Stage ==="
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        url: "${REPO_URL}",
                        credentialsId: 'github-credentials'
                    ]]
                ])
                echo "✓ Code checked out successfully"
                
                sh '''
                    echo "=== Git Information ==="
                    git log -1 --pretty=format:"Commit: %h%nAuthor: %an%nDate: %ad%nMessage: %s"
                    echo "=== Branch Information ==="
                    git branch -v
                '''
            }
        }

        stage('Setup Environment Variables') {
            steps {
                echo "=== Setting Up Environment Variables ==="
                writeFile file: '.env', text: """# ParaBank Test Environment Variables
USERNAME=john
PASSWORD=${PARA_BANK_PASSWORD}
BASE_URL=https://parabank.parasoft.com/parabank/
PLAYWRIGHT_BROWSERS_PATH=/ms-playwright/
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
DISPLAY=:99
PLAYWRIGHT_HEADLESS=true"""
                
                sh '''
                    if [ ! -f ".env" ]; then
                        echo "ERROR: Failed to create .env file"
                        echo "Current directory contents:"
                        ls -la
                        exit 1
                    fi
                    echo "✓ .env file created successfully"
                    
                    echo "=== Environment Variables ==="
                    grep -v "PASSWORD" .env
                '''
            }
        }

        stage('Verify Docker Compose') {
            steps {
                echo "=== Verifying Docker Compose Configuration ==="
                sh '''
                    #!/bin/bash
                    set -e
                    
                    echo "Checking docker-compose.yml file..."
                    if [ ! -f "docker-compose.yml" ]; then
                        echo "ERROR: docker-compose.yml not found"
                        echo "Current directory contents:"
                        ls -la
                        exit 1
                    fi
                    echo "✓ docker-compose.yml found"
                    
                    echo "Validating docker-compose.yml..."
                    # First, verify the .env file is valid
                    echo "Verifying .env file format..."
                    if grep -q "if \[ ! -f" .env; then
                        echo "ERROR: .env file contains shell script syntax"
                        echo "Current .env contents:"
                        cat .env
                        exit 1
                    fi
                    
                    # Then validate docker-compose.yml
                    if ! ${DOCKER_COMPOSE} config; then
                        echo "ERROR: Invalid docker-compose.yml configuration"
                        echo "docker-compose.yml contents:"
                        cat docker-compose.yml
                        echo "=== Environment File Contents ==="
                        cat .env
                        exit 1
                    fi
                    echo "✓ docker-compose.yml is valid"
                '''
            }
        }

        stage('Validate Environment') {
            steps {
                echo "=== Starting Environment Validation ==="
                sh '''
                    #!/bin/bash
                    set -e
                    
                    echo "=== System Information ==="
                    echo "OS: $(uname -a)"
                    echo "Memory: $(free -h)"
                    echo "Disk Space: $(df -h .)"
                    
                    echo "Checking Python version..."
                    if ! python3 --version; then
                        echo "ERROR: Python not found or not working"
                        echo "Python path: $(which python3)"
                        exit 1
                    fi
                    echo "✓ Python version verified"
                    
                    echo "Checking pip version..."
                    if ! pip --version; then
                        echo "ERROR: Pip not found or not working"
                        echo "Pip path: $(which pip)"
                        exit 1
                    fi
                    echo "✓ Pip version verified"
                    
                    echo "Checking Docker version..."
                    if ! docker --version; then
                        echo "ERROR: Docker not found or not working"
                        echo "Docker path: $(which docker)"
                        exit 1
                    fi
                    echo "✓ Docker version verified"
                    
                    echo "Checking Docker Compose version..."
                    if ! docker compose version; then
                        echo "ERROR: Docker Compose not found or not working"
                        echo "Docker Compose path: $(which docker-compose)"
                        exit 1
                    fi
                    echo "✓ Docker Compose version verified"
                    
                    echo "=== Docker Information ==="
                    docker info
                '''
            }
        }

        stage('Setup Environment') {
            steps {
                echo "=== Starting Environment Setup ==="
                sh '''
                    #!/bin/bash
                    set -e
                    
                    echo "Creating test results directory..."
                    if ! mkdir -p test-results; then
                        echo "ERROR: Failed to create test results directory"
                        echo "Current directory permissions:"
                        ls -la
                        exit 1
                    fi
                    chmod -R 755 test-results
                    echo "✓ Test results directory created"
                    
                    echo "Setting up Python virtual environment..."
                    if ! python3 -m venv venv; then
                        echo "ERROR: Failed to create virtual environment"
                        echo "Python version: $(python3 --version)"
                        echo "Current directory: $(pwd)"
                        exit 1
                    fi
                    . venv/bin/activate
                    echo "✓ Virtual environment created and activated"
                    
                    echo "Upgrading pip..."
                    if ! pip install --upgrade pip; then
                        echo "ERROR: Failed to upgrade pip"
                        echo "Pip version: $(pip --version)"
                        exit 1
                    fi
                    echo "✓ Pip upgraded"
                    
                    echo "Installing project dependencies..."
                    if ! pip install -r requirements.txt; then
                        echo "ERROR: Failed to install project dependencies"
                        echo "Requirements file contents:"
                        cat requirements.txt
                        exit 1
                    fi
                    echo "✓ Project dependencies installed"
                    
                    echo "Installing project in development mode..."
                    if ! pip install -e .; then
                        echo "ERROR: Failed to install project in development mode"
                        echo "Project structure:"
                        ls -la
                        exit 1
                    fi
                    echo "✓ Project installed in development mode"
                '''
            }
        }

        stage('Build Test Container') {
            steps {
                echo "=== Starting Test Container Build ==="
                sh '''
                    #!/bin/bash
                    set -e
                    
                    echo "Building test container..."
                    if ! ${DOCKER_COMPOSE} build test; then
                        echo "ERROR: Failed to build test container"
                        echo "=== Docker Build Logs ==="
                        ${DOCKER_COMPOSE} build test --no-cache
                        echo "=== Docker System Info ==="
                        docker system df
                        exit 1
                    fi
                    echo "✓ Test container built successfully"
                '''
            }
        }

        stage('Run Tests') {
            options {
                timeout(time: 30, unit: 'MINUTES')
            }
            steps {
                echo "=== Starting Test Execution ==="
                sh '''
                    #!/bin/bash
                    set -e
                    
                    echo "Running test suite..."
                    if ! ${DOCKER_COMPOSE} run --rm test pytest \
                        -v \
                        --html=test-results/report.html \
                        --self-contained-html \
                        --junitxml=test-results/junit.xml \
                        --capture=tee-sys \
                        --log-cli-level=DEBUG \
                        tests/; then
                        echo "ERROR: Test execution failed"
                        echo "=== Test Logs ==="
                        cat test-results/report.html
                        echo "=== Container Logs ==="
                        ${DOCKER_COMPOSE} logs test
                        echo "WARNING: Check test-results/report.html for detailed test results"
                        exit 1
                    fi
                    echo "✓ All tests passed successfully!"
                '''
            }
        }

        stage('Generate Reports') {
            steps {
                echo "=== Starting Report Generation ==="
                sh '''
                    #!/bin/bash
                    set -e
                    
                    echo "Checking test results directory..."
                    if ! ls -la test-results/; then
                        echo "ERROR: Test results directory not found"
                        echo "Current directory contents:"
                        ls -la
                        exit 1
                    fi
                    echo "✓ Test results directory contents verified"
                    
                    echo "Verifying report files..."
                    if [ ! -f "test-results/report.html" ]; then
                        echo "ERROR: HTML report not found"
                        echo "Test results directory contents:"
                        ls -la test-results/
                        exit 1
                    fi
                    echo "✓ HTML report generated"
                    
                    if [ ! -f "test-results/junit.xml" ]; then
                        echo "ERROR: JUnit XML report not found"
                        echo "Test results directory contents:"
                        ls -la test-results/
                        exit 1
                    fi
                    echo "✓ JUnit XML report generated"
                '''
            }
        }
    }

    post {
        always {
            echo "=== Starting Post-Build Actions ==="
            
            echo "Archiving test results..."
            junit 'test-results/*.xml'
            archiveArtifacts artifacts: 'test-results/*.html', allowEmptyArchive: true
            echo "✓ Test results archived"
            
            sh '''
                echo "=== System State at Failure ==="
                echo "Disk Space:"
                df -h
                echo "Memory Usage:"
                free -h
                echo "Docker Containers:"
                docker ps -a
                echo "Docker Images:"
                docker images
                echo "Docker System Info:"
                docker system df
            '''
            
            echo "Cleaning up workspace..."
            cleanWs()
            echo "✓ Workspace cleaned"
            
            echo "=== Build Process Completed ==="
        }
        success {
            echo "=== Build Succeeded ==="
            echo "✓ All stages completed successfully"
            echo "✓ Test reports are available in the build artifacts"
        }
        failure {
            echo "=== Build Failed ==="
            echo "ERROR: One or more stages failed"
            echo "WARNING: Please check the build logs for details"
            echo "WARNING: Look for ERROR messages to identify failures"
            echo "WARNING: Check the archived artifacts for detailed logs and reports"
        }
    }
}