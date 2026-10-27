"""Analise descritiva dos JSONs reais; nenhuma chamada de API."""
from pathlib import Path
import collections
import itertools
import json
import statistics
from urllib.parse import urlsplit
from datetime import datetime, timezone, timedelta
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import collect_openai as c

BASE=Path(__file__).resolve().parent
DATA=BASE/"resultados_openai"
OUT=BASE/"estudo_completo"
INTENTS={"INFO":"Informacional","COMP":"Comparação","REC":"Recomendação","DEC":"Decisão"}

def avg(xs):
    return statistics.mean(xs) if xs else None
def fmt(v):
    return "N/D" if v is None else f"{v:.1f}".replace(".",",")
def jac(a,b):
    return len(a&b)/len(a|b) if a|b else None
def cv(xs):
    return statistics.stdev(xs)/statistics.mean(xs)*100 if len(xs)>1 and statistics.mean(xs)>0 else None
def local(s):
    return datetime.fromisoformat(s).astimezone(timezone(timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M:%S")

def main():
    OUT.mkdir(exist_ok=True)
    manifest=json.loads((DATA/"manifest.json").read_text(encoding="utf-8"))
    prompts=manifest["config"]["prompts"]
    records=[]
    for path in DATA.glob("*.json"):
        if path.name=="manifest.json":
            continue
        raw=json.loads(path.read_text(encoding="utf-8"))
        response=raw["response"]
        text,urls,brands=c.extract(response)
        if response.get("status")!="completed" or not text:
            raise ValueError(f"Resposta nao concluida: {path.name}")
        domains={urlsplit(u).hostname.lower().removeprefix("www.") for u in urls if urlsplit(u).hostname}
        records.append(dict(pid=raw["id_prompt"],rep=raw["repeticao"],prompt=raw["prompt"],
                            text=text,urls=urls,domains=domains,brands=brands,model=response.get("model"),
                            date=raw["data_hora"],usage=response.get("usage",{}),response_id=response.get("id"),
                            searches=sum(x.get("type")=="web_search_call" for x in response.get("output",[]))))
    records.sort(key=lambda r:(list(prompts).index(r["pid"]),r["rep"]))
    expected={(p,r) for p in prompts for r in range(1,4)}
    actual={(r["pid"],r["rep"]) for r in records}
    if actual!=expected or len(records)!=90 or len({r["response_id"] for r in records})!=90:
        raise ValueError(f"Coleta incompleta/duplicada: {len(records)} registros")
    if any(r["prompt"]!=prompts[r["pid"]] for r in records):
        raise ValueError("Pergunta alterada")
    domains=collections.Counter(d for r in records for d in r["domains"])
    brands=collections.Counter(b for r in records for b in r["brands"])
    metrics=[]
    for pid in prompts:
        rs=[r for r in records if r["pid"]==pid]
        pairs=list(itertools.combinations(rs,2))
        ds=[jac(a["domains"],b["domains"]) for a,b in pairs]
        bs=[jac(set(a["brands"]),set(b["brands"])) for a,b in pairs]
        us=[jac(set(a["urls"]),set(b["urls"])) for a,b in pairs]
        metrics.append(dict(pid=pid,citations=[len(r["urls"]) for r in rs],
                            brands=[len(r["brands"]) for r in rs],
                            citation_cv=cv([len(r["urls"]) for r in rs]),
                            domain_jaccard=avg([v for v in ds if v is not None]),
                            brand_jaccard=avg([v for v in bs if v is not None]),
                            url_jaccard=avg([v for v in us if v is not None])))
    totals={k:sum(r["usage"].get(k,0) for r in records) for k in ["input_tokens","output_tokens","total_tokens"]}
    totals["cached_tokens"]=sum(r["usage"].get("input_tokens_details",{}).get("cached_tokens",0) for r in records)
    summary=dict(responses=90,prompts=30,repetitions=3,models=sorted({r["model"] for r in records}),
                 start=min(r["date"] for r in records),end=max(r["date"] for r in records),
                 usage=totals,search_calls=sum(r["searches"] for r in records),
                 unique_urls=len({u for r in records for u in r["urls"]}),unique_domains=len(domains),
                 responses_without_citations=sum(not r["urls"] for r in records),
                 domains=domains,brands=brands,metrics=metrics,config=manifest["config"])
    (OUT/"resumo.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False})
    for counts,title,name in [(domains,"Domínios citados — presença nas 90 respostas","dominios"),
                              (brands,"Marcas do dicionário — presença nas 90 respostas","marcas")]:
        items=counts.most_common(15)[::-1]
        fig,ax=plt.subplots(figsize=(10,6))
        if items:
            ax.barh([x[0] for x in items],[x[1] for x in items],color="#236b8e")
            ax.set_xlim(0,max(x[1] for x in items)*1.15)
            for i,(_,v) in enumerate(items):
                ax.text(v+.3,i,str(v),va="center")
        ax.set_title(title)
        ax.set_xlabel("Respostas com ao menos uma ocorrência")
        fig.tight_layout()
        fig.savefig(OUT/f"{name}.png",dpi=160)
        plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,6))
    ax.boxplot([[len(r["urls"]) for r in records if r["pid"].startswith(k)] for k in INTENTS],
               tick_labels=list(INTENTS.values()),showmeans=True)
    ax.set_title("URLs citadas por resposta e intenção")
    ax.set_ylabel("URLs únicas por resposta")
    fig.tight_layout()
    fig.savefig(OUT/"fontes_por_intencao.png",dpi=160)
    plt.close(fig)
    mean_citations=avg([len(r["urls"]) for r in records])
    mean_j=avg([m["domain_jaccard"] for m in metrics if m["domain_jaccard"] is not None])
    lines=["# Estudo GEO — crédito: coleta OpenAI","",
           f"Coleta real: {local(summary['start'])} a {local(summary['end'])} (UTC−03:00).","",
           "## Resultado principal","",
           "Foram obtidas **90 respostas completas**, cobrindo as **30 perguntas originais**, com **3 repetições independentes** por pergunta.",
           f"Modelo(s) retornado(s): **{', '.join(summary['models'])}**. Busca web habilitada e exigida em cada chamada.",
           f"Média de **{fmt(mean_citations)} URLs citadas por resposta**; **{len(domains)} domínios** e **{summary['unique_urls']} URLs distintas**.",
           f"Similaridade média de domínios entre repetições da mesma pergunta: **{fmt(mean_j*100 if mean_j is not None else None)}%**, usando Jaccard.","",
           "Este estudo descreve a API da OpenAI. Não estima diferenças entre ChatGPT, Claude, Gemini ou Perplexity e não reaproveita os números dos gráficos antigos.","",
           "## Método","",
           "- Banco original: 8 perguntas informacionais, 8 comparativas, 8 de recomendação e 6 de decisão.",
           "- Cada chamada recebeu apenas o texto original da pergunta, sem histórico ou mensagens adicionais.",
           "- Ordem do banco, com três repetições consecutivas por pergunta. Ordem não aleatorizada.",
           f"- Modelo solicitado: {manifest['config']['model']}; web_search obrigatório; store=false; limite de {manifest['config']['max_output_tokens']} tokens de saída; temperatura não definida explicitamente.",
           "- Piloto excluído. Foram verificadas 90 combinações únicas de pergunta/repetição, 90 IDs distintos e status completed em todos os registros.",
           "- URLs citadas vêm das anotações estruturadas. Fontes consultadas sem citação não entram nessa contagem.",
           "- Domínios são hostnames em minúsculas, removendo apenas www.; subdomínios permanecem distintos. URLs são comparadas literalmente.","",
           "## Resultados por intenção","",
           "| Intenção | Respostas | URLs/resposta (média) | Marcas do dicionário/resposta (média) |","|---|---:|---:|---:|"]
    for key,intent in INTENTS.items():
        rs=[r for r in records if r["pid"].startswith(key)]
        lines.append(f"| {intent} | {len(rs)} | {fmt(avg([len(r['urls']) for r in rs]))} | {fmt(avg([len(r['brands']) for r in rs]))} |")
    lines+=["","![Fontes por intenção](fontes_por_intencao.png)","","## Domínios mais citados","",
            "Cada domínio conta no máximo uma vez por resposta. Frequência não comprova confiabilidade ou influência causal.","",
            "| Domínio | Respostas | Presença |","|---|---:|---:|"]
    for name,count in domains.most_common(15):
        lines.append(f"| {name} | {count} | {fmt(count/90*100)}% |")
    lines+=["","![Domínios mais citados](dominios.png)","","## Menções a marcas","",
            "Contagem por dicionário, sujeita a revisão. Uma menção pode ser comparação, advertência ou recomendação; não significa preferência.","",
            "| Marca | Respostas com menção | Presença |","|---|---:|---:|"]
    for name,count in brands.most_common():
        lines.append(f"| {name} | {count} | {fmt(count/90*100)}% |")
    lines+=["","![Marcas mencionadas](marcas.png)","","## Variação por pergunta","",
            "CV usa desvio-padrão amostral dividido pela média. Jaccard = interseção / união dos conjuntos; média dos três pares de repetições. Dois conjuntos vazios são N/D, não 100% de acordo.","",
            "| Pergunta | URLs R1/R2/R3 | CV URLs (%) | Jaccard domínios (%) | Jaccard marcas (%) |",
            "|---|---|---:|---:|---:|"]
    for m in metrics:
        lines.append(f"| {m['pid']} | {' / '.join(map(str,m['citations']))} | {fmt(m['citation_cv'])} | {fmt(m['domain_jaccard']*100 if m['domain_jaccard'] is not None else None)} | {fmt(m['brand_jaccard']*100 if m['brand_jaccard'] is not None else None)} |")
    lines+=["","## Uso registrado","",f"- Chamadas de busca web registradas: {summary['search_calls']}.",
            f"- Tokens de entrada: {totals['input_tokens']:,}; saída: {totals['output_tokens']:,}; total: {totals['total_tokens']:,}.",
            f"- Tokens em cache: {totals['cached_tokens']:,}, já incluídos nos tokens de entrada.",
            "- Valor monetário não estimado. Consulte o painel da conta para a cobrança efetiva, incluindo buscas.","",
            "## Limitações e interpretação","",
            "- Amostra intencional, três repetições por pergunta; resultados descritivos, sem generalização para todo o nicho.",
            "- Janela temporal curta: não mede estabilidade ao longo dos dias. Busca e resultados da web podem variar.",
            "- Dicionário: "+", ".join(c.BRANDS)+". Marcas fora da lista não foram contadas. Inter e Caixa podem gerar falsos positivos.",
            "- marca_top1 permanece vazia: a primeira marca mencionada é registrada separadamente, sem validação como recomendação. Kappa de Cohen não foi calculado.",
            "- Sem outros motores nesta amostra, não se aplica matriz de concordância entre motores.",
            "- URLs com parâmetros distintos contam separadamente. Páginas citadas não foram auditadas individualmente.",
            "- O estudo analisa respostas de IA; não valida orientações financeiras nem recomenda bancos.","",
            "## Arquivos auditáveis","",
            "- [Todas as perguntas e respostas, com fontes](respostas_completas.md)",
            "- [Base CSV](../resultados_openai/coleta_openai.csv)",
            "- [Resumo e métricas em JSON](resumo.json)",
            "- JSONs brutos e manifesto: pasta ../resultados_openai/.",
            "- Código de análise: ../analyze_openai.py.","",
            "## Conclusão","",
            f"Domínio mais recorrente: **{domains.most_common(1)[0][0] if domains else 'nenhum'}**. Similaridade média de domínios entre repetições: **{fmt(mean_j*100 if mean_j is not None else None)}%**.",
            "Os resultados permitem observar visibilidade nas citações e estabilidade das fontes na API. Não sustentam ranking de melhores bancos nem comparação entre fornecedores de IA."]
    (OUT/"ESTUDO_COMPLETO.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    answers=["# Banco completo de respostas — OpenAI API","",
             "90 respostas reais, preservadas para auditoria. Conteúdo do modelo não revisado como aconselhamento financeiro.",""]
    for pid in prompts:
        answers += [f"## {pid} — {prompts[pid]}",""]
        for r in [r for r in records if r["pid"]==pid]:
            answers += [f"### Repetição {r['rep']}",f"Modelo: {r['model']} · Coleta: {local(r['date'])} (UTC−03:00)","",
                        r["text"],"","**URLs citadas (anotações da API):**",""]
            answers += [f"- [{urlsplit(u).hostname}]({u})" for u in r["urls"]] or ["Nenhuma URL citada."]
            answers += ["","---",""]
    (OUT/"respostas_completas.md").write_text("\n".join(answers),encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k not in ["config","metrics"]},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
