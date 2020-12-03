from django.forms import ModelForm

from CRM.models import Company, Note, ContactPerson


class CompanyForm(ModelForm):
    """Form for adding company"""
    class Meta:
        model = Company
        exclude = ('is_deleted', 'user')


class NoteForm(ModelForm):
    """Form for adding note to company"""
    class Meta:
        model = Note
        exclude = ('user', 'is_deleted', 'company')


class ContactPersonForm(ModelForm):
    """For for adding contact person to company"""
    class Meta:
        model = ContactPerson
        exclude = ('is_deleted', 'user', 'company')
