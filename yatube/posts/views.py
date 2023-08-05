from django.shortcuts import render, get_object_or_404, redirect
from posts.models import Post, Group, User, Comment, Follow
from posts.utils import paginator
from posts.forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.cache import cache_page

POSTS_PER_PAGE = 10

"""# def index_test_orm(request):
#     author = User.objects.get(username='leo')
#     keyword = "утро"
#     posts = Post.objects.filter(
#         text__contains=keyword).filter(author=author).filter(
#         pub_date__range=(datetime.date(
#             1854, 7, 7), datetime.date(1854, 7, 21)))
#     return render(request, "posts/index.html", {"posts": posts})
"""


def index_search(request):
    keyword = request.GET.get("q", None)
    if keyword:
        # posts = Post.objects.annotate(written_posts=Count('pk')).filter(
        #     text__contains=keyword)
        agr = Post.objects.select_related('author', 'group')
        posts = agr.filter(text__contains=keyword)

    else:
        posts = None

    return render(request, "posts/index_search.html",
                  {"posts": posts, "keyword": keyword})


@cache_page(60 * 20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.all()
    page_obj = paginator(post_list, request, settings.POSTS_ON_PAGE)
    context = {
        'page_obj': page_obj,
        'index': True
    }
    return render(request, 'posts/index.html', context)


# View-функция для страницы сообщества:
def group_posts(request, slug):
    # Функция get_object_or_404 получает по заданным критериям объект
    # из базы данных или возвращает сообщение об ошибке, если объект не найден.
    # В нашем случае в переменную group будут переданы объекты модели Group,
    # поле slug у которых соответствует значению slug в запросе
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginator(post_list, request, settings.POSTS_ON_PAGE)
    #
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    # Здесь код запроса к модели и создание словаря контекста
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related("group")
    page_obj = paginator(post_list, request, settings.POSTS_ON_PAGE)
    following = (request.user.is_authenticated and Follow.objects.filter(
        author=author, user=request.user).exists)
    context = {'post_list': post_list,
               'page_obj': page_obj,
               'author': author,
               'following': following,
               }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.select_related('post').filter(post=post)
    form = CommentForm(request.POST or None)
    count_posts = post.author.posts.count()
    context = {'page_obj': post,
               'kolvo': count_posts,
               'form': form,
               'comments': comments,
               }
    if not form.is_valid() or not request.user.is_authenticated:
        return render(
            request, 'posts/post_detail.html', context
        )
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if not request.method == 'POST':
        form = PostForm()
        return render(
            request, 'posts/create_post.html', {'form': form, 'is_edit': False}
        )

    form = PostForm(request.POST,
                    files=request.FILES or None)
    if not form.is_valid():
        return render(
            request, 'posts/create_post.html', {'form': form, 'is_edit': False}
        )

    form.instance.author = request.user

    form.save()

    return redirect('posts:profile', username=request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if not request.user == post.author:
        return redirect('posts:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST or None,
                        files=request.FILES or None,
                        instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
        else:
            post_edit(request, post_id)

    form = PostForm(
        instance=post
    )
    context = {
        'is_edit': True,
        'form': form,
        'post': post,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    # ...
    authors = Follow.objects.select_related('user', 'author').filter(
        user=request.user).values_list('author')

    combined_results = Post.objects. \
        filter(author__in=authors). \
        order_by('-pub_date')
    page_obj = paginator(combined_results, request, settings.POSTS_ON_PAGE)
    context = {
        'page_obj': page_obj,
        'follow': True
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    if request.user.username != username:
        if not Follow.objects.filter(
            user=request.user,
            author=User.objects.get(username=username)
        ):
            Follow.objects.create(
                user=request.user,
                author=User.objects.get(username=username)
            )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author=User.objects.get(username=username)
    ).delete()
    return redirect('posts:profile', username=username)
