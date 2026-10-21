from django.contrib import admin
from .models import BucketItem, Moment, MomentPhoto


class MomentPhotoInline(admin.TabularInline):
    model = MomentPhoto
    extra = 0


@admin.register(Moment)
class MomentAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'period', 'category', 'location')
    list_filter = ('period', 'category')
    search_fields = ('title', 'description', 'location')
    inlines = (MomentPhotoInline,)


@admin.register(BucketItem)
class BucketItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_completed', 'created_at')
    list_filter = ('is_completed',)
    search_fields = ('title',)
