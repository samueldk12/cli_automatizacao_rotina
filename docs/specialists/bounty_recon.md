# Especialista: Bounty Recon
**ID:** `bounty_recon`
**Department:** Bug Bounty
**Arquivo:** `plugins/specialists/bounty_recon.py`

## Descricao

Reconhecimento avancado para bug bounty — enumeracao de subdominios em camadas, fingerprint de tecnologia, descoberta de endpoints, analise profunda de JavaScript e mapeamento de APIs.

## Arquitetura

- **Tipo de Hook:** PRE_LAUNCH, CONTEXT
- **Variavel de Ambiente:** `MYC_PLUGIN_BOUNTY_RECON=1`

### Contexto Injetado

- **Filosofia de recon:** 80% das descobertas vem do recon — superficies esquecidas produzem mais vulns critical
- **Enumeracao de subdominios em camadas:** Passiva (crt.sh, Censys, Google dorking, SecurityTrails), Ativa (brute force com SecLists, permutations, wildcard detection, takeover detection)
- **Fingerprint de tecnologia:** HTTP headers, Wappalyzer, port scanning, versoes de servicos
- **Descoberta de endpoints:** Wayback Machine (waybackurls, gau), brute force de paths, parameter discovery
- **Analise de JavaScript:** Extracao de URLs, API keys, source maps, regex patterns
- **Mapeamento de APIs:** REST, GraphQL, Swagger/OpenAPI, Postman collections
- **Workflow automatizado:** Pipeline de subdomain enum -> DNS resolution -> HTTP probing -> Screenshot/tech fingerprint -> URL discovery -> Parameter discovery -> Analise manual
- **Etica:** Respeitar escopo, nao causar impacto em producao, documentar tudo reproduzivelmente

## Uso

```bash
myc agent add-plugin meu_agente bounty_recon
```

## Especialistas Relacionados
- [Recon](recon.md) — Recon basico
- [OSINT Collector](osint_collector.md) — Coleta OSINT
- [Digital Footprint](digital_footprint.md) — Pegada digital

## Parte do Department
**Empresa de Bug Bounty**
