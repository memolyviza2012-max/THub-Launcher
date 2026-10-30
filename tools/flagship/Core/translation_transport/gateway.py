from copy import deepcopy
import json

from .contracts import WebTransportError
from .settings import load_settings, validate
from .settings import atomic_json, state_dir


def snapshot_config(config, route=None):
    result = dict(config)
    result.pop('_translation_route', None)
    route = validate(deepcopy(load_settings() if route is None else route))
    if route['channel'] == 'web':
        result['_translation_route'] = route
    return result


def is_web(config):
    return config.get('_translation_route', {}).get('channel') == 'web'


class TranslationGateway:
    @staticmethod
    def generate_content(config, prompt, is_local=None, use_search_grounding=False,
                         cancelled=lambda: False):
        if not is_web(config):
            from tstudio_core import CoreAI
            if use_search_grounding:
                return CoreAI.generate_content(config, prompt, is_local=is_local,
                                               use_search_grounding=use_search_grounding)
            if is_local is None:
                return CoreAI.generate_content(config, prompt)
            return CoreAI.generate_content(config, prompt, is_local=is_local)
        from .web_client import WebClient
        route = dict(config['_translation_route'])
        # A request without a selected model is not a valid frozen model choice.
        # Repair only from the saved Web choice for the exact same endpoint, never from API.
        if not route.get('model'):
            saved = load_settings()
            if (saved['channel'] == 'web' and saved['endpoint'] == route.get('endpoint')
                    and saved['model']):
                route = dict(route, model=saved['model'], effort=saved['effort'])
        try:
            import os
            atomic_json(state_dir() / 'last_dispatch.json',
                        {'pid': os.getpid(), 'module': __file__, 'channel': 'web',
                         'endpoint': route.get('endpoint'), 'model': route.get('model'),
                         'settings_path': str(state_dir() / 'settings.json')})
        except OSError:
            pass  # A diagnostic write must never prevent a translation.
        return WebClient(route).generate(prompt, cancelled)

    @staticmethod
    def strict_batch_reply(reply, expected_ids):
        """Never let Web output fall through legacy positional/approximate ID recovery."""
        text = reply.strip()
        if text.startswith('```') and text.endswith('```'):
            text = '\n'.join(text.splitlines()[1:-1])
        if text.lstrip().startswith('['):
            try:
                records = json.loads(text)
                if not isinstance(records, list):
                    raise ValueError('Expected JSON array')
                normalized = []
                for record in records:
                    if (not isinstance(record, dict) or set(record) != {'id', 'translation'}
                            or not isinstance(record['id'], str)
                            or not isinstance(record['translation'], str)
                            or any(c in record['id'] for c in '\t\r\n')):
                        raise ValueError('Invalid translation record')
                    value = record['translation'].replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\\n')
                    normalized.append(record['id'] + '\t' + value)
                text = '\n'.join(normalized)
            except (ValueError, KeyError, TypeError) as error:
                raise WebTransportError('Web ส่ง JSON แปลไม่ถูกต้อง จึงไม่นำเข้าหรือส่งซ้ำอัตโนมัติ') from error
        seen, accepted = set(), []
        allowed = set(expected_ids)
        for line in text.splitlines():
            if not line.strip():
                continue
            key, separator, value = line.partition('\t')
            if not separator or key not in allowed or key in seen or not value.strip():
                raise WebTransportError('รูปแบบคำตอบ Web ไม่ตรง ID ของชุดงาน จึงไม่นำเข้าหรือส่งซ้ำอัตโนมัติ')
            seen.add(key)
            accepted.append(key + '\t' + value)
        if not accepted:
            raise WebTransportError('Web returned no valid batch records')
        return '\n'.join(accepted)

