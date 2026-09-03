import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import requests

SMS_PROVIDERS = {
    1: {"name": "Telnyx", "fields": ["api_key"], "labels": {"api_key": "Telnyx API Key (Bearer Token)"}},
    2: {"name": "Twilio", "fields": ["account_sid", "auth_token"], "labels": {"account_sid": "Twilio Account SID", "auth_token": "Twilio Auth Token"}},
    3: {"name": "Vonage (Nexmo)", "fields": ["api_key", "api_secret"], "labels": {"api_key": "Vonage API Key", "api_secret": "Vonage API Secret"}},
    4: {"name": "Plivo", "fields": ["auth_id", "auth_token"], "labels": {"auth_id": "Plivo Auth ID", "auth_token": "Plivo Auth Token"}},
    5: {"name": "MoceanAPI", "fields": ["api_key", "api_secret"], "labels": {"api_key": "MoceanAPI Key", "api_secret": "MoceanAPI Secret"}},
    6: {"name": "Infobip", "fields": ["base_url", "api_key"], "labels": {"base_url": "Infobip Base URL", "api_key": "Infobip API Key"}},
    7: {"name": "ClickSend", "fields": ["username", "api_key"], "labels": {"username": "ClickSend Username", "api_key": "ClickSend API Key"}},
    8: {"name": "MessageBird (Bird)", "fields": ["api_key"], "labels": {"api_key": "MessageBird Access Key"}},
    9: {"name": "TextMagic", "fields": ["username", "api_key"], "labels": {"username": "TextMagic Username", "api_key": "TextMagic API Key"}},
    10: {"name": "Sinch", "fields": ["service_plan_id", "api_token"], "labels": {"service_plan_id": "Sinch Service Plan ID", "api_token": "Sinch API Token"}},
    11: {"name": "SMSGlobal", "fields": ["api_key", "secret_key"], "labels": {"api_key": "SMSGlobal API Key", "secret_key": "SMSGlobal Secret Key"}},
    12: {"name": "Amazon SNS", "fields": ["access_key", "secret_key", "region"], "labels": {"access_key": "AWS Access Key ID", "secret_key": "AWS Secret Access Key", "region": "AWS Region"}},
}

def _post(url, **kwargs):
    return requests.post(url, timeout=10, **kwargs)

def send_sms_telnyx(c, f, t, text):
    r = _post("https://api.telnyx.com/v2/messages", json={"from": f, "to": t, "text": text}, headers={"Authorization": f"Bearer {c['api_key']}", "Content-Type": "application/json"})
    if r.status_code in (200, 201, 202): return True, r.json().get("data", {}).get("id", "OK")
    try: e = r.json().get("errors", [{}])[0].get("detail", r.text)
    except Exception: e = r.text
    return False, f"Telnyx Error [{r.status_code}]: {e}"

def send_sms_twilio(c, f, t, text):
    r = _post(f"https://api.twilio.com/2010-04-01/Accounts/{c['account_sid']}/Messages.json", data={"From": f, "To": t, "Body": text}, auth=(c["account_sid"], c["auth_token"]))
    if r.status_code in (200, 201): return True, r.json().get("sid", "OK")
    try: e = r.json().get("message", r.text)
    except Exception: e = r.text
    return False, f"Twilio Error [{r.status_code}]: {e}"

def send_sms_vonage(c, f, t, text):
    r = _post("https://rest.nexmo.com/sms/json", json={"api_key": c["api_key"], "api_secret": c["api_secret"], "from": f, "to": t, "text": text})
    if r.status_code == 200:
        m = r.json().get("messages", [{}])[0]
        return (True, m.get("message-id", "OK")) if m.get("status") == "0" else (False, f"Vonage Error: {m.get('error-text', 'Unknown Error')}")
    return False, f"Vonage Error [{r.status_code}]: {r.text}"

def send_sms_plivo(c, f, t, text):
    r = _post(f"https://api.plivo.com/v1/Account/{c['auth_id']}/Message/", json={"src": f, "dst": t, "text": text}, auth=(c["auth_id"], c["auth_token"]))
    if r.status_code in (200, 202): return True, r.json().get("message_uuid", ["OK"])[0]
    try: e = r.json().get("error", r.text)
    except Exception: e = r.text
    return False, f"Plivo Error [{r.status_code}]: {e}"

def send_sms_mocean(c, f, t, text):
    r = _post("https://rest.moceanapi.com/rest/1/sms", data={"mocean-api-key": c["api_key"], "mocean-api-secret": c["api_secret"], "mocean-from": f, "mocean-to": t, "mocean-text": text, "mocean-resp-format": "json"})
    if r.status_code == 200:
        m = r.json().get("messages", [{}])
        if m and m[0].get("status") == 0: return True, m[0].get("msgid", "OK")
        return False, f"MoceanAPI Error: {m[0].get('err_msg', r.text) if m else r.text}"
    return False, f"MoceanAPI Error [{r.status_code}]: {r.text}"

def send_sms_infobip(c, f, t, text):
    r = _post(f"{c['base_url'].rstrip('/')}/sms/2/text/single", json={"from": f, "to": t, "text": text}, headers={"Authorization": f"App {c['api_key']}", "Content-Type": "application/json"})
    if r.status_code == 200: return True, "OK"
    try: e = r.json().get("requestError", {}).get("serviceException", {}).get("text", r.text)
    except Exception: e = r.text
    return False, f"Infobip Error [{r.status_code}]: {e}"

def send_sms_clicksend(c, f, t, text):
    r = _post("https://rest.clicksend.com/v3/sms/send", json={"messages": [{"source": "python", "from": f, "to": t, "body": text}]}, auth=(c["username"], c["api_key"]))
    if r.status_code == 200 and r.json().get("http_code") == 200: return True, "OK"
    try: e = r.json().get("response_msg", r.text)
    except Exception: e = r.text
    return False, f"ClickSend Error [{r.status_code}]: {e}"

def send_sms_messagebird(c, f, t, text):
    r = _post("https://rest.messagebird.com/messages", json={"originator": f, "recipients": [t], "body": text}, headers={"Authorization": f"AccessKey {c['api_key']}"})
    if r.status_code in (200, 201): return True, r.json().get("id", "OK")
    try: e = r.json().get("errors", [{}])[0].get("description", r.text)
    except Exception: e = r.text
    return False, f"MessageBird Error [{r.status_code}]: {e}"

def send_sms_textmagic(c, f, t, text):
    r = _post("https://rest.textmagic.com/api/v2/messages", data={"text": text, "phones": t, "from": f}, headers={"X-TM-Username": c["username"], "X-TM-Key": c["api_key"]})
    if r.status_code == 201: return True, r.json().get("id", "OK")
    try: e = r.json().get("message", r.text)
    except Exception: e = r.text
    return False, f"TextMagic Error [{r.status_code}]: {e}"

def send_sms_sinch(c, f, t, text):
    r = _post(f"https://us.sms.api.sinch.com/xms/v1/{c['service_plan_id']}/batches", json={"from": f, "to": [t], "body": text}, headers={"Authorization": f"Bearer {c['api_token']}", "Content-Type": "application/json"})
    if r.status_code in (200, 201): return True, r.json().get("id", "OK")
    try: e = r.json().get("text", r.text)
    except Exception: e = r.text
    return False, f"Sinch Error [{r.status_code}]: {e}"

def send_sms_smsglobal(c, f, t, text):
    r = _post("https://api.smsglobal.com/v2/sms", json={"from": f, "to": t, "message": text}, headers={"Authorization": f"Bearer {c['api_key']}", "Content-Type": "application/json"})
    if r.status_code in (200, 201): return True, "OK"
    return False, f"SMSGlobal Error [{r.status_code}]: {r.text}"

def send_sms_aws_sns(c, f, t, text):
    return False, "AWS SNS requires boto3 integration; this handler is not enabled in this version."

SMS_HANDLERS = {1: send_sms_telnyx, 2: send_sms_twilio, 3: send_sms_vonage, 4: send_sms_plivo, 5: send_sms_mocean, 6: send_sms_infobip, 7: send_sms_clicksend, 8: send_sms_messagebird, 9: send_sms_textmagic, 10: send_sms_sinch, 11: send_sms_smsglobal, 12: send_sms_aws_sns}

def print_banner():
    print("=" * 60)
    print(" 🚀 Welcome to CasaSender v2.0 🚀")
    print(" Ultimate Multi-Channel Communication Platform")
    print("=" * 60)

def handle_sms_flow():
    print("\n--- 📱 CasaSender SMS Engine ---\n")
    for key, p in SMS_PROVIDERS.items(): print(f" [{key}] {p['name']}")
    try: choice = int(input("\nأدخل رقم الشركة المطلوبة: ").strip())
    except ValueError: print("❌ يرجى إدخال رقم صحيح."); return
    if choice not in SMS_PROVIDERS: print("❌ اختيار غير صحيح!"); return
    p = SMS_PROVIDERS[choice]; credentials = {}
    for field in p["fields"]:
        val = input(f"• أدخل {p['labels'][field]}: ").strip()
        if not val: print("❌ البيانات مطلوبة."); return
        credentials[field] = val
    from_number = input("• أدخل رقم/اسم المرسل: ").strip()
    message_text = input("• أدخل نص الرسالة: ").strip()
    recipients = [x.strip() for x in input("• أدخل الأرقام مفصولة بفاصلة: ").split(",") if x.strip()]
    if not from_number or not message_text or not recipients: print("❌ بيانات الإرسال غير مكتملة."); return
    print(f"\n📋 {p['name']} | المرسل: {from_number} | المستلمون: {len(recipients)}")
    if input("هل تريد بدء الإرسال الآن؟ (y/n): ").strip().lower() != "y": return
    ok = fail = 0
    for i, recipient in enumerate(recipients, 1):
        try: success, ref = SMS_HANDLERS[choice](credentials, from_number, recipient, message_text)
        except Exception as e: success, ref = False, str(e)
        if success: ok += 1; print(f"[{i}/{len(recipients)}] ✅ {recipient} | {ref}")
        else: fail += 1; print(f"[{i}/{len(recipients)}] ❌ {recipient} | {ref}")
        time.sleep(0.4)
    print(f"\n📊 النتيجة: {ok} نجاح | {fail} فشل")

def handle_email_flow():
    print("\n--- 📧 CasaSender Email Engine (SMTP) ---")
    smtp_server = input("• أدخل عنوان سيرفر SMTP: ").strip()
    try: smtp_port = int(input("• أدخل البورت (587 أو 465): ").strip())
    except ValueError: print("❌ البورت يجب أن يكون رقماً."); return
    sender_email = input("• أدخل بريد المرسل: ").strip()
    sender_password = input("• أدخل كلمة المرور أو App Password: ").strip()
    sender_name = input("• أدخل اسم المرسل: ").strip()
    subject = input("• أدخل عنوان البريد: ").strip()
    body = input("• أدخل محتوى الرسالة: ").strip()
    recipients = [x.strip() for x in input("• أدخل الإيميلات مفصولة بفاصلة: ").split(",") if x.strip()]
    if not smtp_server or not sender_email or not sender_password or not recipients: print("❌ بيانات البريد غير مكتملة."); return
    ok = fail = 0
    use_ssl = smtp_port == 465
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=12) if use_ssl else smtplib.SMTP(smtp_server, smtp_port, timeout=12)
        if not use_ssl: server.starttls()
        server.login(sender_email, sender_password)
        for i, recipient in enumerate(recipients, 1):
            try:
                msg = MIMEMultipart(); msg["From"] = f"{sender_name} <{sender_email}>" if sender_name else sender_email; msg["To"] = recipient; msg["Subject"] = subject
                msg.attach(MIMEText(body, "html" if "<" in body and ">" in body else "plain", "utf-8"))
                server.sendmail(sender_email, recipient, msg.as_string()); ok += 1; print(f"[{i}/{len(recipients)}] ✅ {recipient}")
            except Exception as e: fail += 1; print(f"[{i}/{len(recipients)}] ❌ {recipient} | {e}")
        server.quit()
    except Exception as e: print(f"❌ SMTP connection/login failed: {e}"); return
    print(f"\n📊 النتيجة: {ok} نجاح | {fail} فشل")

def main():
    print_banner()
    channel = input("\n[1] SMS API\n[2] Email / SMTP\n\nأدخل الاختيار: ").strip()
    if channel == "1": handle_sms_flow()
    elif channel == "2": handle_email_flow()
    else: print("❌ اختيار غير صالح!")

if __name__ == "__main__": main()
