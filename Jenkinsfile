pipeline {
    agent {
        docker {
            image 'python:3.9-slim'
            args '-v /var/run/docker.sock:/var/run/docker.sock -u root --privileged'
            reuseNode true
        }
    }
    
    environment {
        // Use a consistent Python version
        PYTHONUNBUFFERED = '1'
        // Test results and reports directory
        TEST_RESULTS = 'test-results'
        COVERAGE_REPORT = 'coverage-report'
        // Base URL for the application
        BASE_URL = 'https://parabank.parasoft.com/parabank/'
        TEST_BASE_URL = 'https://parabank.parasoft.com/parabank/'
        // Docker settings
        DOCKER_HOST = 'unix:///var/run/docker.sock'
        DOCKER_BUILDKIT = '1'
        // Playwright settings - use system browsers
        PLAYWRIGHT_BROWSERS_PATH = '0'
        PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = '1'
        
        // Load credentials from Jenkins
        // These will be available as environment variables in the container
        PASSWORD = credentials('PARABANK_PASSWORD')
    }
    
    stages {
        stage('Setup') {
            steps {
                echo 'Setting up environment...'
                sh '''#!/bin/bash -l
                    # Update and install system dependencies
                    apt-get update && apt-get install -y --no-install-recommends \
                        python3 \
                        python3-pip \
                        python3-venv \
                        libnss3 \
                        libnspr4 \
                        libatk1.0-0 \
                        libatk-bridge2.0-0 \
                        libcups2 \
                        libdrm2 \
                        libxkbcommon0 \
                        libxcomposite1 \
                        libxdamage1 \
                        libxfixes3 \
                        libxrandr2 \
                        libgbm1 \
                        libasound2 \
                        libatspi2.0-0 \
                        libx11-xcb1 \
                        xvfb \
                        && rm -rf /var/lib/apt/lists/*
                    
                    # Create virtual environment if it doesn't exist
                    if [ ! -d "venv" ]; then
                        python3 -m venv venv
                    fi
                    
                    # Activate virtual environment using dot operator
                    . venv/bin/activate
                    
                    # Upgrade pip and install Python dependencies
                    python -m pip install --upgrade pip
                    python -m pip install -r requirements.txt
                    
                    # Install Playwright and browsers
                    python -m pip install playwright
                    python -m playwright install --with-deps
                    
                    # Create test directories
                    mkdir -p "${TEST_RESULTS}" "${COVERAGE_REPORT}"
                    
                    # Verify installations
                    echo "=== Environment Setup Complete ==="
                    echo "Python: $(which python)"
                    echo "Python version: $(python --version)"
                    echo "Pip: $(which pip)"
                    echo "Pip version: $(pip --version)"
                    echo "Playwright: $(python -m playwright --version)"
                    echo "Docker: $(which docker)"
                    echo "Docker version: $(docker --version)"
                    echo "Docker Compose: $(which docker-compose || echo 'Not found')"'''
            }
        }
        
        stage('Lint') {
            steps {
                echo 'Running linting...'
                sh '''
                    # Run pylint
                    pylint --output-format=parseable \
                           --reports=no \
                           --rcfile=.pylintrc \
                           pages/ tests/ > ${TEST_RESULTS}/pylint.txt || true
                    
                    # Run black in check mode
                    black --check --diff --color pages/ tests/ > ${TEST_RESULTS}/black.txt || true
                '''
            }
        }
        
        stage('Test') {
            environment {
                // Test-specific environment variables
                BASE_URL = 'https://parabank.parasoft.com/parabank/'
                // Make sure the display is set for headless browser testing
                // PASSWORD is already available from the global environment
                DISPLAY = ':99'
                // Define directories relative to workspace
                TEST_RESULTS = 'test-results'
                COVERAGE_REPORT = 'coverage-report'
            }
            
            steps {
                script {
                    // Create directories for test results and coverage reports
                    sh '''
                    mkdir -p "${WORKSPACE}/test-results"
                    mkdir -p "${WORKSPACE}/coverage-report/html"
                    '''
                    
                    // Run tests with coverage and generate reports
                    withEnv(["WORKSPACE=${env.WORKSPACE}"]) {
                        try {
                            sh '''
                            #!/bin/sh
                            set -e
                            cd "${WORKSPACE}"
                            . venv/bin/activate  # Using dot operator instead of source
                            
                            # Verify Python and pip
                            echo "Using Python: $(which python)"
                            echo "Python version: $(python --version)"
                            
                            # Start Xvfb for headless browser testing
                            Xvfb :99 -screen 0 1024x768x16 &
                            export DISPLAY=:99
                            
                            # Verify Xvfb is running
                            echo "Xvfb process: $(ps aux | grep Xvfb)"
                            
                            # Run pytest with coverage and reporting
                            python -m pytest tests/ \
                                --junitxml="${WORKSPACE}/test-results/junit.xml" \
                                --html="${WORKSPACE}/test-results/report.html" \
                                --self-contained-html \
                                --cov=./ \
                                --cov-report=xml:"${WORKSPACE}/coverage-report/coverage.xml" \
                                --cov-report=html:"${WORKSPACE}/coverage-report/html" \
                                -v
                            '''
                        } finally {
                            // Archive test results and reports
                            junit allowEmptyResults: true, testResults: '**/junit.xml'
                            
                            // Archive HTML reports
                            archiveArtifacts artifacts: 'test-results/**,coverage-report/**', allowEmptyArchive: true
                            
                            // Publish HTML test report
                            publishHTML(target: [
                                allowMissing: true,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'test-results',
                                reportFiles: 'report.html',
                                reportName: 'Test Report',
                                reportTitles: 'Test Results'
                            ])
                            
                            // Publish coverage report
                            publishHTML(target: [
                                allowMissing: true,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'coverage-report/html',
                                reportFiles: 'index.html',
                                reportName: 'Coverage Report',
                                reportTitles: 'Code Coverage'
                            ])
                        }
                    }
                }
            }
        }
        
        stage('Publish Metrics') {
            steps {
                echo 'Publishing metrics to Prometheus...'
                // This would be handled by the metrics_pusher.py in your tests
                // or you can add specific metrics collection here
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'main'  // Only run this stage on main branch
            }
            steps {
                echo 'Deploying to staging environment...'
                // Add your deployment steps here
                // Example: Deploy to a staging server or Kubernetes cluster
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed.'
            
            script {
                // Clean up Xvfb process
                sh 'pkill -f Xvfb || true'
                
                // Archive any remaining test artifacts
                archiveArtifacts artifacts: '**/target/*.jar,**/target/*.war,**/target/*.zip', allowEmptyArchive: true
                
                // Archive test results and coverage reports
                junit allowEmptyResults: true, testResults: '**/test-results/*.xml'
                
                // Archive HTML reports
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'test-results',
                    reportFiles: 'report.html',
                    reportName: 'Test Report',
                    reportTitles: 'Test Results'
                ])
                
                // Archive coverage reports
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'coverage-report/html',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report',
                    reportTitles: 'Code Coverage'
                ])
                
                // Publish coverage report
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'coverage-report',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report'
                ])
                
                // Clean up any remaining processes
                sh 'pkill -f Xvfb || true'
            }
        }
    }
}
