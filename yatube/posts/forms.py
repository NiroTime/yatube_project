from django import forms

from .models import Comment, Follow, Post


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = 'Группа не выбрана'

    class Meta:
        model = Post
        fields = ['text', 'group', 'post_image']
        widgets = {
            'text': forms.Textarea(),
            'group': forms.Select(),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': 'Добавить комментарий'}
        help_texts = {'text': 'Текст комментария'}


class FollowForm(forms.ModelForm):
    class Meta:
        model = Follow
        fields = ['user']
