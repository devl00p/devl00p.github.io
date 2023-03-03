---
title: "Python : Chargement dynamique de modules - un système d'extensions"
tags: [Coding, Python]
---

Je cherchais une méthode pour mettre en place un vrai système *modulaire* de modules en Python, comme un système de plugins où les extensions seraient chargées dynamiquement sans que les informations concernant ces modules soient *hardcodées* dans le programme.  

On pourrait ainsi rajouter directement les modules dans un répertoire sans avoir à les déclarer à un autre endroit dans le code. Bien sûr, ça suppose que chaque module soit créé sur un même modèle, car il faut tout de même savoir à quoi on souhaite accéder.  

Finalement j'ai trouvé l'astuce suivante qui peut vous intéresser ;-)  

Soit l'arborescence suivante :  

```
.
|-- launcher.py
`-- modules
    |-- __init__.py
    |-- abcd.py
    |-- plop.py
    `-- truc.py
```

Le répertoire `modules` est le dossier qui contient les extensions. Le fichier `__init__.py` contient uniquement une ligne qui définit les modules présents dans le dossier (pour se simplifier la tâche) :  

```python
__all__ = ["plop", "abcd", "truc"]
```

Les fichiers `abcd.py`, `plop.py` et `truc.py` contiennent chacun une classe dont le nom correspond au fichier avec un constructeur et une méthode `run()`.  

La classe `plop` a la particularité de contenir une fonction `special()`. Pour l'exemple, le contenu du fichier `plop.py` est le suivant :  

```python
class plop:
  def __init__(self):
    print "Constructeur de plop"

  def run(self):
    print "run() de plop"

  def special(self):
    print "Fonction special() de plop"
```

Enfin, le contenu du fichier `launcher.py` qui a pour rôle de charger dynamiquement ces modules en aveugle est le suivant :  

```python
#!/usr/bin/env python
import modules
for mod_name in modules.__all__:
  mod = __import__ ("modules." + mod_name, fromlist=modules.__all__) # on charge le module
  mod_instance = getattr(mod, mod_name)() # on appelle le constructeur
  mod_instance.run()
  if hasattr(mod_instance, "special"):
    mod_instance.special()
```

Son lancement provoque la sortie suivante :  

```
Constructeur de plop
run() de plop
Fonction special() de plop
Constructeur de abcd
run() de abcd
Constructeur de truc
run() de truc
```

On pourrait s'affranchir encore plus du code en lisant le contenu du répertoire `modules` pour obtenir le nom des fichiers (par `glob` par exemple).  

On pourrait aussi mettre dans chaque classe un attribut définissant sa priorité de lancement pour effectuer un système de chargement dans le même style que `init.d`.

*Published January 11 2011 at 12:55*
