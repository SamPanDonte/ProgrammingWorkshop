from django.urls import path

from . import views

app_name = 'CRM'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:page_num>', views.IndexView.as_view(), name='index'),
    path('add/', views.AddCompany.as_view(), name='add'),
    path('add/<int:company_id>', views.AddCompany.as_view(), name='edit'),
    path('detail/<int:company_id>', views.DetailView.as_view(), name='detail'),
    path('detail/<int:company_id>/add/note', views.AddNoteView.as_view(), name='add_note'),
    path('detail/<int:company_id>/add/note/<int:note_id>', views.AddNoteView.as_view(), name='edit_note'),
    path('detail/<int:company_id>/add/person', views.AddPersonView.as_view(), name='add_person'),
    path('detail/<int:company_id>/add/person/<int:person_id>', views.AddPersonView.as_view(), name='edit_person'),
    path('search/', views.SearchPersonView.as_view(), name='search'),
]
