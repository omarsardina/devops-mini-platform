output "created_namespace" {
  value = kubernetes_namespace_v1.env.metadata[0].name
}

output "config_map_name" {
  value = kubernetes_config_map_v1.app_config.metadata[0].name
}
