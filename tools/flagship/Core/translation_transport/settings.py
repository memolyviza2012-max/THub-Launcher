"""Web preferences are intentionally outside the legacy Core/config.json."""
import json
import os
import re
import tempfile
from pathlib import Path
from urllib.parse import urlsplit


def state_dir():
    base = os.environ.get('THUB_TRANSLATION_STATE_DIR')
    if base:
        return Path(base)
    return Path(os.environ.get('LOCALAPPDATA') or Path.home()) / 'THub' / 'translation_web'


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=str(path.parent), suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def defaults():
    return dict(channel='api', endpoint='http://127.0.0.1:17841/v1',
                model='', effort='medium', timeout=900)


def validate(settings):
    if not isinstance(settings, dict):
        raise ValueError('Invalid Web settings object')
    result = defaults()
    result.update({k: settings[k] for k in result if k in settings})
    if result['channel'] not in ('api', 'web'):
        raise ValueError('Unknown translation channel')
    parsed = urlsplit(str(result['endpoint']))
    if (parsed.scheme != 'http' or parsed.hostname not in ('127.0.0.1', 'localhost', '::1')
            or parsed.username or parsed.password or parsed.query or parsed.fragment):
        raise ValueError('Bridge URL must be a local HTTP address, without credentials or query')
    _ = parsed.port  # Reject invalid ports before a job starts.
    if parsed.path.rstrip('/') not in ('', '/v1'):
        raise ValueError('Bridge URL must end at /v1 (not /responses)')
    result['endpoint'] = str(result['endpoint']).rstrip('/')
    if not parsed.path.rstrip('/'):
        result['endpoint'] += '/v1'
    result['timeout'] = int(result['timeout'])
    if not 15 <= result['timeout'] <= 3600:
        raise ValueError('Web timeout must be between 15 and 3600 seconds')
    result['model'] = str(result['model']).strip()
    # The channel selector shows a friendly label; users may paste that label here.
    # Always retain the Web namespace so this can never select native API passthrough.
    display_model = re.fullmatch(r'Web\s*·\s*([a-z0-9][a-z0-9.-]*)', result['model'])
    if display_model:
        result['model'] = 'chatgpt-web/' + display_model.group(1)
    if result['model'] and not result['model'].startswith('chatgpt-web/'):
        raise ValueError('กรุณาใช้รหัส Web Model เช่น chatgpt-web/gpt-6-sol')
    if result['effort'] not in ('', 'low', 'medium', 'high', 'max', 'xhigh'):
        raise ValueError('Invalid Web reasoning effort')
    return result


def load_settings():
    path = state_dir() / 'settings.json'
    if not path.exists():
        return defaults()
    # A corrupt configuration must not silently switch an intended Web job to paid API.
    settings = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(settings, dict) or 'channel' not in settings:
        raise ValueError('Web settings are damaged; choose a channel explicitly in Web Settings')
    return validate(settings)


def save_settings(settings):
    result = validate(settings)
    atomic_json(state_dir() / 'settings.json', result)
    return result

