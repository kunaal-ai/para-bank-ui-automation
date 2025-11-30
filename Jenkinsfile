pipeline {
    agent {
        docker {
            image 'mcr.microsoft.com/playwright:v1.50.0-jammy'
            args '-v ${WORKSPACE}:/workspace -w /workspace --ipc=host --shm-size=2g -u root'
            reuseNode true
        }
    }

    environment {
        // Application settings
        BASE_URL = 'https://parabank.parasoft.com/parabank/'
        WORKSPACE = '/workspace'
        PYTHONPATH = "${WORKSPACE}:${WORKSPACE}/src"
        
        // Playwright settings
        PLAYWRIGHT_BROWSERS_PATH = '/ms-playwright/'
        
        // Security settings
        BANDIT_SEVERITY_THRESHOLD = 'HIGH'
        BANDIT_CONFIDENCE_THRESHOLD = 'HIGH'
        
        // Credentials
        PASSWORD = credentials('PARABANK_PASSWORD')
        GITHUB_CREDENTIALS = credentials('github-credentials')
        // Test user credentials (default username, password from credentials)
        TEST_USERNAME = 'john'
        
        // Python settings
        PYTHONUNBUFFERED = '1'
        REPO_URL = 'https://github.com/kunaal-ai/para-bank-ui-automation.git'
    }

    stages {
        stage('Setup Environment') {
            steps {
                script {
                    // Install system dependencies
                    sh '''
                        #!/bin/bash -xe
                        set -e
                        
                        echo "Installing system dependencies..."
                        apt-get update
                        apt-get install -y python3 python3-pip python3-venv git
                        
                        echo "Setting up Python environment..."
                        python3 -m pip install --upgrade pip setuptools wheel
                        
                        # Install project dependencies if requirements.txt exists
                        if [ -f "requirements.txt" ]; then
                            echo "Installing project dependencies..."
                            pip install -r requirements.txt
                        else
                            # Fallback: Install test dependencies if requirements.txt is missing
                            echo "Installing test dependencies..."
                            pip install pytest pytest-html pytest-xdist pytest-playwright pytest-rerunfailures
                        fi
                        
                        # Setup Playwright
                        echo "Setting up Playwright..."
                        python3 -m playwright install --with-deps chromium
                        python3 -m playwright --version
                    '''
                }
            }
        }

        stage('Security Checks') {
            parallel {
                stage('Dependency Scan') {
                    steps {
                        sh '''
                            echo "Running dependency security scan..."
                            pip install --no-cache-dir pip-audit
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
                            echo "Running code security scan..."
                            pip install --no-cache-dir bandit
                            bandit -r src/ tests/ -f json -o bandit-report.json || {
                                echo "WARNING: Bandit found security issues. Check bandit-report.json for details."
                                exit 1
                            }
                        '''
                    }
                }
            }
        }

        stage('Prepare Repository') {
            steps {
                script {
                    // Clone or update repository
                    sh '''
                        #!/bin/bash -xe
                        set -e
                        
                        echo "Setting up workspace..."
                        cd "${WORKSPACE}"
                        
                        if [ -d ".git" ]; then
                            echo "Updating existing repository..."
                            git fetch --all
                            git reset --hard origin/main
                        else
                            echo "Cloning repository..."
                            git clone "https://${GITHUB_CREDENTIALS}@github.com/kunaal-ai/para-bank-ui-automation.git" .
                        fi
                        
                        echo "Repository ready"
                    '''
                    
                    // Verify repository structure
                    sh '''
                        #!/bin/bash -xe
                        set -e
                        
                        echo "Verifying repository structure..."
                        cd "${WORKSPACE}"
                        
                        # Check for required directories
                        for dir in "tests" "tests/pages" "src/utils"; do
                            if [ ! -d "$dir" ]; then
                                echo "Error: Required directory '$dir' not found"
                                exit 1
                            fi
                        done
                        
                        echo "Repository structure verified"
                    '''
                }
            }
        }

        stage('Create Config File') {
            steps {
                script {
                    // Create dev.json from environment variables and credentials
                    sh '''
                        #!/bin/bash -xe
                        set -e
                        
                        echo "Creating config/dev.json from environment variables..."
                        cd "${WORKSPACE}"
                        
                        # Create config directory if it doesn't exist
                        mkdir -p config
                        
                        # Create dev.json with credentials from Jenkins
                        # Use PASSWORD from Jenkins credentials and default username
                        cat > config/dev.json << EOF
{
  "base_url": "https://parabank.parasoft.com/parabank",
  "api_url": "https://parabank.parasoft.com/parabank/api",
  "browser": "chromium",
  "headless": true,
  "timeout": 30000,
  "users": {
    "valid": {
      "username": "${TEST_USERNAME}",
      "password": "${PASSWORD}"
    },
    "invalid": {
      "username": "invalid",
      "password": "invalid"
    }
  }
}
EOF
                        
                        echo "Config file created successfully"
                        # Verify the file was created
                        if [ ! -f "config/dev.json" ]; then
                            echo "Error: Failed to create config/dev.json"
                            exit 1
                        fi
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Run tests with retries and reporting
                    sh '''
                        #!/bin/bash -xe
                        set -e
                        
                        echo "Running tests..."
                        cd "${WORKSPACE}"
                        
                        python3 -m pytest \
                            tests/test_*.py \
                            -v \
                            --junitxml=test-results/junit.xml \
                            --html=test-results/report.html \
                            --self-contained-html \
                            --reruns 1 \
                            --browser=chromium
                        
                        echo "Tests completed successfully"
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                // Always archive test results
                echo "Pipeline completed: ${currentBuild.result ?: 'SUCCESS'}"
                
                // Archive JUnit test results
                junit '**/junit.xml'
                
                // Publish HTML report
                publishHTML(target: [
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'test-results',
                    reportFiles: 'report.html',
                    reportName: 'Test Results'
                ])
                
                // Clean up workspace if build failed
                if (currentBuild.result == 'FAILURE') {
                    cleanWs()
                }
            }
        }
    }
}