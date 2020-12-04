from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from CRM.forms import CompanyForm, NoteForm, ContactPersonForm
from CRM.models import Company, Note, ContactPerson, Industry


class IndexView(LoginRequiredMixin, View):
    """View for displaying companies"""
    login_url = 'users:login'
    redirect_field_name = 'redirect'
    template = 'CRM/index.html'

    def get(self, request, page_num=1):
        """Render administration page"""
        industry_filter = request.GET.get('filter', None)
        companies = Company.objects.filter(is_deleted=False)
        if industry_filter:
            companies = companies.filter(industry__id=industry_filter)
        user_pages = Paginator(companies.order_by('id').all(), 20)
        page = user_pages.get_page(page_num)
        return render(request, self.template, {'companies': page, 'title': 'Company list', 'industries': Industry.objects.all()})


class AddCompany(LoginRequiredMixin, View):
    """View for adding company"""
    login_url = 'users:login'
    redirect_field_name = 'redirect'
    template = 'users/form.html'
    form = CompanyForm

    def get(self, request, company_id=None):
        """Render add view for user"""
        if company_id:
            company = Company.objects.get(pk=company_id)
            return render(request, self.template, {'title': 'Add Note', 'form': self.form(instance=company)})
        return render(request, self.template, {'title': 'Add Company', 'form': self.form()})

    def post(self, request, company_id=None):
        """Add company or display error"""
        form = self.form(request.POST, instance=Company.objects.get(pk=company_id)) if company_id else self.form(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.user = request.user
            company.save()
            company_id = company.id
            return HttpResponseRedirect(reverse('CRM:detail', args=(company_id,)))
        return render(request, self.template, {'title': 'Add Company', 'form': form})

    def delete(self, request, company_id):
        company = Company.objects.get(pk=company_id)
        company.is_deleted = True
        company.save()
        return HttpResponse(status=200)


class DetailView(LoginRequiredMixin, View):
    """View for company details"""
    login_url = 'users:login'
    redirect_field_name = 'redirect'
    template = 'CRM/detail.html'

    def get(self, request, company_id):
        """Render detail view for user"""
        company = Company.objects.all().filter(is_deleted=False).get(pk=company_id)
        notes = Note.objects.all().filter(company=company).filter(is_deleted=False)
        contact = ContactPerson.objects.all().filter(company=company).filter(is_deleted=False)
        return render(request, self.template, {'title': 'Company Details', 'company': company, 'notes': notes, 'contact': contact})

    def delete(self, request, company_id):
        company = Company.objects.get(pk=company_id)
        company.is_deleted = True
        company.save()
        return HttpResponse(status=200)


class AddNoteView(LoginRequiredMixin, View):
    """View for adding company note"""
    login_url = 'users:login'
    redirect_field_name = 'redirect'
    template = 'users/form.html'
    form = NoteForm

    def get(self, request, company_id, note_id=None):
        """Render add view for user"""
        if note_id:
            note = Note.objects.get(pk=note_id)
            return render(request, self.template, {'title': 'Add Note', 'form': self.form(instance=note)})
        return render(request, self.template, {'title': 'Add Note', 'form': self.form()})

    def post(self, request, company_id, note_id=None):
        """Add company or display error"""
        form = self.form(request.POST, instance=Note.objects.get(pk=note_id)) if note_id else self.form(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.company = Company.objects.get(pk=company_id)
            note.save()
            return HttpResponseRedirect(reverse('CRM:detail', args=[company_id]))
        return render(request, self.template, {'title': 'Add Note', 'form': form})

    def delete(self, request, company_id, note_id):
        note = Note.objects.get(pk=note_id)
        note.is_deleted = True
        note.save()
        return HttpResponse(status=200)


class AddPersonView(LoginRequiredMixin, View):
    """View for adding contact person"""
    login_url = 'users:login'
    redirect_field_name = 'redirect'
    template = 'users/form.html'
    form = ContactPersonForm

    def get(self, request, company_id, person_id=None):
        """Render add view for user"""
        if person_id:
            person = ContactPerson.objects.get(pk=person_id)
            return render(request, self.template, {'title': 'Add Contact Person', 'form': self.form(instance=person)})
        return render(request, self.template, {'title': 'Add Contact Person', 'form': self.form()})

    def post(self, request, company_id, person_id=None):
        """Add person or display error"""
        form = self.form(request.POST, instance=ContactPerson.objects.get(pk=person_id)) if person_id else self.form(request.POST)
        if form.is_valid():
            person = form.save(commit=False)
            person.user = request.user
            person.company = Company.objects.get(pk=company_id)
            person.save()
            return HttpResponseRedirect(reverse('CRM:detail', args=[company_id]))
        return render(request, self.template, {'title': 'Add Contact Person', 'form': form})

    def delete(self, request, company_id, person_id):
        person = ContactPerson.objects.get(pk=person_id)
        person.is_deleted = True
        person.save()
        return HttpResponse(status=200)


class SearchPersonView(LoginRequiredMixin, View):
    """View for searching contact person by surname"""
    login_url = 'users:login'
    redirect_field_name = 'redirect'
    template = 'CRM/search.html'

    def get(self, request):
        people = []
        if 'search' in request.GET:
            people = ContactPerson.objects.filter(is_deleted=False).filter(surname=request.GET['search'])
        return render(request, self.template, {'people': people})
