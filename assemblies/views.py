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


@login_required
def dashboard(request, assembly_id):
    from datetime import date
    from django.db.models import Q
    from members.models import MembershipPeriod

    assembly = get_object_or_404(Assembly, pk=assembly_id)

    senior_member_pks = MembershipPeriod.objects.filter(
        membership_type='senior',
        start_date__lte=date.today(),
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=date.today())
    ).values_list('member_id', flat=True)

    agendas_data = []
    for agenda in assembly.agendas.all():
        questions_data = []
        for question in agenda.questions.all():
            abstention_option = question.option_set.abstention_option
            all_votes = question.votes.all()
            total_votes = all_votes.count()

            votes_for_percentage = all_votes.exclude(option=abstention_option) if abstention_option else all_votes
            total_for_percentage = votes_for_percentage.count()

            senior_votes_qs = Vote.objects.filter(
                question=question,
                on_behalf_of__in=senior_member_pks
            )
            total_senior_votes = senior_votes_qs.count()
            senior_votes_for_percentage = senior_votes_qs.exclude(option=abstention_option) if abstention_option else senior_votes_qs
            total_senior_for_percentage = senior_votes_for_percentage.count()

            results_data = []
            for option in question.option_set.options.all():
                count = all_votes.filter(option=option).count()
                senior_count = senior_votes_qs.filter(option=option).count()
                is_abstention = abstention_option and option.pk == abstention_option.pk

                percentage = None if is_abstention else (
                    round((count / total_for_percentage * 100), 1) if total_for_percentage > 0 else 0
                )
                senior_percentage = None if is_abstention else (
                    round((senior_count / total_senior_for_percentage * 100), 1) if total_senior_for_percentage > 0 else 0
                )

                results_data.append({
                    'option': option,
                    'count': count,
                    'percentage': percentage,
                    'senior_count': senior_count,
                    'senior_percentage': senior_percentage,
                    'is_abstention': is_abstention,
                })

            questions_data.append({
                'question': question,
                'total_votes': total_votes,
                'total_senior_votes': total_senior_votes,
                'results_data': results_data,
            })

        agendas_data.append({
            'agenda': agenda,
            'questions': questions_data,
        })

    return render(request, 'voting/dashboard.html', {
        'assembly': assembly,
        'agendas_data': agendas_data,
    })