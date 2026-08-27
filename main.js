const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { Client, Mocean } = require('mocean-sdk');

function createWindow() {
  const win = new BrowserWindow({
    width: 1080,
    height: 760,
    minWidth: 900,
    minHeight: 650,
    backgroundColor: '#f6f7fb',
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });
  win.loadFile(path.join(__dirname, 'renderer', 'index.html'));
}

function normalizeNumber(value) {
  const raw = String(value || '').trim();
  let digits = raw.replace(/[^0-9]/g, '');
  if (digits.startsWith('00')) digits = digits.slice(2);
  if (!digits || digits.length < 7 || digits.length > 15) {
    throw new Error('Invalid international phone number');
  }
  return digits;
}

function parseMoceanResponse(response) {
  if (response == null) return { ok: true, raw: response };
  if (typeof response === 'string') {
    try { return parseMoceanResponse(JSON.parse(response)); } catch { return { ok: true, raw: response }; }
  }
  const messages = Array.isArray(response.messages) ? response.messages : [];
  if (messages.length) {
    const first = messages[0];
    const status = Number(first.status);
    return {
      ok: status === 0,
      raw: response,
      message: first.err_msg || (status === 0 ? 'Accepted' : `Mocean status ${first.status}`)
    };
  }
  if (Object.prototype.hasOwnProperty.call(response, 'status')) {
    const status = Number(response.status);
    return { ok: status === 0, raw: response, message: response.err_msg || `Mocean status ${response.status}` };
  }
  return { ok: true, raw: response };
}

ipcMain.handle('mocean-send', async (_, { token, sender, recipient, message }) => {
  if (!token || !sender || !message) throw new Error('Token, Company / Sender Name and message are required');
  const to = normalizeNumber(recipient);
  const from = String(sender).trim();
  if (from.length < 1 || from.length > 15) throw new Error('Sender name/number must be 1–15 characters');

  const client = new Client({ apiToken: String(token).trim() });
  const mocean = new Mocean(client);
  const response = await mocean.sms().send({
    'mocean-from': from,
    'mocean-to': to,
    'mocean-text': String(message)
  });

  const result = parseMoceanResponse(response);
  return { ...result, recipient: to };
});

app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});

app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
