# CloudChat
## Maturitní projekt 2015/2016 
### Jakub Mach, 4.B

Toto je dokumentace k maturitní práci nazvané *Cloudová chatovací aplikace*.
Kód maturitní práce se skládá celkem ze tří částí, v této dokumentaci detailně popíši co, jak a proč v těchto třech částech funguje
a uvedu návod k instalaci aplikace na vlastní server.

## Obsah:
* Část nultá: HTML & CSS
* Část první: Klientská JavaScript část
* Část druhá: API endpoint
* Část třetí: Serverová (bouncer) část
* Návod k instalaci

## Část nultá: HTML & CSS
Kód "nulté" části byl vytvořen jako první (a byl postupem času modifikován) a hlavně jako základ pro další tvorbu. Napsal jsem ho proto, že jsem chtěl stránky statické a dynamičnost těmto stránkám bude přidána až za pomocí JavaScriptu. Jelikož nejsem moc na grafiku a frontend, rozhodl jsem se si práci zjednodušit front-endovou knihovnou jménem *Twitter Bootstrap*.
Kód této části sestává z několika HTML5 a CSS3 souborů, které nyní popíši: 
### index.html
**Hlavní stránka aplikace**, rozdělena na 3 části: navigace, pod ním header s registrací nového uživatele a krátký souhrn informací o aplikaci.
Navigace má celkem tři odkazy, první vede na počátek stránky, druhý vede na "krátký souhrn informací o aplikaci", třetí je odkaz na přihlašovací stránku.
Část s registrací používá obrázek bouřkových mraků s volnou licencí ze služby Flickr.
### login.html
Jedná se o stránku vzhledově podobnou stránce hlavní, na které i byla založena, ovšem místo registračního formuláře se zde vyskytuje **formulář pro přihlášení**.
Pokud je uživatel přihlášen tak je formulář dynamicky skryt (více o tom v části první) a místo něj je zobrazeno tlačítko pro přesměrování do samotné aplikace.

![Tlačítko zobrazené, pokud je uživatel již přihlášen.](1.png)

### chat.html
Nejdůležitější z HTML stránek je stránka chat.html, která již má spoustu statických prvků, které se zdynamičťují JavaScriptovou logikou popsanou v části první.

## Část první: Klientská JavaScript část
Klientská javascript část se skládá z několika funkcí a globálních proměnných. Využívá knihovny jQuery k práci s DOM elementy a k posílání ajax požadavků.
### homepage.js
Obsahuje pouze ajax request pro registrační formulář.
### loginpage.js
Obsahuje ajax request, který se vykoná při načtení stránky a odešle API serveru session cookie uživatele, pro zjištění, zda není již uživatel přihlášen. Pokud je uživatel již přihlášen, zobrazí se formulář 
### chatpage.js
Hlavní javascriptová část celé aplikace, používaná v souboru **chat.html**.
Začíná několika globálními proměnnými, uchovávající informace pro správný běh jako například seznam identifikačních čísel zpráv v určitých kanálech.
Při úspěšném načtení DOM se zavolá funkce, která zjistí, zda je uživatel přihlášen a pokud není, je poslán na přihlašovácí stránku, dále pak načte globální informace do proměnné, přiřadí funkci tlačítku pro odeslání zprávy a spustí první instanci timeru, který volá metodu ping.

#### Metoda ping()
Metoda ping obsluhuje stahování nových zpráv pro kanály a servery. Je volaná každých 1500 ms.
Dále také kontroluje, zda je uživatel stále přihlášen, pokud není, je z aplikace poslán na přihlašovácí stránku login.html.

#### Ajax requesty
V celém souboru chatpage.js se vyskytuje spousta ajax requestů, které volají API backend pro učinění nějaké operace a reagování na odpověď od API.
Využívá se k tomu jquery metoda POST, díky které nemůžou prohlížeče cachovat výsledky a můžou posílat formdata a přijímat JSON, který API server vrací.


## Část druhá: API endpoint
API endpoint využívá knihovny Flask a je rozdělen na dvě části:
První část s pomocnými utilitními funkcemi, které jsou v druhé části. 

## Část třetí: Serverová (bouncer) část


## Návod k instalaci
c
