# Especialista: CV Deployer
**ID:** `cv_deployer`
**Department:** Visao Computacional
**Arquivo:** `plugins/specialists/cv_deployer.py`

## Descricao

Especialista em deploy de modelos de visao computacional — TensorRT, ONNX, edge deployment, inference APIs e monitoramento de model drift.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_CV_DEPLOYER=active`

### Contexto Injetado

- **Otimizacao de modelos:** TensorRT, ONNX, quantizacao (PTQ, QAT), pruning, knowledge distillation
- **Inferencia em tempo real:** Batching dinamico, overlapping pre-processing, pipeline async, CUDA streams
- **Edge deployment:** NVIDIA Jetson, Google Coral TPU, Raspberry Pi + OpenVINO
- **Cloud deployment:** AWS SageMaker, GCP Vertex AI, conteinerizacao com Triton Inference Server, FastAPI
- **APIs de inferencia:** REST, gRPC, streaming, WebSockets, rate limiting
- **Batch processing:** Celery/RabbitMQ, Kafka, checkpoints, retry
- **Monitoramento de model drift:** Covariate drift, concept drift, alertas, retraining, A/B testing, canary releases, shadow deployment

## Uso

```bash
myc agent add-plugin meu_agente cv_deployer
```

## Especialistas Relacionados
- [Model Trainer](model_trainer.md) — Treinamento de modelos
- [CV Architect](cv_architect.md) — Arquitetura
- [DevOps Deploy](devops_deploy.md) — Deploy geral

## Parte do Department
Empresa de Visao Computacional
