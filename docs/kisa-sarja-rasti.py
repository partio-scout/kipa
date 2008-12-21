class Rasti :
	def __init__(self) :
		self.id = None # unsigned int
		pass
	def asetaPaallikko (self, pomo) :
		# returns 
		pass
	def liitaTehtava (self, rastinTehtava) :
		# returns 
		pass
	def liitäRastimies (self, kusessaMukana) :
		# returns 
		pass
	def haeTehtavat (self) :
		# returns Tehtava[]
		pass
	def haeRastimiehet (self) :
		# returns Tekia[]
		pass
	def haeTulokset (self) :
		# returns Lopputulos[]
		pass
	def irroitaTehtava (self, irroitettavaTekia) :
		# returns 
		pass
	def irroitaRastimies (self, irroitettavaTekia) :
		# returns 
		pass
	def haeSarja (self) :
		# returns Sarja
		pass
	def haeKisa (self) :
		# returns Kisa
		pass

class Sarja :
	def __init__(self) :
		self.id = None # unsigned int
		pass
	def asetaNimi (self, sarjanNimi) :
		# returns 
		pass
	def asetaMaksimipisteet (self, parasMahdollinen) :
		# returns 
		pass
	def asetaVartionMaksimikoko (self, suurinSallittu) :
		# returns 
		pass
	def asetaVartionMinimikoko (self, pieninSallittu) :
		# returns 
		pass
	def lisaaRasti (self) :
		# returns Rasti
		pass
	def liitaTekia (self, kusessaMukana) :
		# returns 
		pass
	def liitaVartio (self, ilmoittautuu) :
		# returns 
		pass
	def liitaTehtava (self, sarjanTehtava) :
		# returns 
		pass
	def haeRastit (self) :
		# returns Rasti[]
		pass
	def haeVartiot (self) :
		# returns Vartio[]
		pass
	def haeTekiat (self) :
		# returns Tekia[]
		pass
	def haeTehtavat (self) :
		# returns Tehtava[]
		pass
	def haeNimi (self) :
		# returns String
		pass
	def haeMaksimipisteet (self) :
		# returns float
		pass
	def haeVartionMaksimikoko (self) :
		# returns int
		pass
	def haeVartionMinimikoko (self) :
		# returns int
		pass
	def poistaRasti (self, poistettavaRasti) :
		# returns 
		pass
	def irroitaTekiä (self, irroitettavaTekia) :
		# returns 
		pass
	def irroitaVartio (self, irroitettavaVartio) :
		# returns 
		pass
	def irroitaTehtava (self, irroitettavaTehtava) :
		# returns 
		pass
	def haeKisa (self) :
		# returns Kisa
		pass
class TietokantaHaku :
	def __init__(self) :
		pass
	def haeKisaID (self, KisanNimi) :
		# returns unsigned int
		pass
	def haeKisa (self, id) :
		# returns KisaTaulu
		pass
	def haeSarja (self, id) :
		# returns SarjaTaulu
		pass
	def haeRasti (self, id) :
		# returns RastiTaulu
		pass
	def haeTekia (self, id) :
		# returns TekiaTaulu
		pass
	def haeRastimiesIDt (self) :
		# returns unsigned int[]
		pass
	def haeSarjanRastiIDt (self) :
		# returns unsigned int[]
		pass
	def haeRastinTehtavaIDt (self) :
		# returns unsigned int[]
		pass
	def haeRastinVartioIDt (self) :
		# returns unsigned int[]
		pass
class Kisa :
	def __init__(self) :
		self.id = None # unsigned int
		pass
	def luoKisa (self) :
		# returns Kisa
		pass
	def haeKisa (self, nimi) :
		# returns Kisa
		pass
	def asetaNimi (self, kisanNimi) :
		# returns 
		pass
	def asetaAika (self, kisanNimi) :
		# returns 
		pass
	def asetaPaikka (self, kisanAika) :
		# returns 
		pass
	def asetaPaikka (self, kisanPaikka) :
		# returns 
		pass
	def lisaaSarja (self) :
		# returns Sarja
		pass
	def liitaVartio (self, ilmoittautuu) :
		# returns 
		pass
	def haeNimi (self) :
		# returns String
		pass
	def haeAika (self) :
		# returns Aika
		pass
	def haePaikka (self) :
		# returns String
		pass
	def haeVartiot (self) :
		# returns Vartio[]
		pass
	def haeTekiat (self) :
		# returns Tekia[]
		pass
	def haeSarjat (self) :
		# returns Sarja[]
		pass
	def poistaSarja (self, poistettavaSarja) :
		# returns 
		pass
	def irroitaTekia (self, irtaantuvaTekia) :
		# returns 
		pass
	def irroitaVartio (self, irtaantuvaVartio) :
		# returns 
		pass
	def lisaaTekia (self, mukaan) :
		# returns 
		pass

