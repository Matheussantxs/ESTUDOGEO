"""Coleta GEO pela OpenAI Responses API. Python 3.10+, sem dependencias."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = Path(__file__).resolve().parent
FIELDS = ['id_prompt', 'prompt', 'motor', 'versao_modelo', 'repeticao',
          'data_hora', 'resposta', 'fontes_citadas', 'marcas_mencionadas',
          'marca_top1', 'primeira_marca_mencionada', 'status', 'response_id']
BRANDS = {'Nubank': r'\bnubank\b', 'Itaú': r'\bita[uú]\b',
          'Bradesco': r'\bbradesco\b', 'Santander': r'\bsantander\b',
          'Banco do Brasil': r'\bbanco do brasil\b', 'C6 Bank': r'\bc6(?: bank)?\b',
          'Banco Inter': r'\b(?:banco inter|inter)\b', 'PicPay': r'\bpicpay\b',
          'Caixa': r'\bcaixa\b', 'Creditas': r'\bcreditas\b',
          'BMG': r'\bbmg\b', 'Pan': r'\bbanco pan\b', 'Agibank': r'\bagibank\b'}

def load_prompts(path):
    prompts = {}
    pattern = r'^\|\s*((?:INFO|COMP|REC|DEC)_\d+)\s*\|\s*([^|]+)\|'
    for pid, prompt in re.findall(pattern, Path(path).read_text(encoding='utf-8-sig'), re.M):
        if pid in prompts:
            raise ValueError(f'ID duplicado: {pid}')
        prompts[pid] = prompt.strip()
    if not prompts:
        raise ValueError('Banco de perguntas vazio ou formato invalido.')
    return prompts

def load_env():
    path = BASE / '.env'
    if path.exists():
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            if line.strip() and not line.lstrip().startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip().strip("\"'"))

def request_response(key, payload):
    request = Request('https://api.openai.com/v1/responses',
                      data=json.dumps(payload).encode(),
                      headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
    try:
        with urlopen(request, timeout=180) as response:
            return json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f'HTTP {exc.code}; verifique chave, saldo, modelo e limites.') from None
    except (URLError, TimeoutError):
        raise RuntimeError('Falha de rede/timeout; confira o uso antes de retomar.') from None

def extract(data):
    texts, urls = [], []
    for item in data.get('output', []):
        if item.get('type') != 'message':
            continue
        for part in item.get('content', []):
            if part.get('type') == 'output_text':
                texts.append(part['text'])
                urls.extend(a['url'] for a in part.get('annotations', [])
                            if a.get('type') == 'url_citation' and a.get('url'))
    text = '\n'.join(texts)
    brands = sorted((m.start(), name) for name, pattern in BRANDS.items()
                    if (m := re.search(pattern, text, re.I)))
    return text, list(dict.fromkeys(urls)), [name for _, name in brands]

def export_csv(directory):
    rows = []
    for path in sorted(directory.glob('*.json')):
        if path.name == 'manifest.json':
            continue
        record = json.loads(path.read_text(encoding='utf-8'))
        data = record['response']
        text, urls, brands = extract(data)
        rows.append(dict(id_prompt=record['id_prompt'], prompt=record['prompt'],
                         motor='OpenAI API', versao_modelo=data.get('model', ''),
                         repeticao=record['repeticao'], data_hora=record['data_hora'],
                         resposta=text, fontes_citadas=';'.join(urls),
                         marcas_mencionadas=';'.join(brands), marca_top1='',
                         primeira_marca_mencionada=brands[0] if brands else '',
                         status=data.get('status', ''), response_id=data.get('id', '')))
    target = directory / 'coleta_openai.csv'
    temp = target.with_suffix('.tmp')
    with temp.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(target)

def main(argv=None):
    load_env()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prompts', type=Path, default=BASE / 'prompts_banco_geo_credito.md')
    parser.add_argument('--model', default=os.environ.get('OPENAI_MODEL', 'gpt-4.1'))
    parser.add_argument('--repeticoes', type=int, default=3)
    parser.add_argument('--limite', type=int)
    parser.add_argument('--sem-web', action='store_true')
    parser.add_argument('--max-output-tokens', type=int, default=4000)
    parser.add_argument('--out', type=Path, default=BASE / 'resultados_openai')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    if args.repeticoes < 1 or (args.limite is not None and args.limite < 1) or args.max_output_tokens < 1:
        parser.error('Repeticoes, limite e max-output-tokens devem ser positivos.')
    prompts = load_prompts(args.prompts)
    if args.limite:
        prompts = dict(list(prompts.items())[:args.limite])
    config = dict(model=args.model, web=not args.sem_web, prompts=prompts,
                  max_output_tokens=args.max_output_tokens, schema_version=1)
    signature = hashlib.sha256(json.dumps(config, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    print(f'{len(prompts)} perguntas x {args.repeticoes} repeticoes = {len(prompts)*args.repeticoes} chamadas; modelo={args.model}; web={not args.sem_web}')
    if args.dry_run:
        for pid, prompt in prompts.items():
            print(f'{pid}: {prompt}')
        return 0
    key = os.environ.get('OPENAI_API_KEY', '').strip()
    if not key or key == 'SUA_CHAVE_AQUI':
        parser.error('Configure OPENAI_API_KEY no ambiente ou no .env local. Nao envie sua chave no chat.')
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = args.out / 'manifest.json'
    if manifest.exists():
        if json.loads(manifest.read_text(encoding='utf-8'))['signature'] != signature:
            parser.error('Configuracao diferente: use outra pasta --out para separar os experimentos.')
    else:
        if any(args.out.iterdir()):
            parser.error('Pasta sem manifesto e nao vazia; escolha outra pasta --out.')
        manifest.write_text(json.dumps(dict(signature=signature, config=config), ensure_ascii=False, indent=2), encoding='utf-8')
    for pid, prompt in prompts.items():
        for rep in range(1, args.repeticoes + 1):
            target = args.out / f'{pid}_{rep}.json'
            if target.exists():
                saved = json.loads(target.read_text(encoding='utf-8'))
                if saved['response'].get('status') != 'completed' or not extract(saved['response'])[0]:
                    raise RuntimeError(f'Resposta incompleta em {target.name}; revise antes de nova coleta.')
                continue
            payload = dict(model=args.model, input=prompt, store=False,
                           max_output_tokens=args.max_output_tokens)
            if not args.sem_web:
                payload.update(tools=[dict(type='web_search')], tool_choice='required',
                               include=['web_search_call.action.sources'])
            print(f'Coletando {pid}, repeticao {rep}', flush=True)
            data = request_response(key, payload)
            record = dict(id_prompt=pid, prompt=prompt, repeticao=rep,
                          data_hora=datetime.now(timezone.utc).isoformat(), response=data)
            temp = target.with_suffix('.tmp')
            temp.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
            temp.replace(target)
            export_csv(args.out)
            if data.get('status') != 'completed' or not extract(data)[0]:
                raise RuntimeError(f'Resposta incompleta/vazia em {target.name}; coleta interrompida para revisao.')
    export_csv(args.out)
    print(f'Coleta concluida: {args.out / "coleta_openai.csv"}')
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError) as exc:
        print(f'ERRO: {exc}')
        raise SystemExit(1)
