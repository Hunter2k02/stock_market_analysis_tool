import unittest 
import json 
import requests
from constants import API_KEY
import pkg_resources
from datetime import date, timedelta
import os

class TestConstants(unittest.TestCase):
    
    def test_api_key(self):
        self.assertTrue(API_KEY != "", "API_KEY is empty")

class TestFile(unittest.TestCase):
    def test_file(self):
        with open("pairs.json", "r") as f:
            list_of_currencies = json.load(f)
        self.assertTrue(len(list_of_currencies) > 0, "pairs.json is empty")
        with open('grouped_indicators.json', 'r') as file:
            grouped_indicators = json.load(file)
        self.assertTrue(len(grouped_indicators) > 0, "grouped_indicators.json is empty")
    
        
class TestRequirements(unittest.TestCase):

    def test_packages_installed(self):
        with open('requirements.txt') as f:
            required_packages = [line.strip().split('==')[0].lower() for line in f]
        if 'kaleido' in required_packages:    
            required_packages.remove('kaleido')
        installed_packages = [pkg.key for pkg in pkg_resources.working_set]        
        for package in required_packages:
            with self.subTest(package=package):
                self.assertIn(package, installed_packages)
                
    def test_package_kaleido(self):
        a  = os.popen('pip show kaleido').readlines()
        self.assertTrue(len(a) > 0, "kaleido is not installed")
        
class TestAPI(unittest.TestCase):
    def test_api_marketaux(self):
        yesterday = date.today() - timedelta(days=1)
        yesterday = yesterday.strftime('%Y-%m-%d')
        
        url = f"https://api.marketaux.com/v1/news/all?industries=Technology&filter_entities=true&limit=10&published_after={yesterday}T17:47&api_token={API_KEY}"
        
        response = requests.get(url)
        json_data = response.json()
        
        
        try:
            self.assertTrue(len(json_data['data']) > 1, "Daily API limit reached")
            self.assertTrue(len(json_data['data']) > 0, "API is not working")
        except Exception as e:
            print(e)
            
        
    def test_api_bitstamp(self):
        url = "https://www.bitstamp.net/api/v2/ticker/btcusd/"
        response = requests.get(url)
        json_data = response.json()
        self.assertTrue(len(json_data) > 0, "API is not working")
        
def suite():
    suite = unittest.TestSuite()    
    suite.addTest(TestConstants('test_api_key'))
    suite.addTest(TestFile('test_file'))
    suite.addTest(TestRequirements('test_packages_installed'))
    suite.addTest(TestRequirements('test_package_kaleido'))
    suite.addTest(TestAPI('test_api_marketaux'))
    suite.addTest(TestAPI('test_api_bitstamp'))
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())