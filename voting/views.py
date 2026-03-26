from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.http import Http404
from assemblies.models import Assembly, Question
from voting.models import Vote, Proxy
from auditlog.models import AuditEntry
from voting.forms import VoteForm
from django.utils import timezone


@staff_member_required
def open_question(request, assembly_id, question_id):
    assembly = get_object_or_404(Assembly, pk=assembly_id)
    question = get_object_or_404(Question, pk=question_id, agenda__assembly=assembly)

    question.status = 'open'
    question.opened_at = timezone.now()
    question.save()
    AuditEntry.log(
        action='question_opened',
        actor=str(request.user),
        payload={
            'assembly_id': assembly_id,
            'assembly': str(assembly),
            'question_id': question_id,
            'question': str(question),
        }
    )

    return redirect(reverse('assemblies:assembly_detail', kwargs={'assembly_id': assembly_id}))


@staff_member_required
def hang_question(request, assembly_id, question_id):
    assembly = get_object_or_404(Assembly, pk=assembly_id)
    question = get_object_or_404(Question, pk=question_id, agenda__assembly=assembly)

    question.status = 'pending'
    question.opened_at = question.closed_at = None
    question.save()
    AuditEntry.log(
        action='question_hanged',
        actor=str(request.user),
        payload={
            'assembly_id': assembly_id,
            'assembly': str(assembly),
            'question_id': question_id,
            'question': str(question),
        }
    )

    return redirect(reverse('assemblies:assembly_detail', kwargs={'assembly_id': assembly_id}))


@staff_member_required
def close_question(request, assembly_id, question_id):
    assembly = get_object_or_404(Assembly, pk=assembly_id)
    question = get_object_or_404(Question, pk=question_id, agenda__assembly=assembly)

    question.status = 'closed'
    question.closed_at = timezone.now()
    question.save()
    AuditEntry.log(
        action='question_closed',
        actor=str(request.user),
        payload={
            'assembly_id': assembly_id,
            'assembly': str(assembly),
            'question_id': question_id,
            'question': str(question),
        }
    )

    return redirect(reverse('assemblies:assembly_detail', kwargs={'assembly_id': assembly_id,}))


@login_required
def vote(request, assembly_id, question_id):
    assembly = get_object_or_404(Assembly, pk=assembly_id)
    question = get_object_or_404(Question, pk=question_id, agenda__assembly=assembly)
    member = request.user.member

    if question.status != 'open':
        raise Http404

    already_voted = Vote.objects.filter(
        question=question,
        on_behalf_of=member
    ).exists()

    if already_voted:
        return redirect(reverse('voting:results', kwargs={
            'assembly_id': assembly_id,
            'question_id': question_id
        }))

    if request.method == 'POST':
        form = VoteForm(request.POST, member=member, question=question)
        if form.is_valid():
            form.save()
            AuditEntry.log(
                action='vote_cast',
                actor=str(member),
                payload={
                    'assembly_id': assembly_id,
                    'assembly': str(assembly),
                    'question_id': question_id,
                    'question': str(question),
                    'option': str(form.instance.option.label),
                    'on_behalf_of': str(form.instance.on_behalf_of),
                    'proxy': str(form.instance.proxy) if form.instance.proxy else None,
                }
            )
            return redirect(reverse('voting:results', kwargs={
                'assembly_id': assembly_id,
                'question_id': question_id
            }))
    else:
        form = VoteForm(member=member, question=question)

    return render(request, 'voting/vote.html', {
        'assembly': assembly,
        'question': question,
        'form': form,
    })


@login_required
def edit_vote(request, assembly_id, question_id):
    assembly = get_object_or_404(Assembly, pk=assembly_id)
    question = get_object_or_404(Question, pk=question_id, agenda__assembly=assembly)
    member = request.user.member

    if question.status == 'closed':
        raise Http404

    vote = get_object_or_404(Vote, question=question, on_behalf_of=member)

    if request.method == 'POST':
        form = VoteForm(request.POST, member=member, question=question, instance=vote)
        if form.is_valid():
            form.save()
            AuditEntry.log(
                action='vote_edited',
                actor=str(member),
                payload={
                    'assembly_id': assembly_id,
                    'assembly': str(assembly),
                    'question_id': question_id,
                    'question': str(question),
                    'option': str(form.instance.option.label),
                    'on_behalf_of': str(form.instance.on_behalf_of),
                    'proxy': str(form.instance.proxy) if form.instance.proxy else None,
                }
            )
            return redirect(reverse('voting:results', kwargs={
                'assembly_id': assembly_id,
                'question_id': question_id,
            }))
    else:
        form = VoteForm(member=member, question=question, instance=vote)

    return render(request, 'voting/change_vote.html', {
        'assembly': assembly,
        'question': question,
        'form': form,
        'editing': True,
    })


@login_required
def results(request, assembly_id, question_id):
    from datetime import date
    from django.db.models import Q
    from members.models import MembershipPeriod

    assembly = get_object_or_404(Assembly, pk=assembly_id)
    question = get_object_or_404(Question, pk=question_id, agenda__assembly=assembly)
    member = request.user.member

    options = question.option_set.options.all()
    total_votes = question.votes.count()

    senior_member_pks = MembershipPeriod.objects.filter(
        membership_type='senior',
        start_date__lte=date.today(),
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=date.today())
    ).values_list('member_id', flat=True)

    senior_votes_qs = Vote.objects.filter(
        question=question,
        on_behalf_of__in=senior_member_pks
    )
    total_senior_votes = senior_votes_qs.count()

    results_data = []
    for option in options:
        count = question.votes.filter(option=option).count()
        senior_count = senior_votes_qs.filter(option=option).count()
        percentage = round((count / total_votes * 100), 1) if total_votes > 0 else 0
        senior_percentage = round((senior_count / total_senior_votes * 100), 1) if total_senior_votes > 0 else 0
        results_data.append({
            'option': option,
            'count': count,
            'percentage': percentage,
            'senior_count': senior_count,
            'senior_percentage': senior_percentage,
        })

    votes = Vote.objects.filter(question=question).select_related(
        'voter', 'on_behalf_of', 'option', 'proxy'
    )

    user_vote = Vote.objects.filter(question=question, on_behalf_of=member).first()

    return render(request, 'voting/results.html', {
        'assembly': assembly,
        'question': question,
        'results_data': results_data,
        'total_votes': total_votes,
        'total_senior_votes': total_senior_votes,
        'votes': votes,
        'user_vote': user_vote,
    })
