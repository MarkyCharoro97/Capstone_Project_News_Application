from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.http import JsonResponse
import requests

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Article, Newsletter, Publisher, CustomUser
from .serializers import ArticleSerializer
from .forms import CustomUserCreationForm, ArticleForm, NewsletterForm
from .permissions import (
    role_required, article_creator_required, article_approver_required,
    newsletter_creator_required, newsletter_sender_required
)


def home(request):
    recent_articles = Article.objects.filter(approved=True).order_by('-created_at')[:5]
    return render(request, 'home.html', {'recent_articles': recent_articles})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.first_name}! Your account has been created as a {user.get_role_display()}.')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def article_list(request):
    articles = Article.objects.filter(approved=True).order_by('-created_at')
    user_can_approve = request.user.is_authenticated and (
        request.user.role == 'editor' or request.user.has_perm('core.can_approve_article')
    )
    user_can_create = request.user.is_authenticated and request.user.role in ['journalist', 'editor']
    return render(request, 'article_list.html', {
        'articles': articles, 
        'user_can_approve': user_can_approve,
        'user_can_create': user_can_create
    })


@login_required
@role_required('journalist', 'editor')
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, user=request.user)
        if form.is_valid():
            article = form.save(commit=False)
            article.journalist = request.user
            if request.user.role == 'editor':
                article.approved = True  # Editors can auto-approve their articles
            article.save()
            messages.success(request, 'Article created successfully!')
            return redirect('article_list')
    else:
        form = ArticleForm(user=request.user)
    return render(request, 'create_article.html', {'form': form})


@login_required
@role_required('editor')
def approve_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    article.approved = True
    article.save()
    messages.success(request, f'Article "{article.title}" has been approved.')

    # Notify subscribers
    subscribers = []
    if article.publisher:
        subscribers += list(article.publisher.subscribers.all())
    if article.journalist:
        subscribers += list(article.journalist.journalist_followers.all())

    emails = [user.email for user in subscribers if user.email]
    if emails:
        try:
            send_mail(
                f"New Article: {article.title}",
                f"A new article has been published: {article.title}\n\n{article.content[:200]}...",
                'admin@newsapp.com',
                emails,
                fail_silently=True,
            )
        except Exception as e:
            messages.warning(request, 'Article approved but email notifications failed.')

    return redirect('article_list')


@login_required
def newsletter_list(request):
    newsletters = Newsletter.objects.all().order_by('-created_at')
    user_can_create = request.user.role == 'editor' or request.user.has_perm('core.can_create_newsletter')
    user_can_send = request.user.role == 'editor' or request.user.has_perm('core.can_send_newsletter')
    return render(request, 'newsletter_list.html', {
        'newsletters': newsletters,
        'user_can_create': user_can_create,
        'user_can_send': user_can_send
    })


@login_required
@role_required('editor')
def create_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.created_by = request.user
            newsletter.save()
            messages.success(request, 'Newsletter created successfully!')
            return redirect('newsletter_list')
    else:
        form = NewsletterForm()
    return render(request, 'create_newsletter.html', {'form': form})


@login_required
@role_required('editor')
def send_newsletter(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    
    if newsletter.is_sent:
        messages.warning(request, 'This newsletter has already been sent.')
        return redirect('newsletter_list')
    
    # Determine recipients based on target audience
    recipients = []
    if newsletter.target_audience == 'all':
        recipients = CustomUser.objects.filter(email__isnull=False).exclude(email='')
    elif newsletter.target_audience == 'readers':
        recipients = CustomUser.objects.filter(role='reader', email__isnull=False).exclude(email='')
    elif newsletter.target_audience == 'journalists':
        recipients = CustomUser.objects.filter(role='journalist', email__isnull=False).exclude(email='')
    elif newsletter.target_audience == 'editors':
        recipients = CustomUser.objects.filter(role='editor', email__isnull=False).exclude(email='')
    
    emails = [user.email for user in recipients]
    
    if emails:
        try:
            send_mail(
                newsletter.title,
                newsletter.content,
                'admin@newsapp.com',
                emails,
                fail_silently=False,
            )
            newsletter.is_sent = True
            newsletter.sent_at = timezone.now()
            newsletter.save()
            messages.success(request, f'Newsletter sent to {len(emails)} recipients!')
        except Exception as e:
            messages.error(request, f'Failed to send newsletter: {str(e)}')
    else:
        messages.warning(request, 'No recipients found for this newsletter.')
    
    return redirect('newsletter_list')


@login_required
def subscribe_newsletter(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    if newsletter in request.user.newsletter_subscriptions.all():
        request.user.newsletter_subscriptions.remove(newsletter)
        subscribed = False
        message = 'Unsubscribed from newsletter.'
    else:
        request.user.newsletter_subscriptions.add(newsletter)
        subscribed = True
        message = 'Subscribed to newsletter.'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'subscribed': subscribed, 'message': message})
    
    messages.success(request, message)
    return redirect('newsletter_list')


@login_required
def my_articles(request):
    """View for journalists to see their own articles."""
    if request.user.role not in ['journalist', 'editor']:
        messages.error(request, 'Only journalists and editors can view this page.')
        return redirect('article_list')
    
    if request.user.role == 'editor':
        articles = Article.objects.all().order_by('-created_at')
    else:
        articles = Article.objects.filter(journalist=request.user).order_by('-created_at')
    
    return render(request, 'my_articles.html', {'articles': articles})


@login_required
def pending_articles(request):
    """View for editors to see articles pending approval."""
    if request.user.role != 'editor':
        messages.error(request, 'Only editors can view pending articles.')
        return redirect('article_list')
    
    articles = Article.objects.filter(approved=False).order_by('-created_at')
    return render(request, 'pending_articles.html', {'articles': articles})


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
    queryset = Article.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.role == 'editor':
            return Article.objects.all()
        elif user.role == 'journalist':
            return Article.objects.filter(journalist=user)
        else:  # reader
            return Article.objects.filter(approved=True)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        if request.user.role != 'editor':
            return Response({'error': 'Only editors can approve articles'}, status=403)
        
        article = self.get_object()
        article.approved = True
        article.save()
        return Response({'status': 'article approved'})


def is_editor(user):
    return user.role == 'editor'


def is_journalist_or_editor(user):
    return user.role in ['journalist', 'editor']