import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
import pandas as pd
from datetime import date


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
ua=UserAgent()

def cherche_job(titre,lieu,page):
    url = f"https://fr.indeed.com/emplois?q={titre}&l={lieu}&start={page-1}0"
    return url

def get_soup(url):
    #En 2 temps : choix aléatoire d'un user agent pour ne pas être détecté comme étant un bot, puis requête usuelle
    Attente = random.uniform(0,15)
    print(f"Temps d'attente = {Attente}" )
    time.sleep(Attente) #attente aléatoire pour ne pas être détecté par les systèmes anti-bot
    ua_rand = "iPad"
    #Choix d'un User Agent random hors iPad et Tablette pour apparaître de façon changeante auprès des serveurs indeed
    while "iPad" in ua_rand or "ablet" in ua_rand:
        ua_rand = ua.random
    print(ua_rand)
    hdr = {'User-Agent': ua_rand,
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
  'Accept-Encoding': 'none',
  'Accept-Language': 'en-US,en;q=0.8',
  'Connection': 'keep-alive'}
  #requete get classique
    r=requests.get(url,headers=hdr)
    return BeautifulSoup(r.text,"html.parser")

def liste_liens(titre,lieu):
    liens =[]
    for page in range(15):
        print("User Agent utilisé : ")
        soup = get_soup(cherche_job(titre,lieu,page))
        for link in soup.find_all('a'):
            lien = link.get('href')
            if lien != None :
                if "clk?" in lien:
                    if lien not in liens :
                        liens.append("https://fr.indeed.com" + lien)
        print("Page numéro : " + str(page+1) + " chargée")
    return liens
    
def get_job_desc(soup):
    return soup.find(id="jobDescriptionText").get_text()

def get_job_title(soup):
    mydivs = soup.find_all("div", {"class": "jobsearch-JobInfoHeader-title-container"})
    for div in mydivs:
        if div.get("h1") != "":
            return(div.text)
    return "Employeur non retrouvé"

def get_job_salary(soup):
    salary = soup.find(id="salaryInfoAndJobType")
    if salary != None :
        return soup.find(id="salaryInfoAndJobType").text
    return None

def get_employer_name(soup):
    mydivs = soup.find_all("div", {"class": "icl-u-lg-mr--sm icl-u-xs-mr--xs"})
    for div in mydivs:
        if div.text != "":
            return(div.text)
    return "Employeur non retrouvé"


def main():
    métier=input("Quel métier voulez vous chercher ?")
    localisation = input("A quelle localisation souhaitez-vous réaliser votre recherche?")
    ma_liste_liens = liste_liens(métier,localisation)
    infos = {}
    for i,lien in enumerate(ma_liste_liens) :
        print(f"Avancement : {i} / {len(ma_liste_liens)}")
        ma_soup = get_soup(lien)
        job_title = get_job_title(ma_soup)
        #print("---------------------------------")
        #print(i)
        #print(job_title)
        #print(lien)
        if job_title == "Employeur non retrouvé":
            print(f"Erreur sur {lien}")
        else :
            infos[job_title]={"Description":get_job_desc(ma_soup),"Salaire":get_job_salary(ma_soup),"Employeur":get_employer_name(ma_soup),"Lien":lien}
    date_actuelle = str(date.today())
    date_actuelle = str.replace(date_actuelle,"/","_")
    df = pd.DataFrame.from_dict(infos)
    df.to_json (f'{métier} à {localisation} - Indeed.json')

    


if __name__ == "__main__":
    main()
