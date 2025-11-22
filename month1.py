# main.py


from auth import GmailAuth
from reader import GmailReader
from sender import GmailSender




def main():
    auth = GmailAuth()
    reader = GmailReader(auth)
    sender = GmailSender(auth)


    while True:
        print("\nGmail Utility (Modules & Classes)")
        print("1) Fetch last N mails")
        print("2) Fetch last N mails by email address")
        print("3) Reply to one of the last N mails (by index)")
        print("4) Send an email (with attachments)")
        print("5) Exit")
        choice = input("\nChoose an option (1-5): ").strip()


        if choice == "1":
            try:
                n = int(input("How many messages? ").strip())
            except ValueError:
                n = 5
            mark = input("Mark as read? (y/N): ").strip().lower().startswith("y")
            reader.fetch_last_n(n=n, mark_as_read=mark)


        elif choice == "2":
            email_addr = input("Email address to filter (e.g., alice@example.com): ").strip()
            try:
                n = int(input("How many messages? ").strip())
            except ValueError:
                n = 5
            mark = input("Mark as read? (y/N): ").strip().lower().startswith("y")
            reader.fetch_last_n_by_email(email_address=email_addr, n=n, mark_as_read=mark)


        elif choice == "3":
            try:
                n = int(input("Look at how many recent messages? ").strip())
                idx = int(input("Which index to reply to? (1-based) ").strip())
            except ValueError:
                print("Invalid number.")
                continue
            reply_text = input("Reply text: ").strip()
            reader.reply_to_one_of_last_n(n=n, which_index=idx, reply_text=reply_text)


        elif choice == "4":
            to_addr = input("To: ").strip()
            subject = input("Subject: ").strip()
            body = input("Body: ").strip()
            attach_input = input("Attachments (comma-separated paths, blank for none): ").strip()
            attachments = [p.strip() for p in attach_input.split(",")] if attach_input else []
            sender.send(to=to_addr, subject=subject, body=body, attachments=attachments)


        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")




if __name__ == "__main__":
    main()

print(5)
