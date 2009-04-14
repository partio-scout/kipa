# coding: latin-1
from django.core.exceptions import ObjectDoesNotExist

from django.forms.util import ValidationError
from django import forms
from TulosLaskin import *
from models import *

def luoNimi(forminNimi,objektinID=None,id=None):
        prefix = forminNimi
        if id :
            prefix= prefix +"_" + str(id)
        else :
            prefix= prefix +"_#"
        if objektinID:
            prefix= prefix +"_" + str(objektinID)
        else :
            prefix= prefix +"_#"
        return prefix

def luoPostista(Malli,objekti,Form,forminNimi,post):
     """
     Luo formeja listaan post datasta.
     Malli = Tietokanta taulu jonka dataa formi muokkaa.
     objekti = Tietokanta objekti joka liittyy jokaiseen formiin (formin konstruktorin 1 parametri)
     Form = Formi luokka jonka instansseja tullaan luomaan listaan
     forminNimi = nimi jolla kyseinen formi identifioidaan post datassa.
     post = post data josta formit luodaan.
     """
     formit=[]
     tiedot=set()
     for k,v in post.items() :
           haku = re.search(r'^(' + forminNimi + '_\d*_.*?)-.*', k ) 
           if haku:
               tiedot.add( haku.group(1) )
     for f in tiedot :
           haku = re.search(r'^' + forminNimi + '_(\d*)_(.*)', f ) 
           model=None
           if haku :
               if haku.group(2).isdigit():
                   model = Malli.objects.get(id=haku.group(2))
               formi= Form(objekti,model,post,id=haku.group(1))
               formit.append(formi)
     return formit


tyypit= (("piste","luku"),("aika","aika"))
class MaariteForm(forms.Form) :
       nimi = forms.CharField(max_length=255,required=False)
       tyyppi = forms.ChoiceField(required=False,choices=tyypit)
       vihje = forms.CharField(max_length=255,required=False)

       def __init__(self,tehtava=None,model=None,data=None,id=None) :  
           self.tehtava=tehtava
           self.maarite=model
           self.id=id
           prefix= "maarite_" + str(self.id) + "_"
           initial={}
           if self.maarite :
               prefix=prefix + str(self.maarite.id)
               initial={'nimi': self.maarite.nimi, 'tyyppi': self.maarite.tyyppi, 'vihje': self.maarite.kali_vihje }
           else : 
               prefix=prefix + "#"
           super(forms.Form, self).__init__(data,prefix=prefix,initial=initial)

       def save(self) :
           if self.is_valid() and self.tehtava:
                nimi=self.cleaned_data['nimi'] 
                tyyppi=self.cleaned_data['tyyppi']
                vihje=self.cleaned_data['vihje']
                if not nimi :
                    if self.maarite :
                        self.maarite.delete()
                        self.maarite = None
                else :
                    if not self.maarite :
                        self.maarite=SyoteMaarite()
                        self.maarite.tehtava=self.tehtava
                    self.maarite.nimi=nimi
                    self.maarite.tyyppi=tyyppi
                    self.maarite.kali_vihje=vihje
                    self.maarite.save()
                    self.prefix="maarite_"+ str(self.id) + "_" + str(self.maarite.id)
                    super(forms.Form, self).__init__(prefix=self.prefix,initial=self.cleaned_data)
       def empty(self) :
           if self.is_valid():
               if self.cleaned_data['nimi'] :
                   return False
               else : 
                   return True

def luoMaariteFormit(tehtavalle=None,post=None,tyhjia=0):
    """
    Luo listaan määriteiden formit haluttusta tehtävästä. 
    Mikäli post data on määritelty, täytetään formien sisältö sieltä, muutoin tietokannasta.
    Halutessa lisää listan loppuun tyhjiä formeja.
    """
    formit=[]
    formi_id=1
    if tehtavalle :
        maaritteet= SyoteMaarite.objects.filter(tehtava=tehtavalle)
        # Luodaan post datasta:
        if post:
            formit=luoPostista(SyoteMaarite,tehtavalle,MaariteForm,"maarite",post)
            for f in formit:
                if formi_id<=int(f.id) :
                    formi_id = int(f.id)
        # Tai tietokannan tehtävän määritteistä:
        else :
            for m in maaritteet :
                formi= MaariteForm(tehtavalle,model=m,id=formi_id)
                formi_id=formi_id+1
                formit.append(formi)
    
    # Lisätään tyhjät:
    for i in range(tyhjia) :
        formi= MaariteForm(tehtavalle,id=formi_id)
        formi_id=formi_id+1
        formit.append(formi)
    return formit

class TehtavaForm(forms.Form) :
       nimi = forms.CharField(max_length=255,required=False)
       kaava = forms.CharField(max_length=255,required=False,widget=forms.TextInput(attrs={'size':'50'}))
       def __init__(self,sarja=None,tehtava=None,post=None,id=None) :  
          self.tehtava=tehtava
          self.sarja=sarja
          if not self.sarja and self.tehtava :
              self.sarja = self.tehtava.sarja
             

          self.id = id
          initial={}
          objektinID = None
          if self.tehtava :
              objektinID = tehtava.id
              initial={ 'nimi' : self.tehtava.nimi, 'kaava' : self.tehtava.kaava }
          prefix= luoNimi("tehtava", objektinID , id=self.id)
          super(forms.Form, self).__init__(post,prefix=prefix,initial=initial)
       def save(self) :
          if self.is_valid() and self.sarja :
             nimi=self.cleaned_data["nimi"]
             kaava=self.cleaned_data["kaava"]
             if nimi:
                 if not self.tehtava:
                     self.tehtava=Tehtava()
                     self.tehtava.sarja=self.sarja
                 self.tehtava.nimi=nimi
                 self.tehtava.kaava=kaava
                 self.tehtava.save()
                 prefix= luoNimi("tehtava",self.tehtava.id,self.id)
                 super(forms.Form, self).__init__(prefix=prefix,initial=self.cleaned_data)
             elif self.tehtava:
                 self.tehtava.delete()
                 self.tehtava = None

          
class PisteSyoteForm(forms.Form):
      """
      Formi joka ottaa vastaan merkkijonon jossa on luku, tallentaa sen syötteeseen.
      """
      arvo = forms.CharField( max_length=40, required=False,widget=forms.TextInput(attrs={'size':'2'}))
      def __init__(self,maarite,vartio,post=None) : 
           """
           Luo formin.
           Pakolliset parametrit ovat:
               -Syötteen määrite jota formi edustaa
               -Vartio jota formi edustaa
           Optionaaliset:
               -Sivun post data josta kentään syödetyt tiedot haetaan.
           """
           self.maarite=maarite
           syotteet = Syote.objects.filter(vartio = vartio ).filter(maarite=maarite)
           self.syote=None
           if syotteet:
               self.syote=syotteet[0]
           self.vartio=vartio
           prefix = "piste_syote_" + str(self.maarite.id) + "_" + str(self.vartio.id)
           initial ={}
           if self.syote :
               initial= { "arvo" : self.syote.arvo }    
           super(forms.Form, self).__init__(post,prefix=prefix,initial=initial)
      def clean_arvo(self) :
          """
          Syötetyn arvon validiointi funktio. Tarkistaa että on numero, tai h.
          """
          haku = re.search(r'^\d*\Z|^\d*\.\d*\Z|^h\Z', self.cleaned_data["arvo"] ) 
          if haku :   
             return self.cleaned_data["arvo"]
          else :  
             raise ValidationError('Syöta lukuja tai "h"=hylätty')

      def save(self) :
           """ 
           Tallettaa formin tiedot tietokannan syöte tauluun, mikäli kenttä on syötetty oikein.
           Mikäli taulua ei ole olemassa se luodaan.
           Mikäli formi on tyhjä, formia vastaava tietokannan taulu tuhotaan.
           """
           if self.is_valid() :
              arvo = self.cleaned_data["arvo"]
              if arvo:
                 if not self.syote:
                     self.syote = Syote()
                     self.syote.maarite=self.maarite
                     self.syote.vartio=self.vartio
                 self.syote.arvo = arvo
                 self.syote.save()    
              else :
                 if self.syote:
                    self.syote.delete()
                    self.syote = None

class AikaSyoteForm(forms.Form) :
       h = forms.IntegerField(required=False,widget=forms.TextInput(attrs={'size':'1'}))
       min = forms.IntegerField(required=False,widget=forms.TextInput(attrs={'size':'1'}))
       s = forms.IntegerField(required=False,widget=forms.TextInput(attrs={'size':'1'}))

       def __init__(self,maarite,vartio,post=None) : 
           """
           Pakolliset parametrit ovat:
               -Syötteen määrite jota formi edustaa
               -Vartio jota formi edustaa
           Optionaaliset:
               -Sivun post data jossa kentään syödetyt tiedot.
           """
           self.maarite=maarite
           syotteet = Syote.objects.filter(vartio = vartio ).filter(maarite=maarite)
           self.syote=None
           if syotteet:
               self.syote=syotteet[0]
           self.vartio=vartio
           prefix = "aika_syote_" + str(self.maarite.id) + "_" + str(self.vartio.id)
           initial ={}
           if self.syote and self.syote.arvo:
                  tunnit=divmod(Decimal(self.syote.arvo) , 60*60)[0]
                  minuutit=divmod(Decimal(self.syote.arvo) , 60)[0]- tunnit*60
                  sekuntit= Decimal(self.syote.arvo) - tunnit*60*60 -minuutit*60
                  h = tunnit
                  min = minuutit
                  s = sekuntit
                  initial= { "h" : h, "min" : min , "s" : s }    
           super(forms.Form, self).__init__(post,prefix=prefix,initial=initial)

       def save(self) :
           if self.is_valid() :
               tunnit= self.cleaned_data["h"]
               minuutit= self.cleaned_data["min"]
               sekuntit= self.cleaned_data["s"]
               
               if not tunnit==None or not minuutit==None or not sekuntit==None :
                  arvo=Decimal(0)
                  if tunnit :
                      arvo=arvo + tunnit*60*60
                  if minuutit:
                      arvo=arvo + minuutit*60
                  if sekuntit:
                      arvo= arvo + sekuntit

                  if not self.syote:
                      self.syote=Syote()
                      self.syote.maarite=self.maarite
                      self.syote.vartio=self.vartio
                  self.syote.arvo = str(arvo)
                  self.syote.save()
               else:
                  if self.syote:
                      self.syote.delete()
                      self.syote = None

class VartioForm(forms.Form):
    numero = forms.IntegerField(required=False,widget=forms.TextInput(attrs={'size':'2'}))
    nimi = forms.CharField(max_length=50,required=False)
    def __init__(self,sarja=None,vartio=None,post=None,id=None):
        self.sarja=sarja
        self.vartio=vartio
        self.id=id
        initial={}
        objektinID = None
        sarjanNimi="#"
        if self.sarja :
           sarjanNimi=self.sarja.nimi
        if self.vartio:
             objektinID = vartio.id 
             initial={'nimi': self.vartio.nimi , 'numero' : self.vartio.nro }
        prefix= luoNimi("vartio_"+sarjanNimi,objektinID,id=self.id)
        super(forms.Form, self).__init__(post,prefix=prefix,initial=initial)

    def __cmp__(self,other) :
        if self.is_valid() and other.is_valid():
            return cmp(self.cleaned_data["numero"],other.cleaned_data['numero'] )
        else :
            return 0 

    def save(self) :
        if self.is_valid() and self.sarja :
             nimi=self.cleaned_data["nimi"]
             numero=self.cleaned_data["numero"]
             if nimi:
                 if not self.vartio:
                     self.vartio=Vartio()
                     self.vartio.sarja=self.sarja
                 self.vartio.nimi=nimi
                 self.vartio.nro=numero
                 self.vartio.save()
                 prefix= luoNimi("vartio_"+self.sarja.nimi,self.vartio.id,self.id)
                 super(forms.Form, self).__init__(prefix=prefix,initial=self.cleaned_data)
             elif self.vartio :
                 self.vartio.delete()
                 self.vartio = None

    def empty(self) :
        if self.is_valid() :
            if self.cleaned_data["nimi"] and self.cleaned_data["numero"] :
                return False
            else: 
                return True
        else: 
            return False

def luoVartioFormit(sarjalle,post=None,tyhjia=0):
    formit=[]
    formi_id=1
    vartiot = Vartio.objects.filter(sarja=sarjalle)
    # Luodaan post datasta:
    if post:
        nimi="vartio_"+sarjalle.nimi
        formit=luoPostista(Vartio,sarjalle,VartioForm,"vartio_"+sarjalle.nimi,post)
        formit.sort()
        for f in formit:
            if formi_id<=int(f.id) :
                formi_id = int(f.id)
    # Tai tietokannan tehtävän määritteistä:
    else :
        for v in vartiot :
            formi= VartioForm(sarjalle,v,id=formi_id)
            formi_id=formi_id+1
            formit.append(formi)
    # Lisätään tyhjät:
    for i in range(tyhjia) :
        formi= VartioForm(sarjalle,id=formi_id)
        formi_id=formi_id+1
        formit.append(formi)

    return formit

class KisaForm(forms.Form):
    nimi = forms.CharField(max_length=50,required=False)
    def __init__(self,kisa=None,post=None,id=None):
        self.kisa=kisa
        self.id=id
        initial={}
        objektinID = None
        if self.kisa:
             objektinID = kisa.id 
             initial={'nimi': self.kisa.nimi  }
        prefix= luoNimi("kisa",objektinID,id=self.id)
        super(forms.Form, self).__init__(post,prefix=prefix,initial=initial)

    def save(self) :
         if self.is_valid() :
             nimi=self.cleaned_data["nimi"]
             if nimi:
                 if not self.kisa:
                     self.kisa=Kisa()
                 self.kisa.nimi=nimi
                 self.kisa.save()
                 prefix= luoNimi("kisa",self.kisa.id,self.id)
                 super(forms.Form, self).__init__(prefix=prefix,initial=self.cleaned_data)
             elif self.kisa:
                 self.kisa.delete()
                 self.kisa = None
    def empty(self) :
        if self.is_valid() :
            if self.cleaned_data["nimi"]  :
                return False
            else: 
                return True
        else: 
            return False


class SarjaForm(forms.Form):
    nimi = forms.CharField(max_length=50,required=False)
    def __init__(self,kisa=None,sarja=None,post=None,id=None):
        self.kisa=kisa
        self.sarja=sarja
        self.id=id
        initial={}
        objektinID = None
        if self.sarja:
             objektinID = sarja.id 
             initial={'nimi': self.sarja.nimi}
        prefix= luoNimi("sarja",objektinID,id=self.id)
        super(forms.Form, self).__init__(post,prefix=prefix,initial=initial)
    def save(self) :
           if self.is_valid() and self.kisa:
             nimi=self.cleaned_data["nimi"]
             if nimi :
                 if not self.sarja:
                     self.sarja=Sarja()
                 self.sarja.kisa=self.kisa
                 self.sarja.nimi=nimi
                 self.sarja.save()
                 prefix= luoNimi("sarja",self.sarja.id,self.id)
                 super(forms.Form, self).__init__(prefix=prefix,initial=self.cleaned_data)
             elif self.sarja:
                 self.sarja.delete()
                 self.sarja = None
    def empty(self):
        if self.is_valid() :
            if self.cleaned_data["nimi"]  :
                return False
            else: 
                return True
        else: 
            return False

def luoSarjaFormit(kisalle,post=None,tyhjia=0):
    formit=[]
    formi_id=1
    sarjat= Sarja.objects.filter(kisa=kisalle)
    # Luodaan post datasta:
    if post:
        nimi="sarja"
        formit=luoPostista(Kisa,kisalle,SarjaForm,"sarja",post)
        formit.sort()
        for f in formit:
            if formi_id<=int(f.id) :
                formi_id = int(f.id)
    # Tai tietokannan tehtävän määritteistä:
    else :
        for s in sarjat :
            formi= SarjaForm(kisalle,s,id=formi_id)
            formi_id=formi_id+1
            formit.append(formi)
    # Lisätään tyhjät:
    for i in range(tyhjia) :
        formi= SarjaForm(kisalle,id=formi_id)
        formi_id=formi_id+1
        formit.append(formi)

    return formit

