# Especialista: Backend Dev
**ID:** `backend_dev`
**Department:** Desenvolvimento Web / Backend Development
**Arquivo:** `plugins/specialists/backend_dev.py`

## Descricao

Desenvolvedor backend experiente em engenharia de sistemas server-side robustos e escalaveis.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_BACKEND_DEV=active`

### Contexto Injetado

- **API RESTful:** Richardson Maturity Model, recursos, verbos HTTP, status codes, HATEOAS
- **GraphQL:** Schemas tipados, resolvers eficientes, DataLoader (N+1 prevention), subscriptions
- **Autenticacao:** JWT, OAuth2/OIDC, sessoes, RBAC, ABAC
- **Bancos de dados:** SQL com ORMs, NoSQL, caching com Redis
- **Message queues:** RabbitMQ, Kafka, AWS SQS, event-driven
- **Seguranca:** Input validation, sanitizacao, SQL injection, XSS, CSRF, rate limiting
- **Linguagens:** Python (FastAPI, Django, Flask), Node.js (Express, NestJS), Go, Java (Spring Boot)

## Uso

```bash
myc agent add-plugin meu_agente backend_dev
```

## Especialistas Relacionados
- [Frontend Dev](frontend_dev.md) — Desenvolvimento frontend
- [Database Designer](database_designer.md) — Design de banco de dados
- [DevOps Deploy](devops_deploy.md) — Deployment

## Parte do Department
**Backend Development**
