from django.contrib import admin

class RelatedModelInline(admin.TabularInline):
    model = RelatedModel
    extra = 1

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ('',)
    search_fields = ('',)
    list_filter = ('',)
    ordering = ('',)
    readonly_fields = ('',)
    fieldsets = (
        ("정보", {"fields": ('',)}),
    )

    add_fieldsets = (
        ("정보", {"fields": ('',)}),
    )
    inlines = [RelatedModelInline]
