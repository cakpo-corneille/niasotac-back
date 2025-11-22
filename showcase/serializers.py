from rest_framework import serializers
from .models import (
    Category, Product, ProductImage, ProductStatus, 
    Promotion, PromotionUsage, SiteSettings, SocialLink, Service,
    NewsletterSubscriber, NewsletterTemplate, NewsletterCampaign,
    
)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer basique pour les catégories"""
    
    # Champs calculés (read-only)
    is_main_category = serializers.BooleanField(read_only=True)
    product_count = serializers.IntegerField(read_only=True)
    direct_product_count = serializers.IntegerField(read_only=True)
    full_path = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'icon_file',
            'parent',
            'level',
            'is_main_category',
            'product_count',
            'direct_product_count',
            'full_path',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'level', 'created_at', 'updated_at']
    
    def get_full_path(self, obj):
        """Retourne le chemin complet de la catégorie"""
        return obj.get_full_path()


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Serializer récursif pour afficher l'arborescence complète"""
    
    children = serializers.SerializerMethodField()
    product_count = serializers.IntegerField(read_only=True)
    direct_product_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'level',
            'product_count',
            'direct_product_count',
            'children',
        ]
    
    def get_children(self, obj):
        """Retourne les enfants directs de manière récursive"""
        children = obj.get_children()
        if children.exists():
            return CategoryTreeSerializer(children, many=True).data
        return []


class CategoryListSerializer(serializers.ModelSerializer):
    """Serializer optimisé pour les listes (sans relations lourdes)"""
    
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    product_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'level',
            'parent',
            'parent_name',
            'product_count',
        ]


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour une catégorie individuelle"""
    
    # Relations
    parent = CategorySerializer(read_only=True)
    children = CategorySerializer(many=True, read_only=True, source='get_children')
    breadcrumb = serializers.SerializerMethodField()
    
    # Champs calculés
    is_main_category = serializers.BooleanField(read_only=True)
    product_count = serializers.IntegerField(read_only=True)
    direct_product_count = serializers.IntegerField(read_only=True)
    full_path = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'icon_file',
            'parent',
            'children',
            'breadcrumb',
            'level',
            'is_main_category',
            'product_count',
            'direct_product_count',
            'full_path',
            'created_at',
            'updated_at',
        ]
    
    def get_breadcrumb(self, obj):
        """Retourne le fil d'Ariane"""
        return [{'id': cat.id, 'name': cat.name, 'slug': cat.slug} 
                for cat in obj.get_breadcrumb()]
    
    def get_full_path(self, obj):
        return obj.get_full_path()


class CategoryMinimalSerializer(serializers.ModelSerializer):
    """Serializer minimal pour les select/dropdowns"""
    
    full_path = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'level', 'full_path']
    
    def get_full_path(self, obj):
        return obj.get_full_path()


class SiteSettingsSerializer(serializers.ModelSerializer):
    """Serializer pour les paramètres du site"""

    class Meta:
        model = SiteSettings
        fields = [
            'whatsapp_number', 'contact_email', 'contact_phone',
            'contact_address', 'company_name', 'company_description',
            'social_links', 'updated_at'
        ]
        read_only_fields = ['updated_at']


# ===== Product Image Serializers =====

class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer pour les images de produits"""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


# ===== Product Serializers =====

class ProductListSerializer(serializers.ModelSerializer):
    """Serializer optimisé pour les listes de produits"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    main_image = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    has_discount = serializers.SerializerMethodField()
    is_featured = serializers.BooleanField(source='status.is_featured', read_only=True)
    is_recommended = serializers.BooleanField(source='status.is_recommended', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'brand', 'price', 'compare_at_price',
            'final_price', 'has_discount', 'category', 'category_name',
            'main_image', 'in_stock', 'is_featured', 'is_recommended',
                'short_description', 'created_at'
        ]
    
    def get_main_image(self, obj):
        main_img = obj.images.filter(is_primary=True).first()
        if main_img:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_img.image.url)
            return main_img.image.url
        return None
    
    def get_final_price(self, obj):
        return obj.get_final_price()
    
    def get_has_discount(self, obj):
        return obj.has_discount()

    


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un produit individuel"""
    
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    final_price = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()
    has_discount = serializers.SerializerMethodField()
    whatsapp_link = serializers.SerializerMethodField()
    
    # Status fields
    is_featured = serializers.BooleanField(source='status.is_featured', read_only=True)
    is_recommended = serializers.BooleanField(source='status.is_recommended', read_only=True)
    featured_score = serializers.IntegerField(source='status.featured_score', read_only=True)
    views_count = serializers.IntegerField(source='status.views_count', read_only=True)
    clicks_count = serializers.IntegerField(source='status.clicks_count', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'barcode', 'brand',
            'category', 'short_description', 'description',
            'price', 'compare_at_price', 'cost_price', 'final_price',
            'discount_amount', 'has_discount',
            'stock_quantity', 'in_stock', 'is_active',
            'images', 'whatsapp_link',
            'is_featured', 'is_recommended', 'featured_score',
            'views_count', 'clicks_count',
            
            'meta_title', 'meta_description',
            'published_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sku', 'slug', 'created_at', 'updated_at']
    
    def get_final_price(self, obj):
        return obj.get_final_price()
    
    def get_discount_amount(self, obj):
        return obj.get_discount_amount()
    
    def get_has_discount(self, obj):
        return obj.has_discount()
    
    def get_whatsapp_link(self, obj):
        return obj.get_whatsapp_link()

    





class ProductMinimalSerializer(serializers.ModelSerializer):
    """Serializer minimal pour les select/autocomplete"""
    
    main_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'main_image']
    
    def get_main_image(self, obj):
        main_img = obj.images.filter(is_primary=True).first()
        if main_img:
            return main_img.image.url
        return None


# ===== Promotion Serializers =====

class PromotionListSerializer(serializers.ModelSerializer):
    """Serializer pour les listes de promotions"""
    
    is_active_now = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()
    categories_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Promotion
        fields = [
            'id', 'name', 'slug', 'code', 'promotion_type', 'value',
            'active', 'is_active_now', 'start_at', 'end_at',
            'is_stackable', 'products_count', 'categories_count',
            'applies_to_all'
        ]
    
    def get_is_active_now(self, obj):
        return obj.is_active_now()
    
    def get_products_count(self, obj):
        return obj.products.count()
    
    def get_categories_count(self, obj):
        return obj.categories.count()


class PromotionDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour une promotion"""
    
    products = ProductMinimalSerializer(many=True, read_only=True)
    categories = CategoryMinimalSerializer(many=True, read_only=True)
    is_active_now = serializers.SerializerMethodField()
    usage_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Promotion
        fields = [
            'id', 'name', 'slug', 'code', 'promotion_type', 'value',
            'buy_x', 'get_y', 'active', 'is_active_now',
            'start_at', 'end_at', 'is_stackable',
            'applies_to_all', 'products', 'categories',
            'usage_limit', 'per_user_limit', 'usage_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_is_active_now(self, obj):
        return obj.is_active_now()
    
    def get_usage_count(self, obj):
        return obj.usage_count()


# ===== Newsletter Serializers =====

class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    """Serializer pour les abonnés newsletter"""
    
    class Meta:
        model = NewsletterSubscriber
        fields = [
            'id', 'email', 'name', 'confirmed', 'subscribed',
            'source', 'tags', 'created_at'
        ]
        read_only_fields = ['id', 'confirmed', 'created_at', 'confirmation_token']
    
    def create(self, validated_data):
        # Auto-generate confirmation token
        import uuid
        validated_data['confirmation_token'] = str(uuid.uuid4())
        return super().create(validated_data)


class NewsletterTemplateSerializer(serializers.ModelSerializer):
    """Serializer pour les templates newsletter"""
    
    campaigns_count = serializers.SerializerMethodField()
    
    class Meta:
        model = NewsletterTemplate
        fields = [
            'id', 'name', 'slug', 'subject', 'plain_content',
            'html_content', 'default_from', 'is_active',
            'campaigns_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_campaigns_count(self, obj):
        return obj.campaigns.count()


class NewsletterCampaignListSerializer(serializers.ModelSerializer):
    """Serializer pour les listes de campagnes"""
    
    template_name = serializers.CharField(source='template.name', read_only=True)
    recipients_count = serializers.SerializerMethodField()
    
    class Meta:
        model = NewsletterCampaign
        fields = [
            'id', 'name', 'template', 'template_name', 'status',
            'scheduled_at', 'sent_count', 'recipients_count', 'created_at'
        ]
    
    def get_recipients_count(self, obj):
        return obj.subscribers.count()


class NewsletterCampaignDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour une campagne"""
    
    template = NewsletterTemplateSerializer(read_only=True)
    subscribers = NewsletterSubscriberSerializer(many=True, read_only=True)
    
    class Meta:
        model = NewsletterCampaign
        fields = [
            'id', 'name', 'template', 'status', 'scheduled_at',
            'sent_count', 'subscribers', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sent_count', 'created_at', 'updated_at']


# ===== Service & Settings Serializers =====

class ServiceSerializer(serializers.ModelSerializer):
    """Serializer pour les services"""
    
    class Meta:
        model = Service
        fields = ['id', 'title', 'slug', 'description', 'image', 'order', 'is_active', 'external_link']
        read_only_fields = ['id', 'slug']


class SocialLinkSerializer(serializers.ModelSerializer):
    """Serializer pour les liens sociaux"""
    
    class Meta:
        model = SocialLink
        fields = ['id', 'name', 'url']
        read_only_fields = ['id']
