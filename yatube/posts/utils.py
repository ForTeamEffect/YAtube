from django.core.paginator import Paginator

def paginator(post_list, request, posts_on_page: int = 10):
    pagi = Paginator(post_list, posts_on_page)
    page_number = request.GET.get('page')
    page_obj = pagi.get_page(page_number)
    return page_obj
