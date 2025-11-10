# File: scripts/setup_aws.sh

#!/bin/bash
set -e

echo "Setting up AWS infrastructure for SynergyScope..."

# Initialize Terraform
cd infrastructure/terraform
terraform init

# Validate configuration
terraform validate

# Plan deployment
terraform plan -out=tfplan

# Prompt for confirmation
read -p "Deploy infrastructure? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    terraform apply tfplan
    echo "AWS infrastructure deployed successfully!"
fi