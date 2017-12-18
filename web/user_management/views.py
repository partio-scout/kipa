# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.forms import modelform_factory, modelformset_factory
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages

# Create your views here.

@permission_required('auth.change_user')
def kayttajat(request, kisa_nimi=None):
        """
        Käyttäjien hallintasivu.
        Ylläpitäjä muokkaa kisan käyttäjien oikeuksia

        """
        modelform = modelform_factory(User, 
            fields=('username', 'password', 'first_name', 'last_name', 'email', 'groups'),
            )
        modelformset = modelformset_factory(User, 
            fields=('id', 'username', 'first_name', 'last_name', 'email', 'groups'),
            can_delete = True, 
            extra=0)

        form = modelform()
        formset = modelformset(queryset = User.objects.all().exclude(is_staff = True), auto_id = False)

        if request.method == 'POST':
            '''Käsittele tallennus'''
            if 'username' in request.POST:
                #jos POSTissa uuden käyttäjän tallennus
                form = modelform(request.POST)
                if form.is_valid():
                    user = form.save(commit=False)
                    user.password = make_password(form.cleaned_data['password'])
                    user.save()
                    form.save_m2m()
                    messages.success(request, u'Käyttäjä lisätty' )
                else:
                    messages.error(request, u'Ei onnistu, korjaa merkityt kentät' )

            else:
                #jos POSTissa käyttäjälistan muokkaus
                formset = modelformset(request.POST)
                if formset.is_valid():
                    formset.save()
                    formset = modelformset(queryset = User.objects.all().exclude(is_staff = True), auto_id = False)
                    messages.success(request, u'Tiedot päivitetty' )
                else:
                    messages.error(request, u'Ei onnistu, korjaa merkityt kentät' )

        return render(request, 'user_management/kayttajat.html',{
            'kisa_nimi': kisa_nimi, 
            'heading' : 'Käyttäjät',
            'form' : form,
            'formset' : formset, 
            },)

def kayttajan_tiedot(request, user_name = None):
    """
    Käyttäjä muokkaa omia tietojaan
    """
    if request.user.is_authenticated():
        from django.contrib.auth import update_session_auth_hash
        userform = modelform_factory(User, 
                fields=('username', 'first_name', 'last_name', 'email'),
                )
        form = userform(instance = User.objects.get(id = request.user.id))
        pwform = PasswordChangeForm(request.user)

        if request.method == 'POST':
            '''Käsittele tallennus'''
            if 'username' in request.POST:
                #jos POSTissa käyttäjän tietojen päivitys
                form = userform(request.POST, instance = User.objects.get(id = request.user.id))
                if form.is_valid():
                    form.save()
                    messages.success(request, u'Tiedot päivitetty' )
                else:
                    messages.error(request, u'Ei onnistu, korjaa merkityt kentät' )

            else:
                #jos POSTissa käyttäjän salasanan päivitys
                pwform = PasswordChangeForm(request.user, request.POST)
                if pwform.is_valid():
                    user = pwform.save()
                    update_session_auth_hash(request, user)  # Important!
                    pwform = PasswordChangeForm(request.user)
                    messages.success(request, u'Salasana päivitetty' )
                else:
                    messages.error(request, u'Ei onnistu, korjaa merkityt kentät' )

    else:
        from django.contrib.auth import authenticate, login
        form = UserCreationForm()
        pwform = False
        if request.method == 'POST':
            #jos POSTissa uuden käyttäjän tallennus
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                new_user = authenticate(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'],
                                        )
                login(request, new_user)
                return redirect("/kipa/kayttaja/{}".format(form.cleaned_data['username']))
            else:
                messages.error(request, u'Ei onnistu, korjaa merkityt kentät' )

    return render(request, 'user_management/kayttajan_tiedot.html',{
        'heading' : 'Käyttäjän tiedot',
        'form' : form,
        'pwform' : pwform, 
        },)

