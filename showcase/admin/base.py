from django.contrib.admin import ModelAdmin, TabularInline
from django.db.models import F


class OptimizedModelAdmin(ModelAdmin):
    """Base admin class with query optimizations"""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return self.optimize_queryset(qs)

    def optimize_queryset(self, qs):
        """Override in subclasses to add select_related/prefetch_related"""
        return qs


class OptimizedTabularInline(TabularInline):
    """Base inline class with query optimizations"""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return self.optimize_queryset(qs)

    def optimize_queryset(self, qs):
        """Override in subclasses to add select_related/prefetch_related"""
        return qs


class TimestampReadOnlyMixin:
    """Mixin to add timestamp fields as read-only"""

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))

        if 'created_at' in self.model._meta.get_fields():
            readonly.append('created_at')

        if 'updated_at' in self.model._meta.get_fields():
            readonly.append('updated_at')

        return readonly


class UserTrackingMixin:
    """Mixin to track user who modified the object"""

    def save_model(self, request, obj, form, change):
        if hasattr(obj, 'updated_by'):
            obj.updated_by = request.user

        super().save_model(request, obj, form, change)


class SingletonAdminMixin:
    """Mixin for singleton models (only one instance)"""

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


class FilteredDisplayMixin:
    """Mixin to simplify list_display configuration"""

    def get_list_display(self, request):
        return self.list_display or []

    def get_list_filter(self, request):
        return self.list_filter or []

    def get_search_fields(self, request):
        return self.search_fields or []


class ActionsMixin:
    """Mixin for common admin actions"""

    def get_actions(self, request):
        actions = super().get_actions(request)

        if not self.actions:
            return actions

        return actions


class SoftDeleteMixin:
    """Mixin for soft delete (if model has is_deleted field)"""

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if hasattr(self.model, 'is_deleted'):
            qs = qs.filter(is_deleted=False)

        return qs
