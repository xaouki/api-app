import './style.css';
import { getCountries, getCountryCallingCode, parsePhoneNumberFromString } from 'libphonenumber-js';

const API_URL = 'https://rest.moceanapi.com/rest/2/sms';
const countryNames = new Intl.DisplayNames(['en'], { type: 'region' });

const app = document.querySelector('#app');
const countries = getCountries().map((iso) => ({
  iso,
  name: countryNames.of(iso) || iso,
  code: `+${getCountryCallingCode(iso)}`
})).sort((a, b) => a.name.localeCompare(b.name));

app.innerHTML = `
  <main class="shell">
    <header class="topbar">
      <div class="brand"><div class="logo">M</div><div><h1>Maine SMS API Sender</h1><p>Simple international SMS sending</p></div></div>
      <button id="clear" class="ghost">Clear</button>
    </header>

    <section class="card">
      <h2>API connection</h2>
      <label>API Token<input id="token" type="password" autocomplete="off" placeholder="Paste your API token" /></label>
      <label>Company / Sender Name<input id="sender" maxlength="15" placeholder="YourCompany" /></label>
    </section>

    <section class="card">
      <div class="section-head"><h2>Recipients</h2><span id="count" class="pill">0 numbers</span></div>
      <label>Country for local numbers
        <select id="country">${countries.map(c => `<option value="${c.iso}">${c.name} (${c.code})</option>`).join('')}</select>
      </label>
      <label>Phone numbers
        <textarea id="numbers" rows="7" placeholder="+212600000000\n+12025550123\n+447700900123"></textarea>
      </label>
      <p class="hint">International numbers must start with + and include the country code. Local numbers are converted using the selected country.</p>
      <div id="validation" class="validation"></div>
    </section>

    <section class="card">
      <h2>Message</h2>
      <textarea id="message" rows="5" maxlength="1600" placeholder="Write your SMS message..."></textarea>
      <div class="counter"><span>Sequential sending: one number at a time</span><span id="chars">0 / 1600</span></div>
    </section>

    <section class="actions">
      <button id="start" class="primary">START SENDING</button>
      <button id="pause" class="secondary" disabled>PAUSE</button>
      <button id="stop" class="danger" disabled>STOP</button>
    </section>

    <section class="card progress-card">
      <div class="stats"><div><b id="done">0</b><span>Sent</span></div><div><b id="failed">0</b><span>Failed</span></div><div><b id="remaining">0</b><span>Remaining</span></div></div>
      <div class="progress"><div id="bar"></div></div>
      <div id="status" class="status">Ready</div>
      <div id="log" class="log"></div>
    </section>

    <footer>Use only with recipients who have consented to receive your messages.</footer>
  </main>
`;

const $ = (id) => document.getElementById(id);
let running = false;
let paused = false;
let stopRequested = false;
let currentNumbers = [];
let sent = 0;
let failed = 0;

function selectedCountry() { return $('country').value; }

function normalize(value) {
  const raw = value.trim().replace(/[\u200B-\u200D\uFEFF]/g, '');
  if (!raw) return null;
  if (raw.startsWith('+')) {
    const phone = parsePhoneNumberFromString(raw);
    return phone?.isValid() ? phone.number : null;
  }
  const phone = parsePhoneNumberFromString(raw, selectedCountry());
  return phone?.isValid() ? phone.number : null;
}

function readNumbers() {
  const lines = $('numbers').value.split(/[\n,;]+/).map(x => x.trim()).filter(Boolean);
  const valid = [];
  const invalid = [];
  const seen = new Set();
  for (const line of lines) {
    const n = normalize(line);
    if (!n) invalid.push(line);
    else if (!seen.has(n)) { seen.add(n); valid.push(n); }
  }
  return { valid, invalid };
}

function refreshValidation() {
  const { valid, invalid } = readNumbers();
  $('count').textContent = `${valid.length} numbers`;
  $('validation').innerHTML = invalid.length
    ? `<span class="bad">${invalid.length} invalid/duplicate input(s) will be skipped.</span>`
    : `<span class="good">${valid.length ? 'All numbers are valid.' : 'Add recipient numbers above.'}</span>`;
  return valid;
}

function log(message, type = '') {
  const row = document.createElement('div');
  row.className = `log-row ${type}`;
  row.textContent = message;
  $('log').prepend(row);
}

function updateStats() {
  $('done').textContent = sent;
  $('failed').textContent = failed;
  $('remaining').textContent = Math.max(currentNumbers.length - sent - failed, 0);
  const total = currentNumbers.length || 1;
  $('bar').style.width = `${Math.min(((sent + failed) / total) * 100, 100)}%`;
}

async function sendOne(token, sender, recipient, message) {
  const body = new URLSearchParams({
    'mocean-to': recipient.replace('+', ''),
    'mocean-from': sender,
    'mocean-text': message,
    'mocean-resp-format': 'json'
  });
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/x-www-form-urlencoded' },
    body
  });
  let data = null;
  try { data = await response.json(); } catch { data = {}; }
  const msg = data?.messages?.[0];
  const ok = response.ok && ((msg && Number(msg.status) === 0) || (!msg && Number(data?.status) === 0));
  if (!ok) throw new Error(msg?.err_msg || data?.err_msg || `API HTTP ${response.status}`);
  return data;
}

async function startSending() {
  if (running) return;
  const token = $('token').value.trim();
  const sender = $('sender').value.trim();
  const message = $('message').value;
  currentNumbers = refreshValidation();
  if (!token || !sender || !message.trim()) return alert('Token, sender name and message are required.');
  if (!currentNumbers.length) return alert('Add at least one valid phone number.');
  if (sender.length > 15) return alert('Sender name must be 15 characters or fewer.');

  running = true; paused = false; stopRequested = false; sent = 0; failed = 0;
  $('start').disabled = true; $('pause').disabled = false; $('stop').disabled = false; $('log').innerHTML = '';
  updateStats();

  for (const number of currentNumbers) {
    while (paused && !stopRequested) {
      $('status').textContent = 'Paused';
      await new Promise(r => setTimeout(r, 250));
    }
    if (stopRequested) break;
    $('status').textContent = `Sending to ${number}...`;
    try {
      await sendOne(token, sender, number, message);
      sent++;
      log(`✓ Sent — ${number}`, 'success');
    } catch (error) {
      failed++;
      log(`✕ Failed — ${number} — ${error.message}`, 'error');
    }
    updateStats();
  }

  running = false; paused = false; stopRequested = false;
  $('start').disabled = false; $('pause').disabled = true; $('stop').disabled = true;
  $('pause').textContent = 'PAUSE';
  $('status').textContent = sent + failed === currentNumbers.length ? 'Finished' : 'Stopped';
}

$('numbers').addEventListener('input', refreshValidation);
$('country').addEventListener('change', refreshValidation);
$('message').addEventListener('input', () => $('chars').textContent = `${$('message').value.length} / 1600`);
$('start').addEventListener('click', startSending);
$('pause').addEventListener('click', () => { if (running) { paused = !paused; $('pause').textContent = paused ? 'RESUME' : 'PAUSE'; $('status').textContent = paused ? 'Paused' : 'Sending...'; } });
$('stop').addEventListener('click', () => { stopRequested = true; paused = false; });
$('clear').addEventListener('click', () => { if (running) return; $('numbers').value = ''; $('message').value = ''; $('token').value = ''; $('sender').value = ''; refreshValidation(); $('chars').textContent = '0 / 1600'; $('status').textContent = 'Ready'; });
refreshValidation();
