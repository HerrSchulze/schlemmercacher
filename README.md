# Schlemmercacher Archiv

Statisch archivierter WordPress-Blog von schlemmercacher.de, gehostet auf Cloudflare Pages.

## Struktur

- `build_site.py` — Extrahiert alle Posts via WordPress-REST-API und generiert statische HTML-Seiten in `_site/`
- `_site/` — Generierte Ausgabe (wird auf Cloudflare Pages deployed)
- `wrangler.toml` — Cloudflare Pages Konfiguration
- `.github/workflows/deploy.yml` — GitHub Action für automatisches Deployment bei Push auf `main`

## Lokales Deploy

Voraussetzung: [Node.js](https://nodejs.org/) und Wrangler CLI

```bash
npm install -g wrangler
wrangler login
cd /home/peter/workspace/schlemmercacher
python3 build_site.py
wrangler pages deploy _site --project-name schlemmercacher
```

## Automatisches Deploy via GitHub Actions

1. Im Cloudflare Dashboard ein API-Token erstellen mit der Berechtigung `Cloudflare Pages:Edit`
2. Im GitHub-Repo unter **Settings → Secrets and variables → Actions** den Secret `CLOUDFLARE_API_TOKEN` anlegen
3. Bei jedem Push auf `main` baut die Action die Seite und deployed sie auf Cloudflare Pages

Die Seite ist dann unter der von Cloudflare vergebenen URL (oder deiner Custom Domain `schlemmercacher.de`) erreichbar.
