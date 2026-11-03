# USSR Army Command

A Hearts of Iron IV mod that adds **32 historically real Soviet commanders** (24 army, 8 navy) who are absent from the available vanilla rosters. All were living in 1936 and reached general or flag rank by 1950.

At game start, a human-controlled Soviet Union receives an event asking whether to recruit them. **Declining is the default/timeout-safe option**; accepting recruits the whole roster immediately. This immediate availability is a gameplay choice — the in-game biographies and [docs/roster.md](docs/roster.md) distinguish each officer's actual 1936 rank from later commands.

## Install

1. Copy the `USSR_Army_Command/` folder and `USSR_Army_Command.mod` into your HOI4 mod directory:
   - Windows: `Documents\Paradox Interactive\Hearts of Iron IV\mod\`
   - Linux: `~/.local/share/Paradox Interactive/Hearts of Iron IV/mod/`
   - macOS: `~/Documents/Paradox Interactive/Hearts of Iron IV/mod/`
2. Enable **USSR Army Command** in the launcher.
3. Start a new game as the Soviet Union (human). The recruitment event fires within the first few hours.

Target: HOI4 **1.19.x** (current Steam release). No DLC is required by the mod itself; it only adds characters, an event, portraits and localisation.

## What's inside

- `common/characters/USAC_soviet_commanders.txt` — 32 characters, not recruited by default.
- `common/on_actions/USAC_on_actions.txt` — human-SOV startup trigger.
- `events/USAC_recruitment.txt` — accept/decline event (decline first).
- `interface/USAC_portraits.gfx` + `gfx/leaders/SOV/*.dds` — colorized real-photo portraits (156×210 large, 53×73 small).
- `localisation/english/USAC_l_english.yml`.

## Roster

Tolbukhin, Bagramyan, Batov, Sokolovsky, Katukov, Rotmistrov, Bogdanov, Kravchenko, Badanov, Krivoshein, Beloborodov, Panfilov, Rodimtsev, Kirponos, Pavlov, Petrov, Maslennikov, Khomenko, Pukhov, Shumilov, Lyudnikov, Glagolev, Zhadov, Kozlov; Isakov, Basistiy, Panteleyev, Andreyev, Kholostyakov, Alafuzov, Kucherov, Kharlamov.

Full biographies, sources and portrait attribution: [docs/roster.md](docs/roster.md), [docs/sources.md](docs/sources.md).

## Validation & testing limits

`python tools/validate_mod.py` performs static checks (braces, IDs, localisation, sprites, traits, event refs, vanilla collision). **The mod has not been run in HOI4 in this environment**; please report any in-game issues.

## License

Code/scripts: MIT (see `LICENSE`). Portraits are third-party historical photographs used with attribution for a non-commercial fan mod; no reuse license is asserted. ChromaGAN weights are not redistributed.
