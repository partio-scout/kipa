from __future__ import absolute_import
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site
from .formit import KisaForm
from .models import (
    Kisa,
    KisaOikeus,
    OsaTehtava,
    Parametri,
    Sarja,
    Syote,
    SyoteMaarite,
    Tehtava,
    TestausTulos,
    TuomarineuvosTulos,
    Vartio,
)


class SarjaInline(admin.TabularInline):
    model = Sarja
    extra = 1


class ParametriInline(admin.TabularInline):
    model = Parametri
    extra = 1


class SyoteMaariteInline(admin.TabularInline):
    model = SyoteMaarite
    extra = 1


class OsaTehtavaInline(admin.TabularInline):
    model = OsaTehtava
    extra = 1


class KisaOikeusKisaInline(admin.TabularInline):
    model = KisaOikeus
    extra = 1
    verbose_name_plural = "Käyttäjien oikeudet tähän kisaan"


class KisaOikeusKayttajaInline(admin.TabularInline):
    model = KisaOikeus
    extra = 1
    verbose_name_plural = "Näkyvät kisat ja oikeustaso"


class KipaUserAdmin(UserAdmin):
    inlines = [KisaOikeusKayttajaInline]
    list_display = ("username", "first_name", "last_name", "is_active", "is_superuser")
    list_filter = ("is_active", "is_superuser")
    # Kipa käyttää kisakohtaisia oikeuksia, ei Djangon ryhmiä tai mallioikeuksia.
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Henkilötiedot", {"fields": ("first_name", "last_name", "email")}),
        ("Tila", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Kirjautumiset", {"fields": ("last_login", "date_joined")}),
    )
    readonly_fields = ("last_login", "date_joined")


class KisaOikeusAdmin(admin.ModelAdmin):
    list_display = ("kayttaja", "kisa", "taso")
    list_filter = ("kisa", "taso")
    list_editable = ("taso",)
    search_fields = ("kayttaja__username", "kisa__nimi")


class KisaAdmin(admin.ModelAdmin):
    form = KisaForm
    inlines = [SarjaInline, KisaOikeusKisaInline]


class KaavaInline(admin.TabularInline):
    model = OsaTehtava
    extra = 1


class TehtavaAdmin(admin.ModelAdmin):
    inlines = [OsaTehtavaInline]


class OsaTehtavaAdmin(admin.ModelAdmin):
    inlines = [ParametriInline, SyoteMaariteInline]


admin.site.site_url = "/kipa/"
admin.site.site_header = "Kipan ylläpito"
admin.site.site_title = "Kipan ylläpito"
admin.site.index_title = "Käyttäjät ja kisat"

admin.site.register(Kisa, KisaAdmin)
admin.site.register(KisaOikeus, KisaOikeusAdmin)
admin.site.unregister(User)
admin.site.register(User, KipaUserAdmin)
admin.site.unregister(Group)
admin.site.unregister(Site)
admin.site.register(Sarja)
admin.site.register(Tehtava, TehtavaAdmin)
admin.site.register(Vartio)
admin.site.register(Syote)
admin.site.register(SyoteMaarite)
admin.site.register(TuomarineuvosTulos)
admin.site.register(TestausTulos)
admin.site.register(OsaTehtava, OsaTehtavaAdmin)
admin.site.register(Parametri)
