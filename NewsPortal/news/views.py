from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView

from NewsPortal.tasks import notifications_after_post_created
from .models import Post, Category, PostCategory
from .filters import PostFilter
from .forms import NewsForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group


class PostList(ListView):
    model = Post
    ordering = '-date_in'
    template_name = 'flatpages/post.html'
    context_object_name = 'post'
    paginate_by = 10


class PostDetail(DetailView):
    model = Post
    ordering = 'title'
    template_name = 'flatpages/post_id.html'
    context_object_name = 'post_id'
    # pk_url_kwarg = 'id'


class PostSearch(ListView):
    model = Post
    ordering = '-date_in'
    template_name = 'flatpages/post_search.html'
    context_object_name = 'post'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post', )
    form_class = NewsForm
    model = Post
    template_name = 'flatpages/post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.path == '/news/create/':
            post.post_type = 'NW'
        else:
            post.post_type = 'AR'
        post.save()
        notifications_after_post_created(form.instance.pk)
        return super().form_valid(form)


class PostUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('news.add_post',)
    form_class = NewsForm
    model = Post
    template_name = 'flatpages/post_edit.html'
    context_object_name = 'post'


class PostDelete(DeleteView):
    model = Post
    template_name = 'flatpages/post_delete.html'
    success_url = reverse_lazy('post.html')
    context_object_name = 'post'


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'sign/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context


@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('/')


class CategoryListView(PostList):
    model = Post
    template_name = 'flatpages/category_list.html'
    context_object_name = 'category_post_list'

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(category=self.category).order_by('-date_in')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.category.subscribers.all()
        context['category'] = self.category
        return context


@login_required()
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)

    message = 'Вы успешно подписались на рассылку постов категории'

    return render(request, 'flatpages/subscribe.html', {'category': category, 'message': message})


@login_required()
def unsubscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.remove(user)

    message = 'Вы успешно отписались от категории'

    return render(request, 'flatpages/unsubscribe.html', {'category': category, 'message': message})


