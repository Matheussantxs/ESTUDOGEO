# Metodologia

## Pergunta de pesquisa

Como variam as fontes citadas e as menções a marcas em três respostas independentes à mesma pergunta sobre crédito, usando uma configuração fixa da API da OpenAI?

O estudo é exploratório e descritivo. Não testa técnicas de GEO, causalidade ou superioridade de modelos.

## Amostra e unidade de análise

Amostra intencional de 30 perguntas em português: 8 informacionais, 8 comparativas, 8 de recomendação e 6 de decisão.

A unidade de coleta é uma resposta a uma pergunta em uma repetição. A amostra contém 90 unidades: 30 × 3. As três respostas de uma pergunta não representam três perguntas independentes.

O arquivo do banco preserva notas históricas sobre coleta manual e outros motores. Nesta execução foram extraídos apenas o identificador e o texto das 30 linhas de perguntas. Essas notas não foram enviadas ao modelo nem descrevem o protocolo aplicado.

## Protocolo executado

1. Ler as 30 perguntas do banco original, sem usar respostas antigas como entrada.
2. Seguir a ordem do banco e executar três repetições consecutivas por pergunta.
3. Enviar somente a pergunta, sem histórico ou mensagens adicionais.
4. Solicitar gpt-4.1, com web_search e tool_choice=required.
5. Usar store=false e max_output_tokens=4000; não definir temperatura explicitamente.
6. Preservar cada resposta integral em JSON antes de seguir.
7. Exportar o CSV a partir dos JSONs.
8. Validar completude e gerar análise descritiva.

Modelo retornado nas 90 respostas: gpt-4.1-2025-04-14. Horários de registro: 26/10/2026, 21:04:19–21:18:48, UTC−03:00. Os JSONs armazenam timestamps em UTC.

O piloto foi excluído. O estudo completo contém 90 chamadas de busca web registradas.

## Extração

### Citações

O campo fontes_citadas recebe URLs das anotações estruturadas url_citation, sem duplicatas dentro de uma resposta. Links apenas consultados pela busca não entram automaticamente nessa contagem.

A URL é comparada literalmente. Não são removidos parâmetros, fragmentos ou diferenças de protocolo.

### Domínios

Extrai-se o hostname da URL em minúsculas, removendo apenas o prefixo www. Subdomínios permanecem distintos. “Domínio”, neste estudo, designa esse hostname normalizado, não o domínio registrável.

A frequência de um domínio é o número de respostas que o citam ao menos uma vez. Portanto, o denominador é 90, não a quantidade total de links.

### Marcas

O dicionário inclui Nubank, Itaú, Bradesco, Santander, Banco do Brasil, C6 Bank, Banco Inter, PicPay, Caixa, Creditas, BMG, Pan e Agibank.

A busca usa expressões regulares sem distinção entre maiúsculas e minúsculas. A presença é contada no máximo uma vez por resposta. A primeira marca mencionada segue a posição no texto.

Essa heurística não identifica todas as marcas, não resolve todas as ambiguidades e não determina recomendação. Inter e Caixa podem ocorrer com outros sentidos. marca_top1 permanece vazia.

## Métricas

### Contagem de citações

Número de URLs únicas por resposta. A média por intenção usa as respostas daquele grupo: 24, 24, 24 e 18, respectivamente.

### Coeficiente de variação

CV = 100 × desvio-padrão amostral / média.

É calculado para as três contagens de URLs de cada pergunta. Quando a média é zero, o resultado é N/D. CV igual a zero significa contagens iguais, não necessariamente fontes iguais.

### Similaridade de Jaccard

J(A, B) = tamanho da interseção de A e B / tamanho da união de A e B.

Para cada pergunta, comparam-se os pares R1–R2, R1–R3 e R2–R3. Calcula-se a média dos pares válidos, separadamente para URLs, domínios e marcas.

Se ambos os conjuntos são vazios, o par é N/D e é excluído da média. Se somente um é vazio, Jaccard é zero. Se todos os pares são N/D, a média da pergunta é N/D.

O indicador global de domínios é a média das médias por pergunta. Nesta amostra todas as perguntas têm pares válidos. O valor de 45,3% não é uma taxa de troca de fontes nem uma correlação.

### Visualizações

- Barras: presença de domínios e marcas nas respostas.
- Boxplot: distribuição das contagens de URLs por intenção. Linha laranja = mediana; triângulo verde = média; caixa = intervalo interquartil; hastes até os valores dentro de 1,5 × IQR; círculos = valores além das hastes.

## Verificações realizadas

- 90 combinações únicas de pergunta e repetição.
- Três repetições para cada uma das 30 perguntas.
- 90 IDs de resposta distintos.
- Status completed e texto não vazio em todos os registros.
- Texto de entrada igual ao banco para cada identificador.
- Um único modelo retornado.
- Todas as 90 respostas com citações e busca web registrada.
- Verificação local das fórmulas de Jaccard e CV.
- Inspeção visual dos três gráficos.

Cinco testes automatizados do coletor também passaram, usando respostas fictícias. Eles verificam o banco, a extração, 90 chamadas simuladas e retomada, a interrupção em resposta incompleta e o modo sem API. Esses testes não avaliam qualidade factual das respostas reais.

## Limites de interpretação

Não houve aleatorização, controle de recência das fontes, comparação entre fornecedores, auditoria factual ou avaliação humana de recomendação. Os resultados não sustentam ranking de melhores bancos, conclusões causais sobre GEO ou generalização para outros modelos e períodos.

O desenho e o código podem ser reproduzidos; as respostas não são garantidas como idênticas, pois a geração e a busca web podem variar.
