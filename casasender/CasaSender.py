import tkinter as tk
from tkinter import ttk, messagebox
import threading, time, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests

PROVIDERS = {
    "Telnyx": ["api_key"], "Twilio": ["account_sid", "auth_token"],
    "Vonage (Nexmo)": ["api_key", "api_secret"], "Plivo": ["auth_id", "auth_token"],
    "MoceanAPI": ["api_key", "api_secret"], "Infobip": ["base_url", "api_key"],
    "ClickSend": ["username", "api_key"], "MessageBird (Bird)": ["api_key"],
    "TextMagic": ["username", "api_key"], "Sinch": ["service_plan_id", "api_token"],
    "SMSGlobal": ["api_key", "secret_key"], "Amazon SNS": ["access_key", "secret_key", "region"]
}
LABELS = {
 "api_key":"API Key / Access Key", "api_secret":"API Secret", "account_sid":"Account SID",
 "auth_token":"Auth Token", "auth_id":"Auth ID", "base_url":"Base URL",
 "username":"Username", "service_plan_id":"Service Plan ID", "api_token":"API Token",
 "secret_key":"Secret Key", "region":"AWS Region"
}

def post(provider, c, f, t, text):
    if provider == "Telnyx":
        r=requests.post("https://api.telnyx.com/v2/messages",json={"from":f,"to":t,"text":text},headers={"Authorization":f"Bearer {c['api_key']}","Content-Type":"application/json"},timeout=15)
        return r.ok, r.text
    if provider == "Twilio":
        r=requests.post(f"https://api.twilio.com/2010-04-01/Accounts/{c['account_sid']}/Messages.json",data={"From":f,"To":t,"Body":text},auth=(c['account_sid'],c['auth_token']),timeout=15)
        return r.ok, r.text
    if provider == "Vonage (Nexmo)":
        r=requests.post("https://rest.nexmo.com/sms/json",data={"api_key":c['api_key'],"api_secret":c['api_secret'],"from":f,"to":t,"text":text},timeout=15)
        try: ok=r.ok and r.json().get('messages',[{}])[0].get('status')=='0'
        except: ok=r.ok
        return ok,r.text
    if provider == "Plivo":
        r=requests.post(f"https://api.plivo.com/v1/Account/{c['auth_id']}/Message/",json={"src":f,"dst":t,"text":text},auth=(c['auth_id'],c['auth_token']),timeout=15)
        return r.ok,r.text
    if provider == "MoceanAPI":
        r=requests.post("https://rest.moceanapi.com/rest/1/sms",data={"mocean-api-key":c['api_key'],"mocean-api-secret":c['api_secret'],"mocean-from":f,"mocean-to":t,"mocean-text":text,"mocean-resp-format":"json"},timeout=15)
        try: ok=r.ok and r.json().get('messages',[{}])[0].get('status')==0
        except: ok=r.ok
        return ok,r.text
    if provider == "Infobip":
        r=requests.post(c['base_url'].rstrip('/')+"/sms/2/text/single",json={"from":f,"to":t,"text":text},headers={"Authorization":f"App {c['api_key']}","Content-Type":"application/json"},timeout=15)
        return r.ok,r.text
    if provider == "ClickSend":
        r=requests.post("https://rest.clicksend.com/v3/sms/send",json={"messages":[{"source":"CasaSender","from":f,"to":t,"body":text}]},auth=(c['username'],c['api_key']),timeout=15)
        return r.ok,r.text
    if provider == "MessageBird (Bird)":
        r=requests.post("https://rest.messagebird.com/messages",json={"originator":f,"recipients":[t],"body":text},headers={"Authorization":f"AccessKey {c['api_key']}"},timeout=15)
        return r.ok,r.text
    if provider == "TextMagic":
        r=requests.post("https://rest.textmagic.com/api/v2/messages",data={"text":text,"phones":t,"from":f},headers={"X-TM-Username":c['username'],"X-TM-Key":c['api_key']},timeout=15)
        return r.ok,r.text
    if provider == "Sinch":
        r=requests.post(f"https://us.sms.api.sinch.com/xms/v1/{c['service_plan_id']}/batches",json={"from":f,"to":[t],"body":text},headers={"Authorization":f"Bearer {c['api_token']}","Content-Type":"application/json"},timeout=15)
        return r.ok,r.text
    if provider == "SMSGlobal":
        r=requests.post("https://api.smsglobal.com/v2/sms",json={"from":f,"to":t,"message":text},headers={"Authorization":f"Bearer {c['api_key']}","Content-Type":"application/json"},timeout=15)
        return r.ok,r.text
    return False,"Amazon SNS requires AWS SDK integration"

class App:
    def __init__(self, root):
        self.root=root; root.title("CasaSender v2.0"); root.geometry("820x720"); root.minsize(720,600)
        style=ttk.Style(); style.configure("TButton",padding=7); style.configure("Header.TLabel",font=("Segoe UI",20,"bold"))
        ttk.Label(root,text="CasaSender v2.0",style="Header.TLabel").pack(pady=(15,2)); ttk.Label(root,text="SMS & Email Desktop Sender").pack(pady=(0,12))
        self.nb=ttk.Notebook(root); self.nb.pack(fill="both",expand=True,padx=14,pady=8)
        self.sms=ttk.Frame(self.nb,padding=12); self.email=ttk.Frame(self.nb,padding=12); self.nb.add(self.sms,text="SMS"); self.nb.add(self.email,text="Email SMTP")
        self.build_sms(); self.build_email()
    def build_sms(self):
        self.provider=tk.StringVar(value="Telnyx"); self.creds={}
        top=ttk.Frame(self.sms); top.pack(fill="x"); ttk.Label(top,text="Provider").pack(side="left"); cb=ttk.Combobox(top,textvariable=self.provider,values=list(PROVIDERS),state="readonly",width=25); cb.pack(side="left",padx=8); cb.bind("<<ComboboxSelected>>",lambda e:self.fields())
        self.cf=ttk.LabelFrame(self.sms,text="Credentials",padding=8); self.cf.pack(fill="x",pady=8); self.fields()
        self.fromv=tk.StringVar(); ttk.Label(self.sms,text="From / Sender").pack(anchor="w"); ttk.Entry(self.sms,textvariable=self.fromv).pack(fill="x")
        ttk.Label(self.sms,text="Recipients (one per line or comma-separated)").pack(anchor="w",pady=(8,2)); self.to=tk.Text(self.sms,height=7); self.to.pack(fill="x")
        ttk.Label(self.sms,text="Message").pack(anchor="w",pady=(8,2)); self.msg=tk.Text(self.sms,height=6); self.msg.pack(fill="x")
        bar=ttk.Frame(self.sms); bar.pack(fill="x",pady=10); self.go=ttk.Button(bar,text="SEND",command=self.start_sms); self.go.pack(side="left"); ttk.Button(bar,text="Clear Log",command=lambda:self.log.delete("1.0","end")).pack(side="left",padx=8)
        self.log= tk.Text(self.sms,height=10); self.log.pack(fill="both",expand=True)
    def fields(self):
        for w in self.cf.winfo_children(): w.destroy()
        self.creds={}
        for k in PROVIDERS[self.provider.get()]:
            ttk.Label(self.cf,text=LABELS.get(k,k)).pack(anchor="w"); e=ttk.Entry(self.cf,show="•" if k not in ('base_url','region') else ""); e.pack(fill="x",pady=(0,5)); self.creds[k]=e
    def start_sms(self):
        if not self.fromv.get().strip() or not self.msg.get("1.0","end").strip() or not self.to.get("1.0","end").strip(): return messagebox.showwarning("CasaSender","Fill sender, recipients and message.")
        nums=[x.strip() for x in self.to.get("1.0","end").replace(',','\n').splitlines() if x.strip()]
        if not messagebox.askyesno("Confirm","Send this message to the listed recipients? Make sure you are authorized to contact them."): return
        c={k:e.get().strip() for k,e in self.creds.items()}; p=self.provider.get(); f=self.fromv.get().strip(); text=self.msg.get("1.0","end").strip(); self.go.config(state="disabled")
        threading.Thread(target=self.sms_worker,args=(p,c,f,nums,text),daemon=True).start()
    def sms_worker(self,p,c,f,nums,text):
        for i,n in enumerate(nums,1):
            try: ok,res=post(p,c,f,n,text)
            except Exception as e: ok,res=False,str(e)
            self.root.after(0,self.write,f"[{i}/{len(nums)}] {'OK' if ok else 'FAIL'} {n} | {res[:250]}\n")
            time.sleep(0.4)
        self.root.after(0,lambda:self.go.config(state="normal"))
    def write(self,s): self.log.insert("end",s); self.log.see("end")
    def build_email(self):
        f=self.email; self.es={}
        fields=[("SMTP Server","smtp"),("Port","port"),("Sender Email","sender"),("Password","password"),("Sender Name","name"),("Subject","subject")]
        for label,key in fields:
            ttk.Label(f,text=label).pack(anchor="w"); e=ttk.Entry(f,show="•" if key=="password" else ""); e.pack(fill="x",pady=(0,5)); self.es[key]=e
        ttk.Label(f,text="Recipients (one per line or comma-separated)").pack(anchor="w"); self.er=ttk.Text(f,height=6); self.er.pack(fill="x")
        ttk.Label(f,text="Email Body").pack(anchor="w",pady=(8,2)); self.eb=ttk.Text(f,height=9); self.eb.pack(fill="both",expand=True)
        self.eg=ttk.Button(f,text="SEND EMAIL",command=self.start_email); self.eg.pack(anchor="w",pady=10); self.elog=tk.Text(f,height=8); self.elog.pack(fill="both",expand=True)
    def start_email(self):
        try: port=int(self.es['port'].get() or 587)
        except: return messagebox.showwarning("CasaSender","SMTP port must be a number.")
        nums=[x.strip() for x in self.er.get("1.0","end").replace(',','\n').splitlines() if x.strip()]
        if not nums: return messagebox.showwarning("CasaSender","Add at least one recipient.")
        if not messagebox.askyesno("Confirm","Send this email to the listed recipients? Make sure you are authorized to contact them."): return
        self.eg.config(state="disabled"); data={k:e.get() for k,e in self.es.items()}; threading.Thread(target=self.email_worker,args=(data,port,nums),daemon=True).start()
    def email_worker(self,d,port,nums):
        try:
            server=smtplib.SMTP(d['smtp'],port,timeout=20); server.starttls(); server.login(d['sender'],d['password'])
            for i,n in enumerate(nums,1):
                m=MIMEMultipart(); m['From']=d['sender']; m['To']=n; m['Subject']=d['subject']; m.attach(MIMEText(self.eb.get('1.0','end').strip(),'plain','utf-8')); server.sendmail(d['sender'],n,m.as_string()); self.root.after(0,self.write_email,f"[{i}/{len(nums)}] OK {n}\n"); time.sleep(.4)
            server.quit()
        except Exception as e: self.root.after(0,self.write_email,f"FAIL | {e}\n")
        self.root.after(0,lambda:self.eg.config(state="normal"))
    def write_email(self,s): self.elog.insert('end',s); self.elog.see('end')

if __name__=='__main__':
    root=tk.Tk(); App(root); root.mainloop()
