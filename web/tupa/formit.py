# coding: latin-1

from django.newforms.util import ValidationError
from django import newforms as forms
from TulosLaskin import *
from models import *

def luoPostista(Malli,objekti,Form,forminNimi,post):
     """
     LuoFormit post datasta.
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
               models = Malli.objects.filter(id=haku.group(2))
               if models:
                   model=models[0]
               formi= Form(objekti,data=post,model=model,id=haku.group(1))
               formit.append(formi)
     return formit

def luoMaariteFormit(tehtavalle,post=None,tyhjia=0):
    formit=[]
    formi_id=0
    maaritteet= SyoteMaarite.objects.filter(tehtava=tehtavalle)
    if post:
        formit=luoPostista(SyoteMaarite,tehtavalle,MaariteForm,"maarite",post)
        for f in formit:
            if formi_id<=int(f.id) :
                formi_id = int(f.id)
    else :
        for m in maaritteet :
            formi= MaariteForm(tehtavalle,model=m,id=formi_id)
            formi_id=formi_id+1
            formit.append(formi)
    for i in range(tyhjia) :
        formi= MaariteForm(tehtavalle,id=formi_id)
        formi_id=formi_id+1
        formit.append(formi)
    return formit

tyypit= (("piste","luku"),("aika","aika"))
class MaariteForm(forms.Form) :
       nimi = forms.CharField(max_length=255,required=False)
       tyyppi = forms.ChoiceField(required=False,choices=tyypit)
       vihje = forms.CharField(max_length=255,required=False)

       def __init__(self,tehtava,model=None,data=None,id=None) :  
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
           if self.is_valid():
                nimi=self.clean_data['nimi'] 
                tyyppi=self.clean_data['tyyppi']
                vihje=self.clean_data['vihje']
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
                    initial={'nimi': self.maarite.nimi,
                            'tyyppi': self.maarite.tyyppi, 
                            'vihje': self.maarite.kali_vihje }
                    super(forms.Form, self).__init__(prefix=self.prefix,initial=initial)
       def empty(self) :
           if self.is_valid():
               if self.clean_data['nimi'] :
                   return False
               else : 
                   return True

class TehtavaForm(forms.Form) :
       nimi = forms.CharField(max_length=255)
       kaava = forms.CharField(max_length=255,widget=forms.TextInput(attrs={'size':'50'}))

       def __init__(self,model,data=None) :  
          self.model=model
          prefix = "tehtava_" + str(self.model.id)
          initial={ 'nimi' : self.model.nimi, 'kaava' : self.model.kaava }
          super(forms.Form, self).__init__(data,prefix=prefix,initial=initial)
       def save(self) :
          self.model.nimi=self.clean_data['nimi']
          self.model.kaava=self.clean_data['kaava']
          self.model.save() 
          
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
          haku = re.search(r'^\d*\Z|^\d*\.\d*\Z|^h\Z', self.clean_data["arvo"] ) 
          if haku :   
             return self.clean_data["arvo"]
          else :  
             raise ValidationError('Syöta lukuja tai "h"=hylätty')

      def save(self) :
           """ 
           Tallettaa formin tiedot tietokannan syöte tauluun, mikäli kenttä on syötetty oikein.
           Mikäli taulua ei ole olemassa se luodaan.
           Mikäli formi on tyhjä, formia vastaava tietokannan taulu tuhotaan.
           """
           if self.is_valid() :
              arvo = self.clean_data["arvo"]
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
               tunnit= self.clean_data["h"]
               minuutit= self.clean_data["min"]
               sekuntit= self.clean_data["s"]
               
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

class AikaValiForm(forms.Form):
      pass
          

