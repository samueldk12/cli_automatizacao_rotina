# Especialista: CV Architect
**ID:** `cv_architect`
**Department:** Visao Computacional
**Arquivo:** `plugins/specialists/cv_architect.py`

## Descricao

Arquiteto de visao computacional especialista em projetar e implementar solucoes de deep learning para tarefas de visao (detecao, segmentacao, classificacao).

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_CV_ARCHITECT=active`

### Contexto Injetado

- **Fundamentos de DL para visao:** Tensores, convolucoes, pooling, normalizacao, ativacoes, skip connections
- **Arquiteturas CNN:** ResNet, EfficientNet, MobileNet, ConvNeXt, VGG, Inception
- **Vision Transformers:** ViT, Swin Transformer, DeiT, comparacao CNN vs ViT
- **Detecao de objetos:** YOLO (v5, v8, v9, v10, v11), Faster R-CNN, RetinaNet, SSD, metricas mAP
- **Segmentacao:** U-Net, DeepLabV3+, Mask R-CNN, IoU e Dice
- **Transfer learning:** Fine-tuning, feature extraction, modelos pre-treinados
- **Benchmarking e hardware:** GPUs, edge devices, latencia, memoria, FLOPs, precisao (FP32, FP16, INT8)

## Uso

```bash
myc agent add-plugin meu_agente cv_architect
```

## Especialistas Relacionados
- [Dataset Builder](dataset_builder.md) — Construção de datasets
- [Model Trainer](model_trainer.md) — Treinamento de modelos
- [CV Deployer](cv_deployer.md) — Deploy de modelos

## Parte do Department
Empresa de Visao Computacional (referenciado nas companies/consultoria)
