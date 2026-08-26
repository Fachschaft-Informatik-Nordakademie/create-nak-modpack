# CREATE@NAK-INF

Create-Modpack der Fachschaft Informatik (NAK) — NeoForge 1.21.1, 42 Mods rund um
[Create](https://modrinth.com/mod/create) (Steam'n'Rails, Sophisticated Storage/Backpacks + Create-
Integrationen, Waystones, JEI, Sodium/Lithium/Entity Culling für Performance u.v.m.).

Ausgangspunkt war die Modrinth-Collection
[CREATE@NAK-INF](https://modrinth.com/collection/6nKFrYG6). Vier ihrer Mods gab es nur bis MC 1.20.1
(Create: Structures, Extended Cogwheels, Create Utilities, Steam 'n' Rails) — dafür wurden aktiv
gepflegte 1.21.1/NeoForge-Ersatzprojekte eingesetzt (Details in [MODLIST.md](MODLIST.md)). Fehlende
Pflichtabhängigkeiten (Balm, DragonLib, Sable, KotlinLangForge, Create: Dragons Plus) sind ebenfalls
im Pack enthalten.

## Server

- **NeoForge 1.21.1**, Build 21.1.248
- Adresse: `94.130.19.169:25571`

## Installation

### Option A — Prism Launcher / Modrinth App / ATLauncher (empfohlen)

1. `CREATE-NAK-INF.mrpack` aus dem [neuesten Release](../../releases/latest) herunterladen
2. Im Launcher: **Modpack importieren** → die `.mrpack`-Datei auswählen
3. Der Launcher lädt NeoForge + alle 41 Client-Mods automatisch von Modrinth

### Option B — Lunar Client / manueller Mods-Ordner

Lunar Client unterstützt keinen `.mrpack`-Import, aber eigene Forge/NeoForge-Mods über ein
Custom-Profil:

1. In Lunar Client ein **Forge/NeoForge-1.21.1-Profil** anlegen (NeoForge muss vorher separat
   installiert sein, z. B. via [neoforged.net](https://neoforged.net), Version 21.1.248)
2. `CREATE-NAK-INF-mods-manual.zip` aus dem [neuesten Release](../../releases/latest) herunterladen
   und den kompletten Inhalt in den Mods-Ordner des Profils legen
3. Genaue Schritte je Lunar-Client-Version siehe `LIESMICH.txt` im Zip

### Option C — Manuell (jeder andere NeoForge-Client)

`CREATE-NAK-INF-mods-manual.zip` entpacken → Inhalt in `<Minecraft-Ordner>/mods/` (bei einer separaten
NeoForge-1.21.1-Installation).

## Modliste

Vollständige Liste inkl. Versionen: [MODLIST.md](MODLIST.md)

## Auto-Build

`.github/workflows/build-modpack.yml` löst `mods.txt` (+ alle Pflichtabhängigkeiten) jede Woche
sowie bei jeder Änderung an `mods.txt`/`build_modpack.py` automatisch neu gegen die Modrinth-API auf
und aktualisiert `MODLIST.md`. Ein neues Release mit frischem `.mrpack` + `.zip` erzeugen: Tab
**Actions** → *Build modpack* → **Run workflow**, Versionsnummer eingeben.

## Lizenz / Credits

Alle Mods gehören ihren jeweiligen Autoren (Modrinth-Links in MODLIST.md). Dieses Repo enthält keine
Mod-Jars im Git-Verlauf, nur die Release-Assets (`.mrpack`/`.zip`) und Metadaten.
