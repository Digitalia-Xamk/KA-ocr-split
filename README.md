# KA-ocr-split
Kansallisarkiston päätöspöytäkirjojen ocr luenta ja splittaus. Koodit toteuttanut Xamkin Digitalia-tutkimuskeskus (www.digitalia.fi) ja materiaalit toimittanut Kansallisarkisto (https://www.arkisto.fi/). 
Varsinaisten skriptien lisäksi tarvitaan ainakakin seuraavat ohjelmistot. Alla myös käytetyt versiot mutta uudemmatkin toiminevat.

## Kirjastot ja ohjelmat

### Tesseract
4.0.0-beta.4-50-g07acc,OCR-luku, https://github.com/tesseract-ocr/

### Leptonica
1.75.3, Kirjasto jota Tesseract tarvitsee, asennettava käsin, https://github.com/DanBloomberg/leptonica

### ImageMagick
6.8.9-9 Q16 x86_64 2017-07-31, Ohjelmisto jota Python toteutus käyttää kuvien ja pdf tiedostojen konvertointiin ja muokkaamiseen ennen Tesseractille vientiä, https://imagemagick.org/

### GhostScript
9.26, Käytetään PDF/A ja PDF tiedostojen luontiin, https://www.ghostscript.com/

### pdfminer.six
20181108, pdf-dokumenttien sisällön parsinta,https://pypi.org/project/pdfminer.six/

### Pillow
6.0.0, Kuvien käsittely ja kokolaskenta,https://pypi.org/project/Pillow/

### PyPDF2
1.26.0, pdf-tiedostojen luku ja kirjoitus, https://pypi.org/project/PyPDF2/

### pdfminer
20140328,pdf-dokumenttien sisällön parsinta, https://pypi.org/project/pdfminer/

### pdfplumber 
Tekstin ekstraktointiin https://github.com/jsvine/pdfplumber

### pikepdf
Muodostaa pilkotut tiedostot  https://pypi.org/project/pikepdf/

## Python koodit

* KA-ocr-pdf.py on OCR luvun tekevä skripti. Optimoitu tällä hetkellä suurelle määrälle kansioita, joista jokainen sisältää yhteen kokonaisuuteen kuuluvat kuvat. Lopullisen ocr-tiedon sisältävän pdf tiedoston nimeksi tulee kuvatiedostot sisältävän kansion edeltävä kansionimi_kaikki.pdf  --> Esim. sample/3979637.KA/jpeg hakemiston sisällöstä tehdään 3979637.KA_kaikki.pdf tiedosto. Käyttö muuten järjestellyn materiaalin kanssa vaatii muutoksia koodiin.

* KA-ocr-pdf-speedmod Tekee saman asian kuin ylempi koodi mutta optimointia ja CPU käyttöä parannettu. Lopullinen PDF tiedostojen generointi edelleen optimoimatta

* KARemoveBlanks.py yrittää poistaa yllä mainitun skriptin jättämät tyhjät tiedostot lukemalla sisällön pdfminerillä ja etsimällä sivuja joilla ei ole tekstiksi luokiteltavaa aineistoa

* KACountBefore-After.py Lukee jpeg kansion sisällön ja laskee alkuperäiset sivut. Lisäksi skannaa generoidun kaikki.pdf tiedoston läpi ja laskee sen sivunumerot. Tulokset kirjoitetaan pages_before_ocr.txt ja pages_after_ocr.txt tiedostoihi 

* minePDF.py Varsinainen PDF parsinnan tekevä koodir jota KARemoveBlanks.py ja KAdivPDFbyKEYPlumb.py tarvitsevat

* KAdivPDFbyKEYPlumb.py Suorittaa osa1:n aineistojen pilkonnan

* KACheckPDFPageCount.py Muodostaa osa1:n kansioon sisällysluettelon



## Muut
* formats.csv, tiedostolista ImageMagickin tukemista formaateista joita KA-ocr.pdf.py hyödyntää konvertoidessaan lähtötiedostoja


