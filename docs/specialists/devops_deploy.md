# Especialista: DevOps Deploy
**ID:** `devops_deploy`
**Department:** DevOps / Backend Development
**Arquivo:** `plugins/specialists/devops_deploy.py`

## Descricao

Engenheiro DevOps especialista em automatizacao de infraestrutura, pipelines de entrega continua e operacao de sistemas em producao.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_DEVOPS_DEPLOY=active`

### Contexto Injetado

- **Containerizacao Docker:** Dockerfiles otimizados (multi-stage, distroless), docker-compose
- **Orquestracao Kubernetes:** Pods, Deployments, Services, ConfigMaps, Secrets, Ingress, Helm
- **CI/CD:** GitHub Actions, GitLab CI, estrategias de branching (GitFlow, Trunk-Based)
- **Infraestrutura como codigo:** Terraform, Ansible, Pulumi
- **Monitoramento:** Prometheus, Grafana, ELK Stack, Loki
- **Estrategias de deploy:** Blue-green, canary, rolling updates, feature flags
- **Cloud:** AWS (EC2, ECS, EKS, S3, RDS, Lambda), GCP, Azure
- **Gerenciamento de segredos:** HashiCorp Vault, AWS Secrets Manager, SOPS

## Uso

```bash
myc agent add-plugin meu_agente devops_deploy
```

## Especialistas Relacionados
- [CI/CD Expert](ci_cd_expert.md) — Pipelines CI/CD
- [Software Architect](software_architect.md) — Arquitetura de sistemas
- [Network Analyzer](network_analyzer.md) — Analise de redes

## Parte do Department
**DevOps** — tambem utilizado em Backend Development
