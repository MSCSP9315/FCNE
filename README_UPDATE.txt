FC NE TRAININGSAPP – UPDATE v2.14

Auf GitHub ersetzen:
- index.html
- manifest.webmanifest
- sw.js

Den Ordner icons unverändert lassen.

WICHTIG:
Die bereits auf dem iPhone installierte App muss normalerweise NICHT neu installiert werden.
Beim nächsten Start prüft der Service Worker auf eine neue Version. Die Navigation wird netzwerk-first geladen, damit die aktuelle GitHub-Version bevorzugt wird.

v2.14:
- iPhone/PWA-Kopfbereich mit zusätzlichem Sicherheitsabstand
- Manifest im HTML eingebunden
- Apple-PWA-Metadaten ergänzt
- Service Worker wird automatisch registriert und aktualisiert
- Cache-Version v2.14

Neu in v2.14: Easy2Coach-Katalog wird lokal in IndexedDB gespeichert. Automatische Hintergrund-Synchronisation blockiert den Generator nicht mehr; Aktualisierung manuell über "Datenbank aktualisieren".
