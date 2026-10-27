# Estudo GEO no nicho de crédito: 90 respostas da OpenAI

**Quais fontes aparecem — e quanto elas se repetem — quando uma IA responde a perguntas sobre crédito?**

Este projeto reúne uma coleta exploratória de 30 perguntas em português, repetidas três vezes pela API da OpenAI, com busca web obrigatória. São 90 respostas reais, acompanhadas de citações, dados brutos e análise descritiva reproduzível.

GEO significa *Generative Engine Optimization*. Aqui, o termo delimita o interesse pela visibilidade de fontes e marcas nas respostas geradas. O experimento **não testa uma intervenção de otimização nem demonstra causalidade**.

## Resultados principais

| Indicador | Resultado |
|---|---:|
| Perguntas distintas | 30 |
| Repetições por pergunta | 3 |
| Respostas completas | 90 |
| Respostas com citações | 90 |
| URLs distintas citadas | 305 |
| Domínios distintos citados | 140 |
| Média de URLs citadas por resposta | 6,5 |
| Similaridade média de domínios entre repetições — Jaccard | 45,3% |
| Respostas com citação de serasa.com.br | 60 de 90 — 66,7% |
| Respostas com citação de bcb.gov.br | 30 de 90 — 33,3% |

**Leitura central:** nesta amostra, repetir a mesma pergunta não produziu o mesmo conjunto de fontes. Jaccard de 45,3% é uma medida de interseção sobre união dos conjuntos; não significa que exatamente 54,7% das fontes foram “trocadas”.

![Domínios citados nas 90 respostas](estudo_completo/dominios.png)

## Escopo da coleta

- **Data:** 26/10/2026, entre 21:04:19 e 21:18:48, UTC−03:00, considerando os horários de registro das respostas.
- **Modelo solicitado:** gpt-4.1.
- **Modelo retornado:** gpt-4.1-2025-04-14.
- **Interface:** Responses API, com web_search obrigatório.
- **Amostra:** 8 perguntas informacionais, 8 comparativas, 8 de recomendação e 6 de decisão.
- **Contexto:** cada chamada contém apenas a pergunta original, sem histórico.
- **Ordem:** três repetições consecutivas por pergunta; sem aleatorização.
- **Piloto:** excluído dos resultados.

Os resultados se referem a essa configuração da **API da OpenAI**, não à interface do ChatGPT ou a outros fornecedores.

## Leia o estudo e consulte os dados

- [Relatório completo](estudo_completo/ESTUDO_COMPLETO.md)
- [Todas as perguntas e respostas](estudo_completo/respostas_completas.md)
- [Metodologia e fórmulas](METODOLOGIA.md)
- [Dicionário de dados](DADOS.md)
- [Base de coleta em CSV](resultados_openai/coleta_openai.csv)
- [Resumo e métricas em JSON](estudo_completo/resumo.json)
- [Manifesto da coleta](resultados_openai/manifest.json)

Os 90 arquivos JSON individuais estão em resultados_openai. Eles preservam as respostas retornadas pela API, incluindo citações e uso de tokens.

## Estrutura

- collect_openai.py: coleta, persistência por resposta e exportação CSV.
- run_collect.py: entrada alternativa para o coletor.
- analyze_openai.py: validação da amostra, métricas, gráficos e relatório.
- test_collect_openai.py: testes locais com respostas simuladas, sem chamadas de API.
- prompts_banco_geo_credito.md: banco original de perguntas.
- resultados_openai/: coleta real publicada.
- estudo_completo/: relatório, respostas consolidadas, resumo e gráficos.
- requirements.txt: dependência da análise.
- .env.example: exemplo sem credencial.

## Executar localmente

Requer Python 3.10 ou superior. O coletor usa apenas a biblioteca padrão; a análise usa Matplotlib. O ambiente da execução original tinha Python 3.13.5 e Matplotlib 3.10.0.

Instale a dependência da análise:

```shell
python -m pip install -r requirements.txt
```

Para validar o banco sem chamadas pagas:

```shell
python collect_openai.py --dry-run
python -m unittest -v test_collect_openai.py
```

Para recalcular o relatório a partir dos dados publicados, **sem chave e sem chamadas de API**:

```shell
python analyze_openai.py
```

Esse comando atualiza os arquivos de estudo_completo usando a coleta publicada em resultados_openai.

### Fazer uma nova coleta

Copie .env.example para .env e configure OPENAI_API_KEY apenas no arquivo local. Não publique a chave.

No PowerShell:

```powershell
Copy-Item .env.example .env
```

No Linux/macOS:

```shell
cp .env.example .env
```

Execute um piloto e, depois, a coleta completa em pastas novas:

```shell
python collect_openai.py --limite 1 --repeticoes 1 --out resultados_piloto_novo
python collect_openai.py --repeticoes 3 --out resultados_reproducao
```

Esses comandos usam a API e geram cobrança na conta configurada. Não há estimativa monetária validada neste repositório.

Use --model para escolher outro modelo e --sem-web para desativar a busca, sempre em uma pasta distinta. Essas alterações definem outro experimento.

O analisador atual tem DATA e OUT definidos no início do arquivo. Para analisar uma nova coleta completa, aponte DATA para resultados_reproducao e OUT para outra pasta. A validação do analisador foi escrita para 30 perguntas × 3 repetições; pilotos não passam nessa validação.

### Retomada e falhas

O coletor pula respostas concluídas e impede misturar configurações diferentes na mesma pasta. Respostas incompletas são preservadas e interrompem a execução. Após timeout, confira o uso da conta antes de retomar.

O CSV é regenerado a partir dos JSONs. Faça revisões manuais em uma cópia separada. Não execute dois coletores simultaneamente na mesma pasta.

## Limitações

- Amostra intencional e pequena; não representa todas as buscas sobre crédito.
- Uma janela temporal curta e um único modelo; sem comparação entre motores ou dias.
- Citação não comprova confiabilidade, recomendação ou influência causal.
- Marcas são extraídas por um dicionário limitado, com possíveis falsos positivos e omissões.
- marca_top1 ficou vazia: não houve validação humana de primeira recomendação.
- Não foi calculado Kappa de Cohen.
- URLs com parâmetros diferentes contam separadamente; subdomínios também.
- As respostas e páginas citadas não foram auditadas como orientação financeira.

## Uso de recursos

A coleta registrou 90 chamadas de busca web, 1.574.796 tokens de entrada e 107.535 tokens de saída. Os 200.960 tokens de entrada em cache já estão incluídos no total de entrada. Consulte o painel da conta para a cobrança efetiva.

## Próximos experimentos

- Repetir a coleta em dias diferentes e aleatorizar a ordem.
- Comparar modelos sob configurações equivalentes.
- Revisar as marcas e classificar menção, recomendação e advertência.
- Avaliar qualidade e pertinência das fontes.
- Testar intervenções em conteúdo com desenho experimental adequado.

## Licença

Nenhuma licença foi definida nesta versão. Disponibilidade pública não equivale a autorização irrestrita de reutilização. Conteúdos de terceiros e páginas citadas permanecem sujeitos aos respectivos direitos.

## Referência técnica

A implementação segue a [documentação de busca web na Responses API](https://developers.openai.com/api/docs/guides/tools-web-search). Este é um estudo independente.
