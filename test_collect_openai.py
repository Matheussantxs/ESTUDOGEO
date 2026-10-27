import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import collect_openai as c

def response(status='completed'):
    return dict(status=status, id='fake', model='test-model', output=[
        dict(type='message', content=[dict(type='output_text', text='Itaú antes de Nubank.',
             annotations=[dict(type='url_citation', url='https://example.org/a'),
                          dict(type='url_citation', url='https://example.org/b')])])])

class Tests(unittest.TestCase):
    def test_bank(self):
        p = c.load_prompts(c.BASE / 'prompts_banco_geo_credito.md')
        self.assertEqual(len(p), 30)
        self.assertEqual([sum(x.startswith(k) for x in p) for k in ['INFO','COMP','REC','DEC']], [8,8,8,6])

    def test_extraction(self):
        text, urls, brands = c.extract(response())
        self.assertEqual(len(urls), 2)
        self.assertEqual(brands, ['Itaú', 'Nubank'])

    def test_all_and_resume(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {'OPENAI_API_KEY':'fake'}), patch.object(c, 'load_env'), patch.object(c, 'request_response', return_value=response()) as request, contextlib.redirect_stdout(io.StringIO()):
            args = ['--out', d]
            self.assertEqual(c.main(args), 0)
            self.assertEqual(request.call_count, 90)
            for call in request.call_args_list:
                self.assertEqual(call.args[1]['tool_choice'], 'required')
                self.assertNotIn('previous_response_id', call.args[1])
            self.assertEqual(c.main(args), 0)
            self.assertEqual(request.call_count, 90)
            with self.assertRaises(SystemExit):
                c.main(args + ['--sem-web'])
            self.assertEqual(request.call_count, 90)

    def test_incomplete_preserved(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {'OPENAI_API_KEY':'fake'}), patch.object(c, 'load_env'), patch.object(c, 'request_response', return_value=response('incomplete')) as request, contextlib.redirect_stdout(io.StringIO()):
            args = ['--out', d, '--limite', '1']
            with self.assertRaises(RuntimeError):
                c.main(args)
            self.assertTrue((Path(d)/'INFO_01_1.json').exists())
            with self.assertRaises(RuntimeError):
                c.main(args)
            self.assertEqual(request.call_count, 1)

    def test_dry_run_no_key(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(c, 'load_env'), patch.object(c, 'request_response') as request, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(c.main(['--dry-run']), 0)
            request.assert_not_called()

if __name__ == '__main__':
    unittest.main()
