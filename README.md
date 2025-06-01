# Depanarea programelor la distanță

## Cerința

Aplicația implementează un sistem de depanare la distanță cu următoarele funcționalități:

- Server-ul execută programe constând în instrucțiuni aritmetice cu atribuirea rezultatului într-o variabilă, instrucțiuni ce pot include referiri la valorile altor variabile, constante numerice, operatori aritmetici și paranteze, fiecare atribuire constituind o instrucțiune ce poate fi depanată de la distanță.

- Clienții se conectează la server și înregistrează o serie de puncte de oprire într-un program, identificate prin numele programului și linia fiecărui punct de oprire a execuției.

- Server-ul acceptă un singur client care poate întrerupe execuția unui program la un moment dat.

- Clienții se pot atașa la un program, pot adăuga sau elimina puncte de oprire, sau se pot detașa de la depanarea execuției unui program.

- Aplicația server lansează în execuție mai multe programe în paralel.

- Pe durata execuției unui program, clientul care-i depanează execuția nu mai poate adăuga sau elimina puncte de oprire.

- În momentul în care server-ul ajunge, în timpul execuției unui program, la un punct interceptat de un client, acesta va aștepta din partea clientului comenzi pentru:
  - evaluarea unei variabile după nume
  - setarea valorii acesteia
  - continuarea până la următorul punct de întrerupere a execuției, după primirea din partea clientului a unei comenzi în acest sens

- La încheierea execuției programului depănat, server-ul va notifica clientul care-l monitorizează în acest sens.

## Structura proiectului

Proiectul conține următoarele fișiere:

- `server.py` - serverul principal de depanare
- `client.py` - clientul interactiv pentru depanare
- `test_simple.py` - teste funcționale pentru aplicație

## server.py

### Funcționalitate generală

Serverul de depanare implementează un sistem multi-threaded care poate gestiona mai mulți clienți simultan și poate executa mai multe programe în paralel. Folosește socket-uri TCP pentru comunicarea cu clienții și format JSON pentru mesaje.

**Caracteristici importante:**
- Acceptă multiple conexiuni de clienți simultan
- Permite doar un client să monitorizeze un program la un moment dat
- Execută programe în thread-uri separate
- Gestionează breakpoint-uri și debugging interactiv

### Clasa Program

Reprezintă un program care poate fi executat și depănat:

**Atribute principale:**
- `name` - numele programului
- `lines` - liniile de cod ale programului
- `variables` - dicționarul cu variabilele și valorile lor
- `breakpoints` - set-ul cu punctele de oprire
- `is_running` - starea de execuție
- `is_paused` - starea de pauză
- `debugger_client` - clientul care monitorizează programul

**Metode importante:**
- `parse_expression()` - evaluează expresii aritmetice cu variabile
- `execute_line()` - execută o linie de cod și actualizează variabilele

**Exemple de programe suportate:**
```
x = 5
y = x + 3
z = y * 2
result = z - 1
```

### Clasa DebugServer

Implementează serverul principal:

**Funcționalități de conectare:**
- Acceptă conexiuni TCP pe portul 8888
- Creează un thread pentru fiecare client conectat
- Gestionează deconectarea clienților în siguranță

**Comenzi suportate:**
- `list_programs` - listează toate programele disponibile
- `attach` - atașează un client la un program
- `detach` - detașează clientul de la program
- `add_breakpoint` - adaugă punct de oprire
- `remove_breakpoint` - elimină punct de oprire
- `run_program` - rulează un program
- `evaluate` - evaluează o variabilă
- `set_variable` - setează valoarea unei variabile
- `continue` - continuă execuția după pauză

**Execuție cu debugging:**
- Execută programele linie cu linie într-un thread separat
- Se oprește la breakpoint-uri și notifică clientul
- Permite evaluarea și modificarea variabilelor în timpul execuției
- Notifică terminarea execuției programului

**Restricții de acces:**
- Doar un client poate monitoriza un program la un moment dat
- Al doilea client care încearcă să se atașeze primește eroare
- Clienții pot lucra cu programe diferite simultan

### Programe preîncărcate

Serverul vine cu două programe de test:
- `program1` - calcule simple (x=5, y=x+3, etc.)
- `program2` - operații matematice (a=10, b=a/2, etc.)

## client.py

### Funcționalitate generală

Clientul interactiv permite conectarea la server și controlul execuției programelor. Oferă o interfață simplă prin linia de comandă și ascultă notificările de la server într-un thread separat.

**Caracteristici:**
- Conexiune TCP la server
- Interfață în linia de comandă
- Ascultare asincronă a notificărilor
- Gestionarea disconnectării graceful

### Clasa DebugClient

Implementează clientul de depanare:

**Funcționalități de conectare:**
- `connect()` - stabilește conexiunea cu serverul
- `listen_for_messages()` - ascultă mesajele de la server într-un thread separat
- `disconnect()` - închide conexiunea în siguranță

**Funcționalități de depanare:**
- `attach()` - se atașează la un program și afișează codul
- `detach()` - se detașează de la program
- `add_breakpoint()` - adaugă breakpoint la o linie specifică
- `remove_breakpoint()` - elimină breakpoint
- `run_program()` - pornește execuția unui program
- `evaluate()` - evaluează o variabilă și afișează valoarea
- `set_variable()` - modifică valoarea unei variabile
- `continue_execution()` - continuă execuția după pauză

**Gestionarea notificărilor:**
- Afișează mesaje când programul se oprește la breakpoint
- Arată variabilele curente și valorile lor
- Notifică terminarea execuției programului
- Oferă sfaturi pentru comenzile disponibile

### Interfața utilizator

Clientul oferă comenzi intuitive:
- `list` - vezi programele disponibile și starea lor
- `attach <nume>` - atașează la program și afișează codul
- `break <linie>` - pune breakpoint la linia specificată
- `unbreak <linie>` - elimină breakpoint
- `run <nume>` - rulează program
- `eval <variabilă>` - vezi valoarea variabilei
- `set <var> <valoare>` - schimbă valoarea
- `continue` - continuă execuția
- `detach` - detașează de la program
- `quit` - ieșire

### Coduri de test predefinite

Pentru ușurința testării, clientul recunoaște:
- `load test1 test1` - încarcă primul program de test
- `load test2 test2` - încarcă al doilea program de test

## test_simple.py

### Funcționalitate generală

Fișierul de teste verifică funcționalitatea de bază a aplicației prin teste automate care nu necesită interacțiune manuală. Testele acoperă toate aspectele importante ale cerinței.

### Teste implementate

**Test 1: Logica Program**
- Creează un program simplu cu 4 linii de cod
- Execută manual fiecare linie
- Verifică dacă calculele sunt corecte (x=5, y=8, z=16, result=15)
- Testează atribuirile și expresiile aritmetice

**Test 2: Pornire Server**
- Pornește serverul pe un port de test (9999)
- Verifică dacă acceptă conexiuni TCP
- Testează stabilitatea socket-ului
- Se asigură că serverul răspunde la conexiuni

**Test 3: Mai mulți clienți**
- Testează conectarea simultană a 3 clienți
- Verifică că serverul acceptă multiple conexiuni conform cerinței
- Confirmă că clienții se pot conecta în paralel
- Validează arhitectura multi-client

**Test 4: Parsare expresii**
- Testează evaluarea expresiilor aritmetice simple
- Verifică operațiile cu variabile (a + b, a * 2)
- Testează constante numerice
- Controlează operatorii matematici (+, -, *, /)

**Test 5: Breakpoints**
- Verifică setarea punctelor de oprire
- Testează adăugarea la linii specifice (0, 2)
- Controlează funcționarea set-urilor Python
- Confirmă stocarea corectă a breakpoint-urilor

**Test 6: Restricție un client per program**
- Simulează atașarea a doi clienți la același program
- Verifică că primul client se atașează cu succes
- Confirmă că al doilea client primește eroare
- Validează mesajul "deja monitorizat de alt client"

### Raportare rezultate

Testele afișează progres detaliat:
- Rezultatul fiecărui test individual
- Valori așteptate vs. găsite
- Mesaje de eroare descriptive
- Scorul final (teste trecute/total: 6)
- Instrucțiuni pentru testarea manuală

## Utilizare

### Pas 1: Testare automată

```bash
python test_simple.py
```

Aceasta va rula toate cele 6 teste și va confirma că aplicația funcționează conform cerinței.

### Pas 2: Testare manuală

**Terminal 1 - Server:**
```bash
python server.py
```

**Terminal 2 - Client 1:**
```bash
python client.py
```

**Terminal 3 - Client 2 (opțional):**
```bash
python client.py
```

### Pas 3: Comenzi de test

În clientul interactiv:

```
> list
> attach program1
> break 1
> run program1
> eval x
> set x 10
> continue
```

## Exemple de utilizare

### Scenario 1: Depanare program simplu

1. Pornește serverul și clientul
2. Listează programele: `list`
3. Atașează la program: `attach program1`
4. Pune breakpoint: `break 1`
5. Rulează programul: `run program1`
6. Când se oprește, evaluează: `eval x`
7. Continuă: `continue`

### Scenario 2: Modificare variabile în timpul execuției

1. Atașează la program și rulează cu breakpoint
2. Când se oprește, verifică variabila: `eval y`
3. Modifică valoarea: `set y 100`
4. Verifică schimbarea: `eval y`
5. Continuă execuția: `continue`

### Scenario 3: Mai mulți clienți cu programe diferite

**Client 1:**
```
> attach program1
> break 0
> run program1
```

**Client 2:**
```
> attach program2
> break 1
> run program2
```

### Scenario 4: Încercare acces simultan (va da eroare)

**Client 1:**
```
> attach program1
```

**Client 2:**
```
> attach program1
# Va primi: "program deja monitorizat de alt client"
```

### Scenario 5: Program customizat

1. Încarcă program nou: `load myprogram "a = 5\nb = a * 2"`
2. Atașează: `attach myprogram`
3. Pune breakpoint: `break 0`
4. Rulează: `run myprogram`
5. Depanează pas cu pas

