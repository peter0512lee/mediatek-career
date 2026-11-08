'use strict';
// LG v1 is a teaching format, not a vendor trace decoder.
const sampleHex = '4c 47 01 02 02 00 01 00 01 00 00 00 e8 03 00 00 34 12';
function decodeHex(input) {
  const compact = input.replace(/\s/g, '');
  if (!compact || compact.length % 2 || /[^0-9a-f]/i.test(compact)) return '輸入錯誤：請輸入成對的 hex bytes，只使用 0–9、a–f 與空白。';
  if (compact.length > 4096) return '輸入過長：此單筆練習最多接受 2048 bytes。';
  const bytes = Uint8Array.from(compact.match(/../g), pair => parseInt(pair, 16));
  if (bytes.length < 16) return `NEED_MORE：header 需要 16 bytes，目前只有 ${bytes.length}。`;
  const view = new DataView(bytes.buffer);
  if (bytes[0] !== 0x4c || bytes[1] !== 0x47) return 'INVALID：magic 必須是 4c 47（LG）。';
  if (bytes[2] !== 1) return `INVALID：不支援 version ${bytes[2]}。`;
  if (bytes[3] > 3) return 'INVALID：level 必須為 0–3。';
  const length = view.getUint16(4, true), event = view.getUint16(6, true);
  if (length > 32) return 'INVALID：payload 超過 32 bytes 上限。';
  if (bytes.length - 16 < length) return `NEED_MORE：payload 需要 ${length} bytes，目前只有 ${bytes.length - 16}。`;
  if ((event === 1 && length !== 2) || (event === 2 && (length !== 1 || bytes[16] > 1))) return 'INVALID：已知 event 的 payload 不符合 schema。';
  let payload;
  if (event === 1) payload = `MEASUREMENT value=${view.getUint16(16, true)}`;
  else if (event === 2) payload = `STATE value=${bytes[16]}`;
  else payload = 'UNKNOWN payload=' + [...bytes.slice(16, 16 + length)].map(b => b.toString(16).padStart(2, '0')).join('');
  return `OK · LG v1\nsequence = ${view.getUint32(8, true)}\ntimestamp_ms = ${view.getUint32(12, true)}\nlevel = ${bytes[3]} · event_id = ${event} · payload_length = ${length}\n${payload}` + (bytes.length > 16 + length ? `\n剩餘 ${bytes.length - 16 - length} bytes，可能是下一筆；本工具只解析第一筆。` : '');
}
const hexInput = document.getElementById('hex-input');
if (hexInput) {
  const show = () => { document.getElementById('hex-result').textContent = decodeHex(hexInput.value); };
  document.getElementById('decode-hex').addEventListener('click', show);
  document.getElementById('truncate-hex').addEventListener('click', () => { hexInput.value = sampleHex.slice(0, -3); show(); });
  document.getElementById('reset-hex').addEventListener('click', () => { hexInput.value = sampleHex; show(); });
}
const slots = document.getElementById('queue-slots');
if (slots) {
  let values, head, tail, count, produced, consumed, dropped;
  const render = (message = '') => {
    slots.replaceChildren();
    values.forEach((value, index) => {
      const cell = document.createElement('div');
      cell.className = 'queue-slot' + (value !== null ? ' filled' : '');
      const label = document.createElement('small'); label.textContent = `slot ${index}`;
      const number = document.createElement('strong'); number.textContent = value === null ? '—' : String(value);
      cell.append(label, number); slots.append(cell);
    });
    document.getElementById('queue-status').textContent = `produced=${produced} · queued=${count} · consumed=${consumed} · dropped=${dropped} · head=${head} · tail=${tail}${message ? '\n' + message : ''}`;
  };
  const reset = () => { values = [null, null, null, null]; head = tail = count = produced = consumed = dropped = 0; render(); };
  document.getElementById('queue-push').addEventListener('click', () => {
    produced++;
    if (count === 4) { dropped++; render(`queue 已滿，丟棄新事件 ${produced}。`); return; }
    values[head] = produced; head = (head + 1) % 4; count++; render();
  });
  document.getElementById('queue-pop').addEventListener('click', () => {
    if (!count) { render('queue 為空，沒有可消費的事件。'); return; }
    const value = values[tail]; values[tail] = null; tail = (tail + 1) % 4; count--; consumed++; render(`已消費事件 ${value}。`);
  });
  document.getElementById('queue-reset').addEventListener('click', reset);
  reset();
}
