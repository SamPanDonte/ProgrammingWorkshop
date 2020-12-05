from django.urls import path

from . import views

app_name = 'CRM'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:page_num>', views.IndexView.as_view(), name='index'),
    path('company', views.AddCompany.as_view(), name='add_company'),
    path('company/<int:company_id>', views.AddCompany.as_view(), name='edit_company'),
    path('note/<int:company_id>', views.AddNoteView.as_view(), name='add_note'),
    path('note/<int:company_id>/<int:model_id>', views.AddNoteView.as_view(), name='edit_note'),
    path('person/<int:company_id>', views.AddPersonView.as_view(), name='add_person'),
    path('person/<int:company_id>/<int:model_id>', views.AddPersonView.as_view(), name='edit_person'),
    path('detail/<int:company_id>', views.DetailView.as_view(), name='detail'),
    path('search', views.SearchPersonView.as_view(), name='search'),
]
