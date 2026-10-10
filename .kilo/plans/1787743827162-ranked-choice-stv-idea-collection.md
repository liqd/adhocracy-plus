# Ranked-Choice (STV) im idea-collection-Flow

## Ziel
Ein neues Abstimmungsmodul "ranked-choice": Teilnehmende sammeln in einer ersten
Phase Ideen, danach wird in einer zweiten Rangphase über **alle** Ideen per
**STV (Single Transferable Vote, mehrere Gewinner)** abgestimmt. Teilnehmende
ranken nur ihre Favoriten (partielle Ballots); nicht gewählte Ideen gelten als
letzte Wahl (= Exhaustion, sobald alle gewählten Kandidaten eliminiert sind).

## Entscheidungen (mit Nutzer abgestimmt)
1. **Umfang:** Alle Ideen der Sammlung werden gerankt (kein Kuratieren/Top-N-Subset).
2. **Blueprint:** Neuer Blueprint `ranked-choice` (`CollectPhase` + `RankPhase`).
   Der bestehende `idea-collection` bleibt unverändert (kein Risiko für Live-Projekte).
3. **Verfahren:** STV, ermittelt **mehrere Gewinner**. Anzahl Gewinner über
   Modul-/Blueprint-Konstante konfigurierbar (Default 3).
4. **Ballot:** Partielle Ballots erlaubt (Minimum 1 gerankte Idee, keine
   Vollständigkeitspflicht). Nicht gewählte Ideen sind letzte Wahl =>
   Ballot wird "exhausted", sobald alle gerankten Kandidaten eliminiert sind.

## Defaults / offene Optionen
- Ein Ballot pro Nutzer pro Modul, bis Phasenende **editierbar** (Analogie a4-Poll `Vote`).
- **Ergebnisse bis Phasenende verborgen** (Analogie a4-Poll `hide_results_until_finished`).
- **Deterministisches Tie-Breaking** im Tally: erst Anzahl gerankter Erstwahlen,
  dann positive Rating-Anzahl, dann Erstellungsdatum. (offen: final definieren)
- Anzahl der zu wählenden Gewinner: Default 3, als Konstante im Tally/Modul.

## Architektur
Neue App `apps/ranked_choice` (label `a4_candy_ranked_choice`). Kandidaten sind
die dynamischen `apps.ideas.Idea`-Objekte aus der Sammelphase des Blueprints.
Das Ballot-Modell spiegelt das a4-Poll-Muster (`Vote`/`Answer`), aber generisch
auf `Idea` via ContentType/GenericForeignKey.

## Datenmodell
- `RankedBallot` (a4 `GeneratedContentModel`/`UserGeneratedContentModel`):
  - `module` FK → `a4modules.Module`, related_name `ranked_ballots`
  - `creator` (von Basisklasse) + `created`/`modified`
  - Eindeutigkeit: 1 Ballot pro (module, creator) via `validators.single_vote_per_user`.
  - Properties `project`/`module` delegieren (für Rule-Per-Check wie a4-Poll).
- `RankedChoice`:
  - `ballot` FK → `RankedBallot`, related_name `choices`
  - `content_type` FK + `object_pk` + `content_object` (GenericForeignKey) → `Idea`
  - `rank` PositiveSmallIntegerField (1 = höchste Präferenz)
  - `Meta.ordering = ["rank", "id"]`, `unique_together = ("ballot", "content_type", "object_pk")`
  - Validatoren: `rank >= 1`, Höchst-Rang, keine Duplikate, nur `Idea`-Payloads.

## Phase
`RankPhase(phases.PhaseContent)` in `apps/ranked_choice/phases.py`:
- `app = a4_candy_ranked_choice`, `phase = "rank"`
- `view = ...` (Modul-View, zeigt Abstimmungs-/Ergebnis-UI)
- `name`/`description`/`module_name` = "ranked-choice"
- `features = {"rank": (ideas.models.Idea,)}`
- `phases.content.register(RankPhase())`

## Regeln/Permissions
In `apps/ranked_choice/rules.py`:
- Eigener Predicate `phase_allows_rank` (analog zu a4 `phase_allows_rate`,
  prüft aktive Phase → `has_feature_active(module, Idea, "rank")`).
- `rules.add_perm("a4_candy_ranked_choice.rank_idea", is_allowed_rank_idea)`
  mit dem Muster von a4 `is_allowed_rate_item` (Moderator-Bypass | Mitglied &
  live & Phase erlaubt Rängen).

## API (DRF ViewSet)
`RankedBallotViewSet` (ModuleMixin; Create/Retrieve/Update/Destroy/List):
- `get_queryset` filtert auf `module`, prefetcht `choices__content_object`.
- Schreiben nur während aktiver Rangphase erlaubt (Serializer/Permission).
- `get_permission_object` = module; Permission prüft `rank_idea` u. aktiv.
- Serializer liest `choices` als geordnete Liste (pk-Reihenfolge), validiert
  Ganzzahligkeit/Duplikate/Minimum.

## Views/URLs/Templates
- `module-detail`-View für die Rangphase (Server-renderte Platzhalter-Div mit
  `data-attributes` für das React-Widget) plus Ergebnisansicht (nach Phasenende,
  Sortierung nach STV-Position, nur wenn `hide_results` erfüllt).
- `urls.py` für App-Routen, Einbindung über `module.urls` im Projekt-URLconf.

## Frontend
- React 18-Widget (analog `apps/polls/assets/react_polls.tsx`): `apps/ranked_choice/assets/js/`
  mit `ReactWidgetInit('a4', 'ranked_choice', ...)`; Drag-/Auf/Ab-Ranking-Liste
  mit Reihenfolge-Speichern via **API**.
- `webpack.common.cjs`: neuer `entry`-Key `ranked_choice` (`dependOn: 'adhocracy4'`),
  resolve-Module um `./apps/ranked_choice/assets/js` ergänzen.
- SCSS als `_ranked_choice.scss`-Partial, importiert in `style.scss`.

## STV-Tally
Pure-Python-Modul `apps/ranked_choice/tally.py`:
- `tally(ballots: List[List[int]], candidates: List[int], num_winners: int) -> List[int]`
  (Standard-Hare-Quota + Abstufung der Stimmgewichte; partielle Ballots =>
  exhausted ballots zählen nicht in Nenner; gebunden: definierte Tie-Break-Reihenfolge).
- Ergebnis: geordnete Liste der Sieger (höchste Priorität zuerst).
- Unit-Tests: einfacher Mehrheitssieger, partielles Transferverhalten,
  Exhaustion, Tie-Break, `num_winners` größer als Kandidaten.

## Export + Dashboard
- `apps/ranked_choice/exports.py`: Basis-Export der Ballots
  (nutzergenerierte Inhalte, Idea-Referenznummer, Ränge).
- `DashboardExportView`-Wrapper in `views.py`.
- `apps/ranked_choice/dashboard.py`: `ExportRankedChoiceComponent` via
  `components.register_module(...)`, gated auf Blueprint `"ranked-choice"`.

## Blueprint
in `apps/dashboard/blueprints.py` ergänzen:
`("ranked-choice", ProjectBlueprint(CollectPhase + RankPhase, type="RC", ...))`
(type-Konstante "RC" eindeutig; ggf. Icon wiederverwenden).

## Konfiguration
- `INSTALLED_APPS` += `apps.ranked_choice` (Gruppe "Apps defining phases",
  `adhocracy-plus/config/settings/base.py` ~Zeile 127–137).

## Rand-/Qualitätspunkte
- Übersetzungen: neue Strings in `locale/` (DE/EN + weitere vorhandene Sprachen,
  `makemessages`/`compilemessages`).
- `CHANGELOG.md`: Eintrag unter "Added/Unreleased".
- Lint/Typcheck: `venv/bin/python -m compileall` bzw. Projekt-Flakes; JS via `make watch`.
- Migrationen anlegen; bestehende Tests (`apps/ideas`, `apps/polls`) müssen grün bleiben.

## Risiken / Edge Cases
- Gleichstand im Tally → deterministisches Tie-Breaking fixieren.
- Leere/ungültige Ballots → Validierung verhindert Speichern (min. 1 Rang,
  eindeutige Ränge, nur Idea-PKs).
- Viele Ideen → Performance: prefetch `choices__content_object`, DB-Index auf
  (module), (ballot), (content_type, object_pk).
- Ergebnis-Fairness: Ergebnisse bis Phasenende verborgen (Default).