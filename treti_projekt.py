"""
slama_projekt.py: třetí projekt do Engeto Online Python Akademie
author: David Sláma
email: cimka1@seznam.cz
discord: cimka1#2497
"""
import requests
import sys
import csv
from bs4 import BeautifulSoup


# získání odkazu a názvu souboru z příkazové řádky
odkaz = sys.argv[1]
soubor = sys.argv[2]

# získání kódu obce z odkazu
response = requests.get(odkaz)
soup = BeautifulSoup(response.content, 'html.parser')

# nalezení kódu obce a názvu obce na stránce 
td_elements = soup.findAll("td", class_="cislo")
for td_element in td_elements:
    odkaz_obce = td_element.find('a')['href']
    kod_obce = odkaz_obce.split('&')[2].split('=')[1]
    nazev_obce = td_element.find_next_sibling("td", class_="overflow_name").text.strip()

    # rozdělení řetězce podle znaku ?
    url_params = odkaz.split("?")[1]

    # rozdělení parametrů URL podle znaku &
    param_pairs = url_params.split("&")

    # nalezení hodnoty parametru xkraj a rozdělení podle znaku =
    for param in param_pairs:
        if "xkraj" in param:
            kraj = param.split("=")[1]
            break

    params = dict(param.split('=') for param in odkaz.split('?')[1].split('&'))
    numnuts = params['xnumnuts']

    # vytvoření URL pro obec
    url_obec = f"https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj={kraj}&xobec={kod_obce}&xvyber={numnuts}"

    # získání HTML obsahu stránky s výsledky voleb pro obec
    response = requests.get(url_obec)
    soup = BeautifulSoup(response.content, 'html.parser')


    # nalezení potřebných dat
    volici_v_seznamu = soup.find_all("td", headers="sa2")[0].text.replace(u'\xa0', u' ')
    vydane_obalky = soup.find_all("td", headers="sa3")[0].text.replace(u'\xa0', u' ')
    platne_hlasy = soup.find_all("td", headers="sa6")[0].text.replace(u'\xa0', u' ')

    # nalezení názvů stran
    strany = []
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) > 0:
                strana = cells[1].text.strip()
                if strana != "1" and strana !="-":
                    strany.append(strana)

    # nalezení platných hlasů pro jednotlivé strany
    platne_hlasy_stran = []
    for strana in strany:
        platne_hlasy_stran.append(soup.find("td", string=strana).find_next_sibling("td").text.replace(u'\xa0', u' ').strip())

    # zapsání dat do souboru csv
    with open(soubor, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        if csvfile.tell() == 0:  # pokud je soubor prázdný, zapíšeme hlavičku
            writer.writerow(["Název obce", "Kód obce", "Volici v seznamu", "Vydane obalky", "Platne hlasy"] + strany)
        writer.writerow([nazev_obce, kod_obce, volici_v_seznamu, vydane_obalky, platne_hlasy] + platne_hlasy_stran)