pipeline {
    agent any

    environment {
        APP_NAME    = 'library-management-platform'
        IMAGE_TAG   = "0.${BUILD_NUMBER}"
        VENV_DIR    = '.venv'
        REPORTS_DIR = 'reports'
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
    }

    stages {

        stage('SCM Checkout') {
            steps {
                echo '🔀 Checking out source code…'
                checkout scm
            }
        }

        stage('Environment Setup & Dependencies') {
            steps {
                echo '📦 Setting up Python virtual environment and installing dependencies…'
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    mkdir -p ${REPORTS_DIR}
                '''
            }
        }

        stage('Code Linting & Syntax Gate') {
            steps {
                echo '🔍 Running Flake8 linting…'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    flake8 app/ database/ tests/ run.py \
                        --max-line-length=120 \
                        --exclude=__pycache__,.venv,venv \
                        --statistics \
                        --count
                '''
            }
        }

        stage('Automated Unit & Integration Tests') {
            steps {
                echo '🧪 Running Pytest with coverage…'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pytest -v \
                        --cov=app \
                        --cov-report=term-missing \
                        --cov-report=html:${REPORTS_DIR}/coverage \
                        --junitxml=${REPORTS_DIR}/test-results.xml \
                        tests/
                '''
            }
            post {
                always {
                    junit "${REPORTS_DIR}/test-results.xml"
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: "${REPORTS_DIR}/coverage",
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }

        stage('Build Docker Artifact') {
            steps {
                echo "🐳 Building Docker image ${APP_NAME}:${IMAGE_TAG}…"
                sh '''
                    docker build \
                        -t ${APP_NAME}:${IMAGE_TAG} \
                        -t ${APP_NAME}:latest \
                        .
                    echo "✅ Docker image built: ${APP_NAME}:${IMAGE_TAG}"
                    docker image ls ${APP_NAME}
                '''
            }
        }

        stage('Kubernetes Minikube Deployment') {
            steps {
                echo '☸️  Deploying to Kubernetes / Minikube…'
                sh '''
                    # Update image tag in deployment
                    sed -i "s|image: ${APP_NAME}.*|image: ${APP_NAME}:${IMAGE_TAG}|g" k8s/deployment.yaml

                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml

                    echo "⏳ Waiting for rollout to complete…"
                    kubectl rollout status deployment/library-deployment --timeout=120s

                    echo "📊 Deployment status:"
                    kubectl get pods -l app=library-platform
                    kubectl get services library-service
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
            archiveArtifacts artifacts: "${REPORTS_DIR}/**", fingerprint: true
        }
        failure {
            echo '❌ Pipeline failed. Check the logs above.'
        }
        always {
            echo '🧹 Cleaning workspace…'
            cleanWs()
        }
    }
}
