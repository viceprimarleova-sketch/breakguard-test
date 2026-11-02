# BreakGuard {{VERSION}} — evaluare tehnică gratuită

Prototip local pentru trei familii de modificări Shopify. Evaluarea este
gratuită, fără abonament sau obligație de cumpărare. Nu cerem parole, cod privat
sau acces la magazine. Ai nevoie de un calculator cu Python 3.10 sau mai nou.

## Windows — PowerShell (pas cu pas)

1. Dezarhivează kitul într-un folder simplu, de exemplu `C:\BreakGuard-eval`.
2. În File Explorer, deschide acel folder.
3. Apasă pe bara de adresă, scrie `powershell` și apasă Enter. Se deschide
   PowerShell direct în folderul kitului. Alternativ, în PowerShell folosește
   `cd "C:\BreakGuard-eval"` (înlocuiește calea cu folderul tău real).
4. Rulează **o singură comandă odată** și așteaptă să termine:

```powershell
py -3 --version
.\install_windows.cmd
.\.venv\Scripts\python.exe scripts\release_smoke.py
```

Dacă prima comandă spune că `py` nu este recunoscut, instalează Python 3.10+
de pe python.org, bifează opțiunea de adăugare în PATH, închide PowerShell,
deschide-l din nou în folderul kitului și reîncearcă. Dacă instalarea se oprește,
nu continua cu comenzile următoare: copiază mesajul complet de eroare.

**Important:** în PowerShell, pentru a porni un fișier executabil din folderul
curent se folosește prefixul `.`. De aceea comanda corectă este
`.\.venv\Scripts\python.exe`, nu `.venv\Scripts\python.exe`.
Nu copia promptul `PS C:\...>` și nu lipi mai multe comenzi într-o singură
linie.

## Linux / macOS

Deschide terminalul în folderul kitului și rulează, pe rând:

```sh
sh install_unix.sh
.venv/bin/python scripts/release_smoke.py
```

Instalarea verifică integritatea fișierelor și folosește cele două pachete incluse,
fără descărcări pip. `EVALUATION_IDENTITY.json` identifică sursa și amprenta exactă;
același număr rc2 poate avea builduri diferite. SHA-256 nu este semnătură digitală.

Testul folosește fișiere temporare sintetice: **3 constatări → 2 modificări
GraphQL → 1 caz ScriptTag manual**, apoi verifică revenirea și protecția editărilor
ulterioare. Include o simulare de plată fără rețea și bani; nu confirmă o
tranzacție PayPal Sandbox ori un checkout real.

Instrucțiunile complete sunt în `README_EN.md`. Pe o copie temporară de proiect,
verifică previzualizarea, aplică doar modificările înțelese, controlează diferența
și rulează testele aplicației. Folosește identificatorul afișat pentru revenire.
Codul de ieșire 1 este normal când rămân constatări; 2 înseamnă eroare.
Copiile de siguranță conțin surse necriptate și trebuie păstrate local.

`manual_cases` trebuie să rămână cu patru constatări manuale, fără modificări.
`coverage_cases` include o interogare dinamică neverificată. Acoperirea este
limitată; zero constatări nu certifică compatibilitatea Shopify. Modificările
verifică sintaxa GraphQL, nu schema sau comportamentul unei aplicații reale.

Un dezvoltator Shopify poate urma `TESTER_GUIDE.md` timp de 30–60 de minute și
completa voluntar `FEEDBACK_TEMPLATE.md`. Trimite doar observații și valori
agregate, anonimizate. Demonstrația nu dovedește utilitatea comercială, iar o
cerere de evaluare gratuită nu este vânzare sau acceptare a ofertei plătite.
