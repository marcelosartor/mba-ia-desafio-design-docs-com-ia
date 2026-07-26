# FDD: <Nome da feature>

| Campo | Valor |
| --- | --- |
| **Versão** | 1.0 |
| **Data** | YYYY-MM-DD |
| **Responsável** | <nome> |
| **Documentos relacionados** | [RFC](RFC.md) · [PRD](PRD.md) · [ADRs](adrs/) |

## 1. Contexto e motivação técnica

<O problema técnico, como a feature se encaixa no sistema atual, atores e limites.>

## 2. Objetivos técnicos

| # | Objetivo | Medida / invariante |
| --- | --- | --- |

## 3. Escopo e exclusões

**Incluído**
-

**Excluído**
-

## 4. Fluxos detalhados

### FDD-FLUXO-01 — <Nome do fluxo>

1. <passo>
2. <passo>

**Falhas e variações:**
- <condição → comportamento>

```mermaid
sequenceDiagram
```

## 5. Contratos públicos

### FDD-CONTRATO-01 — `<MÉTODO> /<rota>`

<Semântica em uma linha.>

**Requisição**
```json
{}
```

**Resposta `<status>`**
```json
{}
```

| Status | Significado |
| --- | --- |

| Header | Significado |
| --- | --- |

## 6. Matriz de erros

| ID | Código | Condição | HTTP | Tratamento |
| --- | --- | --- | --- | --- |
| FDD-ERRO-01 | `PREFIXO_NOME` | | | |

## 7. Estratégias de resiliência

| Aspecto | Valor | Origem |
| --- | --- | --- |
| Timeout | | |
| Tentativas | | |
| Backoff | | |
| Fallback | | |

## 8. Observabilidade

**Métricas**

| Métrica | Tipo | Responde |
| --- | --- | --- |

**Logs**

| Evento | Nível | Campos | Nunca logar |
| --- | --- | --- | --- |

**Tracing**

| Span | Cobre | Propagação |
| --- | --- | --- |

## 9. Dependências e compatibilidade

| Componente | Versão mínima | Observação |
| --- | --- | --- |

**Garantias de compatibilidade**
-

## 10. Critérios de aceite técnicos

- [ ] <critério objetivo e verificável>

## 11. Riscos e mitigação

### <Risco>

- **Probabilidade:** <baixa|média|alta>
- **Impacto:** <concreto>
- **Mitigação:** <acionável>
- **Contingência:** <plano B>

## 12. Integração com o sistema existente

### FDD-INT-01 — `<caminho/real/do/arquivo.ext>`

<O que o arquivo faz hoje (com linhas, quando o gancho é específico) e o que muda com a feature.>

### FDD-INT-02 — `<caminho/real/do/arquivo.ext>`

<Idem.>

### Arquivos novos propostos

| Caminho proposto | Papel |
| --- | --- |
