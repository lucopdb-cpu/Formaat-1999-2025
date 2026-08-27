# Formaat 1999–2025

Publiek archief van Stichting Formaat, Werkplaats voor Participatief Drama (Rotterdam, 1999–2025): een kwart eeuw forumtheater, beeldentheater en legislatief theater in onderwijs, zorg, wijk en internationale uitwisseling. Zusterproject van het [Arsenaal van de joker](https://lucopdb-cpu.github.io/Theatre-of-the-Oppressed/).

## Opbouw

| Map | Inhoud |
|---|---|
| `data/projecten.json` | de inventaris: 484 activiteiten met seizoen, beschrijving, cijfers, status en bron |
| `data/projectgroepen.json` | 100 projectlijnen: id, spoor, looptijd, thema's, of er een kaart is |
| `data/sporen.json` | de zes sporen van de tijdlijn (naam, kleur, volgorde) |
| `data/route.json` | Virgilio's route: haltes, vragen, links naar het Arsenaal |
| `data/media.json` | video's (YouTube), fotoseries, publicaties en persitems per projectlijn |
| `data/site.json`, `data/over.md` | teksten van de site, licentie, colofon |
| `kaarten/*.md` | projectkaarten in markdown met YAML-kop |
| `tools/build.py`, `tools/site.css` | generator en stijl |
| `docs/` | de gegenereerde site (GitHub Pages) |

## Bewerken

- **Een kaart aanpassen**: bewerk `kaarten/<id>.md`. De kop (tussen `---`) bevat titel, periode, plaatsen, partners, thema's en cijfers; daaronder de zes secties. Zet `status: definitief` als de kaart is gecontroleerd.
- **Een spoor of projectlijn verplaatsen**: wijzig `spoor` in `data/projectgroepen.json`. Een nieuw spoor: voeg het toe in `data/sporen.json`.
- **Bronnen op een kaart**: alleen openbare bronnen (jaarverslagen, publicaties, pers, video). Interne stukken die als informatiebron dienden staan buiten de repo, in het Formaat-archief (map _Publicatie/bronnen-intern op de archiefschijf).
- **De route wijzigen**: `data/route.json` (volgorde, vraag, Arsenaal-link).
- **Beeld toevoegen**: zet webversies (max. 1600 px) in `docs/beeld/` en vul in `data/media.json` bij de fotoserie het veld `gekozen` met `{"bestand": "...", "bijschrift": "...", "fotograaf": "...", "alt": "..."}`. Alleen beeld dat aan de toestemmingsregel voldoet (zie `data/over.md`).
- **Een document openbaar maken**: zet in `data/media.json` bij de publicatie `openbaar: true` en `url` (bijvoorbeeld een Zenodo-DOI).

Daarna: `python3 tools/build.py` (vereist `pip install markdown pyyaml`). GitHub Pages serveert de map `docs/`.

## Licentie

Nog vast te stellen. Voorstel: teksten en eigen beeld CC BY-SA 4.0, code MIT. Foto's van deelnemers en documenten van derden vallen buiten die licentie tenzij anders vermeld.
