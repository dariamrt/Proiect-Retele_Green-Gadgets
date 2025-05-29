# Depanarea programelor la distanță

- Server-ul execută programe constând în instrucțiuni aritmetice cu atribuirea rezultatului într-o variabilă, instrucțiuni ce pot include referiri la valorile altor variabile, constante numerice, operatori aritmetici și paranteze, fiecare atribuire constituind o instrucțiune ce poate fi depanată de la distanță.

- Clienții se conectează la server și înregistrează o serie de puncte de oprire într-un program, identificate prin numele programului și linia fiecărui punct de oprire a execuției.

- Server-ul acceptă un singur client care poate întrerupe execuția unui program la un moment dat.

- Clienții se pot atașa la un program, pot adăuga sau elimina puncte de oprire, sau se pot detașa de la depanarea execuției unui program.

- Aplicația server lansează în execuție mai multe programe în paralel.

- Pe durata execuției unui program, clientul care-i depanează execuția nu mai poate adăuga sau elimina puncte de oprire.

- În momentul în care server-ul ajunge, în timpul execuției unui program, la un punct interceptat de un client, acesta va aștepta din partea clientului comenzi pentru:
  - evaluarea unei variabile după nume,
  - setarea valorii acesteia,
  - continuarea până la următorul punct de întrerupere a execuției, după primirea din partea clientului a unei comenzi în acest sens.

- La încheierea execuției programului depanat, server-ul va notifica clientul care-l monitorizează în acest sens.