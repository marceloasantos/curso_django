from django import forms
from django.db.models import Avg, Q
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from estoque.models import Livro, Autor, Editora
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy

class AutorListView(ListView):
    fields = '__all__'
    model = Autor

    def get(self, request, *args, **kwargs):
        self.object = None
        return super().get(request, *args, **kwargs)

class AutorCreateView(CreateView):
    model = Autor
    fields = '__all__'
    success_url = reverse_lazy('autor-list')

    def form_valid(self, form):
        if self.request.is_ajax():
            obj = form.save()
            return JsonResponse({
                'obj': {'nome': obj.nome, 'idade': obj.idade}
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse({
                'errors': form.errors, 'non_field_errors': form.non_field_errors()
            })
        return super().form_invalid(form)

class AutorUpdateView(UpdateView):
    model = Autor
    fields = '__all__'
    success_url = reverse_lazy('autor-list')

class AutorDeleteView(DeleteView):
    model = Autor
    success_url = reverse_lazy('autor-list')

class LivroListView(ListView):
    model = Livro

class LivroCreateView(CreateView):
    model = Livro
    fields = '__all__'
    success_url = reverse_lazy('livro-list')

class LivroUpdateView(UpdateView):
    model = Livro
    fields = '__all__'
    success_url = reverse_lazy('livro-list')

class LivroDeleteView(DeleteView):
    model = Livro
    success_url = reverse_lazy('livro-list')

class LivroForm(forms.ModelForm):
    def get_avaliacao_avg(self):
        livros = Livro.objects.filter(autores__in = self.cleaned_data['autores']).distinct()
        media = livros.aggregate(Avg('avaliacao'))
        return media.get('avaliacao__avg', 0) or 0

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.avaliacao = self.get_avaliacao_avg()
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        model = Livro
        fields = ['nome', 'paginas', 'preco', 'autores', 'editora', 'data_pub']

class SearchFormListView(FormMixin, ListView):
    def get(self, request, *args, **kwargs):
        self.form = self.get_form(self.get_form_class())
        self.object_list = self.form.get_queryset()
        return self.render_to_response(self.get_context_data(object_list = self.object_list, form = self.form))

    def get_form_kwargs(self):
        return {'initial': self.get_initial(), 'data': self.request.GET}

class LivroSearchForm(forms.Form):
    #nome = forms.CharField(required = False)
    #autores = forms.CharField(required = False)
    #editora = forms.ModelChoiceField(required = False, queryset = Editora.objects)
    termo = forms.CharField(required = False, widget = forms.TextInput(attrs = {'class': 'form-control'}), label = "")

    def get_queryset(self):
        q = Q()
        if self.is_valid():
            #if self.cleaned_data.get('nome'):
            #    q = q & Q(nome__icontains = self.cleaned_data['nome'])
            #if self.cleaned_data.get('autores'):
            #    q = q & Q(autores__icontains = self.cleaned_data['autores'])
            #if self.cleaned_data.get('editora'):
            #    q = q & Q(editora = self.cleaned_data['editora'])
            if self.cleaned_data.get('termo'):
                q = q | Q(nome__icontains = self.cleaned_data['termo'])
                q = q | Q(editora__nome__icontains = self.cleaned_data['termo'])
                q = q | Q(autores__nome__icontains = self.cleaned_data['termo'])
            return Livro.objects.filter(q)

class AutorSearchForm(forms.Form):
    #nome = forms.CharField(required = False)
    #autores = forms.CharField(required = False)
    #editora = forms.ModelChoiceField(required = False, queryset = Editora.objects)
    termo = forms.CharField(required = False, widget = forms.TextInput(attrs = {'class': 'form-control'}), label = "")

    def get_queryset(self):
        q = Q()
        if self.is_valid():
            #if self.cleaned_data.get('nome'):
            #    q = q & Q(nome__icontains = self.cleaned_data['nome'])
            #if self.cleaned_data.get('autores'):
            #    q = q & Q(autores__icontains = self.cleaned_data['autores'])
            #if self.cleaned_data.get('editora'):
            #    q = q & Q(editora = self.cleaned_data['editora'])
            if self.cleaned_data.get('termo'):
                q = q | Q(nome__icontains = self.cleaned_data['termo'])
            return Autor.objects.filter(q)

class LivroSearchFormView(SearchFormListView):
    form_class = LivroSearchForm

class PageInfoMixin(object):
    page_info = None

    def get_page_info(self):
        if self.model:
            return self.model_meta.verbose_name
        return None

    def get_context_data(self, **kwargs):
        if self.page_info is None:
            kwargs['page_info'] = self.get_page_info()
        return super().get_context_data(**kwargs)

class LivroSearchFormListView(PageInfoMixin, SearchFormListView):
    form_class = LivroSearchForm
    model = Livro

    def get_page_info(self):
        return 'Livros (%s)' % (
                Livro.objects.count()
        )

class AutorSearchFormListView(PageInfoMixin, SearchFormListView):
    form_class = AutorSearchForm
    model = Autor

    def get_page_info(self):
        return 'Autores (%s)' % (
                Autor.objects.count()
        )

class JsonListMixin(object):
    json_fields = []

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset().values_list(*self.json_fields)
        json_dict = {
            'header': self.json_fields,
            'object_list': list(self.object_list)
        }
        return JsonResponse(json_dict)

class LivroJsonListView(JsonListMixin, LivroListView):
    json_fields = [
        'nome', 'paginas', 'preco', 'avaliacao', 'editora__nome', 'autores__nome',
    ]

class AutorJsonListView(JsonListMixin, AutorListView):
    json_fields = [
        'nome', 'idade',
    ]

def autor_nome_registrado(request):
    nome = request.GET.get('nome', None)
    data = {
        'is_taken': Autor.objects.filter(nome__iexact = nome).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'O autor já está cadastrado'
    return JsonResponse(data)

def index(request):
    context = {
            'livros': Livro.objects.all()
            }

    return render(request, 'estoque/index.html', context)
