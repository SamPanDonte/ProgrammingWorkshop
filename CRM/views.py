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
        company_pages = Paginator(companies.order_by('id'), 20)
        company_list = company_pages.get_page(page_num)
        return render(request, self.template, {'company_list': company_list, 'industry_list': Industry.objects.all()})


class AddCompany(LoginRequiredMixin, View):
    """View for adding company"""
    login_url = 'users:login'
    redirect_field_name = 'redirect'
    template = 'form.html'
    form = CompanyForm

    def get(self, request, company_id=None):
        """Render add view for user"""
        form = self.form(instance=Company.objects.get(pk=company_id)) if company_id else self.form()
        return render(request, self.template, {'title': 'Add Company', 'form': form})

    def post(self, request, company_id=None):
        """Add company or display error"""
        if company_id:
            form = self.form(request.POST, instance=Company.objects.get(pk=company_id))
        else:
            form = self.form(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.user = request.user
            company.save()
            return HttpResponseRedirect(reverse('CRM:detail', args=[company.id]))
        return render(request, self.template, {'title': 'Add Company', 'form': form})

    @staticmethod
    def delete(request, company_id):
        company = Company.objects.get(pk=company_id)
        company.is_deleted = True
        company.save()
        return HttpResponse(status=200)


class AddModel(LoginRequiredMixin, View):
    """View for adding and editing models connected to company"""
    login_url = 'users:login'
    redirect_field_name = 'redirect'
    template = 'form.html'
    form = None
    model = None

    def get(self, request, company_id, model_id=None):
        """Render add or edit model view for user"""
        form = self.form(instance=self.model.objects.get(pk=model_id)) if model_id else self.form()
        return render(request, self.template, {'title': 'Add/Edit Model', 'form': form})

    def post(self, request, company_id, model_id=None):
        """Add or save model or display error"""
        if model_id:
            form = self.form(request.POST, instance=self.model.objects.get(pk=model_id))
        else:
            form = self.form(request.POST)
        if form.is_valid():
            model = form.save(commit=False)
            if not model_id:
                model.user = request.user
                model.company = Company.objects.get(pk=company_id)
            model.save()
            return HttpResponseRedirect(reverse('CRM:detail', args=[company_id]))
        return render(request, self.template, {'title': 'Add/Edit Model', 'form': form})

    def delete(self, request, company_id, model_id):
        """Delete model"""
        model = self.model.objects.get(pk=model_id)
        model.is_deleted = True
        model.save()
        return HttpResponse(status=200)


class AddNoteView(AddModel):
    """View for adding company note"""
    form = NoteForm
    model = Note


class AddPersonView(AddModel):
    """View for adding contact person"""
    form = ContactPersonForm
    model = ContactPerson


class DetailView(LoginRequiredMixin, View):
    """View for company details"""
    login_url = 'users:login'
    redirect_field_name = 'redirect'
    template = 'CRM/detail.html'

    def get(self, request, company_id):
        """Render detail view for user"""
        company = Company.objects.all().filter(is_deleted=False).get(pk=company_id)
        notes = Note.objects.all().filter(company=company).filter(is_deleted=False)
        contacts = ContactPerson.objects.all().filter(company=company).filter(is_deleted=False)
        return render(request, self.template, {'company': company, 'notes': notes, 'contacts': contacts})


class SearchPersonView(LoginRequiredMixin, View):
    """View for searching contact person by surname"""
    login_url = 'users:login'
    redirect_field_name = 'redirect'
    template = 'CRM/search.html'

    def get(self, request):
        query = request.GET.get('search')
        people = ContactPerson.objects.filter(is_deleted=False).filter(surname=query) if query else []
        return render(request, self.template, {'people': people})
