from web.tupa.models import *
from django.contrib import admin


class SarjaInline(admin.TabularInline):
    model = Sarja
    extra = 4

class KisaAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['nimi']}),
        ('Optionaalinen informaatio', {'fields': ['aika','paikka'], 'classes': ['collapse']}),
    ]
    inlines = [SarjaInline]

class SyoteMaariteInline(admin.TabularInline):
    model = SyoteMaarite
    extra = 4

class TehtavaAdmin(admin.ModelAdmin) :
    fieldsets = [
        (None,               {'fields': ['nimi','kaava','jarjestysnro']}),
        ('Optionaalinen informaatio', {'fields': ['tehtavaryhma','tehtavaluokka','rastikasky'], 'classes': ['collapse']}),
    ]
    inlines = [SyoteMaariteInline]


admin.site.register(Kisa, KisaAdmin)
admin.site.register(Sarja)
admin.site.register(Tehtava,TehtavaAdmin)
admin.site.register(Vartio)
admin.site.register(Syote)
admin.site.register(SyoteMaarite)
admin.site.register(Allergia)
admin.site.register(TuomarineuvosTulos)

