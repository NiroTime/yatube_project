from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AddPostForm
from .models import Group, Post, User


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.POSTS_FOR_ONE_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'button': True,
    }
    return render(request, template, context=context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.POSTS_FOR_ONE_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
        'button': False
    }
    return render(request, template, context=context)


def profile(request, username):
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author__username=username)
    posts_count = post_list.count()
    paginator = Paginator(post_list, settings.POSTS_FOR_ONE_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'user': user,
        'page_obj': page_obj,
        'button': True,
        'posts_count': posts_count
    }
    return render(request, template, context=context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    posts_count = Post.objects.filter(author=post.author).count()
    context = {
        'post': post,
        'posts_count': posts_count,
    }
    return render(request, template, context=context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = AddPostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('posts:profile', request.user.username)
    else:
        form = AddPostForm()
    return render(
        request, 'posts/create_post.html',
        {'form': form, 'title': 'Добавить запись'}
    )


def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'GET':
        if request.user != post.author:
            return redirect('posts:post_detail', post_id)
        form = AddPostForm(instance=post)

    if request.method == 'POST':
        form = AddPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
        return redirect('posts:profile', request.user.username)
    context = {
        'form': form,
        'title': 'Редактировать запись',
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context=context)
