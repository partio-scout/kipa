# coding: latin-1
from models import *
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect
import operator
import decimal 
from django.newforms import *
from django.forms import *

def index(request):
      kisat = Kisa.objects.all()
      return render_to_response('tupa/index.html', {'latest_kisa_list': kisat })

def kisa(request,kisa_id):
      sarjat = Sarja.objects.filter(kisa__id=kisa_id)
      return render_to_response('tupa/kisa.html', {'sarja_list': sarjat })

def sarja(request,sarja_id) :
      sarja= Kisa.objects.filter(id=sarja_id)[0]
      return render_to_response('tupa/sarja.html', {'sarja_object': sarja })

#tulosten syotto  
def syotto(request):
    manipulator=Syotatulos.AddManipulator()
    
#    if request.method == 'POST':
        
    data = request.POST.copy()
    errors = None  
#   errors = manipulator.get_validation_errors(data)
    manipulator.do_html2python(data)
    
    if not errors:
           haku = data.clean_data
           halututKisat = Kisa.objects.filter(kisa__nimi = haku[0])
           halututSarjat = Sarja.objects.filter(sarja__nimi = haku[1]).filter(kisa = halututKisat)
           halututTehtavat = tehtava.objects.filter(tehtava__jarjestysnro = haku[2]).filter(sarja = halututSarjat)
           
           TulosForm = form_for_model(halututTehtavat)
           
           return render_to_response('tupa/syotto.html', {'form': TulosForm})
        
    else:
           return HttpResponse('Ei hjuva')
 #   else:
  #      return HttpResponse('Ei menty hakuun')
        
#    form = FormWrapper(manipulator, {}, {})
#    return render_to_response('tupa/syotto.html', {'form': form})



def tulokset(request,sarja_id):
    sarja = Sarja.objects.filter(id=sarja_id)[0]
    tulokset= sarja.laskeTulokset()
    return render_to_response('tupa/tulokset2.html', {'tulos_taulukko' : tulokset }  )

