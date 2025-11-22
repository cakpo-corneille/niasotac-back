from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, F
from django.utils import timezone

from .models import (
    Category, Product, ProductImage, Promotion, 
    NewsletterSubscriber, NewsletterTemplate, NewsletterCampaign,
    Service, SocialLink, SiteSettings
)
from .serializers import (
    CategorySerializer, CategoryListSerializer, CategoryDetailSerializer,
    CategoryTreeSerializer, CategoryMinimalSerializer,
    ProductListSerializer, ProductDetailSerializer, ProductMinimalSerializer,
    ProductImageSerializer,
    PromotionListSerializer, PromotionDetailSerializer,
    NewsletterSubscriberSerializer, NewsletterTemplateSerializer,
    NewsletterCampaignListSerializer, NewsletterCampaignDetailSerializer,
    ServiceSerializer, SocialLinkSerializer, SiteSettingsSerializer
)

from .api_filters import (
    ProductFilter, CategoryFilter, PromotionFilter, NewsletterCampaignFilter,
    NewsletterSubscriberFilter, NewsletterTemplateFilter
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les catégories avec arborescence MPTT
    """
    queryset = Category.objects.all().select_related('parent').prefetch_related('children').order_by('level', 'name')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        elif self.action == 'retrieve':
            return CategoryDetailSerializer
        elif self.action == 'tree':
            return CategoryTreeSerializer
        elif self.action == 'minimal':
            return CategoryMinimalSerializer
        return CategorySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Ajouter les annotations pour product_count
        queryset = queryset.annotate(
            product_count=Count('products', distinct=True),
            direct_product_count=Count('products', filter=Q(products__category=F('id')), distinct=True)
        )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Retourne l'arborescence complète des catégories"""
        root_categories = self.get_queryset().filter(parent__isnull=True)
        serializer = self.get_serializer(root_categories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def minimal(self, request):
        """Retourne une liste minimale pour les select/autocomplete"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Retourne les produits d'une catégorie"""
        category = self.get_object()
        products = category.products.filter(is_active=True)
        
        # Utiliser le ProductListSerializer
        from .serializers import ProductListSerializer
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les produits avec filtres avancés
    """
    queryset = Product.objects.all().select_related('category', 'status').prefetch_related('images').order_by('-created_at')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action == 'minimal':
            return ProductMinimalSerializer
        return ProductDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrer uniquement les produits actifs pour les non-authentifiés
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Incrémenter le compteur de vues lors de la consultation"""
        instance = self.get_object()
        
        # Incrémenter les vues
        if hasattr(instance, 'status') and instance.status:
            instance.status.views_count = F('views_count') + 1
            instance.status.save(update_fields=['views_count'])
            instance.status.refresh_from_db()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Retourne les produits mis en avant"""
        queryset = self.get_queryset().filter(status__is_featured=True)
        queryset = queryset.order_by('-status__featured_score', '-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """Retourne les produits recommandés"""
        queryset = self.get_queryset().filter(status__is_recommended=True)
        queryset = queryset.order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        """Retourne les produits en promotion"""
        queryset = self.get_queryset().exclude(
            Q(compare_at_price__isnull=True) | Q(compare_at_price__lte=0)
        )
        queryset = queryset.order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def track_click(self, request, slug=None):
        """Enregistrer un clic sur le produit (WhatsApp par exemple)"""
        product = self.get_object()
        
        if hasattr(product, 'status') and product.status:
            product.status.clicks_count = F('clicks_count') + 1
            product.status.save(update_fields=['clicks_count'])
        
        return Response({'status': 'click tracked'})


class PromotionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les promotions
    """
    queryset = Promotion.objects.all().prefetch_related('products', 'categories').order_by('-created_at')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PromotionFilter
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PromotionListSerializer
        return PromotionDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrer uniquement les promotions actives pour les non-authentifiés
        if not self.request.user.is_authenticated:
            now = timezone.now()
            queryset = queryset.filter(
                active=True,
                start_at__lte=now,
                end_at__gte=now
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Retourne les promotions actuellement actives"""
        now = timezone.now()
        queryset = self.get_queryset().filter(
            active=True,
            start_at__lte=now,
            end_at__gte=now
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def validate_code(self, request):
        """Valider un code promo"""
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Code required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            promotion = Promotion.objects.get(code__iexact=code)
            if promotion.is_active_now():
                serializer = self.get_serializer(promotion)
                return Response(serializer.data)
            else:
                return Response({'error': 'Promotion not active'}, status=status.HTTP_400_BAD_REQUEST)
        except Promotion.DoesNotExist:
            return Response({'error': 'Invalid code'}, status=status.HTTP_404_NOT_FOUND)


class NewsletterSubscriberViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les abonnés newsletter
    """
    queryset = NewsletterSubscriber.objects.all().order_by('-created_at')
    serializer_class = NewsletterSubscriberSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = NewsletterSubscriberFilter
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Les non-authentifiés ne voient que leurs propres abonnements
        if not self.request.user.is_authenticated:
            return queryset.none()
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Créer un nouvel abonné"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(
            {'message': 'Subscription successful! Please check your email to confirm.'},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'])
    def confirm(self, request):
        """Confirmer un abonnement avec le token"""
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscriber = NewsletterSubscriber.objects.get(confirmation_token=token)
            subscriber.confirmed = True
            subscriber.save(update_fields=['confirmed'])
            return Response({'message': 'Email confirmed successfully!'})
        except NewsletterSubscriber.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def unsubscribe(self, request):
        """Se désabonner avec l'email"""
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscriber = NewsletterSubscriber.objects.get(email=email)
            subscriber.subscribed = False
            subscriber.save(update_fields=['subscribed'])
            return Response({'message': 'Successfully unsubscribed'})
        except NewsletterSubscriber.DoesNotExist:
            return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)


class NewsletterTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les templates newsletter
    """
    queryset = NewsletterTemplate.objects.all().order_by('name')
    serializer_class = NewsletterTemplateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = NewsletterTemplateFilter
    lookup_field = 'slug'


class NewsletterCampaignViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les campagnes newsletter
    """
    queryset = NewsletterCampaign.objects.all().select_related('template').prefetch_related('subscribers').order_by('-created_at')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = NewsletterCampaignFilter
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NewsletterCampaignListSerializer
        return NewsletterCampaignDetailSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les services
    """
    queryset = Service.objects.all().order_by('order')
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrer uniquement les services actifs pour les non-authentifiés
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_active=True)
        
        return queryset


class SocialLinkViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les liens sociaux
    """
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SiteSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet en lecture seule pour les paramètres du site
    """
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Retourne les paramètres actuels du site"""
        settings = SiteSettings.get_settings()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)
 
