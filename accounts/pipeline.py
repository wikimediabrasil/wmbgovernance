from social_core.exceptions import AuthForbidden
from members.models import Member
from auditlog.models import AuditEntry


def check_allowed_username(strategy, details, backend, *args, **kwargs):
    username = details.get('username', '')
    if not Member.objects.filter(wiki_username=username).exists():
        raise AuthForbidden(backend)

def get_username(strategy, details, user=None, *args, **kwargs):
    if user:
        return {"username": user.username}
    return {"username": details['username']}

def log_login(strategy, details, user=None, *args, **kwargs):
    if user is None:
        return

    AuditEntry.log(
        action='user_login',
        actor=str(user),
        payload={
            'wiki_username': details.get('username', ''),
        }
    )

def link_member(strategy, details, user=None, *args, **kwargs):
    if user is None:
        return
    Member.objects.filter(
        wiki_username=user.username,
        user__isnull=True
    ).update(user=user)