# Banco de Prompts GEO — Nicho Crédito (pt-BR)

Nível de uso: **coleta manual (Caminho 1)**  
Quantidade: **30 prompts** distribuídos em **4 intenções**  
Motor: Copiar para conversa nova em cada motor (ChatGPT, Gemini, Perplexity, Claude, Copilot)  
Coleta: **2–3 repetições** por prompt, cada repetição em conversa nova, mesmo prompt, mesma configuração de busca na web

---

## Intenção 1 — Informacional (8 prompts)

| id_prompt | Prompt (pt-BR) |
|-----------|----------------|
| INFO_01 | Como funciona a portabilidade de crédito consignado para servidores públicos? |
| INFO_02 | O que é e como funciona o crédito consignado para aposentados e pensionistas do INSS? |
| INFO_03 | Quais documentos são necessários para solicitar um empréstimo pessoal em banco digital? |
| INFO_04 | Qual a diferença entre crédito pessoal e cheque especial? |
| INFO_05 | Como funciona o refinanciamento de financiamento de veículo? |
| INFO_06 | O que é score de crédito e como ele influencia na aprovação de empréstimos? |
| INFO_07 | Quais são os principais requisitos para conseguir um empréstimo com taxa de juros baixa? |
| INFO_08 | Como funciona a portabilidade de salário e quais bancos digitais oferecem essa opção? |

---

## Intenção 2 — Comparação (8 prompts)

| id_prompt | Prompt (pt-BR) |
|-----------|----------------|
| COMP_01 | Qual a diferença entre empréstimo pessoal e crédito com garantia de imóvel? |
| COMP_02 | Empréstimo consignado ou empréstimo pessoal: qual escolher para quitar dívidas? |
| COMP_03 | Cartão de crédito pré-pago ou tradicional: qual é melhor para controle financeiro? |
| COMP_04 | Qual a diferença entre CDC (Crédito Direto ao Consumidor) e leasing de veículos? |
| COMP_05 | Crediário loja vs empréstimo bancário: qual tem taxa menor para compra de eletrodomésticos? |
| COMP_06 | Qual a diferença entre crédito com garantia de veículo e crédito com garantia de imóvel? |
| COMP_07 | Banco tradicional ou fintech: qual oferece melhor taxa para empréstimo pessoal? |
| COMP_08 | Qual a diferença entre portabilidade de crédito consignado e refinanciamento? |

---

## Intenção 3 — Recomendação (8 prompts)

| id_prompt | Prompt (pt-BR) |
|-----------|----------------|
| REC_01 | Qual o melhor banco digital para pedir empréstimo pessoal com taxa baixa? |
| REC_02 | Quais fintechs oferecem empréstimo para negativados com aprovação rápida? |
| REC_03 | Qual o melhor banco para fazer portabilidade de crédito consignado em 2026? |
| REC_04 | Qual fintech oferece as melhores condições de crédito para microempreendedor individual (MEI)? |
| REC_05 | Qual o melhor banco para empréstimo com garantia de veículo com liberação rápida? |
| REC_06 | Qual banco digital oferece a menor taxa de juros para empréstimo pessoal sem comprovação de renda? |
| REC_07 | Qual correspondente bancário é mais seguro para conseguir empréstimo online? |
| REC_08 | Qual o melhor banco para refinanciamento de financiamento de imóvel com parcelas reduzidas? |

---

## Intenção 4 — Decisão (6 prompts)

| id_prompt | Prompt (pt-BR) |
|-----------|----------------|
| DEC_01 | Vale a pena fazer refinanciamento de financiamento de veículo para quitar dívidas de cartão? |
| DEC_02 | Devo usar crédito consignado para pagar empréstimo pessoal com taxa mais alta? |
| DEC_03 | Vale a pena solicitar empréstimo pessoal para investir em negócio próprio? |
| DEC_04 | É melhor fazer portabilidade de crédito consignado ou manter o empréstimo no banco atual? |
| DEC_05 | Vale a pena usar crédito com garantia de imóvel para quitar dívidas de cartão de crédito? |
| DEC_06 | Devo contratar empréstimo pessoal online ou procurar um correspondente bancário presencial? |

---

## Instruções de uso para o coletor

1. Abra uma **conversa nova** no motor escolhido (sem histórico anterior).
2. Configure a busca na web da mesma forma para todos os motores (ativa ou desativa, consistentemente).
3. Cole o prompt exatamente como está na tabela.
4. Registre na planilha: `id_prompt`, `motor`, `versão do modelo`, `repeticao`, `data_hora`, `resposta` (texto completo), `fontes_citadas` (URLs/domínios), `marcas_mencionadas`, `marca_top1` (primeira marca recomendada).
5. Repita o mesmo prompt 2–3 vezes, cada uma em conversa nova, para medir a variação do próprio motor.
6. Repita para cada motor e cada prompt.

---

## Limitações a declarar no estudo final

- Amostra menor que a coleta via API.
- Maior ruído humano na coleta manual.
- Vantagem: mede exatamente o que o usuário final vê no aplicativo.
- YMYL (Your Money Your Life): fontes institucionais (Banco Central, Procon, bancos grandes) tendem a ser preferidas pelas IAs.
- Não oferecer aconselhamento individual de investimento; deixar claro que o estudo analisa respostas de IA, não recomenda produtos financeiros.
