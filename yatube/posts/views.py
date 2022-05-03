from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User
from .utils import paginagor


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.select_related('group', 'author').all()
    page_obj = paginagor(request, post_list)
    context = {
        'page_obj': page_obj,
        'button': True,
    }
    return render(request, template, context=context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('group').all()
    page_obj = paginagor(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
        'button': False
    }
    return render(request, template, context=context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('author').all()
    page_obj = paginagor(request, post_list)
    context = {
        'author': author,
        'page_obj': page_obj,
        'button': True,
        'post_count': page_obj.paginator.count,
    }
    return render(request, template, context=context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    if request.user == post.author:
        owner = True
    else:
        owner = False
    posts_count = Post.objects.filter(author=post.author).count()
    context = {
        'owner': owner,
        'post': post,
        'posts_count': posts_count,
    }
    return render(request, template, context=context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('posts:profile', request.user.username)
    return render(
        request, 'posts/create_post.html',
        {'form': form, 'title': 'Добавить запись'}
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'title': 'Редактировать запись',
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context=context)
