"""Coleta independente: 30 cenarios, tres repeticoes, busca web obrigatoria."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('previous', BASE.parent / 'geo_cartao_credito' / 'collect_openai.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)

def prepare():
    doc = (BASE / 'prompts_escolha_banco.md').read_text(encoding='utf-8-sig')
    instruction = doc.split('## Instrução comum enviada com cada pergunta')[1].split('## Perguntas')[0].strip()
    questions = re.findall(r'^\| (REC_\d{2}) \| ([^|]+) \| ([^|]+) \|$', doc, re.M)
    assert len(questions) == 30 and len({q[0] for q in questions}) == 30
    prompts = {pid: {'tema': theme.strip(), 'pergunta': question.strip(), 'input': instruction + '\n\nPergunta: ' + question.strip()} for pid, theme, question in questions}
    assert all(len(q['pergunta']) > 50 and 'Banco Central' in q['input'] for q in prompts.values())
    return dict(model='gpt-4.1', repetitions=3, max_output_tokens=4000, web=True, prompts=prompts)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    config = prepare()
    (BASE / 'config_coleta.json').write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Validado: 30 perguntas completas x 3 repeticoes; gpt-4.1; busca web obrigatoria.', flush=True)
    if not args.run:
        return
    previous.load_env()
    key = os.environ.get('OPENAI_API_KEY', '').strip()
    if not key:
        raise RuntimeError('Chave OPENAI_API_KEY ausente no ambiente ou projeto anterior.')
    folder = BASE / 'resultados_openai'
    folder.mkdir(exist_ok=True)
    signature = hashlib.sha256(json.dumps(config, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    manifest = folder / 'manifest.json'
    if manifest.exists():
        assert json.loads(manifest.read_text(encoding='utf-8'))['signature'] == signature, 'Configuracao diferente'
    else:
        assert not list(folder.iterdir()), 'Pasta nao vazia sem manifesto'
        manifest.write_text(json.dumps({'signature': signature, 'config': config}, ensure_ascii=False, indent=2), encoding='utf-8')
    pending = []
    for pid, question in config['prompts'].items():
        for rep in range(1, 4):
            target = folder / f'{pid}_{rep}.json'
            if target.exists():
                old = json.loads(target.read_text(encoding='utf-8'))
                assert old['response'].get('status') == 'completed' and previous.extract(old['response'])[0], f'Revisar {target.name}'
            else:
                pending.append((pid, rep, question, target))
    def collect(item):
        pid, rep, question, target = item
        payload = dict(model=config['model'], input=question['input'], store=False, max_output_tokens=config['max_output_tokens'], tools=[{'type':'web_search'}], tool_choice='required', include=['web_search_call.action.sources'])
        response = previous.request_response(key, payload)
        record = dict(id_prompt=pid, repeticao=rep, tema=question['tema'], prompt=question['input'], data_hora=datetime.now(timezone.utc).isoformat(), response=response)
        temp = target.with_suffix('.tmp')
        temp.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
        temp.replace(target)
        if response.get('status') != 'completed' or not previous.extract(response)[0]:
            raise RuntimeError(f'Resposta incompleta: {target.name}')
        return target.name
    errors = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        jobs = {pool.submit(collect, item): item for item in pending}
        done = 90-len(pending)
        for future in as_completed(jobs):
            try:
                name = future.result()
                done += 1
                print(f'{done}/90 salvo: {name}', flush=True)
            except Exception as exc:
                errors.append(str(exc))
                print(f'ERRO: {exc}', flush=True)
                for job in jobs:
                    job.cancel()
                break
    previous.export_csv(folder)
    if errors:
        raise RuntimeError('Coleta interrompida; dados salvos preservados. ' + errors[0])
    print('COLETA CONCLUIDA: 90 respostas.', flush=True)

if __name__ == '__main__':
    main()
