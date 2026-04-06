# Especialista: Dataset Builder
**ID:** `dataset_builder`
**Department:** Visao Computacional
**Arquivo:** `plugins/specialists/dataset_builder.py`

## Descricao

Engenheiro de datasets para visao computacional — coleta, anotacao, augmentacao, balanceamento e versionamento de dados.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_DATASET_BUILDER=active`

### Contexto Injetado

- **Coleta de dados:** Web scraping legal, captura controlada, crowdsourcing, sintese, sensores IoT
- **Ferramentas de anotacao:** Label Studio, CVAT, LabelImg, Roboflow; formatos COCO JSON, Pascal VOC XML, YOLO TXT
- **Pipelines de augmentacao:** Albumentations, ImgAug, geometricas, fotometricas, MixUp, CutMix, Mosaic, domain-specific
- **Gerenciamento de desbalanceamento:** Oversampling, undersampling, class weights, focal loss
- **Dados sinteticos:** Blender/Unity, GANs, diffusion models, Sim2Real com domain randomization
- **Splits de dataset:** Train/val/test estratificado, time-based, group-based, cross-validation
- **Versionamento de dados:** DVC, S3/GCS/Azure, lineage, reproducao
- **Controle de qualidade:** Auditoria estatistica, consenso multi-annotator, deteccao de anomalias

## Uso

```bash
myc agent add-plugin meu_agente dataset_builder
```

## Especialistas Relacionados
- [CV Architect](cv_architect.md) — Arquitetura de modelos
- [Model Trainer](model_trainer.md) — Treinamento
- [Data Quality](data_quality.md) — Qualidade de dados

## Parte do Department
Empresa de Visao Computacional
