# Iran Universities Database

A community-maintained database of Iranian university email domains, usable by any app to verify academic email addresses from Iranian institutions.

## Background

[JetBrains' swot repository](https://github.com/JetBrains/swot) — used by tools like [Zed](https://zed.dev) to validate student/educator email addresses — has stopped accepting new Iranian university domains due to legal and sanctions compliance requirements. This leaves Iranian students without access to features tied to academic email verification.

This repository is an independent alternative maintained by the Iranian developer community, with no such restrictions.

## Data

- **144 universities**, **145 email domains** (seeded from swot, extended with missing entries)
- Source of truth: [`universities.json`](./universities.json)
- Derived formats regenerated automatically by CI on every merge

## How to Integrate

### Option 1: JSON (recommended for new integrations)

Fetch [`universities.json`](./universities.json) directly from the GitHub raw URL. Each entry:

```json
{
  "name": "University of Tehran",
  "name_fa": "دانشگاه تهران",
  "domains": ["ut.ac.ir"],
  "type": "public",
  "city": "Tehran",
  "website": "https://ut.ac.ir"
}
```

To check if an email is from an Iranian university:

```python
import json, urllib.request

url = "https://raw.githubusercontent.com/matinzd/iran-universities-database/main/universities.json"
data = json.loads(urllib.request.urlopen(url).read())
all_domains = {d for u in data["universities"] for d in u["domains"]}

def is_iranian_university_email(email):
    domain = email.split("@")[-1].lower()
    return domain in all_domains
```

### Option 2: Swot-compatible drop-in

The `domains/` directory mirrors swot's exact file structure. Apps already consuming swot can point at this repo instead with no code changes.

```
domains/
  ir/
    ac/
      ut.txt        → "University of Tehran"
      sharif.txt    → "Sharif University of Technology"
      ...
    iau.txt         → "Islamic Azad University"
```

### Option 3: Flat domain list

[`domains.txt`](./domains.txt) contains one domain per line — suitable for simple grep/lookup or loading into a set.

## University Types

| Value             | Description                                      |
| ----------------- | ------------------------------------------------ |
| `public`          | Government-funded public university              |
| `private`         | Private non-governmental university              |
| `islamic-azad`    | Islamic Azad University (branch)                 |
| `medical`         | University of Medical Sciences                   |
| `distance`        | Distance learning institution (e.g. Payame Noor) |
| `applied-science` | University of Applied Science and Technology     |

## Contributing

To add a missing university or correct existing data, edit [`universities.json`](./universities.json) and open a pull request. CI will validate the schema and check for duplicate domains automatically.

**Entry format:**

```json
{
  "name": "Example University",
  "name_fa": "دانشگاه نمونه",
  "domains": ["example.ac.ir"],
  "type": "public",
  "city": "Tehran",
  "website": "https://example.ac.ir"
}
```

**Rules:**

- `name` and `domains` are required; all other fields are optional but encouraged
- Domains must end in `.ac.ir` or `.ir`
- Each domain can only appear once across the entire database
- Add the entry in alphabetical order by `name`

The `domains/` directory and `domains.txt` are auto-generated — do not edit them directly.

## License

[MIT](./LICENSE)
