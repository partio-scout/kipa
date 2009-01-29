# coding: latin-1
from models import *
from django.shortcuts import render_to_response
import operator
import decimal 

def index(request):
      kisat = Kisa.objects.all()
      return render_to_response('tupa2/index.html', {'latest_kisa_list': kisat })

def kisa(request,kisa_id):
      sarjat = Sarja.objects.filter(kisa__id=kisa_id)
      return render_to_response('tupa2/kisa.html', {'sarja_list': sarjat })

def sarja(request,sarja_id) :
      sarja= Kisa.objects.filter(id=sarja_id)[0]
      return render_to_response('tupa2/sarja.html', {'sarja_object': sarja })

def tulokset(request,sarja_id):
    sarja = Sarja.objects.filter(id=sarja_id)[0]

    kisat = Kisa.objects.all()
    for i in kisat :
         i.laskeTulokset()

    vartiot = Vartio.objects.all() 
    tehtavat = Tehtava.objects.all() 
    taulukko= []
    ekarivi= []

    # ekarivi
    ekarivi.append( "Sij")
    ekarivi.append( "No")
    ekarivi.append( "Vartio" )
    ekarivi.append( "Yht" )
    for t in tehtavat :
           ekarivi.append( t.nimi )
    taulukko.append(ekarivi)
  
    # tokarivi
    tokarivi= []
    tokarivi.append( " " )
    tokarivi.append( " " )
    tokarivi.append( "Maxpisteet" )
    tokarivi.append( sarja.maksimipisteet )
    for t in tehtavat :
           tokarivi.append( t.maksimipisteet)
    taulukko.append(tokarivi)

    # vartiot
    tulostaulu=[]
    for v in vartiot :
       rivi = []
       rivi.append("")
       rivi.append(v.nro)
       rivi.append(v.nimi)
       yhteensa = 0.0
       rivi.append(yhteensa)
       for t in tehtavat :
           pisteet = Lopputulos.objects.filter(vartio=v).filter(tehtava=t)[0].pisteet
           if pisteet!=None:
               rivi.append("%.1f" % pisteet)
               yhteensa=yhteensa + pisteet
           else:
               rivi.append("-")
       rivi[3]=yhteensa
       tulostaulu.append(rivi)

    tulostaulu.sort(key=operator.itemgetter(3))
    tulostaulu.reverse()
    for i in range(len(tulostaulu)) :
         tulostaulu[i][0]=i+1
         tulostaulu[i][3]="%.1f" % tulostaulu[i][3]
    taulukko=taulukko+tulostaulu
    return render_to_response('tupa2/tulokset.html', {'tulos_taulukko' : taulukko , 'sarja_objekti' : sarja } )


