# upb-project

## Zadanie 2
Cieľom zadania je implementovať základnú štruktúru webovej aplikácie (podľa konkrétnej témy) s dôrazom na šifrovanie/dešifrovanie súborov. Webovú aplikáciu je potrebné implementovať prostredníctvom platformy Docker.

Úlohy:

1. Vyberte si technológie, ktoré budete použiť na backend, frontend, databázu (napr. Flask (python) + Postgresql)
2. Implementujte základnú štruktúru pre docker-compose spolu so všetkými kontajnermi
3. Implementujte základnú štruktúru databázy, spolu s testovacími dátami, ktoré sa použijú na šifrovanie
4. Vyberte si kryptografické API pre vami vybranú platformu a implementujte:
        a) Extrakcia testovacích dát z databázy (prostredníctvom vybraného databázového API)
        b) Zašifrovanie dát vybranou symetrickou šifrou (symetrický kľúč sa vygeneruje na serveri)
        c) Zašifrovanie symetrického kľúča asymetrickým kľúčom používateľa
        d) Implementujte dešifrovanie súboru (zatiaľ stačí na strane servera)
        e) Implementujte overenie integrity súbor

Okrem zdrojových kódov sa odovzdáva dokumentácia riešenia, s popisom použitých technológií/API a taktiež popisom štruktúry zašifrovaného súboru.

Pozn. pri výbere šifrovacích funkcií a veľkosti kľúčov treba klásť dôraz aj na bezpečnostné odporučania ohľadom šifrovania (výber algoritmov a veľkosti kľúčov zdôvodnite v dokumentácii)

Flask + psql:
https://medium.com/free-code-camp/docker-development-workflow-a-guide-with-flask-and-postgres-db1a1843044a

PHP + mysql:
https://hostadvice.com/how-to/web-hosting/how-to-deploy-a-php-application-using-docker-compose/

Minimalistický príklad (example.zip):
docker-compose build
docker-compose up -d
