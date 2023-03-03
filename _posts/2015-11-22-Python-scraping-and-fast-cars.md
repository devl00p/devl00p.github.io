---
title: "Python, scraping and fast cars"
tags: [Coding, Python]
---

**TLDR**: Ça se passe [ici](/assets/data/autoevolution/index.html).  

Introduction
------------

Dans un élan de curiosité, l'idée m'est venue de recouper les performances des automobiles avec leurs prix dans l'objectif de déterminer quelles sont les voitures qui disposent des meilleurs moteurs pour des prix intéressants.  

La qualité d'un moteur ne se limite bien sûr pas à ses qualités dynamiques (reprise, couple) mais aussi à sa consommation de carburant, son volume sonore, ses émissions de co2 et bien sûr le plaisir que peut vous procurer une boîte de vitesse mécanique.  

De même la qualité d'une voiture ne se limite pas à son moteur. À titre d'exemple, la *Subaru Impreza WRX STI 2.5 Turbo* est plus rapide d'un dixième de seconde que la *Bentley Mulsanne 6.75 V8* (boîte auto) et (puisque ça peut entrer en compte) 255000 euros moins chère mais voilà : si vous passez une soirée en voiture avec une *Lady* comment conserver les coupes de champagne au frais dans la *Subaru* ?  

Voilà une question qui n'est certes pas à la portée de tout le monde, mais dont l'objectif est surtout de faire en sorte que vous preniez les données qui vont suivre pour ce qu'elles sont : une simple corrélation entre le temps pour atteindre les 100km/h en départ arrêté avec le prix minimum du véhicule (finition d'entrée de gamme pour le modèle ayant la motorisation offrant la performance correspondante).  

Bien sûr, il est possible que je succombe à la tentation de quelques trolls faciles (et gratuits) !  

Première étape : trouver les données
-----------------------------------

Quand on cherche des bases de données concernant les spécifications techniques des automobiles, on se retrouve vite face à un vide intersidéral de l'open-data.  

Il y a une tonne de sites regroupant les fiches techniques d'automobiles malheureusement aucun ne dispose d'une API permettant d’accéder aux données sans scraper le site comme un barbare.  

Le site le plus accueillant en la matière est [Edmunds.com](http://www.edmunds.com/) qui dispose d'une API qui semble efficace.  

Toutefois :
* le site est américain et de nombreux véhicules n'ont pas traversé l'Atlantique. Les motorisations peuvent aussi être fortement différentes.
* le temps pour le 0 à 100km/h n'est pas proposé [dans les résultats](http://developer.edmunds.com/api-documentation/vehicle/spec_engine_and_transmission/v2/)

Pourquoi vouloir à tout prix le 0 à 100 km/h ? Eh bien, c'est une indication généralement suffisante et assez parlante des performances d'un véhicule.  

Le nombre de chevaux et le couple sont d'autres indicateurs utiles, mais il faut alors prendre en compte le poids du véhicule, le type de transmission (traction, propulsion, intégrale), le type de boite de vitesse, la présence d'un turbo... un vrai casse-tête.  

On pourrait tricher et se rabattre sur certains sites de calcul du 0 à 100 comme [0-60 mph calculator](http://www.060calculator.com/) qui utilisent effectivement certains de ces indicateurs, mais dont les résultats ne semblent pas fiables (8.9 secondes calculés pour ma voiture contre les 9.4s officielles).  

Le temps de 0 à 100 fournit dans les spécifications à l'avantage de prendre en considération tous ces paramètres même si on peut imaginer que les constructeurs ne soient pas toujours honnêtes sur le sujet :(   

J'ai finalement posé mon dévolu sur [autoevolution](http://www.autoevolution.com/cars/). Ce site semble disposer de modèles européens (le site est basé en Europe, en Roumanie pour être exact) avec (la plupart du temps) les performances qui nous intéressent et le tout est dans l'ensemble à jour (modèles récents).  

Un autre point très important de ce site est qu'il semble s'en tenir aux motorisations de chaque modèle sans nous noyer sous une tonne de finitions comme c'est le cas sur *Caradisiac* qui recense par exemple [une cinquantaine de finitions pour le *Renault Captur*](http://www.caradisiac.com/fiches-techniques/modele--renault-captur/) alors qu'aucune ne dispose d'une motorisation digne de ce nom. (indice : on a passé le premier troll, sauras-tu le retrouver ?)  

Seconde étape : Scrape everything
---------------------------------

![Scrape everything](/assets/data/autoevolution/scrape.jpg)

Notre premier point d'accès au site est la page des constructeurs qui est simple à scraper.  

Grosso-modo il nous suffit d'extraire tous les liens hypertextes présents dans la div de classe CSS `brandlist`. On obtient ainsi le nom de chaque constructeur présent et l'URL de sa section.  

Le code que j'ai écrit utilise le langage Python avec les modules *Requests* et *BeautifulSoup* (what else ?)  

On doit ensuite visiter la page de chaque constructeur pour en extraire la liste des modèles actuellement produits.  

La page d'*Acura* (qui est à *Honda* ce que *Lexus* est à *Toyota*) sépare les modèles en production des modèles qui ne sont plus produits. Sur certains constructeurs on peut s'attendre à ne voir que des modèles produits (si la marque est récente comme *RAM Trucks*) ou au contraire que des modèles abandonnés (si la marque a sombré dans l'oubli comme *Lancia*... il était facile celui-là).  

Chaque modèle est situé dans une div correspondant aux classes CSS `carslist`, `mgtop22` et enfin `faded` s'il s'agit d'un modèle qui n'est plus en production.  

Avec *BeautifulSoup* on peut chercher un élément qui correspond à une classe CSS donnée en revanche la librairie ne permet pas de faire une recherche décrivant exactement le texte présent dans l'attribut `class` d'un élément ni de faire une recherche sur une liste de noms de classes pour extraire les éléments qui rassemblent ces classes.  

Du coup si on cherche les éléments correspondant à la classe `mgtop22` on aura aussi bien les `faded` que les non-`faded`.  

Cela nous force à faire une vérification supplémentaire (tester la présence de `faded`) dans les valeurs (type `list`) de l'attribut `class` de la node trouvée par *BeautifulSoup*.  

Le format des URLs (ex: `http://www.autoevolution.com/acura/tlx/` ) est en revanche une aubaine pour extraire le nom du modèle.  

Notre aventure ne s'arrête pas là puisqu'il faut récupérer depuis la page d'un modèle le lien pour la dernière version produite.  

Ainsi sur la page de la [MX-5](http://www.autoevolution.com/mazda/mx-5-miata/), seule la dernière version (2015) nous intéresse pour disposer de données à jour.  

Le dernier modèle en cours est dans une div disposant de la classe CSS `mgbot11`. Il suffit de récupérer la première instance avec la fonction `find()` de *BeautifulSoup*.  

La première URL dans cette div correspond à la page finale qui nous intéresse. Cette dernière a l'avantage de regrouper les spécifications de toutes les motorisations du modèle ce que l'on ne voit pas forcément à cause de l'utilisation de javascript dans la page.  

Les spécifications sont regroupées dans un bloc `dl/dt/dd` ce qui permet d'extraire facilement les informations.  

Le script suivant qui regroupe ces opérations a permis de générer un fichier JSON de plus de 5Mo avec les informations.  

```python
from __future__ import print_function
import requests
from bs4 import BeautifulSoup
from urlparse import urlparse
from time import sleep
import json

def extract_model_infos(html_code):
    soup = BeautifulSoup(html_code)
    engines = {}
    for div_engine in soup.find_all("div", class_="engine-block"):
        engine_name = div_engine.h3.span.text
        keys = [tag.text.lower().strip() for tag in div_engine.find_all("dt")]
        values = [tag.get_text().lower().strip() for tag in div_engine.find_all("dd")]
        engines[engine_name] = dict(zip(keys, values))
    return engines

sess = requests.session()

def get_page(url):
    global sess
    try:
        r = sess.get(url)
    except requests.exceptions.RequestException:
        return None
    sleep(1)
    return r.text

soup = BeautifulSoup(get_page("http://www.autoevolution.com/cars/"))

brands_dict = {}

for brands in soup.find_all("div", class_="brandlist"):
    for brand_link in brands.find_all("a", href=True):
        brand_url = brand_link["href"]
        brand_name = urlparse(brand_url).path[1:-1]
        print(brand_name.upper())

        soup2 = BeautifulSoup(get_page(brand_url))

        cars_dict = {}
        for div in soup2.find_all("div", class_="mgtop22"):
            if "faded" in div["class"]:
                continue
            for car_link in div.find_all("a", href=True):
                car_url = car_link["href"]
                car_name = urlparse(car_url).path.split("/")[-2]
                print("\t", car_name.capitalize())

                soup3 = BeautifulSoup(get_page(car_url))
                last_model_div = soup3.find("div", class_="mgbot11")
                if last_model_div:
                    try:
                        model_link = last_model_div.h2.a
                        model_url = model_link["href"]

                        model_infos = extract_model_infos(get_page(model_url))
                        cars_dict[car_name] = model_infos
                    except AttributeError:
                        print("No specs for this model")
        brands_dict[brand_name] = cars_dict

with open("cars.json", "w") as fd:
    json.dump(brands_dict, fd, indent=2)
```

Troisième étape : coller un prix sur les voitures
------------------------------------------------

*AutoEvolution* ne dispose pas des informations de prix des véhicules (qui varient d'ailleurs selon les pays).  

Pour faire le recoupement pas de magie : j'ai fouillé sur *Caradisiac* pour retrouver les modèles (en faisant bien attention à ce que le temps de 0 à 100 km/h corresponde ainsi que le type de transmission, de boîte, carburant, etc) et noter les prix en euros.  

J'ai édité le fichier JSON à la main ce qui était loin d'être passionnant et retrouver les modèles sur *Caradisiac* pouvait parfois être désagréable (enfin surtout quand on tombe sur des photos de véhicules *Fiat*).  

J'ai fait une exception pour *Caterham* dont les modèles ne sont pas listés sur *Caradisiac* : je trouvais dommage de ne pas mettre ces véhicules atypiques dans les données du coup j'ai récupéré le prix en £ sur le site anglais et l'ai converti en euros avec le taux en cours (ce qui n'améliore pas le prix).

Quatrième étape : alléger le fichier JSON
-----------------------------------------

En retirant les caractéristiques qui ne nous intéressent pas (taille des pneus, types de freins, etc) on peut réduire le fichier à 175Ko de JSON :  

```python
from __future__ import with_statement, print_function
import json

useless_keys = [
    "gross weight limit", 
    "tire size",
    "torque",
    "displacement",
    "height",
    "ground clearance",
    "city",
    "co2 emissions",
    "fuel system",
    "cargo volume",
    "cd",
    "width",
    "combined",
    "highway",
    "power",
    "unladen weight",
    "front/rear track",
    "front",
    "rear",
    "cylinders",
    "wheelbase",
    "length",
    "gross weight limit",
    ""
]

with open("cars.json") as fd:
    data = json.load(fd)
    brands = data.keys()
    for brand in brands:
        models = data[brand].keys()
        for model in models:
            motors = data[brand][model].keys()
            for motor in motors:
                specs = data[brand][model][motor]
                if "price" not in specs:
                    # remove whole motor spec
                    data[brand][model].pop(motor)
                else:
                    for key in useless_keys:
                        if key in specs:
                            data[brand][model][motor].pop(key)

            if not data[brand][model]:
                data[brand].pop(model)

        if not data[brand]:
            data.pop(brand)

print(json.dumps(data))
```

Cinquième étape : faire un beau graphique
-----------------------------------------

Je ne suis pas un expert Javascript mais en reprenant des modèles *Highcharts* existants, on peut obtenir à mesure de retouches un résultat visuellement agréable comme celui-ci :  

[Graphique comparatif automobiles prix / performance](/assets/data/autoevolution/index.html)  

Parmi les difficultés rencontrées :  

* formater le tooltip pour qu'il prenne les informations du point survolé (les spécs) et intègre le logo de la marque (voir ci-après).
* faire en sorte que les points d'une même marque aient la même forme et même couleur.

Le graphe est assez parlant et *Highcharts* permet des manipulations utiles comme zoomer, n'afficher que certains constructeurs, etc.  

Le nuage de points de chaque constructeur est révélateur et permet de deviner facilement son positionnement économique, ses concurrents directs et la performance générale de ses véhicules (par exemple en regardant la proportion de véhicules à plus de 11 secondes, ce qui ne va pas en faveur de *Fiat* et *Mitsubishi* notamment).  

Sixième étape : récupérer les logos des constructeurs
-----------------------------------------------------

Durant la réalisation du graphique j'ai trouvé dommage de ne pas intégrer les logos de chaque constructeur qui permettent de savoir en un clin d’œil à quoi l'on a affaire.  

J'ai cherché des logos en `16*16` pixels et je suis finalement tombé sur *carlogos.net*.  

Le site dispose d'un script PHP qu'il est très facile d'exploiter pour récupérer les différents logos.  

```python
from __future__ import with_statement
import requests
import json
import shutil

url = "http://carlogos.net/demothumb.php?sizeid=2&name="

with open("cars.json") as fdin:
    data = json.load(fdin)
    sess = requests.session()
    for maker in data:
        r = sess.get(url + maker.capitalize(), stream=True)
        if r.headers["content-type"] == "image/png":
            with open("logos/{0}.png".format(maker), "wb") as fdout:
                shutil.copyfileobj(r.raw, fdout)
```

J'ai dû traiter séparément les noms de constructeurs en deux mots (*Mercedes Benz*) ou ceux qui disposaient d'un tiret (*Rolls Royce*).  

Enfin j'ai récupéré ailleurs les logos manquants (les logos de *Fisker* et *McLaren* sont d'ailleurs ceux qui rendent le mieux) via une recherche *Google Images*.  

Septième étape : faire des classements supplémentaires
------------------------------------------------------

Comme je n'ai pas récupéré que les temps de 0 à 100 km/h j'en ai profité pour faire différents scripts qui classent les véhicules selon une caractéristique donnée :  

* [fast-cars](/assets/data/autoevolution/top.html) : le top des exploseuses de chrono
* [mad-cars](/assets/data/autoevolution/speed.html) : le top des vitesses maximales
* [bad-cars](/assets/data/autoevolution/co2.html) : le top des autos les plus polluantes
* [parking-hell](/assets/data/autoevolution/longueur.html) : le top des autos les plus longues
* [soirée mousse](/assets/data/autoevolution/coffre.html) : le top des autos avec le coffre le plus volumineux
* [Bring Your Own Hippopotame](/assets/data/autoevolution/charge.html) : le top des autos selon la charge maximale supportée

Voici l'un des scripts à titre d'exemple :  

```python
from __future__ import print_function, with_statement

import json
from operator import itemgetter
import sys
import os
import re

table = []
models_len = set()

with open("cars.json") as fd:
    brands = json.load(fd)
    for brand in brands:
        for car in brands[brand]:
            models = brands[brand][car]
            for model in models:
                charge = models[model]["gross weight limit"].strip()
                if charge == "-":
                    continue
                weight = models[model]["unladen weight"].strip()
                if weight == "-":
                    continue

                search1 = re.search(r"(\d+) kg$", charge)
                search2 = re.search(r"(\d+) kg$", weight)
                if search1 and search2:
                    charge = int(search1.group(1)) - int(search2.group(1))
                    if charge < 185:
                        continue
                    model = model.encode("utf-8", "ignore").strip()
                    table.append((model, charge))
                    models_len.add(len(model))

max_len = max(models_len)
old_charge = ""

print("""<!DOCTYPE html>
<html lang="fr">
<head>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css" integrity="sha512-dTfge/zgoMYpP7QbHy4gWMEGsbsdZeCXz7irItjcC3sPUFtf0kuFbDz/ixG7ArTxmDjLXDmezHubeNikyKGVyQ==" crossorigin="anonymous">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap-theme.min.css" integrity="sha384-aUGj/X2zp5rLCbBxumKTCw2Z50WgIr1vs/PFN4praOTvYXWlVyh2UtNUU0KAUhAX" crossorigin="anonymous">
    <style>
    .dl-horizontal dd { margin-bottom: 1em; background-color: rgb(247, 247, 249); padding: 5px; border: 1px solid #e1e1e8; border-radius: 4px; }
    .dl-horizontal dt { padding-top: 5px; }
    h1 { text-align: center; }
    h5 { text-align: center; }
    </style>
</head>
<body>
  <div class="container">
    <div class="page-header">
        <h1>Classement automobiles sur le poids maximal possible en kilos</h1>
        <h5>donn&eacute;es autoevolution.com</h5>
    </div>
    <dl class="dl-horizontal">""")

for model, charge in sorted(table, key=itemgetter(1), reverse=True):
    if old_charge != charge:
        if old_charge:
            print("\n      </dd>")
        print("      <dt>{0} kg</dt><dd>".format(charge))
        old_charge = charge

    try:
        brand = model.split(" ")[0].lower()
        image_path = "logos/{0}.png".format(brand)
        if os.path.isfile(image_path):
            print("<img src=\"{0}\"/> {1}<br />".format(image_path, model))
        else:
            print(model, "<br />")
    except UnicodeEncodeError:
        print("Error with model name {0}".format(repr(model)), file=sys.stderr)
        continue

print("""</dt>
    </dl>
  </div>
</body>
</html>""")
```

À propos des données
--------------------

Certaines des données peuvent être erronées. Lors du traitement de ces informations, j'ai parfois croisé des incohérences improbables aussi bien sur *AutoEvolution* que sur *Caradisiac*.  

Je suppose que les données sont reçues sous la forme de brochures envoyées par les constructeurs et saisies à la main donc sujettes à l'erreur humaine (typo, copier/coller, etc).  

Parmi les erreurs les plus flagrantes j'ai vu :  

* une voiture de 45 mètres de long (en limousine ça doit être confortable, mais bonjour les créneaux).
* une *Mazda 6* faisant le 0 à 100 km/h en 139 secondes (avec un moteur de *Twizy* peut être, mais ce n'était pas le cas).
* une *Kia Rio* de 11 tonnes (en granit ?)
* une *Kia Picanto* permettant une charge de 5kg maximum (on peut la conduire en passant le bras par la fenêtre, mais pas être dedans).

Il y a aussi des incohérences plus difficiles à discerner au vu de la quantité d'informations comme un *Dacia Duster TCE* de 105 chevaux réalisant le même chrono que sa version 125 chevaux...  

J'ai bien sûr corrigé les erreurs que j'ai relevées, mais il est fort probable que des incohérences soient toujours présentes dans les données. Il faut donc prendre ces données avec des pincettes.  

Il manque des véhicules. La nouvelle *NSX* n'est par exemple pas listé sur *AutoEvolution* et à l'inverse les prix de certains véhicules n'apparaissent pas sur *Caradisiac* d'où l'absence de certains modèles.  

J'ai parfois pu me rabattre sur la version break de tel ou tel modèle, mais ce n'est pas toujours le cas.  

Enfin il faut savoir interpréter certaines données : sur le classement des volumes de coffre le *FORD Grand C-Max* apparaît avec un volume de seulement 57 litres. C'est en réalité le volume du coffre une fois que les 7 sièges sont levés et non le volume que l'on pourrait effectivement obtenir.  

Bonne visualisation.

*Published November 22 2015 at 17:17*
