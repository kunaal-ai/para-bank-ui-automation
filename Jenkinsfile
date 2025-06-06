pipeline {
    agent {
        docker {
            image 'mcr.microsoft.com/playwright:v1.42.1-jammy'
            args '--ipc=host --shm-size=2g -u root'
            reuseNode true
        }
    }

    environment {
        BASE_URL = 'https://parabank.parasoft.com/parabank/'
        DISPLAY = ':99'
        PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = '1'
        PASSWORD = credentials('PARABANK_PASSWORD')
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                // Checkout code from SCM
                checkout scm
                
                sh '''
                    echo "Workspace after checkout:"
                    ls -la
                    echo "Tests directory contents:"
                    ls -la tests/ || echo "Tests directory not found yet"
                '''
            }
        }

        stage('Setup') {
            steps {
                sh '''
                    # Install Python and pip
                    apt-get update -qq
                    apt-get install -y python3-pip
                    
                    # Install testing dependencies
                    pip3 install playwright pytest pytest-html
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    # Start headless display
                    Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset > /tmp/xvfb.log 2>&1 &
                    XPID=$!
                    
                    # Verify tests directory exists
                    if [ ! -d "tests" ]; then
                        echo "ERROR: tests directory not found!"
                        echo "Current workspace contents:"
                        ls -la
                        echo "Creating tests directory structure for debugging"
                        mkdir -p tests
                        echo "import pytest" > tests/test_sample.py
                    fi
                    
                    # Run tests
                    echo "Running tests from: $(pwd)"
                    python3 -m pytest tests/ \
                        -v \
                        --junitxml=test-results/junit.xml \
                        --html=test-results/report.html \
                        --self-contained-html
                    
                    # Stop display server
                    kill $XPID
                '''
            }
            post {
                always {
                    junit 'test-results/junit.xml'
                    archiveArtifacts artifacts: 'test-results/report.html', allowEmptyArchive: true
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline completed: ${currentBuild.result ?: 'SUCCESS'}"
            sh 'pkill -f "Xvfb :99" || true'
            archiveArtifacts artifacts: '**/playwright-traces/*.zip,**/test-results/*.png', allowEmptyArchive: true
            deleteDir()
        }
    }
}
