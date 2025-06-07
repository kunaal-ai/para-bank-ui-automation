pipeline {
    agent any

    environment {
        DOCKER_COMPOSE = 'docker compose'
        REPO_URL = 'https://github.com/kunaal-ai/para-bank-ui-automation.git'
        GITHUB_CREDENTIALS = credentials('github-credentials')
        PARA_BANK_PASSWORD = credentials('PARABANK_PASSWORD')
        PYTHONPATH = "${WORKSPACE}:${WORKSPACE}/src"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "=== Starting Checkout Stage ==="
                cleanWs()
                echo "✓ Workspace cleaned"
                
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        url: "${REPO_URL}",
                        credentialsId: 'github-credentials'
                    ]]
                ])
                echo "✓ Code checked out successfully"
            }
        }

        stage('Setup Environment Variables') {
            steps {
                echo "=== Setting Up Environment Variables ==="
                sh '''
                    #!/bin/bash
                    set -e
                    
                    echo "Creating .env file..."
                    cat > .env << EOL
                    # ParaBank Test Environment Variables
                    USERNAME=john
                    PASSWORD=${PARA_BANK_PASSWORD}
                    BASE_URL=https://parabank.parasoft.com/parabank/
                    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright/
                    PYTHONUNBUFFERED=1
                    PYTHONDONTWRITEBYTECODE=1
                    DISPLAY=:99
                    PLAYWRIGHT_HEADLESS=true
                    EOL
                    
                    if [ ! -f ".env" ]; then
                        echo "ERROR: Failed to create .env file"
                        exit 1
                    fi
                    echo "✓ .env file created successfully"
                '''
            }
        }

        stage('Validate Environment') {
            steps {
                echo "=== Starting Environment Validation ==="
                sh '''
                    #!/bin/bash
                    set -e
                    
                    echo "Checking Python version..."
                    if ! python3 --version; then
                        echo "ERROR: Python not found or not working"
                        exit 1
                    fi
                    echo "✓ Python version verified"
                    
                    echo "Checking pip version..."
                    if ! pip --version; then
                        echo "ERROR: Pip not found or not working"
                        exit 1
                    fi
                    echo "✓ Pip version verified"
                    
                    echo "Checking Docker version..."
                    if ! docker --version; then
                        echo "ERROR: Docker not found or not working"
                        exit 1
                    fi
                    echo "✓ Docker version verified"
                    
                    echo "Checking Docker Compose version..."
                    if ! docker compose version; then
                        echo "ERROR: Docker Compose not found or not working"
                        exit 1
                    fi
                    echo "✓ Docker Compose version verified"
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
                        exit 1
                    fi
                    chmod -R 777 test-results
                    echo "✓ Test results directory created"
                    
                    echo "Setting up Python virtual environment..."
                    if ! python3 -m venv venv; then
                        echo "ERROR: Failed to create virtual environment"
                        exit 1
                    fi
                    . venv/bin/activate
                    echo "✓ Virtual environment created and activated"
                    
                    echo "Upgrading pip..."
                    if ! pip install --upgrade pip; then
                        echo "ERROR: Failed to upgrade pip"
                        exit 1
                    fi
                    echo "✓ Pip upgraded"
                    
                    echo "Installing project dependencies..."
                    if ! pip install -r requirements.txt; then
                        echo "ERROR: Failed to install project dependencies"
                        exit 1
                    fi
                    echo "✓ Project dependencies installed"
                    
                    echo "Installing project in development mode..."
                    if ! pip install -e .; then
                        echo "ERROR: Failed to install project in development mode"
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
                        exit 1
                    fi
                    echo "✓ Test container built successfully"
                '''
            }
        }

        stage('Run Tests') {
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
                        tests/; then
                        echo "ERROR: Test execution failed"
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
                        exit 1
                    fi
                    echo "✓ Test results directory contents verified"
                    
                    echo "Verifying report files..."
                    if [ ! -f "test-results/report.html" ]; then
                        echo "ERROR: HTML report not found"
                        exit 1
                    fi
                    echo "✓ HTML report generated"
                    
                    if [ ! -f "test-results/junit.xml" ]; then
                        echo "ERROR: JUnit XML report not found"
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
        }
    }
}