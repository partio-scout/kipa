
if __name__ == "__main__":
        source=open( "fixtures/old.xml" , "r" )
        koodi=source.read()
        source.close()        
        koodi=koodi.replace("legacy","tupa")
        source=open( "fixtures/old.xml","w" )
        source.write(koodi)

