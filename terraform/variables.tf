variable "aws_region" {
  description = "AWS deployment region"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name tag prefix"
  type        = string
  default     = "library-management-system"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "instance_type" {
  description = "EC2 instance size for free-tier eligible hosting"
  type        = string
  default     = "t3.micro"
}

variable "ssh_allowed_cidr" {
  description = "CIDR block permitted for SSH access (restricted to user current public IP)"
  type        = string
  default     = "103.218.102.53/32"
}

variable "app_port" {
  description = "Internal application port"
  type        = number
  default     = 5000
}

variable "key_name" {
  description = "Name of existing EC2 Key Pair for SSH"
  type        = string
  default     = "library-deploy-key"
}
