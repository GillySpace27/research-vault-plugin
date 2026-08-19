---
name: vault-instruments
description: Verified reference files for scientific instruments, telescopes, spacecraft payloads, and detectors, living in the vault's `instruments/` directory. Use this skill WHENEVER an instrument is named in conversation, in a file being read, in data being analyzed, or in prose being drafted — for example LASCO, AIA, PUNCH, SUVI, K-Cor, ASPIICS, CCOR, EUVI, SoloHI, WISPR, Metis, SWAP, HMI, EIS, SPICE, MAG, SWEAP, or any other instrument, filter, bandpass, field of view, cadence, data level, or calibration factor. Use it to look up an instrument fact, to check a claim someone (including you) just made against the vault's sourced record, to surface disagreements between the two, and to add newly verified instrument facts with full provenance. Every number in these files carries a link to the exact page, table, or header it came from.
---

# Vault instruments

`instruments/` is the vault's sourced record of the hardware. It exists because
instrument facts are the ones most often half-remembered, most often quoted
into manuscripts, and most expensive to get wrong. A number in this directory
without a working link to its exact source is a bug in the directory.

Location: `$RESEARCH_VAULT_DIR/instruments/`. Index and alias table:
`instruments/README.md`. Template: `_templates/instrument.md`.

## The check

**Any time an instrument is named, check the vault before you answer.** Not
only when asked to. Naming includes: the user mentions it, a file you read
mentions it, you are about to write it into a draft, or you are about to state
a number about it.

1. **Resolve the name.** Read `instruments/README.md` once per session and hold
   the alias table. Aliases are the point: "C2", "LASCO C2", and "LASCO-C2" all
   resolve to `instruments/LASCO.md`. Sub-instruments live in their parent's
   file unless they have genuinely separate optics, teams, and data products.
2. **Read the file** if one resolved.
3. **Compare** every claim in play against it, in either direction: a claim from
   the user, from a paper, from a data header, or from your own memory.
4. **Act on the comparison** per the table below.

| Outcome | What to do |
|---|---|
| Claim agrees with the file | Proceed. Say nothing. Do not narrate a successful check; it is noise. |
| Claim **disagrees** with the file | **Stop and surface it before continuing.** See below. |
| Claim is not covered by the file | Answer from your source, name that source, and offer to add it. Add it only once verified. |
| No file exists for the instrument | Answer normally. Offer to create one from the template if the instrument is recurring rather than incidental. |

## Surfacing a disagreement

A disagreement is never resolved silently, and the vault does not automatically
win. Present it and let the evidence decide:

```
Disagreement on <instrument> <property>.
  Vault:   <value>  — <source S#, locator>  (recorded <date>)
  Claim:   <value>  — <where it came from>
  Better-sourced: <which, and why under the precedence order>
```

Then do exactly one of:

- **Claim wins.** Correct the file, bump `last_verified`, and keep the old value
  in `## 12. Unverified and open` with a line on why it was wrong. Superseded
  values are kept, not deleted; a value that was wrong once tends to come back.
- **Vault wins.** Tell the user which of their numbers to fix and where.
- **Neither is decisive.** Record both in `## 12`, marked `[VERIFY]`, and say
  plainly that it is unresolved. Do not pick one to make the prose flow.

Never edit a value in place without showing the old value, the new value, and
both sources.

## Section 0 is the point of the file

Every instrument file opens with a **Start here** section: the portals and the
canonical documents, tiered. Nobody should ever have to find these from scratch
twice. Fill it first, before any physical parameter, because a file with only
§0 is already useful and a file with parameters but no §0 strands the next
reader.

- **Portals**: official instrument site (the team's own page, not a mission
  overview), mission site, primary archive, search interface, quick-look,
  data-product docs, analysis software, event catalog, local cache path.
- **Tier 1**: team documents. Handbooks, user guides, calibration memos.
- **Tier 2**: refereed instrument papers, with DOIs. Name which one is *the*
  paper to cite; there is usually one instrument paper and several calibration
  papers, and citing a calibration paper as the instrument paper is a common
  error.
- **Tier 3**: mission and archive documentation, and dataset DOIs.

**Verify DOIs by resolving them, never by recall.** Content negotiation returns
the full citation and proves existence in one step:

```bash
curl -sL -H "Accept: text/x-bibliography; style=apa" "https://doi.org/<DOI>"
```

For preprints, the arXiv API's `doi` and `journal_ref` fields settle whether a
paper has been refereed yet, and give the real author order. Search engines
routinely surface an older design paper above the actual instrument paper, and
first authors get misremembered.

Record the publication year the journal gives, not the one everybody says.

## Provenance rules

These are the reason the directory is worth maintaining.

1. **Every factual row carries a source key.** Format: a link to an anchor in
   the same file's `## 11. Sources` section, e.g. `[S2](#s2)`.
2. **A source is a locator, not a site.** "The LASCO handbook" is not a source.
   "LASCO Handbook Ch. 6, Table 6-1, at
   `https://lasco-www.nrl.navy.mil/handbook/tab6-1.gif`" is. Link the page that
   carries the number, and, when the number lives in a table, figure, or PDF
   page, link that item directly as well.
3. **Both links.** The human-readable page *and* the exact item, when they
   differ. A reader who lands on the item alone loses its context; a reader who
   lands on the chapter alone has to hunt.
4. **Every source carries a retrieval date and an evidence type** using the
   standard markers ([Observed], [Derived], [Model-dependent], [Hypothesis],
   [Unknown]).
5. **No source, no row.** A value you believe but cannot locate goes in
   `## 12. Unverified and open` marked `[VERIFY]`, with a note on where you
   already looked and where to look next. It does not go in a table.
6. **Numbers read off real data files are first-class sources**, and are
   `[Observed]`. Their locator is the file, the keyword, and the command that
   reads it, e.g. `cache/24024565.fts`, keyword `FILTER`, via
   `astropy.io.fits.getheader`. Say which archive the file came from.
7. **Design facts and frame facts are different claims.** "C2's wheel has an
   Orange filter at 540-640 nm" is a design fact and needs the handbook. "Our
   02:00:31 frame was taken through Orange" is a frame fact and needs the
   header. Do not let one stand in for the other.

### Source precedence

When two sources conflict, the earlier tier wins unless there is a stated
reason otherwise:

1. Instrument handbook or calibration document from the instrument team
2. The refereed instrument paper
3. Mission or data-product documentation from the archive
4. FITS headers or metadata of the actual data (authoritative for frame facts,
   tier 1 for those, and outranks everything for "what did this file do")
5. Refereed secondary literature using the instrument
6. Web summaries, wikis, search-result snippets

Tier 6 values are recorded as `[VERIFY]` in `## 12`, never as table rows. A
figure quoted from a search snippet has burned us before: a plausible effective
bandpass got mistaken for an instrument spec.

## Adding an instrument

Copy `_templates/instrument.md`, fill only the sections that apply, delete the
rest outright, and add a row to the alias table in `instruments/README.md`.
Partial is fine and expected; an instrument file with three sourced facts beats
no file. Leave unfilled sections out rather than stubbed, so the file never
implies coverage it does not have.

Name the file for the canonical short name in the community's own casing:
`LASCO.md`, `AIA.md`, `PUNCH.md`, `K-Cor.md`. One file per instrument, with
sub-instruments as sections inside it.

## Checking the directory

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lint_instruments.py" "$RESEARCH_VAULT_DIR"
```

Verifies that every `[S#]` reference resolves to a source block, that no source
is defined and never cited, that each carries a retrieval date and an evidence
type, and that table rows in sourced tables actually cite something. Add
`--urls` to check that every link still answers, which is how link rot gets
caught before a referee catches it. Run it after editing any instrument file.

## Keeping it honest

- **`last_verified` means checked, not written.** Bump it only when a source was
  actually re-opened.
- **Retired instruments stay.** Archival analysis is most of the work; deleting
  a retired instrument's file deletes the reason its quirks exist.
- **The absence rule.** Before writing that an instrument lacks a capability, a
  filter, or a data level, state where you searched. An absence claim needs a
  search wider than the file you are editing. When an absence is *predicted* by
  a source, say so, because that converts a gap into a confirmation.
- **Cross-link, don't duplicate.** Facts that live in another instrument's file
  are linked, e.g. `[[PUNCH#3. Spatial coverage]]`. Two copies drift.
- **Not the same as `memory/`.** `memory/` holds people, projects, and
  shorthand: what the user means. `instruments/` holds sourced external facts
  about hardware: what is true regardless of the user. Route accordingly.
