# Schlemmercacher Archiv

Statisch archivierter WordPress-Blog von schlemmercacher.de.

## Struktur

- `build_site.py` — Extrahiert alle Posts via WordPress-REST-API und generiert statische HTML-Seiten
- `_site/` — Generierte Ausgabe (wird von GitHub Pages ausgespielt)
- `.github/workflows/deploy.yml` — GitHub Action für automatisches Deployment

## Lokales Testen

```bash
python3 build_site.py
cd _site && python3 -m http.server 8000
```

## Deployment

1. Repository auf GitHub erstellen und Code pushen.
2. Im Repository unter **Settings → Pages** als Build source "GitHub Actions" wählen.
3. Bei jedem Push auf `main` wird die Seite neu gebaut und deployed.

Optional: Für Custom Domain `schlemmercacher.de` eine `CNAME`-Datei im `_site`-Ordner anlegen (wird beim Build nicht überschrieben) und DNS-Eintrag bei Cloudflare setzen.
