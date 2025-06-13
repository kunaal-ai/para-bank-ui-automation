pipeline {
    agent {
        docker {
            image 'mcr.microsoft.com/playwright:v1.42.1-jammy'
            args '-v ${WORKSPACE}:/workspace -w /workspace --ipc=host --shm-size=2g -u root'
            reuseNode true
        }
    }

    environment {
        BASE_URL = 'https://parabank.parasoft.com/parabank/'
        WORKSPACE = '/workspace'
        PLAYWRIGHT_BROWSERS_PATH = '/ms-playwright/'
        PASSWORD = credentials('PARABANK_PASSWORD')
        PYTHONUNBUFFERED = '1'
        REPO_URL = 'https://github.com/kunaal-ai/para-bank-ui-automation.git'
        GITHUB_CREDENTIALS = credentials('github-credentials')
        PYTHONPATH = "${WORKSPACE}:${WORKSPACE}/src"
        // Security scan thresholds
        BANDIT_SEVERITY_THRESHOLD = 'HIGH'
        BANDIT_CONFIDENCE_THRESHOLD = 'HIGH'
    }

    stages {
        stage('Setup') {
            steps {
                sh '''#!/bin/bash -xe
                    set -e
                    echo "=== Installing Python and pip ==="
                    apt-get update || { echo "Failed to update apt"; exit 1; }
                    apt-get install -y python3 python3-pip python3-venv git || { echo "Failed to install dependencies"; exit 1; }
                    
                    echo "=== System Information ==="
                    uname -a
                    python3 --version
                    python3 -m pip --version
                    
                    echo "=== Python Environment ==="
                    python3 -c "import sys; print(f'Python Path: {sys.path}')"
                    
                    echo "=== Installing Python Dependencies ==="
                    python3 -m pip install --upgrade pip setuptools wheel || { echo "Failed to upgrade pip"; exit 1; }
                    
                    # Install requirements if exists
                    if [ -f "requirements.txt" ]; then
                        echo "=== Installing requirements ==="
                        python3 -m pip install -r requirements.txt || { echo "Failed to install requirements"; exit 1; }
                    fi
                    
                    # Install test dependencies
                    echo "=== Installing Test Dependencies ==="
                    python3 -m pip install pytest pytest-html pytest-xdist pytest-playwright pytest-rerunfailures || { echo "Failed to install test dependencies"; exit 1; }
                    
                    echo "=== Installing Playwright ==="
                    python3 -m playwright install --with-deps chromium || { echo "Failed to install Playwright"; exit 1; }
                    
                    echo "=== Verifying Playwright ==="
                    python3 -m playwright --version

                    # Install security scanning tools
                    echo "=== Installing Security Tools ==="
                    python3 -m pip install bandit safety || { echo "Failed to install security tools"; exit 1; }
                '''
            }
        }

        stage('Dependency Scan') {
            steps {
                sh '''
                    echo "=== Running Dependency Security Scan  ==="
                    if [ ! -f requirements.txt ]; then
                        echo "ERROR: requirements.txt not found"
                        exit 1
                    fi
                    
                    echo "Installing security tools..."
                    pip install --no-cache-dir bandit pip-audit
                    
                    echo "Running pip-audit on requirements.txt..."
                    pip-audit --format json -o safety-report.json --requirement requirements.txt || {
                        echo "WARNING: pip-audit found vulnerabilities. Check safety-report.json for details."
                        exit 1
                    }
                '''
            }
        }

        stage('Code Scan') {
            steps {
                sh '''
                    echo "=== Running Code Security Scan ==="
                    
                    echo "Installing security tools..."
                    pip install --no-cache-dir bandit
                    
                    echo "Running Bandit scan..."
                    bandit -r src/ tests/ -f json -o bandit-report.json || {
                        echo "WARNING: Bandit found security issues. Check bandit-report.json for details."
                        exit 1
                    }
                '''
            }
        }

        stage('Clone Repository') {
            steps {
                sh '''#!/bin/bash -xe
                    set -e
                    # Navigate to workspace
                    cd "${WORKSPACE}" || { echo "Failed to change to workspace directory"; exit 1; }
                    
                    echo "=== Current Workspace Contents ==="
                    ls -la
                    
                    echo "=== Cloning Repository ==="
                    # Remove existing contents except .git if it exists
                    if [ -d ".git" ]; then
                        echo "Git repository exists, resetting to remote..."
                        git fetch --all || { echo "Failed to fetch from remote"; exit 1; }
                        git reset --hard origin/main || { echo "Failed to reset to remote branch"; exit 1; }
                        # git pull || { echo "Failed to pull latest changes"; exit 1; }  # No longer needed
                    else
                        echo "No git repository found, cleaning workspace and cloning..."
                        # Create a temporary directory for venv if it exists
                        if [ -d "venv" ]; then
                            mv venv /tmp/venv_backup || { echo "Failed to backup venv"; exit 1; }
                        fi
                        
                        # Clean the workspace
                        rm -rf .[!.]* * 2>/dev/null || true
                        
                        # Clone the repository with credentials
                        git clone https://${GITHUB_CREDENTIALS}@github.com/kunaal-ai/para-bank-ui-automation.git . || { echo "Failed to clone repository"; exit 1; }
                        
                        # Restore venv if it existed
                        if [ -d "/tmp/venv_backup" ]; then
                            rm -rf venv
                            mv /tmp/venv_backup venv || { echo "Failed to restore venv"; exit 1; }
                        fi
                    fi
                    
                    echo "=== Repository Contents After Clone ==="
                    ls -la
                '''
            }
        }

        stage('Verify Repository') {
            steps {
                sh '''#!/bin/bash -xe
                    set -e
                    # Navigate to workspace
                    cd "${WORKSPACE}" || { echo "Failed to change to workspace directory"; exit 1; }
                    
                    echo "=== Repository Structure ==="
                    echo "Working directory: $(pwd)"
                    echo "Contents:"
                    ls -la
                    
                    # Check for required directories
                    for dir in "tests" "src" "src/pages" "src/utils"; do
                        if [ ! -d "$dir" ]; then
                            echo "ERROR: Required directory '$dir' not found!"
                            echo "Current directory contents:"
                            ls -la
                            exit 1
                        fi
                    done
                    
                    echo "=== Tests Directory Contents ==="
                    ls -la tests/
                    
                    echo "=== Source Directory Contents ==="
                    ls -la src/
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''#!/bin/bash -xe
                    set -e
                    # Navigate to workspace
                    cd "${WORKSPACE}" || { echo "Failed to change to workspace directory"; exit 1; }
                    
                    # Run tests
                    echo "=== Running Tests ==="
                    python3 -m pytest \
                        tests/test_*.py \
                        -v \
                        --junitxml=junit.xml \
                        --html=report.html \
                        --self-contained-html \
                        --reruns 1 \
                        --browser=chromium
                '''
            }
        }
    }

    post {
        always {
            echo "Pipeline completed: ${currentBuild.result ?: 'SUCCESS'}"
            
            // Archive test results and security reports
            archiveArtifacts artifacts: 'junit.xml,report.html,safety-report.json,bandit-report.json', allowEmptyArchive: true
            
            // Clean workspace after archiving
            cleanWs()
        }
    }
}