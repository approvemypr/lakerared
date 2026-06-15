pipeline {
    agent any

    environment {
        LAKERA_RED_API_KEY   = credentials('red_key')
        TARGET_AGENT_API_KEY = credentials('app_key')
        TARGET_AGENT_URL     = 'https://chentest.app.n8n.cloud/webhook/chat'
        RED_FAIL_THRESHOLD   = '0'
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Setup') {
            steps {
                sh '''
                    if ! command -v python3 >/dev/null 2>&1; then
                        apt-get update && apt-get install -y python3 python3-venv python3-pip
                    fi
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install lakera-red-sdk httpx
                '''
            }
        }

        stage('DAST - Lakera RED Scan') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python red_scan.py
                '''
            }
        }
    }

    post {
        always {
            node(null) {
                archiveArtifacts artifacts: 'red-results.json',
                                 allowEmptyArchive: true
            }
        }
        failure {
            echo 'Lakera RED scan failed or found issues. Check the console output and archived red-results.json.'
        }
    }
}
