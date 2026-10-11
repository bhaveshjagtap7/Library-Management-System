"""Generate architecture diagrams and illustrations for DevOps Mini Project 4."""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs('documentation/figures', exist_ok=True)

# 1. System Architecture Diagram
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis('off')

# Background container
bg = patches.FancyBboxPatch((0.5, 0.5), 9.0, 5.0, boxstyle="round,pad=0.2", ec="#cbd5e1", fc="#f8fafc", lw=1.5)
ax.add_patch(bg)
ax.text(0.8, 5.2, "AWS Cloud — ap-south-1 (Mumbai Region) | Isolated VPC (10.0.0.0/16)", fontsize=11, fontweight='bold', color='#1e293b')

# Internet Gateway & Public Subnet
igw = patches.FancyBboxPatch((0.8, 3.8), 2.2, 1.0, boxstyle="round,pad=0.1", ec="#3b82f6", fc="#eff6ff", lw=1.5)
ax.add_patch(igw)
ax.text(1.9, 4.4, "Internet Gateway\n(IGW)", ha='center', va='center', fontsize=9, fontweight='bold', color='#1e3a8a')

# Security Group
sg = patches.FancyBboxPatch((3.5, 1.0), 5.6, 4.0, boxstyle="round,pad=0.15", ec="#6366f1", fc="#ffffff", lw=2, linestyle='--')
ax.add_patch(sg)
ax.text(3.8, 4.7, "Security Group (Port 22, 80, 443, 5000)", fontsize=10, fontweight='bold', color='#4338ca')

# EC2 Instance
ec2 = patches.FancyBboxPatch((3.8, 1.3), 5.0, 3.2, boxstyle="round,pad=0.1", ec="#f59e0b", fc="#fffbeb", lw=1.5)
ax.add_patch(ec2)
ax.text(4.0, 4.2, "AWS EC2 Instance: t3.micro (Ubuntu 22.04 LTS)", fontsize=9, fontweight='bold', color='#b45309')

# Nginx Box
nginx = patches.FancyBboxPatch((4.1, 2.5), 4.4, 1.4, boxstyle="round,pad=0.1", ec="#10b981", fc="#ecfdf5", lw=1.5)
ax.add_patch(nginx)
ax.text(6.3, 3.5, "Nginx Reverse Proxy (Port 80/443)", ha='center', va='center', fontsize=9, fontweight='bold', color='#065f46')
ax.text(6.3, 2.9, "Gzip Compression • Cache Controls • Header Passthrough", ha='center', va='center', fontsize=7.5, color='#047857')

# Docker Container Box
docker = patches.FancyBboxPatch((4.1, 1.5), 4.4, 0.8, boxstyle="round,pad=0.1", ec="#0284c7", fc="#f0f9ff", lw=1.5)
ax.add_patch(docker)
ax.text(6.3, 1.9, "Docker Container: Library Management Platform (Port 5000)", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0369a1')

# Arrows
ax.annotate("", xy=(3.5, 4.3), xytext=(3.0, 4.3), arrowprops=dict(arrowstyle="->", lw=2, color="#2563eb"))
ax.annotate("", xy=(6.3, 2.3), xytext=(6.3, 2.5), arrowprops=dict(arrowstyle="->", lw=2, color="#059669"))

plt.tight_layout()
plt.savefig('documentation/figures/fig1_system_architecture.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. DevOps Deployment Pipeline Flow
fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 4)
ax.axis('off')

stages = [
    ("1. Code & UI\nRefinement", "GitHub Repo\nPytest 97%", "#3b82f6"),
    ("2. Docker\nContainer", "Multi-stage\nPython 3.11", "#0284c7"),
    ("3. Terraform\nIaC", "AWS VPC, SG,\nEC2, KeyPair", "#7c3aed"),
    ("4. Ansible\nConfig", "Docker & Nginx\nAutomation", "#ea580c"),
    ("5. Live Public\nEndpoint", "Public IP / URL\nHealth Check", "#10b981"),
]

for idx, (title, desc, color) in enumerate(stages):
    x = 0.5 + idx * 1.9
    box = patches.FancyBboxPatch((x, 1.2), 1.6, 2.0, boxstyle="round,pad=0.1", ec=color, fc="#ffffff", lw=2)
    ax.add_patch(box)
    header = patches.FancyBboxPatch((x, 2.4), 1.6, 0.8, boxstyle="round,pad=0.1", ec=color, fc=color, lw=1)
    ax.add_patch(header)
    ax.text(x + 0.8, 2.8, title, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#ffffff')
    ax.text(x + 0.8, 1.8, desc, ha='center', va='center', fontsize=8, color='#334155')
    if idx < len(stages) - 1:
        ax.annotate("", xy=(x + 1.85, 2.2), xytext=(x + 1.65, 2.2), arrowprops=dict(arrowstyle="->", lw=2, color="#64748b"))

plt.tight_layout()
plt.savefig('documentation/figures/fig2_devops_workflow.png', dpi=300, bbox_inches='tight')
plt.close()

print("Architecture and workflow diagrams generated successfully.")
