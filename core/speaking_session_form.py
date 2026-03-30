from django import forms

class SpeakingSessionForm(forms.Form):
    name = forms.CharField(label='Full Name', max_length=100)
    email = forms.EmailField(label='Email Address')
    phone = forms.CharField(label='Phone Number', max_length=30, required=False)
    session_for = forms.ChoiceField(
        label='Who is this session for?',
        choices=[
            ('myself', 'Myself'),
            ('family', 'Family Member'),
            ('caregiver', 'Caregiver'),
            ('organization', 'Organization / Group'),
        ]
    )
    session_type = forms.ChoiceField(
        label='Session Type',
        choices=[
            ('individual', 'Individual Session'),
            ('group', 'Group Session'),
            ('awareness', 'Awareness Talk (for organizations)'),
        ]
    )
    mode = forms.ChoiceField(
        label='Preferred Mode',
        choices=[
            ('online', 'Online (Zoom/Google Meet)'),
            ('in_person', 'In-Person'),
        ]
    )
    date = forms.DateField(label='Preferred Date', widget=forms.DateInput(attrs={'type': 'date'}))

    def clean_date(self):
        import datetime
        date = self.cleaned_data['date']
        today = datetime.date.today()
        if date < today:
            raise forms.ValidationError('You can only book for today or a future date.')
        return date
    time = forms.TimeField(label='Preferred Time', widget=forms.TimeInput(attrs={'type': 'time'}))
    participants = forms.IntegerField(label='Number of Participants', required=False, min_value=1)
    purpose = forms.CharField(label='Purpose of Booking', max_length=200)
    notes = forms.CharField(label='Additional Notes', widget=forms.Textarea, required=False)