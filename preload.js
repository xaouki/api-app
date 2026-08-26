const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('desktopAPI', {
  openExternal: (url) => ipcRenderer.invoke('open-external', url)
});
