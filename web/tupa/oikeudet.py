from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Kisa, KisaOikeus


def kayttajan_taso(user, kisa):
    if not user.is_authenticated or not user.is_active:
        return 0
    if user.is_superuser:
        return KisaOikeus.YLLAPITO
    oikeus = KisaOikeus.objects.filter(kisa=kisa, kayttaja=user).first()
    return oikeus.taso if oikeus else 0


def nakyvat_kisat(user):
    if not user.is_authenticated or not user.is_active:
        return Kisa.objects.none()
    if user.is_superuser:
        return Kisa.objects.all()
    return Kisa.objects.filter(kisaoikeus__kayttaja=user)


def aseta_oikeudet(request, taso):
    """Oikeudet templateille: {% if request.oikeudet.maaritys %}"""
    request.oikeudet = {
        "tulokset": taso >= KisaOikeus.TULOKSET,
        "syotto": taso >= KisaOikeus.SYOTTO,
        "maaritys": taso >= KisaOikeus.MAARITYS,
        "yllapito": taso >= KisaOikeus.YLLAPITO,
    }


def tarkista_oikeus(request, kisa, vaadittu_taso):
    taso = kayttajan_taso(request.user, kisa)
    if taso < vaadittu_taso:
        raise PermissionDenied
    aseta_oikeudet(request, taso)


def vaadi_oikeus(vaadittu_taso):
    """Näkymän dekoraattori: vaatii kirjautumisen ja oikeustason kisaan kisa_nimi."""

    def decorator(view):
        @wraps(view)
        def wrapper(request, kisa_nimi, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            kisa = get_object_or_404(Kisa, nimi=kisa_nimi)
            tarkista_oikeus(request, kisa, vaadittu_taso)
            return view(request, kisa_nimi, *args, **kwargs)

        return wrapper

    return decorator
