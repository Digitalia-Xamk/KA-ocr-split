# KA-ocr-split
Kansallisarkiston päätöspöytäkirjojen ocr luenta ja splittaus. Varsinaisten skriptien lisäksi tarvitaan ainakakin seuraavat ohjelmistot. Alla myös käytetyt versiot mutta uudemmatkin toiminevat.

Tesseract
4.0.0-beta.4-50-g07acc
OCR-luku
https://github.com/tesseract-ocr/

Leptonica
1.75.3 
Kirjasto jota Tesseract tarvitsee, asennettava käsin
https://github.com/DanBloomberg/leptonica

ImageMagick
6.8.9-9 Q16 x86_64 2017-07-31
Ohjelmisto jota Python toteutus käyttää kuvien ja pdf tiedostojen konvertointiin ja muokkaamiseen ennen Tesseractille vientiä
https://imagemagick.org/

GhostScript
9.26
Käytetään PDF/A ja PDF tiedostojen luontiin
https://www.ghostscript.com/

pdfminer.six
20181108
pdf-dokumenttien sisällön parsinta
https://pypi.org/project/pdfminer.six/

Pillow
6.0.0
Kuvien käsittely ja kokolaskenta
https://pypi.org/project/Pillow/

PyPDF2
1.26.0
pdf-tiedostojen luku ja kirjoitus
https://pypi.org/project/PyPDF2/

pdfminer
20140328
pdf-dokumenttien sisällön parsinta
https://pypi.org/project/pdfminer/

