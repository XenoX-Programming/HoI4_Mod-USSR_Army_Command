# Sources and portrait attribution

This mod uses **real historical photographs** that were cropped, colorized with a non-generative chroma-prediction network (ChromaGAN), contrast/vignette adjusted, and exported as DDS. No replacement faces were generated.

## Historical sources

- Generals.dk — Soviet officer biographies and promotion dates: https://generals.dk/
- Warheroes.ru — Ivan Isakov: https://warheroes.ru/hero/hero.asp?Hero_id=1466
- Wikipedia / RUWiki biographies for naval officers (Isakov, Basistiy, Panteleyev, Andreyev, Kholostyakov, Alafuzov, Kucherov, Kharlamov) and Sokolovsky.
- Proza.ru (Oleg Kaminsky) — Basistiy and Alafuzov biographies.
- Military.wikireading.ru (N. Skritsky, *Flagmany Pobedy*) — Kucherov, Basistiy.
- Russian Ministry of Defence encyclopedia — Sokolovsky: https://encyclopedia.mil.ru/encyclopedia/history/more.htm?id=12134159@cmsArticle

Per-commander source links are in [roster.md](roster.md).

## Portrait sources

Portraits were located via web image search and downloaded from the pages below. Copyright remains with the original photographers/archives/publishers; inclusion here is for a non-commercial fan mod with attribution. No reuse license is asserted.

| Commander | Portrait source page |
|---|---|
| Tolbukhin, Batov, Katukov, Rotmistrov, Bogdanov, Kravchenko, Badanov, Beloborodov, Panfilov, Rodimtsev, Kirponos, Pavlov, Petrov, Maslennikov, Pukhov, Shumilov, Glagolev, Zhadov, Kozlov, Kholostyakov, Kharlamov | https://generals.dk/ (individual general pages) |
| Bagramyan | https://100.histrf.ru/ |
| Sokolovsky | https://nasledie-sluck.by/ru/Nahodki_zagadki/4876/ |
| Krivoshein | https://cyclowiki.org/wiki/Семён_Моисеевич_Кривошеин |
| Khomenko, Zhadov, Kucherov | https://biografiaru.wordpress.com/ |
| Lyudnikov | https://prussia39.ru/fame/index.php?fid=139 |
| Kozlov | https://peoples.ru/military/commander/dmitriy_kozlov |
| Isakov | https://warheroes.ru/hero/hero.asp?Hero_id=1466 |
| Basistiy | https://ussr-cccp.moy.su/publ/grazhdane_sssr/admiraly_sssr/basistyj_nikolaj_efremovich_sovetskij_voenachalnik_admiral_sssr_22_05_1898_20_10_1971/379-1-0-2803 |
| Panteleyev | https://w.people-archive.ru/character/panteleev-uriy-aleksandrovich |
| Andreyev | https://ru.ruwiki.ru/wiki/Андреев,_Владимир_Александрович_(адмирал) |
| Alafuzov | https://ru.wikipedia.org/wiki/Алафузов,_Владимир_Антонович |

## Colorization tooling

- ChromaGAN weights/code: ColorfulSoft, *StyleTransfer-Colorization-SuperResolution* (MIT). The network predicts only the two chroma channels from the original luminance; it does not synthesize faces. Weights are development assets and are **not** redistributed in this repository.
- Conversion/inference scripts: `tools/build_chromagan_onnx.py`, `tools/process_portraits.py`.

## Vanilla roster audit

- Base-game SOV characters: `prisle123/hoi4-archive` @ `8425c11f` (labelled 1.19.4), file `common/characters/SOV.txt`, SHA-256 `28c16c68170784d6ff22223cc577a637bdcf8c851cbaba9ebfa10f012ad30098`.
- No Step Back-era SOV characters: `cbrzeczysz/hoi4-history` (1.14.1) and two additional mirrors.
- All 32 added character IDs were checked against these baselines with exact-token matching; none collide. Existing advisor-only characters (Tributs, Yumashev, Kuznetsov) were deliberately excluded to avoid duplicate tokens.
- Limitation: a current 1.19 DLC-path character mirror was not obtainable; the audit is against the available base + NSB-era baselines.
