fractal
=======

Mandelbrot fractal drawer

Joonistab Mandelbrot fraktali. Selle jaoks käib kõik punktid läbi komplekstasandil. Näiteks kui punkt on c, siis tehakse mingi arv korda tehteid z->z^2+c, alguses z=0. Programm teeb seda tehet iga piksli puhul 200 korda ja kui kompleksarvu magnituud läheb üle kahe, siis järelikult jada läheb lõpmatusse, kui jääb alla kahe, siis oletame et ei lähegi lõpmatusse. Kui jada läheb lõpmatuks, siis jätame meelde, mitme sammuga läks magnituud üle kahe ja selle järgi määrame piksli tumeduse, kui ei läinudki on piksel must. Fraktalil saab hetkel sisse zuumida tõmmates hiirega ristküliku, aga välja zuumida ei saa. Kuskilt maalt alates ei ole fraktal enam piisavalt detailne, sest floati täpsus ei ole piisav. Samuti suure iteratsioonide arvu puhul (hetkel 200) on uue pildi genereerimine üpris aeglane, minu arvutil väiksemate suuruste puhul kuni 10 sekundit. Hetkel on joonistusala suurus 300x300 pikslit, ehk 90 000 pikslit ja iga piksli jaoks tehakse kuni 200 iteratsiooni, ehk suurusjärk 20 miljonit iteratsiooni. Nüüd tuleks mõelda, kas algoritmi saab kuidagi efektiivsemaks teha, et saaks teha kiiremat zuumimist ja et see töötaks ka väga suurte suurendust ehk väikeste arvude korral, lisada välja zuumimine, teha värve võib-olla huvitavamaks, võib-olla lisada teisi fraktale juurde (Julia set-ist).

Nüüd väljas versioon 2.
Nüüd saab fraktalit ringi tõsta, välja zuumida. Lisaks kasutab programm nelja protsessi, et pildijuppe saaks arvutada paralleelselt, kui protsessoril on neli tuuma. Kiirema arvutamise jaoks võtsin kasutusele just-in-time kompileerija, mis kompileerib pythoni koodi. See teeb fraktali arvutamise kuni mitukümmend korda kiiremaks. Seega nüüd on fraktali joonistamine kiirem ja fraktal suurem.

V3
Kasutab gmpy2, mille abil saab teha arvutusi kui tahes täpselt (kuni mitu tuhat komakohta kindlasti), võrreldes tavalise doublega, mis on alla 20 komakoha. Kuna kompileerija gmpy2-te ei tunne, siis kompileerimine ei anna kiirust juurde ja on hoopis ilma kiirem. Gmpy2 on ise ka aeglasem, kui tavaliste floatidega arvutamine, seega on kokkuvõttes see mitusada korda aeglasem ja erilist interaktiivsust ei ole nagu kompileeritud versioonis ja mõistliku aja jooksul pildi saamiseks tuleb pikslite arvu vähendada (size). Seda versiooni saab muuta tavaliseks (sama kiire kui V2), kui võtta jit eest # ära ja algsuurused defineerida tavaliste arvudena, mitte gmpy2 kaudu.

V4
Nüüd saab panna ekraani suuruseks ükskõik mida. Lisaks saab määrata ristkülikute suurust, mille kaupa programm arvutab. Ringi tõstes hakkab ta kohe arvutama ainult neid piirkondi, mis on veel arvutamata.
