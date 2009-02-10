import unittest

from models import *
from peruslaskin import *

class peruslaskin_test(unittest.TestCase):

    """
    Peruslaskimen unit testit

    """

    def testYhteenlasku(self):
        assert  laske('5+5') == '10'
    
    def testYhteenlasku_spacet(self):
        assert  laske(' 5 + 5 ') == '10'
    
    def testDesimaaliluku(self):
        assert  laske('0.5*2+10.5000') == '11.5'
    
    def testMuuttujavirhe(self):
        assert  laske('tyhja_muuttuja*5') == None

    def testSulkulauseke(self):
        assert  laske('2*(1+9)') == '20'

    def testSulut_sisakkain(self):
        assert  laske('10*((1+2)+(5*10))') == '530'

    def testSulut_vaarinpain(self):
        assert  laske('10*)(1+2)+(5*10))') == None

    def testSulut_vaaramaara(self):
        assert  laske('10*(1+2)+(5*10))') == None

    def testNollallajako(self):
        assert  laske('10/0') == None 

     
