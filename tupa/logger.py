# KiPa(KisaPalvelu), tuloslaskentajärjestelmä partiotaitokilpailuihin
#    Copyright (C) 2010  Espoon Partiotuki ry. ept@partio.fi


from django.conf import settings
from xml.dom.minidom import parse, parseString
import os.path
import re
lokkeri=None
from django.shortcuts import get_object_or_404
from duplicate import kisa_xml
#coding: utf-8

#recorder middleware:
class PostDataRecorder:
        """
        Nauhoittaa post requestit record.xml tietokanta tiedoston loppuun mikali se on olemassa ja settings.RECORDING==True
        """
        def process_request(self, request) : 
                if settings.RECORDING==True: 
                        if request.method == 'POST':
                                posti=request.POST
                                address=request.path
                                
                                kisa_haku = re.search("^/tupa/(.*?)/.*$",address)
                                if not kisa_haku:
                                        return None
                                kisa_nimi = kisa_haku.group(1)

                                data = None
                                if os.path.isfile("record.xml"):
                                        data = parse('record.xml')
                                else:
                                        return None

                                post_test = data.createElement('post_request')
                                post_test.setAttribute("address", address )

                                for n,v in posti.iteritems():
                                        elem = data.createElement('input')
                                        elem.setAttribute("name", n )
                                        elem.setAttribute("value", v )
                                        post_test.appendChild(elem)
                                        data.childNodes[0].appendChild(post_test) 
                                
                                FILE = open("record.xml","w")
                                FILE.write(data.toxml(encoding="utf-8") )
                return None

