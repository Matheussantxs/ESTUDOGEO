# Dicionário e organização dos dados

## Base CSV

Arquivo: resultados_openai/coleta_openai.csv. Codificação UTF-8 com BOM; delimitador vírgula; listas internas separadas por ponto e vírgula. Os campos de resposta podem conter quebras de linha.

| Campo | Significado |
|---|---|
| id_prompt | Identificador da pergunta: INFO, COMP, REC ou DEC e número. |
| prompt | Texto original enviado à API. |
| motor | Rótulo OpenAI API. |
| versao_modelo | Identificador de modelo retornado pela API. |
| repeticao | Número da repetição, de 1 a 3. |
| data_hora | Horário UTC de registro da resposta, em ISO 8601. |
| resposta | Texto completo extraído dos blocos output_text. |
| fontes_citadas | URLs únicas das anotações url_citation. |
| marcas_mencionadas | Marcas do dicionário encontradas, na ordem da primeira ocorrência. |
| marca_top1 | Vazio: primeira recomendação não validada. |
| primeira_marca_mencionada | Primeira marca detectada no texto; não implica recomendação. |
| status | Status retornado pela API; completed nesta amostra. |
| response_id | Identificador técnico da resposta. |

## JSONs individuais

Nome: ID_REPETICAO.json, por exemplo INFO_01_1.json.

Contêm id_prompt, prompt, repeticao, data_hora e response. O objeto response preserva o retorno da API, incluindo saída, anotações, modelo, status e uso de tokens. Campos adicionais dependem da API.

Os dados foram coletados para o estudo; não são respostas simuladas. O piloto não integra esta pasta.

## Manifesto

manifest.json registra a configuração e uma assinatura SHA-256 calculada a partir dela. O coletor usa essa assinatura para impedir a mistura de configurações em uma pasta. Ela não é um hash de integridade de todos os arquivos de dados.

## Resumo

estudo_completo/resumo.json contém:

- Quantidades de respostas, perguntas e repetições.
- Modelo, intervalo de coleta, uso de tokens e número de buscas.
- URLs e domínios distintos.
- Frequências de presença de domínios e marcas por resposta.
- Métricas por pergunta: contagens, CV e Jaccard.
- Configuração da coleta.

As frequências de marcas dependem do dicionário; não devem ser interpretadas como cobertura completa de todas as marcas citadas.

## Uso e revisão

O coletor regenera o CSV a partir dos JSONs. Faça anotações e revisão humana em uma cópia ou tabela separada, ligada por id_prompt e repeticao.

O repositório contém perguntas públicas do banco e respostas geradas. O .env e as credenciais não integram a entrega. Não adicione credenciais em scripts, arquivos de dados ou histórico de commits.

Consulte [a metodologia](METODOLOGIA.md) antes de reutilizar as métricas.
