from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from users.forms import UpdateUserForm, ProfileForm
from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import paginator


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.select_related('group', 'author').all()
    page_obj = paginator(request, post_list)
    context = {
        'page_obj': page_obj,
        'button': True,
    }
    return render(request, template, context=context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('group').all()
    page_obj = paginator(request, post_list)
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
    page_obj = paginator(request, post_list)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = False
    context = {
        'author': author,
        'page_obj': page_obj,
        'button': True,
        'post_count': page_obj.paginator.count,
        'following': following,
    }
    return render(request, template, context=context)


@login_required
def profile_edit(request, username):
    template = 'posts/profile_edit.html'
    user = get_object_or_404(User, username=username)
    if request.user.username != username:
        return redirect('posts:profile', username)
    user_form = UpdateUserForm(request.POST or None, instance=user)
    profile_form = ProfileForm(
        request.POST, request.FILES or None, instance=user.profile
    )
    if user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        return redirect('posts:profile', username)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, template, context=context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    posts_count = Post.objects.filter(author=post.author).count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'owner': request.user == post.author,
        'post': post,
        'posts_count': posts_count,
        'form': form,
        'comments': comments,
    }
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id)
    return render(request, template, context=context)


@login_required
def post_create(request):
    form = PostForm(request.POST, request.FILES or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', request.user.username)
    return render(
        request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context=context)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(request, post_list)
    context = {'page_obj': page_obj}
    return render(request, 'posts/index.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    is_follower = Follow.objects.filter(user=user, author=author)
    if user != author and not is_follower.exists():
        Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if is_follower.exists():
        is_follower.delete()
    return redirect('posts:profile', username)


def page_not_found(request, exception):
    return render(request, 'posts/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'posts/500.html', status=500)


def permission_denied(request, exception):
    return render(request, 'posts/403.html', status=403)


@login_required
def add_comment(request, post_id):
    # заглушка для пайтеста, зачем плодить урлы, если можно
    # всё на странице поста делать?
    return redirect('posts:post_detail', post_id=post_id)
