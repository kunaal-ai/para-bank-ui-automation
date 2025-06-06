pipeline {
    agent any

    environment {
        DOCKER_COMPOSE = 'docker compose'
        REPO_URL = 'https://github.com/kunaal-ai/para-bank-ui-automation.git'
        GITHUB_CREDENTIALS = credentials('github-credentials')
        PYTHONPATH = "${WORKSPACE}:${WORKSPACE}/src"
    }

    stages {
        stage('Checkout') {
            steps {
                cleanWs()
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        url: "${REPO_URL}",
                        credentialsId: 'github-credentials'
                    ]]
                ])
            }
        }

        stage('Setup Environment') {
            steps {
                sh '''
                    #!/bin/bash
                    set -e
                    
                    # Create necessary directories
                    mkdir -p test-results
                    chmod -R 777 test-results
                    
                    # Set up Python environment
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install -e .
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    #!/bin/bash
                    set -e
                    
                    # Run tests with Docker Compose
                    ${DOCKER_COMPOSE} build test
                    ${DOCKER_COMPOSE} run --rm test
                '''
            }
        }
    }

    post {
        always {
            // Archive test results
            junit 'test-results/*.xml'
            archiveArtifacts artifacts: 'test-results/*.html', allowEmptyArchive: true
            
            // Clean up
            cleanWs()
        }
    }
}