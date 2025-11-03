# =============================================================================
# SageMaker Module - Model Registry
# =============================================================================

# -----------------------------------------------------------------------------
# SageMaker Model Package Group (Model Registry)
# -----------------------------------------------------------------------------
resource "aws_sagemaker_model_package_group" "main" {
  model_package_group_name        = "${var.project_name}-model-group-${var.environment}"
  model_package_group_description = "Model registry for ${var.project_name} ${var.environment} - Diabetes classification models"

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-model-group-${var.environment}"
    }
  )
}
