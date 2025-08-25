resource "aws_ecr_repository" "repo" {
  name                 = var.repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}


output "image_uri" {
  value = "${aws_ecr_repository.repo.repository_url}:${var.image_tag}"
}
