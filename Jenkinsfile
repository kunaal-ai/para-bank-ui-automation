pipeline {
    agent {
        docker {
            image 'mcr.microsoft.com/playwright:v1.50.0-jammy'
            args '--ipc=host --shm-size=2g -u root'
            reuseNode true
        }
    }

    parameters {
        booleanParam(name: 'RUN_STAGE_TESTS', defaultValue: false, description: 'Run UI tests against STAGE environment')
        booleanParam(name: 'RUN_PROD_TESTS', defaultValue: false, description: 'Run UI tests against PROD environment')
    }

    environment {
        // Application settings
        BASE_URL = 'https://parabank.parasoft.com/parabank/'
        PYTHONPATH = "$WORKSPACE:$WORKSPACE/src"

        // Playwright settings
        PLAYWRIGHT_BROWSERS_PATH = '/ms-playwright/'

        // Security settings
        BANDIT_SEVERITY_THRESHOLD = 'HIGH'
        BANDIT_CONFIDENCE_THRESHOLD = 'HIGH'

        // Credentials
        PASSWORD = credentials('PARABANK_PASSWORD')
        GITHUB_CREDENTIALS = credentials('github-credentials')
        TEST_USERNAME = 'john'

        // Python settings
        PYTHONUNBUFFERED = '1'
        REPO_URL = 'https://github.com/kunaal-ai/para-bank-ui-automation.git'
    }

    stages {
        stage('Setup Environment') {
            steps {
                script {
                    sh '''
                        #!/bin/bash -xe
                        set -e
                        apt-get update
                        apt-get install -y python3 python3-pip python3-venv git
                        python3 -m pip install --upgrade pip setuptools wheel
                        if [ -f "requirements.txt" ]; then
                            pip install -r requirements.txt
                        else
                            pip install pytest pytest-html pytest-xdist pytest-playwright pytest-rerunfailures
                        fi
                        python3 -m playwright install --with-deps
                    '''
                }
            }
        }

        stage('Security Checks') {
            parallel {
                stage('Dependency Scan') {
                    steps {
                        sh '''
                            pip install --no-cache-dir pip-audit
                            pip-audit --format json -o safety-report.json --requirement requirements.txt || true
                        '''
                    }
                }
                stage('Code Scan') {
                    steps {
                        sh '''
                            pip install --no-cache-dir bandit
                            bandit -r src/ tests/ -f json -o bandit-report.json || true
                        '''
                    }
                }
            }
        }

        stage('Create Config Files') {
            steps {
                script {
                    sh '''
                        mkdir -p config

                        create_config() {
                            local env=$1
                            local url=$2
                            cat > config/${env}.json << EOF
{
  "base_url": "${url}",
  "api_url": "${url}/api",
  "browser": "chromium",
  "headless": true,
  "timeout": 30000,
  "users": {
    "valid": { "username": "${TEST_USERNAME}", "password": "${PASSWORD}" },
    "invalid": { "username": "invalid", "password": "invalid" }
  }
}
EOF
                        }

                        create_config "dev" "https://parabank.parasoft.com/parabank"
                        create_config "stage" "https://stage.parabank.parasoft.com/parabank"
                        create_config "prod" "https://prod.parabank.parasoft.com/parabank"
                    '''
                }
            }
        }

        stage('Run Tests') {
            parallel {
                stage('Dev Environment') {
                    parallel {
                        stage('Chromium') { steps { script { runBrowserTest('dev', 'chromium') } } }
                        stage('Firefox') { steps { script { runBrowserTest('dev', 'firefox') } } }
                        stage('Webkit') { steps { script { runBrowserTest('dev', 'webkit') } } }
                    }
                    post { always { publishEnvironmentResults('dev') } }
                }

                stage('Stage Environment') {
                    when { expression { params.RUN_STAGE_TESTS } }
                    parallel {
                        stage('Chromium') { steps { script { runBrowserTest('stage', 'chromium') } } }
                        stage('Firefox') { steps { script { runBrowserTest('stage', 'firefox') } } }
                        stage('Webkit') { steps { script { runBrowserTest('stage', 'webkit') } } }
                    }
                    post { always { publishEnvironmentResults('stage') } }
                }

                stage('Prod Environment') {
                    when { expression { params.RUN_PROD_TESTS } }
                    parallel {
                        stage('Chromium') { steps { script { runBrowserTest('prod', 'chromium') } } }
                        stage('Firefox') { steps { script { runBrowserTest('prod', 'firefox') } } }
                        stage('Webkit') { steps { script { runBrowserTest('prod', 'webkit') } } }
                    }
                    post { always { publishEnvironmentResults('prod') } }
                }
            }
        }
    }

    post {
        always {
            script {
                sh 'mkdir -p test-results'
                try {
                    junit 'test-results/**/junit.xml'
                } catch (e) {
                    echo "No JUnit results found to archive."
                }

                // Consolidate summary
                sh '''
                    cat > test-results/summary.html << 'EOF'
<!DOCTYPE html><html><head><title>Test Summary</title><style>body{font-family:sans-serif;margin:20px}.env{margin-bottom:20px;padding:10px;border:1px solid #ddd}</style></head>
<body><h1>Cross-Browser Test Results</h1>
<div class="env"><h2>Dev</h2><ul><li><a href="dev/chromium/report.html">Chromium</a></li><li><a href="dev/firefox/report.html">Firefox</a></li><li><a href="dev/webkit/report.html">Webkit</a></li></ul></div>
<div class="env"><h2>Stage</h2><ul><li><a href="stage/chromium/report.html">Chromium</a></li><li><a href="stage/firefox/report.html">Firefox</a></li><li><a href="stage/webkit/report.html">Webkit</a></li></ul></div>
<div class="env"><h2>Prod</h2><ul><li><a href="prod/chromium/report.html">Chromium</a></li><li><a href="prod/firefox/report.html">Firefox</a></li><li><a href="prod/webkit/report.html">Webkit</a></li></ul></div>
</body></html>
EOF
                '''
                publishHTML(target: [
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'test-results',
                    reportFiles: 'summary.html',
                    reportName: 'Final Test Summary'
                ])
            }
        }
    }
}

def runBrowserTest(env, browser) {
    sh """
        mkdir -p test-results/${env}/${browser}
        python3 -m pytest tests/test_*.py -v --env=${env} \
            --junitxml=test-results/${env}/${browser}/junit.xml \
            --html=test-results/${env}/${browser}/report.html \
            --self-contained-html --reruns 1 --browser=${browser} || true
    """
}

def publishEnvironmentResults(env) {
    junit "test-results/${env}/**/junit.xml"
    publishHTML(target: [
        allowMissing: true,
        alwaysLinkToLastBuild: true,
        keepAll: true,
        reportDir: "test-results/${env}",
        reportFiles: "**/report.html",
        reportName: "${env.toUpperCase()} Results"
    ])
}
