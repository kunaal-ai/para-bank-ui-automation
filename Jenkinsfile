pipeline {
    agent {
        docker {
            image 'mcr.microsoft.com/playwright:v1.50.0-jammy'
            args "-v ${env.WORKSPACE}:/workspace -w /workspace --ipc=host --shm-size=2g -u root"
            reuseNode true
        }
    }

    environment {
        // Application settings
        BASE_URL = 'https://parabank.parasoft.com/parabank/'
        CONTAINER_WORKDIR = '/workspace'
        PYTHONPATH = "${CONTAINER_WORKDIR}:${CONTAINER_WORKDIR}/src"

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
        // Note: For stage and prod, you can create separate credentials:
        // PARABANK_STAGE_PASSWORD and PARABANK_PROD_PASSWORD
        // If not set, they will fallback to PARABANK_PASSWORD in the config creation stage

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
                        cd "${CONTAINER_WORKDIR}"

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
                        cd "${CONTAINER_WORKDIR}"

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

        stage('Create Config Files') {
            steps {
                script {
                    // Create config files for all environments
                    // Note: By default, all environments use PARABANK_PASSWORD
                    // To use different passwords for stage/prod, you can:
                    // 1. Create separate Jenkins credentials: PARABANK_STAGE_PASSWORD and PARABANK_PROD_PASSWORD
                    // 2. Modify this stage to use those credentials
                    sh '''
                        #!/bin/bash -xe
                        set -e

                        echo "Creating config files for all environments..."
                        cd "${CONTAINER_WORKDIR}"

                        # Create config directory if it doesn't exist
                        mkdir -p config

                        # Create dev.json
                        echo "Creating config/dev.json..."
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

                        # Create stage.json
                        # Note: Using same password as dev by default
                        # To use different password, create PARABANK_STAGE_PASSWORD credential
                        echo "Creating config/stage.json..."
                        cat > config/stage.json << EOF
{
  "base_url": "https://stage.parabank.parasoft.com/parabank",
  "api_url": "https://stage.parabank.parasoft.com/parabank/api",
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

                        # Create prod.json
                        # Note: Using same password as dev by default
                        # To use different password, create PARABANK_PROD_PASSWORD credential
                        echo "Creating config/prod.json..."
                        cat > config/prod.json << EOF
{
  "base_url": "https://prod.parabank.parasoft.com/parabank",
  "api_url": "https://prod.parabank.parasoft.com/parabank/api",
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

                        echo "All config files created successfully"
                        # Verify the files were created
                        for env in dev stage prod; do
                            if [ ! -f "config/${env}.json" ]; then
                                echo "Error: Failed to create config/${env}.json"
                                exit 1
                            fi
                            echo "Created config/${env}.json"
                        done
                    '''
                }
            }
        }

        stage('Run Tests') {
            parallel {
                stage('Dev Environment') {
                    steps {
                        script {
                            // Run tests against dev environment
                            sh '''
                                #!/bin/bash -xe
                                set -e

                                echo "Running tests against DEV environment..."
                                cd "${CONTAINER_WORKDIR}"

                                # Create test-results directory for dev
                                mkdir -p test-results/dev

                                # Run tests with reporting
                                python3 -m pytest \
                                    tests/test_*.py \
                                    -v \
                                    --env=dev \
                                    --junitxml=test-results/dev/junit.xml \
                                    --html=test-results/dev/report.html \
                                    --self-contained-html \
                                    --reruns 1 \
                                    --browser=chromium || {
                                    echo "WARNING: Some tests failed in DEV environment"
                                    exit 1
                                }

                                echo "DEV environment tests completed"
                            '''
                        }
                    }
                    post {
                        always {
                            // Archive dev test results
                            junit 'test-results/dev/junit.xml'
                            publishHTML(target: [
                                allowMissing: true,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'test-results/dev',
                                reportFiles: 'report.html',
                                reportName: 'DEV Test Results'
                            ])
                        }
                    }
                }

                stage('Stage Environment') {
                    steps {
                        script {
                            // Run tests against stage environment
                            sh '''
                                #!/bin/bash -xe
                                set -e

                                echo "Running tests against STAGE environment..."
                                cd "${CONTAINER_WORKDIR}"

                                # Create test-results directory for stage
                                mkdir -p test-results/stage

                                # Run tests with reporting
                                python3 -m pytest \
                                    tests/test_*.py \
                                    -v \
                                    --env=stage \
                                    --junitxml=test-results/stage/junit.xml \
                                    --html=test-results/stage/report.html \
                                    --self-contained-html \
                                    --reruns 1 \
                                    --browser=chromium || {
                                    echo "WARNING: Some tests failed in STAGE environment"
                                    exit 1
                                }

                                echo "STAGE environment tests completed"
                            '''
                        }
                    }
                    post {
                        always {
                            // Archive stage test results
                            junit 'test-results/stage/junit.xml'
                            publishHTML(target: [
                                allowMissing: true,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'test-results/stage',
                                reportFiles: 'report.html',
                                reportName: 'STAGE Test Results'
                            ])
                        }
                    }
                }

                stage('Prod Environment') {
                    steps {
                        script {
                            // Run tests against prod environment
                            sh '''
                                #!/bin/bash -xe
                                set -e

                                echo "Running tests against PROD environment..."
                                cd "${CONTAINER_WORKDIR}"

                                # Create test-results directory for prod
                                mkdir -p test-results/prod

                                # Run tests with reporting
                                python3 -m pytest \
                                    tests/test_*.py \
                                    -v \
                                    --env=prod \
                                    --junitxml=test-results/prod/junit.xml \
                                    --html=test-results/prod/report.html \
                                    --self-contained-html \
                                    --reruns 1 \
                                    --browser=chromium || {
                                    echo "WARNING: Some tests failed in PROD environment"
                                    exit 1
                                }

                                echo "PROD environment tests completed"
                            '''
                        }
                    }
                    post {
                        always {
                            // Archive prod test results
                            junit 'test-results/prod/junit.xml'
                            publishHTML(target: [
                                allowMissing: true,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'test-results/prod',
                                reportFiles: 'report.html',
                                reportName: 'PROD Test Results'
                            ])
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                // Always archive test results
                echo "Pipeline completed: ${currentBuild.result ?: 'SUCCESS'}"

                // Create the test-results directory if it doesn't exist
                sh 'mkdir -p test-results'

                // Archive JUnit test results from all environments
                script {
                    try {
                        junit 'test-results/**/junit.xml'
                    } catch (Exception e) {
                        echo "WARNING: Failed to archive JUnit results: ${e.getMessage()}"
                        echo "Checking for test result files..."
                        sh '''
                            echo "Current directory: $(pwd)"
                            echo "Looking for junit.xml files..."
                            find test-results -name "junit.xml" -type f 2>/dev/null || echo "No junit.xml files found"
                            if [ -d "test-results" ]; then
                                echo "Contents of test-results directory:"
                                ls -la test-results/ || true
                                for env in dev stage prod; do
                                    if [ -d "test-results/${env}" ]; then
                                        echo "Contents of test-results/${env}:"
                                        ls -la test-results/${env}/ || true
                                    fi
                                done
                            fi
                        '''
                    }
                }

                // Publish HTML reports for each environment
                def environments = ['dev', 'stage', 'prod']
                environments.each { env ->
                    def reportDir = "test-results/${env}"
                    if (fileExists(reportDir)) {
                        publishHTML(target: [
                            allowMissing: true,
                            alwaysLinkToLastBuild: true,
                            keepAll: true,
                            reportDir: reportDir,
                            reportFiles: 'report.html',
                            reportName: "${env.toUpperCase()} Test Results"
                        ])
                    } else {
                        echo "WARNING: Test results directory not found: ${reportDir}"
                    }
                }

                // Publish consolidated HTML report summary
                script {
                    sh '''
                        #!/bin/bash
                        echo "Generating test results summary..."
                        cd "${CONTAINER_WORKDIR}"

                        # Create a summary of test results
                        cat > test-results/summary.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Test Results Summary</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .env-section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .env-section h2 { margin-top: 0; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Test Results Summary - All Environments</h1>
    <div class="env-section">
        <h2>Development Environment</h2>
        <p><a href="dev/report.html">View DEV Test Report</a></p>
    </div>
    <div class="env-section">
        <h2>Staging Environment</h2>
        <p><a href="stage/report.html">View STAGE Test Report</a></p>
    </div>
    <div class="env-section">
        <h2>Production Environment</h2>
        <p><a href="prod/report.html">View PROD Test Report</a></p>
    </div>
</body>
</html>
EOF
                    '''
                }

                // Publish summary HTML report
                publishHTML(target: [
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'test-results',
                    reportFiles: 'summary.html',
                    reportName: 'Test Results Summary (All Environments)'
                ])

                // Clean up workspace if build failed
                if (currentBuild.result == 'FAILURE') {
                    cleanWs()
                }
            }
        }
    }
}
