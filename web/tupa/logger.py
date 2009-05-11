#coding: latin-1

class Logger:
    """
    Logger Class
    """
    def __init__(self) :
        self.stack=[""]
        self.file="log.log"
    def setFileName(self,fileName) :
        self.file=fileName
        return self
    def setMessage(self,message) :
        if message :
                self.stack[-1]=message
        else:
                self.stack[-1]="None"
        return self
    def push(self) :
        self.stack.append("")
        return self
    def pop(self) :
        if len(self.stack) > 1 :
           self.stack.pop()
        return self
    def clearStack(self) :
        self.stack=[""]
        return self
    def clearLog(self) :
        
        log = open(self.file, "w")
        log.write("")
        log.close()
        return self
        
    def logMessage(self) :
        log = open(self.file, "a")
        for r in self.stack:
           log.write(unicode(r).encode('ascii', 'ignore'))
        log.write("\n")
        log.close()
        return self
        
lokkeri=Logger()
lokkeri.setFileName("laskenta.log")


