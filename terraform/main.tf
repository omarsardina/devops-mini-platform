resource "kubernetes_namespace_v1" "env" {
  metadata {
    name = var.environment
    labels = {
      managed-by = "terraform"
    }
  }
}

resource "kubernetes_config_map_v1" "app_config" {
  metadata {
    name      = "app-config"
    namespace = kubernetes_namespace_v1.env.metadata[0].name
  }

  data = {
    APP_ENV   = var.environment
    LOG_LEVEL = "info"
  }
}

resource "kubernetes_resource_quota_v1" "env_quota" {
  metadata {
    name      = "${var.environment}-quota"
    namespace = kubernetes_namespace_v1.env.metadata[0].name
  }

  spec {
    hard = {
      pods              = "4"
      "requests.cpu"    = "1"
      "requests.memory" = "1Gi"
    }
  }
}
