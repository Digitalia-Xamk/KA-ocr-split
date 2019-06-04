# KA-ocr-split
Kansallisarkiston päätöspöytäkirjojen ocr luenta ja splittaus. Koodit toteuttanut Xamkin Digitalia-tutkimuskeskus (www.digitalia.fi) ja materiaalit toimittanut Kansallisarkisto (https://www.arkisto.fi/). 
Varsinaisten skriptien lisäksi tarvitaan ainakakin seuraavat ohjelmistot. Alla myös käytetyt versiot mutta uudemmatkin toiminevat.

## Tesseract
4.0.0-beta.4-50-g07acc
OCR-luku
https://github.com/tesseract-ocr/

## Leptonica
1.75.3 
Kirjasto jota Tesseract tarvitsee, asennettava käsin
https://github.com/DanBloomberg/leptonica

## ImageMagick
6.8.9-9 Q16 x86_64 2017-07-31
Ohjelmisto jota Python toteutus käyttää kuvien ja pdf tiedostojen konvertointiin ja muokkaamiseen ennen Tesseractille vientiä
https://imagemagick.org/

## GhostScript
9.26
Käytetään PDF/A ja PDF tiedostojen luontiin
https://www.ghostscript.com/

## pdfminer.six
20181108
pdf-dokumenttien sisällön parsinta
https://pypi.org/project/pdfminer.six/

## Pillow
6.0.0
Kuvien käsittely ja kokolaskenta
https://pypi.org/project/Pillow/

## PyPDF2
1.26.0
pdf-tiedostojen luku ja kirjoitus
https://pypi.org/project/PyPDF2/

## pdfminer
20140328
pdf-dokumenttien sisällön parsinta
https://pypi.org/project/pdfminer/

*KA-ocr-pdf.py on OCR luvun tekevä skripti. Optimoitu tällä hetkellä suurelle määrälle kansioita, joista jokainen sisältää yhteen kokonaisuuteen kuuluvat kuvat. Lopullisen ocr-tiedon sisältävän pdf tiedoston nimeksi tulee kuvatiedostot sisältävän kansion edeltävä kansionimi_kaikki.pdf  --> Esim. sample/3979637.KA/jpeg hakemiston sisällöstä tehdään 3979637.KA_kaikki.pdf tiedosto. Käyttö muuten järjestellyn materiaalin kanssa vaatii muutoksia koodiin.

*KARemoveBlanks.py yrittää poistaa yllä mainitun skriptin jättämät tyhjät tiedostot lukemalla sisällön pdfminerillä ja etsimällä sivuja joilla ei ole tekstiksi luokiteltavaa aineistoa

*KACountBefore-After.py Lukee jpeg kansion sisällön ja laskee alkuperäiset sivut. Lisäksi skannaa generoidun kaikki.pdf tiedoston läpi ja laskee sen sivunumerot. Tulokset kirjoitetaan pages_before_ocr.txt ja pages_after_ocr.txt tiedostoihin 



