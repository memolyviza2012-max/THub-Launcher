"""Prepare the installed local Bridge from a translation worker, never the Qt thread."""
import os
from pathlib import Path
import subprocess
import time

import requests

from .contracts import WebTransportError


def health(endpoint):
    with requests.Session() as session:
        session.trust_env = False
        with session.get(endpoint.removesuffix('/v1') + '/healthz', timeout=(2, 3),
                         allow_redirects=False) as response:
            response.raise_for_status()
            value = response.json()
    if value.get('service') != 'codex-chatgpt-web' or value.get('mode') != 'browser-only':
        raise WebTransportError('Bridge ที่พอร์ตนี้ไม่ใช่ ChatGPT Web กรุณาเปิด Codex Web GPT')
    return value


def start_installed(endpoint):
    # Never launch an arbitrary executable from a configurable endpoint or HTTP response.
    if os.name != 'nt' or endpoint != 'http://127.0.0.1:17841/v1':
        raise WebTransportError('เชื่อมต่อ ChatGPT Web ไม่ได้ กรุณาเปิด Codex Web GPT แล้วกดแปลอีกครั้ง')
    home = Path.home() / '.codex-chatgpt-web'
    app = Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs/Codex Web GPT/Codex Web GPT.exe'
    runtime = home / 'versions/6.1.9-win32-x64'
    bun, cli = runtime / 'runtime/bun.exe', runtime / 'app/cli.js'
    if not all(path.is_file() for path in (app, bun, cli, home / 'config.json')):
        raise WebTransportError('ยังไม่พบ ChatGPT Web ที่ติดตั้ง กรุณาเปิด Codex Web GPT เพื่อตั้งค่าครั้งแรก')
    flags = subprocess.CREATE_NO_WINDOW
    subprocess.Popen([str(app), '--hidden'], creationflags=flags,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # The launcher may start its own backend. Give it time before starting a fallback.
    return bun, cli


def ensure_ready(endpoint, cancelled=lambda: False):
    try:
        value = health(endpoint)
    except (requests.RequestException, ValueError):
        bun, cli = start_installed(endpoint)
        deadline = time.monotonic() + 25
        launched = False
        while time.monotonic() < deadline:
            if cancelled():
                raise WebTransportError('ยกเลิกก่อนส่งงาน Web')
            try:
                value = health(endpoint)
                break
            except (requests.RequestException, ValueError):
                if not launched and time.monotonic() > deadline - 20:
                    subprocess.Popen([str(bun), str(cli), 'serve'],
                                     creationflags=subprocess.CREATE_NO_WINDOW,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    launched = True
                time.sleep(0.25)
        else:
            raise WebTransportError('เปิด ChatGPT Web ไม่สำเร็จ กรุณาเปิด Codex Web GPT แล้วกดแปลอีกครั้ง')
    if not value.get('accepting_turns'):
        raise WebTransportError('ChatGPT Web กำลังปิดหรืออัปเดต กรุณารอสักครู่แล้วกดแปลอีกครั้ง')
    return value


def wait_idle(endpoint, timeout, cancelled=lambda: False):
    deadline = time.monotonic() + timeout
    idle_checks = 0
    while time.monotonic() < deadline:
        if cancelled():
            raise WebTransportError('ยกเลิกก่อนส่งงาน Web')
        value = ensure_ready(endpoint, cancelled)
        # Missing counters are not proof that an older Bridge has stopped.
        idle = (type(value.get('active_http_turns')) is int and value['active_http_turns'] == 0
                and type(value.get('active_browser_turns')) is int and value['active_browser_turns'] == 0)
        idle_checks = idle_checks + 1 if idle else 0
        if idle_checks >= 2:
            return
        time.sleep(0.25)
    raise WebTransportError('ChatGPT Web ยังทำงานเดิมอยู่ กรุณารอแล้วกดแปลอีกครั้ง')
