# Pesquisa: escolha de banco por novos clientes

Coleta concluída: **30 perguntas × 3 repetições = 90 respostas**, todas com status completed. Modelo retornado: gpt-4.1-2025-04-14. Busca web obrigatória, sem histórico compartilhado entre chamadas.

- [Navegar pelas perguntas e respostas](respostas.html)
- [Ler as 90 respostas integrais](RESPOSTAS_COMPLETAS.md)
- [Baixar dados CSV](resultados_openai/coleta_openai.csv)
- [Consultar perguntas e protocolo](prompts_escolha_banco.md)
- [Ler revisão inicial de qualidade](REVISAO_QUALIDADE.md)
- [Ver estatísticas técnicas](summary.json)

Escopo: bancos, cooperativas e instituições de pagamento. Banco Central e Serasa podem ser fontes, mas ficam fora do conjunto de opções elegíveis.

O modelo nem sempre respeitou o escopo ou o limite de opções. A revisão documenta exemplos de apps, redes de atendimento e programas públicos oferecidos como opções, além de associações inconsistentes entre marcas. Os dados originais foram preservados. Não há ranking validado de indicações nesta entrega; contagem de palavras não substitui classificação contextual.

A amostra avalia respostas da API na configuração registrada, e não todos os usos do ChatGPT nem a qualidade real dos serviços. As três repetições não equivalem a consumidores independentes. Não reaproveita respostas dos estudos anteriores.

## Reproduzir

O script run_study.py usa o módulo collect_openai.py do estudo irmão geo_cartao_credito e a chave local desse projeto, sem exibi-la. Executar sem --run valida a configuração sem chamadas; --run coleta somente registros ausentes com a mesma configuração. publish_answers.py verifica as 90 respostas e gera esta entrega sem novas chamadas. Nenhum segredo está incluído no pacote.

Configuração da busca: [documentação oficial OpenAI](https://developers.openai.com/api/docs/guides/tools-web-search).
