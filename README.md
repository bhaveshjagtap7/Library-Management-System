# 📚 Enterprise Smart Library Management Platform

A production-ready library management system built with Python 3 + Flask 3, featuring a full REST API, interactive web dashboard, automated tests, Docker containerization, Kubernetes orchestration, and a Jenkins CI/CD pipeline.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flask Application                        │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │  Frontend  │  │  REST API    │  │  Library Service   │  │
│  │  (Jinja2)  │  │  Blueprint   │  │  (Business Logic)  │  │
│  └────────────┘  └──────────────┘  └────────────────────┘  │
│                                    ┌────────────────────┐  │
│                                    │  Thread-safe DB    │  │
│                                    │  (In-memory)       │  │
│                                    └────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Features

- **Book Catalog** — Add, search (title/author/ISBN), view, borrow
- **User Management** — Add students/faculty, delete (only if no active loans)
- **Loan Tracking** — Borrow/return with full history, status badges
- **Business Rules** — Student max 3 loans, Faculty max 5, inventory guards
- **Dashboard** — Live stats: total books, copies, users, active/returned loans
- **REST API** — 12 endpoints with proper HTTP codes and JSON responses
- **Automated Tests** — 91 tests, 97% coverage
- **Docker** — Multi-stage build, non-root user, health check
- **Kubernetes** — 3 replicas, RollingUpdate, liveness/readiness probes
- **Jenkins** — 5-stage declarative pipeline

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3 (3.11+ recommended) |
| Web Framework | Flask 3.0.3 |
| WSGI | Gunicorn 22.0 |
| Testing | Pytest 8.3 + pytest-cov |
| Linting | Flake8 7.1 |
| Containerization | Docker (python:3.11-slim) |
| Orchestration | Kubernetes / Minikube |
| CI/CD | Jenkins (Declarative Pipeline) |

## Repository Structure

```
library-management-platform/
├── app/
│   ├── __init__.py          # Application factory (create_app)
│   ├── routes/
│   │   ├── api.py           # REST API blueprint (/api/*)
│   │   └── frontend.py      # Frontend page routes
│   ├── services/
│   │   └── library_service.py  # All business logic
│   ├── models/
│   │   ├── book.py          # Book dataclass
│   │   └── user.py          # User dataclass
│   └── templates/           # Jinja2 HTML templates
│       ├── base.html
│       ├── dashboard.html
│       ├── books.html
│       ├── users.html
│       └── loans.html
├── database/
│   └── db.py                # Thread-safe singleton in-memory DB
├── tests/
│   ├── test_user_service.py
│   ├── test_book_service.py
│   ├── test_borrow_return.py
│   └── test_api_endpoints.py
├── k8s/
│   ├── deployment.yaml      # 3-replica Deployment + probes
│   └── service.yaml         # NodePort service (port 30080)
├── static/
│   ├── css/style.css
│   └── js/app.js
├── reports/                 # JUnit XML + coverage HTML
├── Jenkinsfile              # 5-stage CI/CD pipeline
├── Dockerfile               # Multi-stage, non-root
├── .dockerignore
├── .gitignore
├── requirements.txt
├── setup.cfg                # Flake8 configuration
├── run.py                   # Entry point
└── README.md
```

---

## Local Installation

### Prerequisites
- Python 3.11+ (or 3.14+ works too)
- Git

### Setup

```bash
git clone <repo-url>
cd library-management-platform

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Application

```bash
python run.py
```

Open your browser: **http://localhost:5000**

---

## Running Tests

```bash
# Run all tests with coverage
pytest -v --cov=app --cov-report=term-missing --junitxml=reports/test-results.xml tests/

# Run specific test file
pytest tests/test_borrow_return.py -v

# Coverage HTML report
pytest --cov=app --cov-report=html:reports/coverage tests/
```

**Results:** 91 tests, **97% coverage**

## Code Linting

```bash
flake8 app/ database/ tests/ run.py --max-line-length=120
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check (status UP) |
| GET | `/api/dashboard` | Aggregate statistics |
| GET | `/api/users` | List all users |
| POST | `/api/users` | Create user |
| GET | `/api/users/<id>` | Get user by ID |
| DELETE | `/api/users/<id>` | Delete user (no active loans) |
| GET | `/api/books` | List/search books (`?q=devops`) |
| POST | `/api/books` | Add book |
| GET | `/api/books/<id>` | Get book by ID |
| GET | `/api/loans` | List all loans |
| POST | `/api/borrow` | Borrow a book |
| POST | `/api/return` | Return a book |

### Example Requests

```bash
# Health check
curl http://localhost:5000/api/health

# Search books
curl "http://localhost:5000/api/books?q=cloud"

# Create user
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"user_id":"U200","name":"Grace Hopper","email":"grace@navy.mil","role":"Faculty"}'

# Borrow book
curl -X POST http://localhost:5000/api/borrow \
  -H "Content-Type: application/json" \
  -d '{"user_id":"U101","book_id":"B001"}'

# Return book
curl -X POST http://localhost:5000/api/return \
  -H "Content-Type: application/json" \
  -d '{"user_id":"U101","book_id":"B001"}'
```

---

## Docker

### Build Image

```bash
docker build -t library-management-platform:0.0 .
```

### Run Container

```bash
docker run -d -p 5000:5000 --name library-app library-management-platform:0.0
```

### Verify Health Check

```bash
curl http://localhost:5000/api/health
# {"status":"UP","service":"Enterprise Smart Library Management Platform","version":"1.0.0"}

# Check Docker health status
docker inspect --format='{{.State.Health.Status}}' library-app
```

### Stop Container

```bash
docker stop library-app && docker rm library-app
```

---

## Kubernetes / Minikube

### Prerequisites
- Minikube installed
- kubectl installed

### Deploy

```bash
# Start Minikube
minikube start --driver=docker

# Load local Docker image into Minikube (if not using registry)
minikube image load library-management-platform:0.0

# Apply manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Verify 3 replicas are running
kubectl get pods -l app=library-platform

# Verify rollout
kubectl rollout status deployment/library-deployment

# Get service URL
minikube service library-service --url
# OR access directly: http://<minikube-ip>:30080
```

### Self-Healing Test

```bash
# Delete a pod — Kubernetes will recreate it automatically
kubectl delete pod <pod-name>
kubectl get pods -l app=library-platform -w
```

### Cleanup

```bash
kubectl delete -f k8s/deployment.yaml
kubectl delete -f k8s/service.yaml
```

---

## Jenkins CI/CD

### Pipeline Stages

1. **SCM Checkout** — Clone/checkout the repository
2. **Environment Setup & Dependencies** — Create venv, `pip install`
3. **Code Linting & Syntax Gate** — Flake8 (fails build if violations)
4. **Automated Unit & Integration Tests** — Pytest + JUnit XML + coverage
5. **Build Docker Artifact** — `docker build` tagged with `BUILD_NUMBER`
6. **Kubernetes Minikube Deployment** — `kubectl apply` + rollout verify

### Setup

1. Install Jenkins with Pipeline and HTML Publisher plugins
2. Create a new Pipeline job
3. Set **Pipeline definition** → **Pipeline script from SCM**
4. Point to your repository — Jenkins will detect `Jenkinsfile` automatically

---

## Demo Data

The system starts with seeded data:

**Users:**
| ID | Name | Email | Role |
|----|------|-------|------|
| U101 | Alice Johnson | alice@university.edu | Student |
| U102 | Dr. Robert Smith | robert.smith@university.edu | Faculty |

**Books:**
| ID | Title | Author | ISBN | Copies |
|----|-------|--------|------|--------|
| B001 | Cloud Native DevOps Architecture | Linus Torvalds | 978-0134685991 | 5 |
| B002 | Continuous Delivery Principles | Jez Humble & David Farley | 978-0321601919 | 3 |

**Business Rules:**
- Students: max **3** active loans
- Faculty: max **5** active loans
- Inventory never goes negative
- Users with active loans cannot be deleted

---

## URLs

| Service | URL |
|---------|-----|
| Dashboard (local) | http://localhost:5000 |
| Books page | http://localhost:5000/books |
| Users page | http://localhost:5000/users |
| Loans page | http://localhost:5000/loans |
| Health endpoint | http://localhost:5000/api/health |
| Kubernetes NodePort | http://\<minikube-ip\>:30080 |

---

## Troubleshooting

**App won't start:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check port 5000 is not already in use: `netstat -an | grep 5000`

**Tests failing:**
- Ensure you are in the project root directory
- Run `pip install -r requirements.txt` first

**Docker build fails:**
- Ensure Docker Desktop is running
- Try: `docker system prune` and rebuild

**Minikube pods not healthy:**
- Run `kubectl describe pod <pod-name>` to see events
- Ensure the image is available inside Minikube: `minikube image ls`
- Load image: `minikube image load library-management-platform:0.0`
