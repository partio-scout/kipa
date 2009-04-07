# coding: latin-1

from django.newforms.util import ValidationError
from django import newforms as forms
from TulosLaskin import *
from models import*
class MaariteForm(forms.Form) :
       nimi = forms.CharField(max_length=255)
       tyyppi = forms.CharField(max_length=255)
       vihje = forms.CharField(max_length=255)

       def __init__(self,model,data=None) :  
           self.model=model
           prefix="maarite_" + str(self.model.id)
           initial={'nimi': self.model.nimi, 'tyyppi': self.model.tyyppi, 'vihje': self.model.kali_vihje }
           super(forms.Form, self).__init__(data,prefix=prefix,initial=initial)
       
       def save(self) :
           self.model.nimi=self.clean_data['nimi']
           self.model.tyyppi=self.clean_data['tyyppi']
           self.model.kali_vihje=self.clean_data['vihje']
           self.model.save()

class TehtavaForm(forms.Form) :
       nimi = forms.CharField(max_length=255)
       kaava = forms.CharField(max_length=255)

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
      arvo = forms.CharField( max_length=40, required=False)
      def __init__(self,maarite,vartio,post=None) : 
           """
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
          haku = re.search(r'^\d*\Z|^\d*\.\d*\Z', self.clean_data["arvo"] ) 
          if haku :   
             return self.clean_data["arvo"]
          else :  
             raise ValidationError("Syöta Numeroita!")

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
"""
class SyoteForm( forms.Form ) :
       def __init__(self,model,data=None) :  
          self.model=model
          prefix = "syote_" + str(self.model.id)
          
          if self.model.maarite.tyyppi=="piste" :
              arvo= self.model.arvo 
          elif self.model.maarite.tyyppi=="aika" :
              if self.model.arvo and not self.model.arvo == " " :
                  tunnit=divmod(Decimal(self.model.arvo) , 60*60)[0]
                  minuutit=divmod(Decimal(self.model.arvo) , 60)[0]- tunnit*60
                  sekuntit= Decimal(self.model.arvo) - tunnit*60*60 -minuutit*60
                   self.= tunnit 
                      = minuutit
                      = sekuntit
              else : 
                  arvo=self.model.arvo

          initial = {'arvo': arvo}
          super(forms.Form, self).__init__(data,prefix=prefix,initial=initial)
       
       arvo = forms.CharField( max_length=40)

       def clean_arvo(self):
           if not self.tyyppi :
               raise ValidationError("FORMIN TYYPPIÄ EI OLE MÄÄRÄTTY")
           elif self.tyyppi=="aika":
               tunnit = self.clean_data["h"]
               minuutit = self.clean_data["min"]
               sekuntit = self.clean_data["sek"]
               if haku :     
                    return str(Decimal(tunnit*60*60 + Decimal(minuutit)*60 + Decimal(sekuntit)))
               else :
                    raise ValidationError("Syota hh:mm:ss!")
           elif self.tyyppi=="piste" :
               haku = re.search(r'^\d*\Z|^\d*\.\d*\Z', self.clean_data["arvo"] ) 
               if haku :   
                    return self.clean_data["arvo"]
               else :  
                    raise ValidationError("Syöta Numeroita!")
           else: 
               raise ValidationError("Syotteen maritteen tyyppi tuntematon.")

       def save(self) :
          self.model.arvo=self.clean_data['arvo']
          self.model.save()
"""
class AikaValiForm(forms.Form):
      pass
          

