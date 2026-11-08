# kvpslavi.cz

Microsite k 35. narozeninám Klubu vozíčkářů Petýrkova.

- `site/` – hotový statický web (nasazuje se na Vercel, root directory = `site`)
  - `/` hlavní stránka pro firmy
  - `/mei` osobní pozvánka pro MEI Property Services
  - `/siemens` osobní pozvánka pro Siemens
- `build.py` – převodník z návrhových souborů (Claude Design) do `site/`

Texty se upravují přímo v `site/**/index.html`.
