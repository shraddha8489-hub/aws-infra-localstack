variable "queue_name" {
  description = "Name of the SQS queue"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name for tagging"
  type        = string
}

variable "visibility_timeout" {
  description = "Visibility timeout in seconds"
  type        = number
  default     = 30
}

variable "message_retention_seconds" {
  description = "Message retention period in seconds"
  type        = number
  default     = 86400
}