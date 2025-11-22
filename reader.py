# reader.py


from typing import Dict, List, Optional, Tuple
from googleapiclient.errors import HttpError


from auth import GmailAuth
from utils import get_header, extract_plain_text_from_payload




class GmailReader:
    """
    Reads emails:
      - fetch_last_n: last n recent inbox mails (with optional mark-as-read)
      - fetch_last_n_by_email: last n mails filtered by an email address
      - reply_to_one_of_last_n: convenience reply by index among last n
    """


    def __init__(self, auth: GmailAuth):
        self.service = auth.get_service()


    def _print_message_summary(self, msg: Dict):
        payload = msg.get("payload", {})
        headers = payload.get("headers", [])
        frm = get_header(headers, "From")
        subject = get_header(headers, "Subject")
        date = get_header(headers, "Date")
        snippet = msg.get("snippet", "")
        body_text = extract_plain_text_from_payload(payload)


        print(f"🆔 ID: {msg.get('id')}")
        print(f"📨 From: {frm}")
        print(f"🧾 Subject: {subject}")
        print(f"🗓  Date: {date}")
        print(f"🔎 Snippet: {snippet}")
        if body_text:
            preview = body_text if len(body_text) <= 1200 else body_text[:1200] + "\n…(truncated)…"
            print("— Body (plain text):")
            print(preview)
        else:
            print("— Body: (no plain-text part found)")
        print("-" * 60)


    def _fetch_full_messages(self, ids: List[str]) -> List[Dict]:
        full_msgs: List[Dict] = []
        for mid in ids:
            try:
                m = self.service.users().messages().get(userId="me", id=mid, format="full").execute()
                m["id"] = mid  # keep at top level
                full_msgs.append(m)
            except HttpError as e:
                print(f"⚠️ Could not fetch {mid}: {e}")
        return full_msgs


    # -------- Feature 1: Fetch last n mails (with reply capability) --------
    def fetch_last_n(self, n: int = 5, mark_as_read: bool = False) -> List[Dict]:
        try:
            listed = self.service.users().messages().list(userId="me", q="in:inbox", maxResults=n).execute()
            msgs_meta = listed.get("messages", []) or []
            if not msgs_meta:
                print("📭 No messages found.")
                return []


            ids = [m["id"] for m in msgs_meta]
            full_msgs = self._fetch_full_messages(ids)


            for msg in full_msgs:
                self._print_message_summary(msg)
                if mark_as_read and "UNREAD" in msg.get("labelIds", []):
                    try:
                        self.service.users().messages().modify(
                            userId="me", id=msg["id"], body={"removeLabelIds": ["UNREAD"], "addLabelIds": []}
                        ).execute()
                    except HttpError as e:
                        print(f"⚠️ Could not mark as read for {msg['id']}: {e}")


            return full_msgs
        except HttpError as e:
            print(f"❌ Read error: {e}")
            return []


    # Convenience reply by index among last n
    def reply_to_one_of_last_n(self, n: int, which_index: int, reply_text: str) -> Optional[str]:
        from sender import GmailSender  # import here to avoid circulars at module load
        sender = GmailSender(GmailAuth())  # reuse auth


        messages = self.fetch_last_n(n=n, mark_as_read=False)
        if not messages:
            print("No messages to reply to.")
            return None


        if which_index < 1 or which_index > len(messages):
            print("Invalid index.")
            return None


        original_id = messages[which_index - 1].get("id")
        if not original_id:
            print("Missing message ID.")
            return None


        return sender.reply(original_message_id=original_id, reply_text=reply_text)


    # -------- Feature 2: Fetch last n mails filtered by an email address --------
    def fetch_last_n_by_email(self, email_address: str, n: int = 5, mark_as_read: bool = False) -> List[Dict]:
        if not email_address:
            print("Please provide an email address.")
            return []


        query = f'(from:{email_address}) OR (to:{email_address})'
        try:
            listed = self.service.users().messages().list(userId="me", q=query, maxResults=n).execute()
            msgs_meta = listed.get("messages", []) or []
            if not msgs_meta:
                print("📭 No messages found for that address.")
                return []


            ids = [m["id"] for m in msgs_meta]
            full_msgs = self._fetch_full_messages(ids)


            for msg in full_msgs:
                self._print_message_summary(msg)
                if mark_as_read and "UNREAD" in msg.get("labelIds", []):
                    try:
                        self.service.users().messages().modify(
                            userId="me", id=msg["id"], body={"removeLabelIds": ["UNREAD"], "addLabelIds": []}
                        ).execute()
                    except HttpError as e:
                        print(f"⚠️ Could not mark as read for {msg['id']}: {e}")


            return full_msgs
        except HttpError as e:
            print(f"❌ Read error: {e}")
            return []
