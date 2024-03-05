---
title: "Solution du challenge Marrakech de SadServers.com"
tags: [CTF,AdminSys,SadServers]
---

**Scenario:** "Marrakech": Word Histogram

**Level:** Medium

**Type:** Do

**Tags:** [bash](https://sadservers.com/tag/bash)  

**Description:** Find in the file `frankestein.txt` the **second** most frequent word and save in **UPPER** (capital) case in the `/home/admin/mysolution` file.

A word is a string of characters separated by space or newlines or punctuation symbols `.,:;`. Disregard case ('The', 'the' and 'THE' is the same word) and for simplification consider the apostrophe as another character not as punctuation ("it's" would be a word, distinct from "it" and "is"). Also disregard plurals ("car" and "cars" are different words) and other word variations (don't do "stemming").

We are providing a shorter *test.txt* file where the second most common word in upper case is "WORLD", so we could save this solution as: `echo "WORLD" > /home/admin/mysolution`

This problem can be done with a programming language (Python, Golang and sqlite3) or with common Linux utilities.

**Test:** `echo "SOLUTION" | md5sum` returns `19bf32b8725ec794d434280902d78e18`

See `/home/admin/agent/check.sh` for the test that "Check My Solution" runs.

**Time to Solve:** 20 minutes.

Pour résoudre le challenge j'ai tout de suite pensé à `collections.Counter` qui compte les occurrences des éléments dans des listes, etc. 

Pour le reste, je mets en majuscules, je remplace les caractères spéciaux par des espaces puis j'utilise bêtement `split` pour couper sur les whitespaces.

```python
import sys
import re
from collections import Counter

with open(sys.argv[1]) as fd:
    buff = fd.read().upper()
    buff = re.sub(r"[.,:;]", " ", buff)
    counts = Counter(buff.split())
    print(counts.most_common(2))
```

```console
admin@i-006c4795f4f0f63af:~$ python3 freq.py frankestein.txt 
[('THE', 4339), ('AND', 3024)]
admin@i-006c4795f4f0f63af:~$ echo AND > mysolution
```
