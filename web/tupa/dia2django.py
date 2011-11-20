# encoding: utf-8
# KiPa(KisaPalvelu), tuloslaskentajärjestelmä partiotaitokilpailuihin
#    Copyright (C) 2010  Espoon Partiotuki ry. ept@partio.fi


import codecs
import gzip
import xml.dom.minidom
import re
import sys

class Atribuutti:
        nimi = ""
        tyyppi = ""
        arvo = ""

class Luokka:
        nimi = ""
        atribuutit=[]

class Kaavio:
        luokat=[]

def haeNimi( luokalle) :
        nimi = ""
        for c in luokalle.childNodes:
                if c.nodeType==xml.dom.minidom.Node.ELEMENT_NODE and c.hasAttributes():
                        if c.getAttribute("name")=="name":
                                nimi= c.getElementsByTagName("dia:string")[0].childNodes[0].data[1:-1]
        return nimi

def haeAtribuutit( luokalle ) : 
    atribuutit=[]
    for c in luokalle.childNodes:
       if c.nodeType==xml.dom.minidom.Node.ELEMENT_NODE and c.hasAttributes():
           if c.getAttribute("name")=="attributes":
               for l in c.getElementsByTagName("dia:composite") :
                   if l.getAttribute("type")=="umlattribute":
                        atr=Atribuutti()
                        #Look for the attribute name and type
                        for k in l.getElementsByTagName("dia:attribute") :
                            if k.getAttribute("name")=="name":
                                atr.nimi = k.getElementsByTagName("dia:string")[0].childNodes[0].data[1:-1]
                            elif k.getAttribute("name")=="type":
                                atr.tyyppi = k.getElementsByTagName("dia:string")[0].childNodes[0].data[1:-1]
                            elif k.getAttribute("name")=="value":
                                atr.arvo = k.getElementsByTagName("dia:string")[0].childNodes[0].data[1:-1]
                        atribuutit.append(atr)
    return atribuutit

def haeLuokat(objekteista):
    luokat=[]
    for o in objekteista:
        if o.getAttribute("type")=="UML - Class":
            luokka=Luokka()
            luokka.nimi=haeNimi( o )
            luokka.atribuutit= haeAtribuutit(o)
            luokat.append(luokka)
    return luokat

dictSqlDjango= {"text":"TextField" , "date":"DateField" , "varchar":"CharField" , "int":"IntegerField" , "float":"FloatField" , "serial":"AutoField" , "boolean":"BooleanField" , "numeric":"FloatField" , "timestamp":"DateTimeField" , "bigint":"IntegerField" , "datetime":"DateTimeField"  , "date":"DateField" , "time" : "TimeField" , "bool" : "BooleanField" , "int" : "IntegerField" , "decimal":"DecimalField" }

varcharRE= re.compile('varchar\((\d+)\)')

def haeLuokanRunko(luokka,rivin_alku) :
        runko = "\n"
        for a in luokka.atribuutit:
                varchar=varcharRE.search(a.tyyppi)
                tyyppi=""
        
                if a.tyyppi.strip(" ") in dictSqlDjango.keys() :
                        tyyppi = dictSqlDjango[a.tyyppi.strip()]+ "()"
                else:
                        tyyppi = a.tyyppi
                if varchar:
                        tyyppi = "CharField(max_length="+varchar.group(1)+")"
                if len(a.arvo)>0 :
                        if not re.search(".*\(\)",tyyppi) :
                                tyyppi = tyyppi.replace(")",", "+a.arvo+" )")
                        else :
                                tyyppi = tyyppi.replace(")",a.arvo+" )")
                runko += rivin_alku + a.nimi + " = models."+ tyyppi + "\n"
        return runko


def korvaaLuokanRunko(koodi,luokka):
        sisennys_haku =  re.search('.*?(?=#gen_dia_class ' + luokka.nimi +'\n)',koodi)
        sisennys=""
        if sisennys_haku:
                sisennys=len(sisennys_haku.group(0)) * " "
        runko=haeLuokanRunko(luokka,sisennys)
        return re.sub(ur'(?s)(?<=#gen_dia_class '+ luokka.nimi +'\n).*?#end_dia_class',
                                runko+"\n"+sisennys +r"#end_dia_class",koodi)

def luoMallienRungot(kaavion_nimi,koodin_nimi):
        source=open( koodin_nimi , "r" )
        koodi=source.read()
        koodi=unicode(koodi,"utf-8")
        source.close()            

        f=codecs.open(kaavion_nimi,"rb")
        data = gzip.GzipFile(fileobj=f).read()
        dataObjectModel =xml.dom.minidom.parseString(data)
        objektit=dataObjectModel.getElementsByTagName("dia:diagram")[0].getElementsByTagName("dia:layer")[0].getElementsByTagName("dia:object")

        for l in haeLuokat(objektit):
                koodi= korvaaLuokanRunko(koodi,l)
        source=open( koodin_nimi,"w" )
        source.write( koodi.encode("utf-8"))


if __name__ == '__main__':
        if len(sys.argv) == 3:
                luoMallienRungot(sys.argv[1],sys.argv[2])            
        else :
                print sys.argv[0] + ' - Generates bodies of django data models to python sources. \n'
                print ' bodies to be generated have to be tagged in source with comments: '
                print '    #gen_dia_class CLASSNAME'
                print '    #end_dia_class \n'
                print " Use:\n "+sys.argv[0]+" diagram.dia source.py\n\n"

