pipeline {
    agent {
        docker {
            image 'python:3.12-slim'
            // 如果需要走代理出站,可在这里传环境变量或挂载配置
            args '-e HTTPS_PROXY -e HTTP_PROXY -e NO_PROXY'
        }
    }

    environment {
        LAKERA_RED_API_KEY = credentials('red_key')
        TARGET_AGENT_URL   = 'https://chentest.app.n8n.cloud/webhook/chat'
        RED_FAIL_THRESHOLD = '0'
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
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install lakera-red-sdk
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
            archiveArtifacts artifacts: 'red-results.json',
                             allowEmptyArchive: true
        }
        failure {
            echo 'Lakera RED found security issues above threshold. Check archived red-results.json.'
        }
    }
}
