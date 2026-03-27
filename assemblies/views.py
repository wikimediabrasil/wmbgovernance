import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Assembly, Agenda, Question
from voting.models import Vote, Proxy
from django.contrib.admin.views.decorators import staff_member_required
from auditlog.utils import verify_chain
from django.http import HttpResponse
from auditlog.models import AuditEntry


@login_required
def assembly_list(request):
    assemblies = Assembly.objects.all()
    return render(request, 'assemblies/assembly_list.html', {'assemblies': assemblies})


@login_required
def assembly_detail(request, assembly_id):
    assembly = get_object_or_404(Assembly, pk=assembly_id)
    agendas = assembly.agendas.prefetch_related('questions').all()
    member = request.user.member

    proxy_as_grantee = Proxy.objects.filter(assembly=assembly, grantee=member).first()
    proxy_as_grantor = Proxy.objects.filter(assembly=assembly, grantor=member).first()


    voted_question_ids = set(
        Vote.objects.filter(
            on_behalf_of=member,
            question__agenda__assembly=assembly
        ).values_list('question_id', flat=True)
    )

    proxy_voted_question_ids = set()
    if proxy_as_grantee:
        proxy_voted_question_ids = set(
            Vote.objects.filter(
                on_behalf_of=proxy_as_grantee.grantor,
                question__agenda__assembly=assembly
            ).values_list('question_id', flat=True)
        )

    grantor_voted_question_ids = set()
    if proxy_as_grantor:
        grantor_voted_question_ids = set(
            Vote.objects.filter(
                on_behalf_of=member,
                question__agenda__assembly=assembly
            ).values_list('question_id', flat=True)
        )

    grantee_voted_for_me_question_ids = set()
    if proxy_as_grantor:
        grantee_voted_for_me_question_ids = set(
            Vote.objects.filter(
                on_behalf_of=member,
                proxy=proxy_as_grantor,
                question__agenda__assembly=assembly
            ).values_list('question_id', flat=True)
        )
    return render(request, 'assemblies/assembly_detail.html', {
        'assembly': assembly,
        'agendas': agendas,
        'voted_question_ids': voted_question_ids,
        'proxy_grantor_voted_question_ids': proxy_voted_question_ids,  # renomeado
        'grantee_voted_for_me_question_ids': grantee_voted_for_me_question_ids,
        'proxy_as_grantee': proxy_as_grantee,
        'proxy_as_grantor': proxy_as_grantor,
        'member': member,
    })


@staff_member_required
def assembly_audit_report(request, assembly_id):
    assembly = get_object_or_404(Assembly, pk=assembly_id)

    # Fetch all entries and filter in Python since payload is encrypted
    all_entries = AuditEntry.objects.order_by('timestamp')
    entries = [
        e for e in all_entries
        if json.loads(e.payload).get('assembly_id') == assembly_id
    ]

    report = {
        'assembly': str(assembly),
        'assembly_id': assembly_id,
        'chain_intact': verify_chain(),
        'entries': [
            {
                'timestamp': e.timestamp.isoformat(),
                'action': e.action,
                'actor': e.actor,
                'payload': json.loads(e.payload),
                'entry_hash': e.entry_hash,
                'previous_hash': e.previous_hash,
            }
            for e in entries
        ]
    }

    response = HttpResponse(
        json.dumps(report, indent=2, ensure_ascii=False),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="audit_{assembly_id}.json"'
    return response