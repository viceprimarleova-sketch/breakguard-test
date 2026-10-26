# BreakGuard {{VERSION}} — evaluare tehnică gratuită

Prototip local pentru trei familii de modificări Shopify. Evaluarea este
gratuită, fără abonament sau obligație de cumpărare. Nu cerem parole, cod privat
sau acces la magazine. Ai nevoie de un calculator cu Python 3.10 sau mai nou.

Dezarhivează într-un folder nou și deschide terminalul în acel folder.

Windows PowerShell:
```powershell
.\install_windows.cmd
.\.venv\Scripts\python.exe scripts\release_smoke.py
```

Linux / macOS:
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
