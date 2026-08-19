---
instrument: <CANONICAL_SHORT_NAME>
full_name: <Full expanded instrument name>
aliases: [<every string a person might type>, <sub-instrument names>, <bare designators>]
platform: <spacecraft, observatory, or site>
agency: <NASA / ESA / NOAA / NSF / joint>
kind: <coronagraph | EUV imager | magnetograph | spectrometer | in-situ field | in-situ plasma | energetic particle | radio | other>
measures: [<physical quantities, e.g. white-light Thomson-scattered brightness>]
status: <operational | extended | degraded | retired | pre-launch>
operational: <YYYY-MM to YYYY-MM or "present">
homepage: <official instrument or team site>
archive: <primary data portal>
instrument_paper: <first-author YEAR, journal vol, page>
instrument_doi: <https://doi.org/...>
bibtex_key: <key in the project .bib, if one exists>
last_verified: <YYYY-MM-DD>
---

# <CANONICAL_SHORT_NAME> — <Full expanded instrument name>

One paragraph: what it is, what it is for, and the single thing most likely to
be got wrong about it. No numbers here that do not appear sourced below.

Sections that do not apply to this instrument kind are deleted outright, not
left empty. An in-situ magnetometer has no field of view; a coronagraph has no
energy channels. Deleting is correct; a heading with "N/A" under it is noise.

## 0. Start here

The point of this section is that nobody should ever have to find these
documents from scratch again. Every entry is a live link that was checked on
the date in [§11](#11-sources). A link that has rotted is fixed, not deleted;
if the document has genuinely moved, record the new home and note the old one.

### Portals

| Resource | Link | Notes |
|---|---|---|
| Official instrument site | | team's own page, not a mission overview |
| Mission site | | |
| Primary data archive | | where the science files actually live |
| Search / query interface | | VSO, JSOC, SDAC, Fido, web form |
| Quick-look / browse | | daily images, movies, latest frame |
| Data-product documentation | | product definitions, level definitions |
| Analysis software | | official reduction package + any port |
| Event catalog | | if the team or community maintains one |
| Local cache | | path in this vault or an associated repo |

### Tier 1 — instrument team documents

Handbooks, user guides, calibration memos, interface control documents,
release notes. These outrank everything else for design facts.

| Document | Locator | Link |
|---|---|---|
| | chapter / table / section | |

### Tier 2 — refereed instrument papers

The paper to cite, plus the calibration and performance papers that carry the
numbers. Give the DOI, and the BibTeX key if the project has one.

| Citation | Covers | DOI |
|---|---|---|
| | | |

### Tier 3 — mission and archive documentation

Data-product guides, archive layout descriptions, level definitions, file
naming conventions, release notes from the archive rather than the team.

| Document | Covers | Link |
|---|---|---|
| | | |

## 1. Identity and heritage

| Fact | Value | Source |
|---|---|---|
| Full name | | |
| Platform | | |
| Launch / first light | | |
| Principal investigator institution | | |

## 2. What it measures

The observable, stated precisely enough that someone could tell whether two
instruments measure the same thing. Name the physical quantity, the units it is
distributed in, and any normalization. Say what it does *not* measure that a
reader might assume.

| Quantity | Native unit | Distributed unit | Source |
|---|---|---|---|
| | | | |

## 3. Spatial coverage

For remote sensing: field of view, inner and outer edge, occulter geometry,
plate scale, pixel count, vignetting. For in-situ: orbit, heliocentric distance
range, latitude range, sampling volume.

| Property | Value | Source |
|---|---|---|
| Field of view | | |
| Plate scale | | |
| Detector format | | |

## 4. Spectral, energy, or channel response

Filters, passbands, energy bins, polarizer states. One row per selectable
configuration, with the code that appears in filenames or FITS keywords if
there is one, because that is what a reader will actually be holding.

| Code | Name | Range | Source |
|---|---|---|---|
| | | | |

## 5. Cadence and timing

Nominal cadence per observing mode, exposure time, time standard of the
timestamps, and what the timestamp refers to (start, midpoint, end of
exposure). Note any known clock offsets or light-travel corrections already
applied.

| Property | Value | Source |
|---|---|---|
| Nominal cadence | | |
| Time standard | | |
| Timestamp refers to | | |

## 6. Data products and levels

What each level means *for this instrument*, since level numbering is not
standardized across missions. Mark explicitly which levels are actually
distributed and which are user-generated, because that distinction wastes more
time than any other single fact in this file.

| Level | Contents | Distributed? | Source |
|---|---|---|---|
| | | | |

## 7. Calibration and units

How to get from what is served to a physical quantity: calibration factors,
their time dependence, background subtraction, flat fields, vignetting
correction. Name the canonical routine or package, and any port of it.

## 8. Coordinates, pointing, and conventions

Coordinate frame, sign conventions, roll, position-angle zero point, whether
North is up in the served product, and any keyword whose meaning departs from
the FITS standard.

## 9. Gotchas

The failure modes that cost real time. Each one gets a sentence on the symptom
and a sentence on the fix. This section earns the file its keep.

## 10. Citing and acknowledging

What the team asks for, which is not always what is obvious. Record the exact
acknowledgement string if one is prescribed, the data-use or rules-of-the-road
policy, and whether co-authorship or advance notice is expected for particular
data products.

| Item | Value | Source |
|---|---|---|
| Cite this paper | | |
| Required acknowledgement | | |
| Data-use policy | | |

## 11. Sources

Every numbered source resolves to an exact locator plus a clickable link. A
source that is only a site root is not a source; find the page, table, or
section that actually carries the number.

Evidence type follows the standard markers: **[Observed]** (measured or read
directly off the data), **[Derived]**, **[Model-dependent]**, **[Hypothesis]**,
**[Unknown]**.

#### S1
<Author or organization>, *<Document title>*, <exact locator: chapter, section,
table, page, or figure number>.
- Page: <https://...>
- Exact item: <https://...>
- Retrieved <YYYY-MM-DD>. Type: **[Observed]**. Tier: <1 team document /
  2 instrument paper / 3 mission or archive doc / 4 data headers /
  5 secondary literature / 6 web summary>.

#### S2
...

## 12. Unverified and open

Anything believed but not yet sourced, carried explicitly rather than dropped.
Nothing here may be quoted into a manuscript without first being resolved.

- `[VERIFY]` <claim> — tried <where>, not found. Next place to look: <where>.
