# DevOps Mini Project 4: Library Management System Deployment Guide

**Student:** Bhavesh Jagtap  
**PRN:** 2125UDSM1049  
**Degree:** B.Tech Artificial Intelligence and Data Science, Sanjivani University  
**Repository:** [https://github.com/bhaveshjagtap7/Library-Management-System](https://github.com/bhaveshjagtap7/Library-Management-System)  
**Target Cloud:** Amazon Web Services (AWS) — Region `ap-south-1` (Mumbai)  

---

## 1. Project Overview

This project provides an end-to-end DevOps deployment pipeline for the **Enterprise Smart Library Management Platform** using:
- **Python 3 / Flask 3** application with modular REST API and Jinja2 frontend.
- **Docker** containerization with a hardened, multi-stage image running as a non-root user.
- **HashiCorp Terraform** for Infrastructure as Code (IaC) provisioning on AWS (`ap-south-1`).
- **Red Hat Ansible** for configuration management, Docker engine provisioning, and automated container startup.
- **Nginx** reverse proxy configured on port 80 to terminate web traffic and forward to the internal application container on port 5000.
- **Pytest** automated testing suite with 91 unit and integration tests (98% statement coverage).

---

## 2. Directory Structure

```text
library-management-platform/
├── app/                        # Application source code
│   ├── routes/                 # Flask route blueprints (web, api)
│   ├── services/               # Core business logic (library_service.py)
│   └── templates/              # Jinja2 HTML templates
├── static/                     # CSS stylesheets and client JavaScript
├── tests/                      # Automated test suite (91 tests)
├── terraform/                  # Terraform IaC configurations
│   ├── main.tf                 # VPC, Subnet, IGW, Route Table, SG, EC2 instance
│   ├── variables.tf            # AWS region, instance type, restricted SSH CIDR
│   ├── outputs.tf              # Instance ID, Public IP, Public URL
│   └── versions.tf             # Provider constraints (~> 5.0)
├── ansible/                    # Ansible automation playbooks
│   ├── inventory/hosts.ini     # Managed target EC2 host
│   └── playbooks/deploy.yml    # Docker, Nginx, App deployment playbook
├── nginx/                      # Nginx reverse proxy configuration
│   └── library-management.conf
├── documentation/              # Academic report and execution evidence
│   ├── DevOps_Mini_Project_4_Final_Report.docx (45-page comprehensive report)
│   ├── architecture.png        # System architecture diagram
│   ├── test-results.txt        # Verified pytest execution output
│   ├── deployment-status.txt   # Live status and blocker diagnostic
│   ├── generate_word_report.py # Document generation script
│   └── screenshots/            # Real terminal and UI screenshots
├── Dockerfile                  # Multi-stage production container build
├── docker-compose.yml          # Local container composition
└── run.py                      # Application entry point
```

---

## 3. Local Setup & Execution

### Prerequisites
- Python 3.11+ (Python 3.13 supported)
- Git
- Docker Desktop (for container builds)

### Step-by-Step Local Run
```powershell
# 1. Clone repository
git clone https://github.com/bhaveshjagtap7/Library-Management-System.git
cd library-management-platform

# 2. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install production dependencies
pip install -r requirements.txt

# 4. Start local development server
python run.py
# Server binds to http://127.0.0.1:5000/
```

---

## 4. Automated Testing

Run the full pytest suite with statement code coverage:
```powershell
pytest --cov=app tests/
```
**Results Verified:**
- Total Tests: **91 passed**
- Coverage: **98% statement coverage**
- Execution Duration: **~4.71s**

---

## 5. Docker Containerization

### Build Image
```powershell
docker build -t library-management-system:latest .
```

### Run Container Locally
```powershell
docker run -d --name library-app -p 5000:5000 library-management-system:latest
```

### Verify Container Health
```powershell
curl http://127.0.0.1:5000/api/health
# Response: {"service":"Enterprise Smart Library Management Platform","status":"UP","version":"1.0.0"}
```

---

## 6. Terraform AWS Infrastructure Provisioning

All infrastructure is defined declaratively in `terraform/`:

```powershell
cd terraform

# 1. Initialize Terraform providers and backend
terraform init

# 2. Validate syntax and configuration integrity
terraform fmt -check
terraform validate

# 3. Generate execution plan
terraform plan
```

### Security Hardening Applied:
1. **Restricted SSH Ingress:** Port 22 is strictly restricted to the user's specific `/32` IP address (`103.218.102.53/32`). Ingress from `0.0.0.0/0` is explicitly disallowed.
2. **Private Application Port:** Port 5000 is removed from the AWS Security Group. Ingress is restricted to Port 80 (HTTP) and Port 443 (HTTPS). The application binds locally on loopback (`127.0.0.1:5000`) behind the Nginx reverse proxy.
3. **Credentials Shielding:** Private keys, credentials, and state files are excluded from Git via `.gitignore`.

---

## 7. Current AWS Blocker & Resolution Guide

### Diagnosis
Execution of `terraform plan` on AWS Account `029006055983` triggers an authorization failure:
```text
Error: reading EC2 AMIs: operation error EC2: DescribeImages, https response error StatusCode: 403,
api error UnauthorizedOperation: You are not authorized to perform this operation.
User: arn:aws:iam::029006055983:user/bhavesh-devops-deployer is not authorized to perform:
ec2:DescribeImages with an explicit deny in a service control policy:
arn:aws:organizations::021158484728:policy/o-86g05w7f4e/service_control_policy/p-qwhkfd7v
```

### Root Cause
- The member account is part of AWS Organization `o-86g05w7f4e`.
- The management/root account (`021158484728`) has attached Service Control Policy (SCP) `p-qwhkfd7v`.
- In AWS IAM evaluation logic, an **Explicit Deny** in an SCP overrides all IAM policies and cannot be modified or bypassed within member account `029006055983`.

### Action Required by AWS Organization Administrator
1. Sign in to the AWS Management Account (`021158484728`).
2. Navigate to **AWS Organizations** > **Policies** > **Service control policies**.
3. Select policy `p-qwhkfd7v` (`arn:aws:organizations::021158484728:policy/o-86g05w7f4e/service_control_policy/p-qwhkfd7v`).
4. Update the policy statement to permit `ec2:*` in region `ap-south-1` for member account `029006055983`, or detach the restricting SCP from the organizational unit containing account `029006055983`.

---

## 8. Deployment Resumption Once SCP is Cleared

Once the SCP restriction is resolved:
```powershell
# 1. Run Terraform apply
cd terraform
terraform apply -auto-approve

# 2. Note output IP
# e.g., instance_public_ip = "<ACTUAL_EC2_IP>"

# 3. Update Ansible inventory
cd ../ansible
# Set hosts.ini to the real public IP

# 4. Run Ansible deployment playbook
ansible-playbook -i inventory/hosts.ini playbooks/deploy.yml

# 5. Verify live public endpoint
curl http://<ACTUAL_EC2_IP>/api/health
```

---

## 9. Regenerating Academic Word Report

The comprehensive 45-page Word report can be regenerated at any time:
```powershell
python documentation/generate_word_report.py
```
Output files:
- `documentation/DevOps_Mini_Project_4_Final_Report.docx`
- `documentation/DevOps_Mini_Project_4_Library_Management_System_Report.docx`
