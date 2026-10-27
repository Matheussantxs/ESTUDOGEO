import json, re
from pathlib import Path
base=Path(__file__).resolve().parent
records=[]
for path in sorted((base/'resultados_openai').glob('REC_*.json')):
    r=json.loads(path.read_text(encoding='utf-8'))
    r['text']='\n'.join(c['text'] for o in r['response'].get('output',[]) if o.get('type')=='message' for c in o.get('content',[]) if c.get('type')=='output_text')
    records.append(r)
lines=['# Respostas integrais — escolha de banco','',f'Respostas salvas: {len(records)} de 90.','']
for r in records:
    lines.extend([f"## {r['id_prompt']} — repetição {r['repeticao']}",'',f"Modelo: {r['response'].get('model')}. Data UTC: {r['data_hora']}",'',r['prompt'],'',r['text'],''])
(base/'RESPOSTAS_COMPLETAS.md').write_text('\n'.join(lines),encoding='utf-8')
print(f'{len(records)}/90 respostas exportadas')
for r in records:
    headings=[line for line in r['text'].splitlines() if re.match(r'^\s*(?:#{1,6}\s|\*\*\d|\d+[.)]\s|\|)',line)]
    print(f"\n{r['id_prompt']}_{r['repeticao']}: " + '\n'.join(headings)[:2800])
