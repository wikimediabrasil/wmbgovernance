from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Vote, Proxy


class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['option']
        widgets = {
            'option': forms.RadioSelect
        }

    def __init__(self, *args, **kwargs):
        self.member = kwargs.pop('member', None)
        self.question = kwargs.pop('question', None)
        self.forced_on_behalf_of = kwargs.pop('forced_on_behalf_of', None)

        super().__init__(*args, **kwargs)

        if not self.question:
            return

        self.fields['option'].queryset = self.question.option_set.options.all()
        self.fields['option'].label = _('Choose an option')
        self.fields['option'].empty_label = None
        self.fields['option'].required = True

        if self.instance.pk and self.instance.option_id:
            self.initial['option'] = self.instance.option_id

        self.proxy = Proxy.objects.filter(
            assembly=self.question.agenda.assembly,
            grantee=self.member
        ).first()

        if self.proxy:
            if self.forced_on_behalf_of is not None:
                self.fields['on_behalf_of'] = forms.ChoiceField(
                    label=_('Voting on behalf of'),
                    choices=[
                        (self.member.pk, _('Myself (%(name)s)') % {'name': self.member}),
                        (self.proxy.grantor.pk, _('On behalf of %(name)s') % {'name': self.proxy.grantor}),
                    ],
                    widget=forms.HiddenInput(),
                    initial=str(self.forced_on_behalf_of),
                )
                self.initial['on_behalf_of'] = str(self.forced_on_behalf_of)
            else:
                if self.instance.pk and self.instance.on_behalf_of_id:
                    initial_behalf = str(self.instance.on_behalf_of_id)
                else:
                    initial_behalf = str(self.member.pk)

                self.fields['on_behalf_of'] = forms.ChoiceField(
                    label=_('Voting on behalf of'),
                    choices=[
                        (self.member.pk, _('Myself (%(name)s)') % {'name': self.member}),
                        (self.proxy.grantor.pk, _('On behalf of %(name)s') % {'name': self.proxy.grantor}),
                    ],
                    widget=forms.RadioSelect(),
                    initial=initial_behalf,
                )
                self.initial['on_behalf_of'] = initial_behalf

    def save(self, commit=True):
        vote = super().save(commit=False)
        vote.question = self.question
        vote.voter = self.member

        if self.proxy and self.cleaned_data.get('on_behalf_of') == str(self.proxy.grantor.pk):
            vote.on_behalf_of = self.proxy.grantor
            vote.proxy = self.proxy
        else:
            vote.on_behalf_of = self.member
            vote.proxy = None

        if commit:
            vote.full_clean()
            vote.save()
        return vote