import time
import requests

APP_NAME = "Telnyx Bulk SMS Sender"
URL = "https://api.telnyx.com/v2/messages"


def main():
    print("=" * 55)
    print(f"        {APP_NAME}")
    print("=" * 55)
    print("Use only for recipients who have consented to receive your messages.\n")

    api_key = input("[+] Telnyx API Key: ").strip()
    if not api_key:
        print("[-] Error: API Key is required.")
        return

    from_number = input("[+] Sending number (example +12025550199): ").strip()
    if not from_number:
        print("[-] Error: sending number is required.")
        return

    print("\n" + "-" * 55)
    message_body = input("[+] Message text:\n> ").strip()
    if not message_body:
        print("[-] Error: message cannot be empty.")
        return

    print("\n" + "-" * 55)
    print("[+] Enter recipient numbers with country code, separated by commas.")
    raw_numbers = input("> ")
    numbers = [n.strip() for n in raw_numbers.split(",") if n.strip()]

    if not numbers:
        print("[-] Error: no recipient numbers were entered.")
        return

    print("\n" + "=" * 55)
    print("[*] Operation summary")
    print(f"    Recipients: {len(numbers)}")
    print(f"    From:       {from_number}")
    print(f"    Message:    {message_body}")
    print("=" * 55)

    confirm = input("\nStart sending? (y/n): ").strip().lower()
    if confirm != "y":
        print("[!] Operation cancelled.")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    print("\n[>] Sending...\n" + "-" * 55)
    success_count = 0
    fail_count = 0

    for index, number in enumerate(numbers, 1):
        payload = {"from": from_number, "to": number, "text": message_body}
        try:
            response = requests.post(URL, json=payload, headers=headers, timeout=10)
            if response.status_code in (200, 201, 202):
                data = response.json()
                msg_id = data.get("data", {}).get("id", "N/A")
                print(f"[{index}/{len(numbers)}] OK  {number} (ID: {msg_id})")
                success_count += 1
            else:
                detail = response.text
                try:
                    errors = response.json().get("errors", [])
                    if errors:
                        detail = errors[0].get("detail", detail)
                except Exception:
                    pass
                print(f"[{index}/{len(numbers)}] FAIL {number} | {detail}")
                fail_count += 1
        except requests.RequestException as exc:
            print(f"[{index}/{len(numbers)}] FAIL {number} | connection error: {exc}")
            fail_count += 1
        except Exception as exc:
            print(f"[{index}/{len(numbers)}] FAIL {number} | {exc}")
            fail_count += 1

        time.sleep(0.5)

    print("-" * 55)
    print(f"[RESULT] {success_count} successful | {fail_count} failed")
    print("=" * 55)
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
