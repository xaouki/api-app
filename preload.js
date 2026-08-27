const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('desktopAPI', {
  sendMocean: (payload) => ipcRenderer.invoke('mocean-send', payload)
});
