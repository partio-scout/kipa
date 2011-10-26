import settings

laskentaloki=""

def __noLogString(string):
        return None

def __logString(string):
        string=string.replace("\n","<br>")
        string=string.replace(" ","&nbsp")
        global laskentaloki
        laskentaloki+=string+"<br>"

def __noLogFunction(function,params,result):
        return None

def __logFunction(function,params,result):
        global laskentaloki
        
        if(params):
            if hasattr(params, '__len__') and len(params)==1 and (hasattr(params[0], 'keys') or hasattr(params[0], '__contains__' )) and  len(params[0])>5 :
                laskentaloki+= unicode(function.__name__)  + u"(x)=" + unicode(result) + "  kun <br>"
                laskentaloki+= "x= " + unicode(params[0]) 

            else :
                laskentaloki+= unicode(function.__name__)  + "("
                try :
                        for p in params : laskentaloki += unicode(p) + ", "
                except: pass
                laskentaloki=laskentaloki[:-2]
                laskentaloki+= ")= " + unicode(result)
        laskentaloki += "<br>"



def enableLogging() :
        global logString
        global logFunction
        logString= __logString
        logFunction= __logFunction

def disableLogging() :
        global logString
        global logFunction
        logString= __noLogString
        logFunction= __noLogFunction

def clearLoki() :
        global laskentaloki
        laskentaloki=""

def palautaLoki() :
        global laskentaloki
        return laskentaloki


try:
        logString
except:
        logString=None

try:
        logFunction
except:
        logFunction=None

if not logString or not logFunction:
        enableLogging()

