from django.contrib import admin


from .models import MenuItem


class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'parent')
    search_fields = ('name',)


admin.site.register(MenuItem, MenuItemAdmin)
