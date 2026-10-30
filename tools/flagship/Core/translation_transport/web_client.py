"""Local browser bridge client; no OpenAI API credentials are accepted or forwarded."""
import hashlib
import json
import os
import threading
import time
import uuid
from contextlib import contextmanager

import requests

from .contracts import WebTransportError
from .settings import atomic_json, state_dir, validate

_lock = threading.Lock()


def _paths(endpoint):
    identity = hashlib.sha256(endpoint.encode('utf-8')).hexdigest()[:16]
    root = state_dir()
    root.mkdir(parents=True, exist_ok=True)
    return root / (identity + '.lock'), root / (identity + '.pending.json')


@contextmanager
def bridge_slot(endpoint, cancelled=lambda: False, wait=True):
    """Serialize requests in this process AND other TStudio/TRun processes."""
    while not _lock.acquire(timeout=0.1):
        if not wait:
            raise WebTransportError('มีคำขอ Web กำลังทำงาน กรุณารอให้หยุดก่อนรับทราบ')
        if cancelled():
            raise WebTransportError('Web job cancelled before sending')
    handle = None
    locked = False
    try:
        lock_path, _ = _paths(endpoint)
        handle = open(lock_path, 'a+b')
        handle.seek(0, 2)
        if handle.tell() == 0:
            handle.write(b'0')
            handle.flush()
        while not locked:
            if cancelled():
                raise WebTransportError('Web job cancelled before sending')
            handle.seek(0)
            try:
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
            except OSError:
                if not wait:
                    raise WebTransportError('มีคำขอ Web ในโปรแกรมอื่นกำลังทำงาน กรุณารอให้หยุดก่อน')
                time.sleep(0.1)
        yield
    finally:
        if handle is not None:
            if locked:
                handle.seek(0)
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            handle.close()
        _lock.release()


def acknowledge_pending(endpoint):
    """Called only after the user explicitly acknowledges inspecting the browser."""
    with bridge_slot(endpoint, wait=False):
        _, path = _paths(endpoint)
        if path.exists():
            archive = path.with_name(path.stem + '.' + uuid.uuid4().hex + '.acknowledged.json')
            os.replace(path, archive)


def pending_details(endpoint):
    """Read recovery metadata only; never clear or resend an uncertain request."""
    _, path = _paths(endpoint)
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {'state': 'unknown'}
    except (OSError, ValueError):
        return {'state': 'unknown'}


def build_request(model, prompt, effort='medium'):
    # Independent conversation per logical request; these IDs provide lifecycle identity,
    # never Codex filesystem/tool authority. browser-only mode is required.
    thread_id, turn_id = str(uuid.uuid4()), str(uuid.uuid4())
    body = {
        'model': model, 'stream': True, 'store': False,
        'input': [{'type': 'message', 'role': 'user', 'id': 'msg_' + uuid.uuid4().hex,
                   'internal_chat_message_metadata_passthrough': {'turn_id': turn_id},
                   'content': [{'type': 'input_text', 'text': prompt}]}],
        'tools': [], 'tool_choice': 'none',
        'client_metadata': {'x-codex-turn-metadata': json.dumps(
            {'thread_id': thread_id, 'turn_id': turn_id})},
    }
    if effort:
        body['reasoning'] = {'effort': effort}
    return body


def completed_text(response):
    if (not isinstance(response, dict) or response.get('status') != 'completed'
            or response.get('error') or response.get('incomplete_details')):
        raise WebTransportError('Bridge returned an incomplete or failed response')
    answers = []
    for item in response.get('output', []):
        if item.get('type') != 'message' or item.get('role') != 'assistant':
            continue
        if item.get('phase') == 'commentary':
            continue
        if item.get('status', 'completed') != 'completed':
            raise WebTransportError('Bridge returned an unfinished message')
        for part in item.get('content', []):
            if part.get('type') == 'refusal':
                raise WebTransportError('ChatGPT did not return a translation (refusal)')
            if part.get('type') == 'output_text':
                answers.append(part.get('text', ''))
    text = '\n'.join(answers).strip()
    if not text:
        raise WebTransportError('Bridge completed without final answer text')
    return text


class WebClient:
    def __init__(self, settings):
        self.settings = validate(settings)
        self.catalog_source = 'server'

    def models(self):
        with requests.Session() as session:
            session.trust_env = False
            with session.get(self.settings['endpoint'] + '/models', timeout=(3, 6),
                             allow_redirects=False) as response:
                if response.status_code != 200:
                    # Upstream 6.1.9 forwards /models to native Codex even for browser-only
                    # users. Do not borrow an API key/token just to discover Web models.
                    try:
                        message = response.json().get('error', {}).get('message', '')
                    except (ValueError, AttributeError):
                        message = ''
                    if (response.status_code == 502
                            and 'Native Codex passthrough requires the incoming Bearer authorization' in message):
                        base = self.settings['endpoint'].rsplit('/v1', 1)[0]
                        with session.get(base + '/healthz', timeout=(3, 6), allow_redirects=False) as health:
                            data = health.json() if health.status_code == 200 else {}
                        if (data.get('service') == 'codex-chatgpt-web'
                                and data.get('mode') == 'browser-only' and data.get('accepting_turns')):
                            self.catalog_source = 'configured'
                            if self.settings['model']:
                                return [self.settings['model']]
                            raise WebTransportError('Bridge พร้อม แต่รุ่นนี้อ่านรายชื่อ Web Models โดยไม่มีสิทธิ์ Codex ไม่ได้ กรุณากรอก Web Model ที่ใช้ทดสอบ')
                    raise WebTransportError('Cannot read Bridge models (HTTP %s)' % response.status_code)
                return [item['id'] for item in response.json().get('data', [])
                        if isinstance(item.get('id'), str) and item['id'].startswith('chatgpt-web/')]

    def generate(self, prompt, cancelled=lambda: False):
        cfg = self.settings
        if not cfg['model']:
            raise WebTransportError('ยังไม่มี Web Model ในคำขอนี้ กรุณากด Web ⚙ เลือกโมเดลและกด Save\n'
                                    'ไฟล์ตั้งค่าที่กำลังใช้: ' + str(state_dir() / 'settings.json'))
        with bridge_slot(cfg['endpoint'], cancelled):
            from .bridge_runtime import ensure_ready, wait_idle
            ensure_ready(cfg['endpoint'], cancelled)
            _, pending = _paths(cfg['endpoint'])
            if pending.exists():
                wait_idle(cfg['endpoint'], cfg['timeout'], cancelled)
                # A new Run is explicit authorization for this new request. Preserve the old
                # unknown outcome; do not replay it, invent its answer, or silently import it.
                archive = pending.with_name(pending.stem + '.' + uuid.uuid4().hex + '.recovered.json')
                os.replace(pending, archive)
            body = build_request(cfg['model'], prompt, cfg['effort'])
            atomic_json(pending, {'request_id': body['input'][0]['id'], 'started': time.time(),
                                  'model': cfg['model'], 'state': 'sending'})
            started = time.monotonic()
            try:
                with requests.Session() as session:
                    session.trust_env = False
                    with session.post(cfg['endpoint'] + '/responses', json=body, stream=True,
                                      timeout=(3, 10), allow_redirects=False) as response:
                        if response.status_code != 200:
                            # Request acceptance is unknown for upstream server failures.
                            raise WebTransportError('Bridge HTTP %s; ตรวจหน้า ChatGPT ก่อนส่งซ้ำ' % response.status_code)
                        if 'text/event-stream' not in response.headers.get('Content-Type', ''):
                            result = completed_text(response.json())
                        else:
                            response.encoding = 'utf-8'
                            data = []
                            result = None
                            for line in response.iter_lines(decode_unicode=True, chunk_size=1):
                                if cancelled():
                                    raise WebTransportError('ยกเลิกงาน Web แล้ว ผลที่มาภายหลังจะไม่ถูกนำเข้า; ตรวจหน้า ChatGPT ก่อนเริ่มใหม่')
                                if time.monotonic() - started > cfg['timeout']:
                                    raise WebTransportError('Web timeout; ไม่ส่งข้อความซ้ำอัตโนมัติ')
                                if line.startswith('data:'):
                                    data.append(line[5:].lstrip())
                                elif not line and data:
                                    raw = '\n'.join(data)
                                    data = []
                                    if raw == '[DONE]':
                                        break
                                    event = json.loads(raw)
                                    kind = event.get('type')
                                    if kind in ('error', 'response.failed', 'response.incomplete'):
                                        raise WebTransportError('Bridge ไม่สามารถสร้างคำตอบที่สมบูรณ์ได้; ตรวจหน้า ChatGPT')
                                    if kind == 'response.completed':
                                        result = completed_text(event.get('response'))
                                        break
                            if result is None:
                                raise WebTransportError('Web stream ended without response.completed; ไม่ส่งซ้ำอัตโนมัติ')
                        if cancelled():
                            raise WebTransportError('Web job cancelled; late answer discarded')
                        # Keep completed answers even if later UI validation or saving fails.
                        atomic_json(state_dir() / 'results' / (body['input'][0]['id'] + '.json'),
                                    {'request_id': body['input'][0]['id'], 'model': cfg['model'],
                                     'reply': result, 'completed': time.time()})
                        pending.unlink()
                        return result
            except WebTransportError as error:
                self._record_failure(pending, error)
                raise
            except Exception as error:
                self._record_failure(pending, error)
                raise WebTransportError('การเชื่อมต่อ Web ขัดข้องหรือยังไม่ทราบผล; ตรวจหน้า ChatGPT ก่อนส่งใหม่ (%s)' % type(error).__name__) from error

    @staticmethod
    def _record_failure(pending, error):
        # Diagnostic writes must never hide the original error or erase its journal.
        try:
            value = json.loads(pending.read_text(encoding='utf-8'))
            value.update(state='unknown', failed=time.time(),
                         last_error=str(error)[:500] if isinstance(error, WebTransportError)
                         else type(error).__name__)
            atomic_json(pending, value)
        except (OSError, ValueError, TypeError):
            pass

