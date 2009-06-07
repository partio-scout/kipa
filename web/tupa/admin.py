from web.tupa.models import *
from django.contrib import admin
from formit import *

class SarjaInline(admin.TabularInline):
    model = Sarja
    extra = 4

class KisaAdmin(admin.ModelAdmin):
    form = KisaForm
    fieldsets = [
        (None,               {'fields': ['nimi']}),
        ('Optionaalinen informaatio', {'fields': ['aika','paikka'], 'classes': ['collapse']}),
    ]
    inlines = [SarjaInline]

class KaavaInline(admin.TabularInline):
    model = OsapisteKaava
    extra = 1

class SyoteMaariteInline(admin.TabularInline):
    model = SyoteMaarite
    extra = 2

class TehtavaAdmin(admin.ModelAdmin) :
    fieldsets = [
        (None,               {'fields': ['nimi','kaava','jarjestysnro']}),
        ('Optionaalinen informaatio', {'fields': ['tehtavaryhma','tehtavaluokka','rastikasky'], 'classes': ['collapse']}),
    ]
    inlines = [SyoteMaariteInline,KaavaInline]


admin.site.register(Kisa, KisaAdmin)
admin.site.register(Sarja)
admin.site.register(Tehtava,TehtavaAdmin)
admin.site.register(Vartio)
admin.site.register(Syote)
admin.site.register(SyoteMaarite)
admin.site.register(Allergia)
admin.site.register(TuomarineuvosTulos)
admin.site.register(TestausTulos)

