---
title: "Writeup for the Huntress 2023 Steganography challenge"
tags: [CTF, Stéganographie, Huntress 2023]
---

## Land Before Time

### Description

> This trick is nothing new, you know what to do: **iSteg**. Look for the tail that's older than time, this Spike, you shouldn't climb.  

### Solution

LSB (Least Significant Bit) is a common way to hide data into images, however, depending on the software used you may obtain different results...

Here, [iSteg](https://github.com/rafiibrahim8/iSteg) is mentioned so let's use it.

```console
$ java -jar iSteg-v2.01_CLI.jar
iSteg CLI v-2.01
Enter your choice:
        1. Hide a file with Steg
        2. Hide a message with Steg
        3. Extract stuff from Steg
        Enter any things to exit.
3
Enter file name with extension:
dinosaurs1.png
Password (Press enter if the steganographic data wasn't encrypted):

Message extraction successful. The text is:

flag{da1e2bf9951c9eb1c33b1d2008064fee}
```
