---
title: "Writeups for Huntress 2023 Warmups challenges"
tags: [CTF, Huntress 2023]
---

## Baking

### Description

> Do you know how to make cookies? How about HTTP flavored? 

### Solution

You are given a URL to a webapp that looks like an oven.

You can click several buttons, and it will put something in the oven and start a timer, for example cooking Muffins takes 15 minutes.

When you choose Muffins a cookie named `in_oven` is set in your browser with the following value:

```
eyJyZWNpcGUiOiAiTXVmZmlucyIsICJ0aW1lIjogIjEwLzE0LzIwMjMsIDEzOjUwOjU3In0=
```

This is base64 encoded data with decodes to:

```json
{"recipe": "Muffins", "time": "10/14/2023, 13:50:57"}
```

You had to notice that cooking `Magic Cookies` takes 7200 minutes which is abnormally long.

You have to forge a cookie with an old date in order to get the `Magic Cookies` cooked:

```json
{"recipe": "Magic Cookies", "time": "01/01/2022, 13:50:57"}
```

You encode it to base64:

```
eyJyZWNpcGUiOiAiTWFnaWMgQ29va2llcyIsICJ0aW1lIjogIjAxLzAxLzIwMjIsIDEzOjUwOjU3In0K%
```

And add it to your browser with the `EditThisCookie` extension. Then you refresh the webpage and get the flag:

```
flag{c36fb6ebdbc2c44e6198bf4154d94ed4}
```

## BaseFFFF+1

### Description

> Maybe you already know about base64, but what if we took it up a notch?

### Solution

base65536 is a method to convert data to valid Unicode code points.

There is [a Python library](https://github.com/qntm/base65536) to code/decode stuff:
```python
import base65536

with open("baseffff1", mode="r") as f:
    data = f.read()

    decoded_contents = base65536.decode(contents_of_file)
    print(decoded_contents)
```

## Book By Its Cover

### Description

> They say you aren't supposed to judge a book by its cover, but this is one of my favorites! 

### Solution

This is very basic, check the file type of the unknown file with the following command :

```
file book.rar
```

It turns out the file is a PNG file. Use whatever tool you want to see the flag.

## CaesarMirror

### Description

> Caesar caesar, on the wall, who is the fairest of them all? 
> Perhaps a clever ROT13?

### Solution

When we get the file it sure looks like rot13 a.k.a. the Caesar cipher:

```
     Bu obl! Jbj, guvf jnezhc punyyratr fher   bf V !erugrtbg ghc bg ahs sb gby n fnj
    qrsvavgryl nofbyhgryl nyjnlf ybir gelvat   ftavug rivgnibaav qan jra ch xavug bg
       gb qb jvgu gur irel onfvp, pbzzba naq   sb genc gfevs ruG !frhdvauprg SGP pvffnyp
     lbhe synt vf synt{whyvhf_ naq gung vf n   tavuglerir gba fv gv gho gengf gnret
 gung lbh jvyy arrq gb fbyir guvf punyyratr.    qan rqvu bg tavleg rxvy g'abq V
  frcnengr rnpu cneg bs gur synt. Gur frpbaq   bq hbl gho _n_av fv tnys rug sb genc
   arrq whfg n yvggyr ovg zber. Jung rknpgyl   rxnz qan leg bg reru rqhypav rj qyhbuf
     guvf svyyre grkg ybbx zber ratntvat naq   ?fravyjra qqn rj qyhbuF ?ryvujugebj
    Fubhyq jr nqq fcnprf naq gel naq znxr vg   uthbar fv fravy lanz jbU ?ynpvegrzzlf
 gb znxr guvf svyyre grkg ybbx oryvrinoyr? N    n avugvj ferggry sb renhdf qvybf
 fvzcyr, zbabfcnpr-sbag grkg svyr ybbxf tbbq   rug gn gfbzyn rj reN .rz bg uthbar
   raq? Vg ybbxf yvxr vg! V ubcr vg vf tbbq.   }abvgprysre fv tnys ehbl sb genc qevug ruG
naq ng guvf cbvag lbh fubhyq unir rirelguvat   ebs tnys fvug gvzohf bg qrra hbl gnug
    cbvagf. Gur ortvaavat vf znexrq jvgu gur   ,rpneo lyehp tavarcb rug qan kvsrec tnys
  naq vg vapyhqrf Ratyvfu jbeqf frcnengrq ol   lyehp tavfbyp n av qar bg ,frebpferqah
  oenpr. Jbj! Abj GUNG vf n PGS! Jub xarj jr   fvug bg erucvp enfrnp rug xyvz qyhbp
            rkgrag?? Fbzrbar trg gung Whyvhf   !ynqrz n lht enfrnP
```

You can give the text to [rot13.com](https://rot13.com/) which will decode the text (rot13 is just shifting ascii letters 13 positions forward in the alphabet).

You then get the following text:

```
     Oh boy! Wow, this warmup challenge sure   os I !rehtegot tup ot nuf fo tol a saw
    definitely absolutely always love trying   sgniht evitavonni dna wen pu kniht ot
       to do with the very basic, common and   fo trap tsrif ehT !seuqinhcet FTC cissalc
     your flag is flag{julius_ and that is a   gnihtyreve ton si ti tub trats taerg
 that you will need to solve this challenge.    dna edih ot gniyrt ekil t'nod I
  separate each part of the flag. The second   od uoy tub _a_ni si galf eht fo trap
   need just a little bit more. What exactly   ekam dna yrt ot ereh edulcni ew dluohs
     this filler text look more engaging and   ?senilwen dda ew dluohS ?elihwhtrow
    Should we add spaces and try and make it   hguone si senil ynam woH ?lacirtemmys
 to make this filler text look believable? A    a nihtiw srettel fo erauqs dilos
 simple, monospace-font text file looks good   eht ta tsomla ew erA .em ot hguone
   end? It looks like it! I hope it is good.   }noitcelfer si galf ruoy fo trap driht ehT
and at this point you should have everything   rof galf siht timbus ot deen uoy taht
    points. The beginning is marked with the   ,ecarb ylruc gninepo eht dna xiferp galf
  and it includes English words separated by   ylruc gnisolc a ni dne ot ,serocsrednu
  brace. Wow! Now THAT is a CTF! Who knew we   siht ot rehpic raseac eht klim dluoc
            extent?? Someone get that Julius   !ladem a yug raseaC
```

It looks like the right part of the text is reversed. Let's fix that:

```python
with open("out.txt") as fd:
    for line in fd:
        line = line.strip("\n")
        start = line[:44]
        end = line[45:][::-1]
        print(start, end)
```

And here we go:

```
     Oh boy! Wow, this warmup challenge sure  was a lot of fun to put together! I so
    definitely absolutely always love trying  to think up new and innovative things
       to do with the very basic, common and  classic CTF techniques! The first part of
     your flag is flag{julius_ and that is a  great start but it is not everything
 that you will need to solve this challenge.  I don't like trying to hide and
  separate each part of the flag. The second part of the flag is in_a_ but you do
   need just a little bit more. What exactly should we include here to try and make
     this filler text look more engaging and worthwhile? Should we add newlines?
    Should we add spaces and try and make it symmetrical? How many lines is enough
 to make this filler text look believable? A solid square of letters within a
 simple, monospace-font text file looks good enough to me. Are we almost at the
   end? It looks like it! I hope it is good. The third part of your flag is reflection}
and at this point you should have everything that you need to submit this flag for
    points. The beginning is marked with the flag prefix and the opening curly brace,
  and it includes English words separated by underscores, to end in a closing curly
  brace. Wow! Now THAT is a CTF! Who knew we could milk the caesar cipher to this
            extent?? Someone get that Julius Caesar guy a medal!
```

We just need to read carefully to get the flag:

```
flag{julius_in_a_reflection}
```

## Chicken Wings

### Description

> I ordered chicken wings at the local restaurant, but uh... this really isn't what I was expecting... 

### Solution

_Wings_ is a reference to the _Wingding_ font used in Microsoft Words.

The font is using symbols only and each symbol is now standard unicode.

We can use the [dcode Wingding decoder](https://www.dcode.fr/wingdings-font) to get the flag:

♐●♋♑❀♏📁🖮🖲📂♍♏⌛🖰♐🖮📂🖰📂🖰🖰♍📁🗏🖮🖰♌📂♍📁♋🗏♌♎♍🖲♏❝

It decodes to:

```
flag{e0791ce68f718188c0378b1c0a3bdc9e}
```

Not that this exercise is almost a complete rip [of another challenge](https://1erkankilic.medium.com/nahamcon-ctf-writeup-c1ddffdc1655).

## Comprezz

### Description

> Someone stole my S's and replaced them with Z's! Have you ever seen this kind of file before? 

### Solution

The downloaded file is compressed with the `compress` utility:

```console
$ file comprezz
comprezz: compress'd data 16 bits
```

We can uncompress it with the `uncompress` command line or use `zcat` to display its content:

```console
$ zcat comprezz
flag{196a71490b7b55c42bf443274f9ff42b}
```

## Dialtone

### Description

> Well would you listen to those notes, that must be some long phone number or something! 

### Solution

When you open it, you get several dial tones.

Dial tones are in fact a multi-frequency signal code called Dual-tone multi-frequency signaling (DTMF).  
See :
- https://en.wikipedia.org/wiki/Dual-tone_multi-frequency_signaling
- https://fr.wikipedia.org/wiki/Code_DTMF

Each number is encoded with 2 frequencies, so we can decode the file on this website for example : https://dtmf.netlify.app/.

We get this decoded sequence of numbers `13040004482820197714705083053746380382743933853520408575731743622366387462228661894777288573`.

At first look, we could think that it is a string that we need to split or whatever, maybe to obtain a hex version of the string.  
But we have to consider it as a big int to solve this challenge ! (It took us a few hours of work to find this trick).

```python
# DTMF tones
dialtones = "13040004482820197714705083053746380382743933853520408575731743622366387462228661894777288573"

# Convert to big int
bg = int(dialtones)

# Get hex version of the big hint
hex_str = format(bg, 'x')

# Decode the hex string to utf-8
byte_str = bytes.fromhex(hex_str)
regular_str = byte_str.decode('utf-8')

# TA DA
print(regular_str)
```

## F12

### Description

> Remember when Missouri got into hacking!?! You gotta be fast to catch this flag! 

### Solution

You receive a link to a page with a `Capture The Flag` button.

The HTML code looks like that:

```html
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
        <meta name="description" content="" />
        <meta name="author" content="" />
        <title>Fast Hands</title>
        <!-- Favicon-->
        <link rel="icon" type="image/x-icon" href="assets/favicon.ico" />
        <!-- Core theme CSS (includes Bootstrap)-->
    </head>
    <body>
        
        <!-- Page content-->
        <div class="container p-5">
            <div class="text-center mt-5 p-5">
                <button type="button" onclick="ctf()" class="btn btn-primary"><h1>Capture The Flag</button>
            </div>
        </div>
        <!-- Bootstrap core JS-->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    <script type="text/javascript">
        function ctf() {
            window.open("./capture_the_flag.html", 'Capture The Flag', 'width=400,height=100%,menu=no,toolbar=no,location=no,scrollbars=yes');
        }
    </script>
</html>
```

So clicking on the button will open the `capture_the_flag.html` page but the windows disappear and seems empty.

When in `view-source` mode in Chrome, just append the file name to the URL so it becomes `view-source:http://chal.ctf.games:32324/capture_the_flag.html`

Here we can see the flag in a hidden div (`display: none`) :

```html
    <body>
        
        <!-- Page content-->
        <div class="container p-5">
            <div class="text-center mt-5 p-5">
                <button type="button" onclick="ctf()" class="btn btn-success"><h1>Your flag is:<br>
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                  <span style="display:none">
                  flag{03e8ba07d1584c17e69ac95c341a2569}
                </span></button>
            </div>
        </div>
        <!-- Bootstrap core JS-->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    <script type="text/javascript">
        window.close();
    </script>
```

## Layered Security

### Description

> It takes a team to do security right, so we have layered our defenses! 

### Solution

The file turns out to be a GIMP image:

```console
$ file layered_security
layered_security: GIMP XCF image data, version 011, 1024 x 1024, RGB Color
```

Let's open it with GIMP and see the different layers:

![Opened with GIMP](/assets/img/Huntress2023/layered_security_gimp.png)

One seems to have a strange header, let's take a closer look:

![flag](/assets/img/Huntress2023/layered_security_flag.png)

## Notepad

### Description

> Just a sanity check... you do know how to use a computer, right? 

### Solution

I'm not a robot:

```console
$ cat notepad 
+------------------------------------------------------+
| [✖] [□] [▬]  Notepad                               - |
|------------------------------------------------------|
| File   Edit   Format   View   Help                   |
|------------------------------------------------------|
|                                                      |
|                                                      |
|   New Text Document - Notepad                        |
|                                                      |
|     flag{2dd41e3da37ef1238954d8e7f3217cd8}           |
|                                                      |
|                                                      |
|                                                      |
|                                                      |
|                                                      |
|                                                      |
|                                                      |
|                                                      |
|                                                      |
|                                                      |
+------------------------------------------------------+
| Ln 1, Col 40                                         |
+------------------------------------------------------+
```


## Query Code

### Description

> What's this? 

### Solution

The image is an image of a QR code.

You can use a lot of different tools to solve this.

```console
$ wget -q https://github.com/sayanarijit/qrscan/releases/download/v0.1.9/qrscan-0.1.9-x86_64-unknown-linux-gnu.tar.gz
$ tar xzf qrscan-0.1.9-x86_64-unknown-linux-gnu.tar.gz
$ ./qrscan-0.1.9/qrscan query_code.png 
flag{3434cf5dc6a865657ea1ec1cb675ce3b}
```

## String Cheese

### Description

> Oh, a cheese stick! This was my favorite snack as a kid. My mom always called it by a different name though... 

### Solution

This is an image but the flag doesn't appear in the EXIF tags. Just extract the strings:

```console
$ strings -a cheese.jpg | grep flag
flag{f4d9f0f70bf353f2ca23d81dcf7c9099}
```
