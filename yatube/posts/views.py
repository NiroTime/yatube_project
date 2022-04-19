from django.shortcuts import get_object_or_404, render

from yatube.settings import POSTS_FOR_ONE_PAGE
from .models import Group, Post


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()[:POSTS_FOR_ONE_PAGE]
    context = {
        'posts': posts,
        'button': True
    }
    return render(request, template, context=context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:POSTS_FOR_ONE_PAGE]
    context = {
        'group': group,
        'posts': posts,
        'button': False
    }
    return render(request, template, context=context)
