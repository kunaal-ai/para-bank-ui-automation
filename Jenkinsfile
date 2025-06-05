pipeline {
    agent {
        docker {
            image 'python:3.9-slim'
            args '-u root --network=host'
        }
    }
    
    environment {
        // Test results and reports directory
        TEST_RESULTS = 'test-results'
        COVERAGE_REPORT = 'coverage-report'
        
        // Base URL for the application
        BASE_URL = 'https://parabank.parasoft.com/parabank/index.htm'
    }
    
    stages {
        stage('Setup') {
            steps {
                echo 'Setting up environment...'
                sh '''
                    # Update package lists and install system dependencies
                    apt-get update && apt-get install -y --no-install-recommends \
                        curl \
                        git \
                        wget \
                        unzip \
                        xvfb \
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
                        libx11-xcb1

                    # Create test results directory
                    mkdir -p ${TEST_RESULTS} ${COVERAGE_REPORT}
                    
                    # Install Python dependencies
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    
                    # Install Playwright browsers
                    playwright install --with-deps
                    playwright install-deps
                    pip install pytest-cov pylint black
                    
                    # Install Playwright browsers
                    playwright install --with-deps chromium
                    
                '''
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
                sh '''
                    # Start Xvfb for headless browser testing
                    Xvfb :99 -screen 0 1024x768x16 &
                    
                    # Run tests with coverage and generate JUnit XML report
                    python -m pytest \
                        --base-url=${BASE_URL} \
                        --junitxml=${TEST_RESULTS}/junit.xml \
                        --cov=. \
                        --cov-report=xml:${TEST_RESULTS}/coverage.xml \
                        --cov-report=html:${COVERAGE_REPORT} \
                        -v tests/
                    
                    # Generate HTML report for test results
                    python -m junit2html ${TEST_RESULTS}/junit.xml ${TEST_RESULTS}/test-report.html
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
            // Clean up any resources if needed
            sh '''
                # Kill Xvfb if it's still running
                pkill -f Xvfb || true
            '''
            
            // Send notification
            script {
                def buildStatus = currentBuild.currentResult
                def subject = "${buildStatus}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'"
                def details = """
                    <p>${buildStatus}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'</p>
                    <p>Check console output at <a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a></p>
                    <p>Test Results: <a href='${env.BUILD_URL}testReport/'>Test Report</a></p>
                    <p>Coverage Report: <a href='${env.BUILD_URL}Coverage_20Report/'>Coverage Report</a></p>
                """
                
                if (buildStatus == 'SUCCESS') {
                    emailext (
                        subject: subject,
                        body: details,
                        to: 'your-email@example.com',
                        recipientProviders: [[$class: 'DevelopersRecipientProvider']]
                    )
                } else {
                    emailext (
                        subject: subject,
                        body: details,
                        to: 'your-email@example.com',
                        recipientProviders: [
                            [$class: 'DevelopersRecipientProvider'],
                            [$class: 'RequesterRecipientProvider']
                        ]
                    )
                }
            }
        }
    }
}
