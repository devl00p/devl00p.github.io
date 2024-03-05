---
title: "Solution du challenge Ivujivik de SadServers.com"
tags: [CTF,AdminSys,SadServers]
---

**Scenario:** "Ivujivik": Parlez-vous Français?

**Level:** Medium

**Type:** Do

**Tags:** [csv](https://sadservers.com/tag/csv)   [sql](https://sadservers.com/tag/sql)   [realistic-interviews](https://sadservers.com/tag/realistic-interviews)  

**Description:** Given the CSV file `/home/admin/table_tableau11.csv`, find the *Electoral District Name/Nom de circonscription* that has the largest number of *Rejected Ballots/Bulletins rejetés* and also has a population of less than 100,000.

The initial CSV file may be corrupted or invalid in a way that can be fixed without changing its data.

Installed in the VM are: Python3, Go, sqlite3, [miller](https://miller.readthedocs.io/en/latest/) directly and PostgreSQL, MySQL in Docker images.

Save the solution in the `/home/admin/mysolution`, with the name as it is in the file, for example: `echo "Trois-Rivières" > ~/mysolution` (the solution must be terminated by newline).

**Test:** `md5sum /home/admin/mysolution` returns e399d171f21839a65f8f8ab55ed1e1a1

**Time to Solve:** 20 minutes.

Commençons par regarder la structure du CSV :

```console
admin@i-0e3c248419faf2776:~$ ls
agent  table_tableau11.csv
admin@i-0e3c248419faf2776:~$ head table_tableau11.csv 
Province,Electoral District Name/Nom de circonscription,Electoral District Number/Numéro de circonscription,Population,Electors/Électeurs,Polling Stations/Bureaux de scrutin,Valid Ballots/Bulletins valides,Percentage of Valid Ballots /Pourcentage des bulletins valides,Rejected Ballots/Bulletins rejetés,Percentage of Rejected Ballots /Pourcentage des bulletins rejetés,Total Ballots Cast/Total des bulletins déposés,Percentage of Voter Turnout/Pourcentage de la participation électorale,Elected Candidate/Candidat élu
"Newfoundland and Labrador/Terre-Neuve-et-Labrador","Avalon",10001,81540,68487,220,42086,99.6,162,.4,42248,61.7,"McDonald, Ken Liberal/Libéral"
"Newfoundland and Labrador/Terre-Neuve-et-Labrador","Bonavista--Burin--Trinity",10002,76704,62462,260,35092,99.5,173,.5,35265,56.5,"Foote, Judy M. Liberal/Libéral"
"Newfoundland and Labrador/Terre-Neuve-et-Labrador","Coast of Bays--Central--Notre Dame",10003,78092,64226,233,35448,99.6,145,.4,35593,55.4,"Simms, Scott Liberal/Libéral"
"Newfoundland and Labrador/Terre-Neuve-et-Labrador","Labrador",10004,26728,20045,84,12373,99.6,53,.4,12426,62,"Jones, Yvonne Liberal/Libéral"
"Newfoundland and Labrador/Terre-Neuve-et-Labrador","Long Range Mountains",10005,87592,71918,253,41824,99.7,108,.3,41932,58.3,"Hutchings, Gudie Liberal/Libéral"
"Newfoundland and Labrador/Terre-Neuve-et-Labrador","St. John's East/St. John's-Est",10006,81936,66304,186,44880,99.8,111,.2,44991,67.9,"Whalen, Nick Liberal/Libéral"
"Newfoundland and Labrador/Terre-Neuve-et-Labrador","St. John's South--Mount Pearl/St. John's-Sud--Mount Pearl",10007,81944,67596,185,44801,99.7,133,.3,44934,66.5,"O'Regan, Seamus Liberal/Libéral"
"Prince Edward Island/Île-du-Prince-Édouard","Cardigan",11001,36005,28889,90,22485,99.6,96,.4,22581,78.2,"MacAulay, Lawrence Liberal/Libéral"
"Prince Edward Island/Île-du-Prince-Édouard","Charlottetown",11002,34562,28129,82,21165,99.5,99,.5,21264,75.6,"Casey, Sean Liberal/Libéral"
```

Avec Python, il est important de noter l'index de chaque section, par exemple en prenant l'un des enregistrements :

```csv
"British Columbia/Colombie-Britannique","Cowichan--Malahat--Langford",59010,99160,81888,227,61778,99.6,230,.4,62008,75.7,"MacGregor, Alistair NDP-New Democratic Party/NPD-Nouveau Parti démocratique"
```

Soir les colonnes suivantes :

- Province: British Columbia/Colombie-Britannique

- Electoral District Name/Nom de circonscription: Cowichan--Malahat--Langford

- Electoral District Number/Numéro de circonscription: 59010

- Population: 99160

- Electors/Électeurs: 81888

- Polling Stations/Bureaux de scrutin: 227

- Valid Ballots/Bulletins valides: 61778

- Percentage of Valid Ballots /Pourcentage des bulletins valides: 99.6

- Rejected Ballots/Bulletins rejetés: 230

- Percentage of Rejected Ballots /Pourcentage des bulletins rejetés: .4

- Total Ballots Cast/Total des bulletins déposés: 62008

- Percentage of Voter Turnout/Pourcentage de la participation électorale: 75.7

- Elected Candidate/Candidat élu: MacGregor, Alistair NDP-New Democratic Party/NPD-Nouveau Parti démocratique

Par conséquent, les index qui nous intéressent sont les 3 (population) et 8 (Bulletins rejetés).

```python
import csv
from hashlib import md5

with open('table_tableau11.csv') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    max_rejected = 0
    solution = ""
    for row in reader:
        population = int(row[3])
        if population < 100000:
            rejected = float(row[8])
            if rejected > max_rejected:
                solution = row[1]
                max_rejected = rejected
    print(solution)
    print(md5(solution + "\n").hexdigest())
```

Solution :

```console
admin@i-0bd86aa83a6d8e57b:~$ python3 find.py 
Montcalm
e399d171f21839a65f8f8ab55ed1e1a1
```
