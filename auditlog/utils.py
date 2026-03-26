import hashlib
import json
from .models import AuditEntry


def verify_chain():
    entries = AuditEntry.objects.order_by('timestamp')
    previous_hash = '0' * 64
    for entry in entries:
        raw = json.dumps({
            'action': entry.action,
            'actor': entry.actor,
            'payload': entry.payload,
            'previous_hash': previous_hash,
        }, sort_keys=True, default=str)
        expected_hash = hashlib.sha256(raw.encode()).hexdigest()
        if expected_hash != entry.entry_hash:
            return False
        previous_hash = entry.entry_hash
    return True