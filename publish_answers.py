"""Exporta e verifica as respostas sem converter mencoes em recomendacoes."""
import csv
from collections import Counter
from datetime import datetime
import hashlib
from html import escape
import json
from pathlib import Path
import re
from zipfile import ZipFile, ZIP_DEFLATED

BASE=Path(__file__).resolve().parent
config=json.loads((BASE/'config_coleta.json').read_text(encoding='utf-8'))
records=[]
for path in sorted((BASE/'resultados_openai').glob('REC_*.json')):
    r=json.loads(path.read_text(encoding='utf-8'))
    response=r['response']
    assert response['status']=='completed', path.name
    r['text']='\n'.join(c['text'] for o in response['output'] if o.get('type')=='message' for c in o.get('content',[]) if c.get('type')=='output_text')
    r['urls']=list(dict.fromkeys(a['url'] for o in response['output'] if o.get('type')=='message' for c in o.get('content',[]) for a in c.get('annotations',[]) if a.get('type')=='url_citation'))
    r['web_calls']=sum(o.get('type')=='web_search_call' for o in response['output'])
    assert r['text'].strip() and r['web_calls']>=1, path.name
    assert r['prompt']==config['prompts'][r['id_prompt']]['input'], path.name
    r['file']=path.name
    records.append(r)
assert len(records)==90
assert len({(r['id_prompt'],r['repeticao']) for r in records})==90
assert Counter(r['id_prompt'] for r in records)==Counter({pid:3 for pid in config['prompts']})
assert len({r['response']['id'] for r in records})==90
fields=['id_prompt','tema','pergunta','repeticao','data_hora_utc','modelo','status','response_id','buscas_web','resposta','fontes_citadas']
with (BASE/'resultados_openai'/'coleta_openai.csv').open('w',encoding='utf-8-sig',newline='') as stream:
    writer=csv.DictWriter(stream,fieldnames=fields); writer.writeheader()
    for r in records:
        writer.writerow(dict(id_prompt=r['id_prompt'],tema=r['tema'],pergunta=config['prompts'][r['id_prompt']]['pergunta'],repeticao=r['repeticao'],data_hora_utc=r['data_hora'],modelo=r['response']['model'],status=r['response']['status'],response_id=r['response']['id'],buscas_web=r['web_calls'],resposta=r['text'],fontes_citadas=';'.join(r['urls'])))
summary={'perguntas':30,'repeticoes':3,'respostas':len(records),'status':dict(Counter(r['response']['status'] for r in records)),'modelos':dict(Counter(r['response']['model'] for r in records)),'buscas_web':sum(r['web_calls'] for r in records),'urls_unicas':len({url for r in records for url in r['urls']}),'primeira_resposta_utc':min(r['data_hora'] for r in records),'ultima_resposta_utc':max(r['data_hora'] for r in records),'tokens_entrada':sum(r['response'].get('usage',{}).get('input_tokens',0) for r in records),'tokens_saida':sum(r['response'].get('usage',{}).get('output_tokens',0) for r in records),'ranking_indicacoes':'Nao calculado: exige revisao contextual; mencoes automaticas nao sao indicacoes.'}
(BASE/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
intro=['# Respostas completas — escolha de banco','', 'Coleta concluída: 30 perguntas, três repetições e 90 respostas independentes. Textos originais do modelo preservados, inclusive eventuais erros. Esta coletânea não valida as condições dos produtos nem é uma recomendação financeira.','', 'Banco Central e Serasa podem aparecer nas fontes e no texto original, mas não são instituições elegíveis para o ranking. Consulte [a revisão inicial de qualidade](REVISAO_QUALIDADE.md).','', '## Índice','']
for pid,q in config['prompts'].items(): intro.append(f'- [{pid} — {q["tema"]}](#{pid.lower()})')
html=['<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Pesquisa — escolha de banco</title><style>body{font:17px/1.6 system-ui;max-width:1050px;margin:40px auto;padding:0 24px;color:#172b45;background:#fafbfd}h1,h2{line-height:1.2}details{background:white;border:1px solid #ccd7e5;border-radius:8px;padding:16px;margin:14px 0}summary{cursor:pointer;font-weight:650}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:15px/1.65 system-ui}input{padding:12px;width:95%;font:inherit}a{color:#1265ab}</style><h1>Escolha de banco: 30 perguntas, 90 respostas</h1><p>Respostas originais geradas pela API. Incluem erros e desvios de escopo identificados na revisão; não representam validação de produtos. Banco Central e Serasa não são opções elegíveis.</p><p><a href="REVISAO_QUALIDADE.md">Revisão de qualidade</a> · <a href="RESPOSTAS_COMPLETAS.md">Textos em Markdown</a> · <a href="resultados_openai/coleta_openai.csv">Dados CSV</a></p><input aria-label="Buscar perguntas" placeholder="Buscar pergunta ou tema" oninput="document.querySelectorAll(\'section\').forEach(s=>s.hidden=!s.dataset.search.includes(this.value.toLowerCase()))">']
for pid,q in config['prompts'].items():
    intro.extend(['',f'## {pid}','',f'**Tema:** {q["tema"]}','',q['pergunta'],''])
    html.append(f'<section data-search="{escape((pid+" "+q["tema"]+" "+q["pergunta"]).lower(),quote=True)}"><h2>{pid} — {escape(q["tema"])}</h2><p>{escape(q["pergunta"])}</p>')
    for r in [r for r in records if r['id_prompt']==pid]:
        intro.extend([f'### Repetição {r["repeticao"]}','',f'Modelo: {r["response"]["model"]}. Data UTC: {r["data_hora"]}. [JSON original](resultados_openai/{r["file"]})','',r['text'],''])
        html.append(f'<details><summary>Repetição {r["repeticao"]}</summary><p>{escape(r["response"]["model"])} · {escape(r["data_hora"])} · <a href="resultados_openai/{r["file"]}">JSON original</a></p><pre>{escape(r["text"])}</pre><p>Fontes: '+ ' · '.join(f'<a href="{escape(url,quote=True)}" target="_blank" rel="noopener">{i+1}</a>' for i,url in enumerate(r['urls']))+'</p></details>')
    html.append('</section>')
html.append('</html>')
(BASE/'RESPOSTAS_COMPLETAS.md').write_text('\n'.join(intro),encoding='utf-8')
(BASE/'respostas.html').write_text('\n'.join(html),encoding='utf-8')
quality='''# Revisão inicial de qualidade

A coleta técnica foi concluída e validada. A revisão contextual inicial identificou os casos abaixo. Esta lista não é uma auditoria exaustiva das condições comerciais ou da classificação de todas as instituições.

| Resposta | Achado | Tratamento para análise de marcas |
|---|---|---|
| REC_01_1 | Uma opção é apenas cooperativa local, sem nome. | Não atribuir marca por inferência. |
| REC_02_1 | Uma das três opções agrupa várias instituições. | Registrar o desvio do limite de três; não cortar silenciosamente o texto. |
| REC_07_1 e REC_07_2 | Screder e CDC aparecem como opções; a classificação precisa de confirmação documental. | Manter como pendência de elegibilidade, sem concluir que são instituições inexistentes. |
| REC_09_1 | Banco24Horas e Saque e Pague aparecem como opções. | Redes de atendimento não entram como bancos indicados. |
| REC_09_3 | ORO é citada; seus termos distinguem a empresa da instituição parceira. | Não atribuir automaticamente a indicação à parceira nem presumir licença própria. |
| REC_14_1 a REC_14_3 | Aplicativos de orçamento são apresentados junto a instituições. | Não presumir que app de Open Finance é instituição financeira ou de pagamento. |
| REC_15_1 | A resposta cita um ranking do quarto trimestre de 2026, ainda não encerrado em 27/10/2026. | Alegação temporal problemática; não reproduzir como evidência de qualidade. |
| REC_15_2 | O texto associa BNDES ao Banco do Nordeste. | Registrar inconsistência de identidade; não contar ambos como indicações distintas. |
| REC_16_1 e REC_16_3 | Programa Celular Seguro ocupa uma opção. | Excluir programa governamental do ranking de instituições. |
| REC_18_2 | Clara é apresentada com foco empresarial e dúvida sobre uso por pessoa física. | Sinalizar inadequação potencial ao perfil; não tratar como indicação favorável sem ressalva. |
| REC_21_1 e REC_21_3 | PagBank aparece associado a Santander e Banco Inter no mesmo título. | Não criar indicações para Santander ou Inter a partir dessa associação inconsistente. |
| REC_22_1 e REC_22_3 | Cartão Méliuz aparece com identificação de parceiro diferente ou imprecisa. | Revisar emissor; não normalizar por suposição. |
| REC_24_1 a REC_24_3 | Aplicativos de orçamento aparecem como alternativas a bancos. | Excluir apps sem enquadramento confirmado no escopo institucional. |
| REC_26_2 | Há quatro categorias, incluindo cartões de débito globais, apesar do pedido de até três instituições e cartão de crédito. | Registrar desvio de formato e de produto. |

## Critério para o ranking

Uma menção não equivale a uma indicação. A contagem requer revisão por resposta, elegibilidade institucional, identificação da opção, evidência textual e classificação favorável, condicional ou sem indicação. Não foi publicado um ranking automático com base no dicionário do coletor anterior. O CSV entregue contém respostas e fontes, sem colunas de classificação não revisadas.

Banco Central e Serasa permanecem no registro original quando citados como fontes ou contexto. Eles não são opções elegíveis. Bandeiras, mídia, comparadores, aplicativos de orçamento e programas governamentais também não devem receber pontuação como instituição.

## Fontes para revisão de identidade

- [Infopago — página institucional e conta PF](https://www.infopago.com.br/): apresenta a marca como instituição de pagamento; não é auditoria independente de toda sua situação regulatória.
- [ORO — termos de uso](https://orooficial.com.br/termos-uso/): distingue a empresa que oferece os serviços da instituição financeira parceira. Essa distinção impede uma normalização automática segura.

A presença dessas marcas nas respostas não comprova a adequação, disponibilidade ou qualidade dos produtos. A revisão de conteúdo deve ser concluída antes de publicar um ranking de recomendações.
'''
(BASE/'REVISAO_QUALIDADE.md').write_text(quality,encoding='utf-8')
readme=f'''# Pesquisa: escolha de banco por novos clientes

Coleta concluída: **30 perguntas × 3 repetições = 90 respostas**, todas com status completed. Modelo retornado: {', '.join(summary['modelos'])}. Busca web obrigatória, sem histórico compartilhado entre chamadas.

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
'''
(BASE/'README.md').write_text(readme,encoding='utf-8')
doc=(BASE/'prompts_escolha_banco.md').read_text(encoding='utf-8-sig')
doc=doc.replace('Instrumento de pesquisa; coleta ainda não realizada.','Instrumento de pesquisa; coleta concluída com 90 respostas.')
doc=doc.replace('30 perguntas preparadas. Nenhuma chamada à API foi feita para esta versão. Ainda não existem resultados ou ranking deste novo banco.','Coleta concluída: 30 perguntas, três repetições e 90 respostas. Consulte RESPOSTAS_COMPLETAS.md e REVISAO_QUALIDADE.md. Ranking de indicações ainda não validado.')
(BASE/'prompts_escolha_banco.md').write_text(doc,encoding='utf-8')
checksums={str(p.relative_to(BASE)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE/'resultados_openai').glob('*.json')}
(BASE/'checksums.json').write_text(json.dumps(checksums,indent=2),encoding='utf-8')
with ZipFile(BASE.parent/'pesquisa_escolha_banco_90_respostas.zip','w',ZIP_DEFLATED) as archive:
    for path in BASE.rglob('*'):
        if path.is_file() and path.suffix in {'.md','.json','.csv','.html','.py'} and '__pycache__' not in path.parts:
            archive.write(path,'geo_escolha_banco/'+str(path.relative_to(BASE)))
print(json.dumps(summary,ensure_ascii=False,indent=2))
print('Entregaveis gerados e 90 respostas verificadas.')
