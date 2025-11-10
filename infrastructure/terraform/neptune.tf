# File: infrastructure/terraform/neptune.tf

resource "aws_neptune_subnet_group" "main" {
  name       = "synergyscope-neptune-subnet-group"
  subnet_ids = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]
}

resource "aws_neptune_cluster" "main" {
  cluster_identifier                  = "synergyscope-cluster"
  engine                             = "neptune"
  backup_retention_period            = 7
  preferred_backup_window            = "07:00-09:00"
  skip_final_snapshot                = true
  neptune_subnet_group_name          = aws_neptune_subnet_group.main.name
  vpc_security_group_ids             = [aws_security_group.neptune_sg.id]
  
  tags = {
    Name = "synergyscope-neptune"
  }
}

resource "aws_neptune_cluster_instance" "main" {
  count              = 2
  cluster_identifier = aws_neptune_cluster.main.id
  instance_class     = "db.r5.large"
  engine             = "neptune"
}