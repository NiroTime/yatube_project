from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

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


@login_required
def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:settings.POSTS_FOR_ONE_PAGE]
    context = {
        'group': group,
        'posts': posts,
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
