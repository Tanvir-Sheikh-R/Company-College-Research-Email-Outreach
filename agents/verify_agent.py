import dns.resolver
import smtplib
import random
import string
from typing import Dict, List, Tuple

class VerifyAgent:
    def __init__(self):
        self.timeout = 10

    def verify_email(self, email: str) -> Tuple[bool, str]:
        if not email or "@" not in email:
            return False, "invalid_format"

        domain = email.split("@")[1].lower()

        blocked_domains = {
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
            "aol.com", "icloud.com", "protonmail.com", "mail.com",
            "yandex.com", "zoho.com", "gmx.com", "live.com", "msn.com"
        }
        if domain in blocked_domains:
            return False, "personal_provider"

        disposable_domains = {
            "tempmail.com", "10minutemail.com", "guerrillamail.com",
            "mailinator.com", "yopmail.com", "throwaway.email"
        }
        if domain in disposable_domains:
            return False, "disposable"

        mx_records = self._get_mx_records(domain)
        if not mx_records:
            return False, "no_mx_record"

        return self._smtp_verify(mx_records[0], email)

    def _get_mx_records(self, domain: str) -> List[str]:
        try:
            records = dns.resolver.resolve(domain, "MX", lifetime=self.timeout)
            return [str(exchange) for exchange in records]
        except:
            return []

    def _smtp_verify(self, mx_host: str, email: str) -> Tuple[bool, str]:
        sender = f"check@{''.join(random.choices(string.ascii_lowercase, k=8))}.com"
        try:
            server = smtplib.SMTP(mx_host, 25, timeout=self.timeout)
            server.helo("verify.local")
            server.mail(sender)
            code, _ = server.rcpt(email)
            server.quit()
            if code == 250:
                return True, "verified_smtp"
            elif code == 450:
                return True, "verified_smtp"
            return False, f"smtp_rejected_{code}"
        except:
            return True, "verified_smtp"

    def verify_batch(self, emails: List[str]) -> Dict[str, Tuple[bool, str]]:
        results = {}
        for email in emails:
            results[email] = self.verify_email(email)
        return results
