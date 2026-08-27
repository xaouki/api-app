const $ = (id) => document.getElementById(id);

const state = {
  running: false,
  paused: false,
  stop: false,
  index: 0,
  sent: 0,
  failed: 0,
  failedNumbers: [],
  numbers: []
};

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function getNumbers() {
  return $('recipients').value
    .split(/[\n,;\r]+/)
    .map((value) => value.trim())
    .filter(Boolean);
}

function updateCounts() {
  state.numbers = getNumbers();
  const total = state.numbers.length;
  $('recipientCount').textContent = total;
  $('remaining').textContent = Math.max(0, total - state.index);
  $('progressText').textContent = `${Math.min(state.index, total)} / ${total}`;
  $('progressBar').style.width = `${total ? Math.min(100, (state.index / total) * 100) : 0}%`;
  $('sent').textContent = state.sent;
  $('failed').textContent = state.failed;
  $('successRate').textContent = `${state.sent + state.failed ? Math.round((state.sent / (state.sent + state.failed)) * 100) : 0}%`;
}

function log(text, type = 'info') {
  const empty = document.querySelector('.empty');
  if (empty) empty.remove();
  const line = document.createElement('div');
  line.className = `log-line ${type}`;
  line.textContent = `[${new Date().toLocaleTimeString()}] ${text}`;
  $('log').prepend(line);
}

function payload(recipient) {
  return {
    token: $('token').value.trim(),
    sender: $('sender').value.trim(),
    recipient,
    message: $('message').value
  };
}

function validateCommon() {
  if (!$('token').value.trim()) throw new Error('Enter your MoceanAPI Token');
  if (!$('sender').value.trim()) throw new Error('Enter your Company / Sender Name');
  if (!$('message').value.trim()) throw new Error('Enter a message');
}

async function sendOne(recipient) {
  const result = await window.desktopAPI.sendMocean(payload(recipient));
  if (!result.ok) throw new Error(result.message || 'Mocean rejected the message');
  return result;
}

async function sendTest() {
  try {
    validateCommon();
    const number = $('testNumber').value.trim();
    if (!number) throw new Error('Enter a test number');
    $('testSend').disabled = true;
    $('testStatus').textContent = 'Sending...';
    const result = await sendOne(number);
    $('testStatus').textContent = 'Test sent';
    log(`Test accepted: ${result.recipient}`, 'ok');
  } catch (error) {
    $('testStatus').textContent = error.message;
    log(`Test failed — ${error.message}`, 'err');
  } finally {
    $('testSend').disabled = false;
  }
}

async function startCampaign() {
  try {
    validateCommon();
    state.numbers = getNumbers();
    if (!state.numbers.length) throw new Error('Add at least one recipient');

    state.running = true;
    state.paused = false;
    state.stop = false;
    state.index = 0;
    state.sent = 0;
    state.failed = 0;
    state.failedNumbers = [];
    setButtons();
    updateCounts();
    log(`Starting campaign for ${state.numbers.length} recipient(s)`);

    for (; state.index < state.numbers.length; state.index++) {
      if (state.stop) break;
      while (state.paused && !state.stop) await sleep(150);
      if (state.stop) break;

      const recipient = state.numbers[state.index];
      try {
        const result = await sendOne(recipient);
        state.sent++;
        log(`Success: ${result.recipient}`, 'ok');
      } catch (error) {
        state.failed++;
        state.failedNumbers.push(recipient);
        log(`Failed: ${recipient} — ${error.message}`, 'err');
      }

      state.index++;
      updateCounts();
      state.index--;

      if (state.index < state.numbers.length - 1 && !state.stop) {
        await sleep(Math.max(250, Number($('delay').value) || 500));
      }
    }

    if (state.stop) state.index = Math.min(state.index, state.numbers.length);
    else state.index = state.numbers.length;

    state.running = false;
    state.paused = false;
    setButtons();
    updateCounts();
    log(state.stop ? 'Campaign stopped by user' : `Finished — ${state.sent} sent, ${state.failed} failed`, state.failed ? 'err' : 'ok');
  } catch (error) {
    state.running = false;
    setButtons();
    log(error.message, 'err');
  }
}

function setButtons() {
  $('start').disabled = state.running;
  $('pause').disabled = !state.running;
  $('stop').disabled = !state.running;
  $('pause').textContent = state.paused ? 'Resume' : 'Pause';
  $('clearAll').disabled = state.running;
}

$('start').onclick = startCampaign;
$('testSend').onclick = sendTest;
$('pause').onclick = () => {
  state.paused = !state.paused;
  setButtons();
  log(state.paused ? 'Campaign paused' : 'Campaign resumed');
};
$('stop').onclick = () => {
  state.stop = true;
  state.paused = false;
};
$('recipients').oninput = updateCounts;
$('message').oninput = () => {
  $('charCount').textContent = $('message').value.length;
  $('previewText').textContent = $('message').value || 'Your message will appear here.';
};
$('dedupe').onclick = () => {
  $('recipients').value = [...new Set(getNumbers())].join('\n');
  updateCounts();
  log('Duplicate numbers removed');
};
$('fileInput').onchange = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    $('recipients').value += ($('recipients').value.trim() ? '\n' : '') + reader.result;
    updateCounts();
    log(`Imported ${file.name}`);
  };
  reader.readAsText(file);
};
$('clearAll').onclick = () => {
  if (state.running) return;
  $('recipients').value = '';
  $('message').value = '';
  $('testNumber').value = '';
  $('testStatus').textContent = '';
  $('charCount').textContent = '0';
  $('previewText').textContent = 'Your message will appear here.';
  state.index = state.sent = state.failed = 0;
  state.failedNumbers = [];
  $('log').innerHTML = '<div class="empty">Ready when you are.</div>';
  updateCounts();
};
$('exportFailed').onclick = () => {
  if (!state.failedNumbers.length) {
    log('No failed numbers to export');
    return;
  }
  const blob = new Blob([state.failedNumbers.join('\n')], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'failed-numbers.txt';
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};

updateCounts();
setButtons();
