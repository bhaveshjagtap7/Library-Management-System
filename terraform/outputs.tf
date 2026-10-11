output "instance_id" {
  description = "EC2 Instance identifier"
  value       = aws_instance.library_app_server.id
}

output "instance_public_ip" {
  description = "Public IP address assigned to the EC2 server"
  value       = aws_instance.library_app_server.public_ip
}

output "public_url" {
  description = "Public URL for Library Management System"
  value       = "http://${aws_instance.library_app_server.public_ip}"
}

output "security_group_id" {
  description = "Security Group identifier"
  value       = aws_security_group.web_sg.id
}

output "vpc_id" {
  description = "VPC identifier"
  value       = aws_vpc.main.id
}
