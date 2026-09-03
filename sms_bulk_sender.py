import threading
import time
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from twilio.rest import Client

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class SMSApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SMS Bulk Sender - برنامج إرسال الرسائل")
        self.geometry("600x700")
        self.resizable(False, False)

        self.lbl_title = ctk.CTkLabel(
            self, text="برنامج إرسال الرسائل الجماعية (SMS API)",
            font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_title.pack(pady=15)

        self.frame_api = ctk.CTkFrame(self)
        self.frame_api.pack(padx=20, pady=10, fill="x")

        self.entry_sid = ctk.CTkEntry(self.frame_api, placeholder_text="Twilio Account SID")
        self.entry_sid.pack(padx=10, pady=5, fill="x")
        self.entry_token = ctk.CTkEntry(self.frame_api, placeholder_text="Twilio Auth Token", show="*")
        self.entry_token.pack(padx=10, pady=5, fill="x")
        self.entry_from = ctk.CTkEntry(
            self.frame_api, placeholder_text="رقم الإرسال From Number (e.g., +123456789)")
        self.entry_from.pack(padx=10, pady=5, fill="x")

        self.lbl_msg = ctk.CTkLabel(self, text="نص الرسالة:")
        self.lbl_msg.pack(anchor="w", padx=20, pady=(10, 0))
        self.txt_message = ctk.CTkTextbox(self, height=100)
        self.txt_message.pack(padx=20, pady=5, fill="x")

        self.lbl_numbers = ctk.CTkLabel(
            self, text="الأرقام (ضع رقم بكل سطر أو افصل بينهم بفاصلة):")
        self.lbl_numbers.pack(anchor="w", padx=20, pady=(10, 0))
        self.txt_numbers = ctk.CTkTextbox(self, height=120)
        self.txt_numbers.pack(padx=20, pady=5, fill="x")

        self.btn_send = ctk.CTkButton(
            self, text="بدء الإرسال 🚀",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.start_sending_thread)
        self.btn_send.pack(pady=15)

        self.txt_log = ctk.CTkTextbox(self, height=150, state="disabled")
        self.txt_log.pack(padx=20, pady=5, fill="both", expand=True)

    def log(self, text):
        self.after(0, self._log_ui, text)

    def _log_ui(self, text):
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", text + "\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def start_sending_thread(self):
        threading.Thread(target=self.send_messages, daemon=True).start()

    def send_messages(self):
        sid = self.entry_sid.get().strip()
        token = self.entry_token.get().strip()
        from_num = self.entry_from.get().strip()
        message_body = self.txt_message.get("1.0", "end-1c").strip()
        raw_numbers = self.txt_numbers.get("1.0", "end-1c").strip()

        if not all([sid, token, from_num, message_body, raw_numbers]):
            self.after(0, lambda: messagebox.showerror(
                "خطأ", "يرجى ملء جميع الخانات المتاحة قبل الإرسال!"))
            return

        numbers = raw_numbers.replace("\n", ",").replace(";", ",").split(",")
        numbers = [n.strip() for n in numbers if n.strip()]

        if not numbers:
            self.after(0, lambda: messagebox.showerror("خطأ", "لم يتم العثور على أرقام صالحة!"))
            return

        self.after(0, lambda: self.btn_send.configure(state="disabled"))
        self.log(f"--- بدء عملية الإرسال إلى {len(numbers)} رقم ---")

        try:
            client = Client(sid, token)
        except Exception as e:
            self.log(f"❌ خطأ في الاتصال بالحساب: {e}")
            self.after(0, lambda: self.btn_send.configure(state="normal"))
            return

        success = failed = 0
        for num in numbers:
            try:
                client.messages.create(body=message_body, from_=from_num, to=num)
                self.log(f"✅ تم الإرسال بنجاح إلى {num}")
                success += 1
            except Exception as e:
                self.log(f"❌ فشل الإرسال إلى {num} | السبب: {e}")
                failed += 1
            time.sleep(0.5)

        self.log(f"\n--- اكتملت العملية: {success} نجاح | {failed} فشل ---")
        self.after(0, lambda: self.btn_send.configure(state="normal"))
        self.after(0, lambda: messagebox.showinfo(
            "اكتمل الإرسال", f"تم إرسال الرسائل!\nالناجحة: {success}\nالفاشلة: {failed}"))


if __name__ == "__main__":
    app = SMSApp()
    app.mainloop()
