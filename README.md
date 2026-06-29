# Universities Database

A community-maintained database of university email domains that any app can use to verify academic email addresses from institutions around the world.

## Background

This project started as a response to [JetBrains' swot repository](https://github.com/JetBrains/swot) stopping acceptance of new Iranian university domains, citing sanctions and export control compliance. This excluded Iranian students from academic verification features on any platform that depends on swot.

### A note on sanctions

JetBrains' position may not be legally required. OFAC's General License D-2, now codified as [31 CFR § 560.540 of the Iranian Transactions and Sanctions Regulations (ITSR)](https://www.ecfr.gov/current/title-31/subtitle-B/chapter-V/part-560#560.540), explicitly authorizes the export of software and services related to education and personal communications to Iran. This includes collaboration platforms, e-learning platforms, cloud-based services, and user authentication services. OFAC has confirmed it covers educational technology that allows students to access course materials, receive grades, and participate in discussions.

Providing academic email verification for Iranian students appears to fall within this authorization. This was raised with JetBrains in [a comment on the relevant pull request](https://github.com/JetBrains/swot/pull/40330#issuecomment-4822220928), but the request was still rejected.

This repository started so that Iranian students have the same access to academic verification as students anywhere else in the world — and has since grown into a general-purpose global universities database open to contributions from any country.

## Data

- **148 universities**, **149 email domains** (seeded from swot with Iranian universities, now expanding globally)
- Source of truth: [`universities/`](./universities/) — one JSON file per country (e.g. `universities/IR.json`)
- Derived formats regenerated automatically by CI on every merge

> **v2 breaking change:** `name_fa` has been renamed to `name_local`, and `country` (ISO 3166-1 alpha-2) is now a required field. Update your key lookups accordingly.

## How to Integrate

### Option 1: JSON (recommended for new integrations)

Fetch the per-country files from [`universities/`](./universities/) directly from the GitHub raw URL (e.g. `universities/IR.json` for Iran, `universities/US.json` for the US). Each entry:

```json
{
  "name": "University of Tehran",
  "name_local": "دانشگاه تهران",
  "country": "IR",
  "domains": ["ut.ac.ir"],
  "type": "public",
  "city": "Tehran",
  "website": "https://ut.ac.ir"
}
```

To check if an email is from a university in the database, fetch whichever country files you need or all of them:

```python
import json, urllib.request

def load_country(code):
    url = f"https://raw.githubusercontent.com/matinzd/iran-universities-database/main/universities/{code}.json"
    return json.loads(urllib.request.urlopen(url).read())["universities"]

# Or load all countries by fetching the directory listing via the GitHub API
universities = load_country("IR") + load_country("US")  # etc.
all_domains = {d for u in universities for d in u["domains"]}

def is_university_email(email):
    domain = email.split("@")[-1].lower()
    return domain in all_domains
```

### Option 2: Swot-compatible drop-in

The `domains/` directory mirrors swot's exact file structure. Apps already consuming swot can point at this repo instead with no code changes. Global entries appear under their respective country TLD directories.

```
domains/
  ir/
    ac/
      ut.txt        → "University of Tehran"
      sharif.txt    → "Sharif University of Technology"
      ...
    iau.txt         → "Islamic Azad University"
  edu/
    mit.txt         → "Massachusetts Institute of Technology"
  uk/
    ac/
      ox.txt        → "University of Oxford"
```

### Option 3: Flat domain list

[`domains.txt`](./domains.txt) contains one domain per line, suitable for simple grep/lookup or loading into a set.

## University Types

These types originated from the Iranian university system and remain valid for global entries where applicable. New types can be proposed via PR.

| Value             | Description                                      |
| ----------------- | ------------------------------------------------ |
| `public`          | Government-funded public university              |
| `private`         | Private non-governmental university              |
| `islamic-azad`    | Islamic Azad University (branch)                 |
| `medical`         | University of Medical Sciences                   |
| `distance`        | Distance learning institution                    |
| `applied-science` | University of Applied Science and Technology     |

## Contributing

To add a missing university or correct existing data, edit the relevant file in [`universities/`](./universities/) (e.g. `universities/IR.json` for Iran, `universities/US.json` for the US) and open a pull request. If no file exists for the country yet, create one. CI will validate the schema and check for duplicate domains automatically.

**Entry format** (inside the `universities` array of a country file):

```json
{
  "name": "Example University",
  "name_local": "Université Exemple",
  "country": "FR",
  "domains": ["example.edu"],
  "type": "public",
  "city": "Paris",
  "website": "https://example.edu"
}
```

**Country file format** (`universities/XX.json`):

```json
{
  "$schema": "../schema.json",
  "universities": [ ... ]
}
```

**Rules:**

- `name`, `country`, and `domains` are required; all other fields are optional but encouraged
- `country` must be an ISO 3166-1 alpha-2 code (e.g. `IR`, `US`, `GB`)
- Domains must be valid lowercase email domains (e.g. `.ac.ir`, `.edu`, `.ac.uk`)
- Each domain can only appear once across the entire database
- Add entries in alphabetical order by `name` within the country file

The `domains/` directory and `domains.txt` are auto-generated. Do not edit them directly.

## License

[MIT](./LICENSE)
