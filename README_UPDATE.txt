FC NE Trainingsapp v2.4 – GitHub Update

Diese drei Dateien im Hauptverzeichnis des GitHub-Repositories ersetzen:
- index.html
- manifest.webmanifest
- sw.js

Den Ordner icons unverändert lassen.

Der neue Service Worker verwendet einen neuen Cache-Namen und löscht alte fcne-training-* Caches beim Aktivieren.
