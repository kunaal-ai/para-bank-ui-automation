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
        BASE_URL = 'https://parabank.parasoft.com/parabank/index.htm'
        // Docker settings
        DOCKER_HOST = 'unix:///var/run/docker.sock'
        DOCKER_BUILDKIT = '1'
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
                    
                    # Create and activate virtual environment
                    python3 -m venv venv
                    source venv/bin/activate
                    
                    # Upgrade pip and install Python dependencies
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    
                    # Install Playwright and browsers
                    pip install playwright
                    playwright install --with-deps
                    
                    # Create test directories
                    mkdir -p ${TEST_RESULTS} ${COVERAGE_REPORT}
                    
                    # Verify installations
                    echo "=== Environment Setup Complete ==="
                    echo "Python: $(python3 --version)"
                    echo "Pip: $(pip --version)"
                    echo "Playwright: $(playwright --version)"
                    echo "Docker: $(docker --version)"
                    echo "Docker Compose: $(docker-compose --version)"'''
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
                BASE_URL = 'https://parabank.parasoft.com/parabank/index.htm'
                // Make sure the display is set for headless browser testing
                DISPLAY = ':99'
            }
            
            steps {
                echo 'Running tests...'
                sh '''#!/bin/bash -l
                    # Activate virtual environment
                    source venv/bin/activate
                    
                    # Start Xvfb for headless browser testing
                    Xvfb :99 -screen 0 1024x768x16 &
                    
                    # Run tests with coverage
                    set +e  # Don't fail immediately if tests fail
                    python -m pytest tests/ \
                        --junitxml=${TEST_RESULTS}/junit.xml \
                        --cov=. \
                        --cov-report=xml:${COVERAGE_REPORT}/coverage.xml \
                        --cov-report=html:${COVERAGE_REPORT}/
                    
                    # Capture the exit code
                    TEST_EXIT_CODE=$?
                    
                    # Generate HTML report
                    python -m pytest tests/ --html=${TEST_RESULTS}/report.html --self-contained-html || true
                    
                    # Exit with the test status
                    exit $TEST_EXIT_CODE
                '''
            }
            
            post {
                always {
                    // Archive test results and coverage report
                    junit allowEmptyResults: true, testResults: '${TEST_RESULTS}/*.xml'
                    publishHTML(target: [
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '${TEST_RESULTS}',
                        reportFiles: 'test-report.html',
                        reportName: 'Test Report'
                    ])
                    publishHTML(target: [
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '${COVERAGE_REPORT}',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                    
                    // Publish coverage report to Codacy (if configured)
                    withCredentials([string(credentialsId: 'codacy-project-token', variable: 'CODACY_PROJECT_TOKEN')]) {
                        sh '''
                            # Install codacy-coverage-reporter if not installed
                            if ! command -v codacy-coverage-reporter &> /dev/null; then
                                curl -Ls https://coverage.codacy.com/get.sh | bash
                            fi
                            
                            # Upload coverage report to Codacy
                            codacy-coverage-reporter report -l python -r ${TEST_RESULTS}/coverage.xml || echo "Failed to upload to Codacy"
                        '''
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
            
            // Clean up Xvfb process
            sh 'pkill -f Xvfb || true'
            
            // Publish test results and coverage
            script {
                // Publish JUnit test results
                junit allowEmptyResults: true, testResults: 'test-results/junit.xml'
                
                // Publish HTML test report
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'test-results',
                    reportFiles: 'report.html',
                    reportName: 'Test Report'
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
