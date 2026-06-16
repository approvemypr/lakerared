pipeline {
    agent any

    environment {
        // 非敏感配置放这里
        TARGET_AGENT_URL   = 'https://chentest.app.n8n.cloud/webhook/chat'
        RED_FAIL_THRESHOLD = '0'
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
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
                    pip install "lakera-red-sdk[yaml]" httpx
                '''
            }
        }

        stage('DAST - Lakera RED Scan') {
            steps {
                withCredentials([
                    string(credentialsId: 'red_key', variable: 'red_key'),
                    string(credentialsId: 'app_key', variable: 'app_key')
                ]) {
                    sh '''
                        . .venv/bin/activate
                        python red_scan.py
                    '''
                }
                archiveArtifacts artifacts: 'red-results.json', allowEmptyArchive: true
            }
        }
    }

}
