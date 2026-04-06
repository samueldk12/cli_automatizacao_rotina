# Especialista: Model Trainer
**ID:** `model_trainer`
**Department:** Visao Computacional
**Arquivo:** `plugins/specialists/model_trainer.py`

## Descricao

Treinador de modelos de visao computacional — loops de treino, learning rate, loss functions, hiperparametros e experiment tracking.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_MODEL_TRAINER=active`

### Contexto Injetado

- **Training loops:** PyTorch Lightning, loops customizados, gradient accumulation, gradient clipping
- **Learning rate scheduling:** Warmup, cosine annealing, one-cycle policy, reduce on plateau
- **Loss functions para visao:** CrossEntropy, BCE, Focal Loss, IoU/Dice, Huber/Smooth L1, contrastive, triplet
- **Early stopping:** Monitoramento, paciencia, best model checkpointing
- **Checkpointing:** Pesos, optimizer state, random seed, resumo de treino
- **Mixed precision:** AMP com autocast e GradScaler, speedup 1.5-3x
- **Distributed training:** DDP, FSDP, DeepSpeed
- **Otimizacao de hiperparametros:** Grid search, random search, Bayesian (Optuna), population-based
- **Experiment tracking:** Weights & Biases, MLflow
- **Metricas de avaliacao:** mAP, IoU, precision/recall/F1, confusion matrix, ROC-AUC

## Uso

```bash
myc agent add-plugin meu_agente model_trainer
```

## Especialistas Relacionados
- [CV Architect](cv_architect.md) — Arquitetura
- [Dataset Builder](dataset_builder.md) — Dados
- [CV Deployer](cv_deployer.md) — Deploy

## Parte do Department
Empresa de Visao Computacional
