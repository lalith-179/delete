# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.sites import AdminSite
from django.urls import path
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.contrib.auth.views import redirect_to_login
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.urls import reverse

from .forms import SignUpForm, LoginForm
from .models import Account
from .views import admin_login
from staff.models import film, show, banner

class FilmAdmin(admin.ModelAdmin):
    list_display = ('movie_name', 'movie_lang', 'movie_genre', 'movie_year', 'date_added')
    list_filter = ('movie_lang', 'movie_genre', 'movie_year')
    search_fields = ('movie_name', 'movie_plot')
    ordering = ('-date_added',)

class ShowAdmin(admin.ModelAdmin):
    list_display = ('movie', 'showtime', 'start_date', 'end_date', 'price')
    list_filter = ('start_date', 'end_date')
    search_fields = ('movie__movie_name',)
    ordering = ('-start_date',)

class BannerAdmin(admin.ModelAdmin):
    list_display = ('movie', 'modified')
    list_filter = ('modified',)
    search_fields = ('movie__movie_name',)
    ordering = ('-modified',)

class CustomAdminSite(AdminSite):
    site_header = 'Movie Ticket Booking Administration'
    site_title = 'Movie Admin'
    index_title = 'Movie Management'
    login_template = 'admin/login.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='admin_dashboard'),
            path('movies/', self.admin_view(self.movies_view), name='admin_movies'),
            path('shows/', self.admin_view(self.shows_view), name='admin_shows'),
            path('banners/', self.admin_view(self.banners_view), name='admin_banners'),
            path('users/', self.admin_view(self.users_view), name='admin_users'),
        ]
        return custom_urls + urls

    @method_decorator(staff_member_required)
    def dashboard_view(self, request):
        context = {
            'title': 'Dashboard',
            'movies_count': film.objects.count(),
            'shows_count': show.objects.count(),
            'banners_count': banner.objects.count(),
            'users_count': Account.objects.count(),
            'movies_url': reverse('admin:staff_film_changelist'),
            'shows_url': reverse('admin:staff_show_changelist'),
            'banners_url': reverse('admin:staff_banner_changelist'),
            'users_url': reverse('admin_users'),
            **self.each_context(request),
        }
        return render(request, 'admin/dashboard.html', context)

    @method_decorator(staff_member_required)
    def movies_view(self, request):
        return redirect('admin:staff_film_changelist')

    @method_decorator(staff_member_required)
    def shows_view(self, request):
        return redirect('admin:staff_show_changelist')

    @method_decorator(staff_member_required)
    def banners_view(self, request):
        return redirect('admin:staff_banner_changelist')

    @method_decorator(staff_member_required)
    def users_view(self, request):
        return redirect('admin:accounts_account_changelist')

    def has_permission(self, request):
        return request.user.is_active and request.user.is_staff

custom_admin_site = CustomAdminSite(name='admin')

# Register models with custom admin site
custom_admin_site.register(Account, UserAdmin)
custom_admin_site.register(film, FilmAdmin)
custom_admin_site.register(show, ShowAdmin)
custom_admin_site.register(banner, BannerAdmin)