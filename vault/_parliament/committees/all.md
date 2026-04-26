# Parliamentary Committees

## Senate (Senat) - 15 Standing Committees

| # | Committee Name | Romanian Name |
|---|---------------|----------------|
| 1 | Economic Affairs | Afaceri Economice |
| 2 | Budget, Finance, Banking | Buget, Finanțe, Bănci |
| 3 | Industries and Services | Industrii și Servicii |
| 4 | Agriculture, Forestry, Food | Agricultură, Silvicultură, Industrie Alimentară |
| 5 | Human Rights, Equal Opportunities | Drepturile Omului, Egalitate de Șanse |
| 6 | Public Administration | Administrație Publică |
| 7 | Labour and Social Protection | Muncă și Protecție Socială |
| 8 | Health and Family | Sănătate și Familie |
| 9 | Education, Science, Youth, Sports | Educație, Știință, Tineret, Sport |
| 10 | Culture, Arts, Mass Media | Cultură, Arte, Mass Media |
| 11 | Legal Affairs, Discipline, Immunities | Afaceri Juridice, Disciplină, Imunități |
| 12 | Defense, Public Order, National Security | Apărare, Ordine Publică, Securitate Națională |
| 13 | Foreign Policy | Politică Externă |
| 14 | European Affairs | Afaceri Europene |
| 15 | Petitions | Petiții |

## Chamber of Deputies (Camera Deputatilor) - 17 Standing Committees

| # | Committee Name | Romanian Name |
|---|---------------|----------------|
| 1 | Economic Policies, Reform, Privatisation | Politici Economice, Reformă, Privatizare |
| 2 | Budget, Finance, Banking | Buget, Finanțe, Bănci |
| 3 | Industries and Services | Industrii și Servicii |
| 4 | Agriculture, Forestry, Food Industry | Agricultură, Silvicultură, Industrie Alimentară |
| 5 | Human Rights, Religious Issues, Minorities | Drepturile Omului, Culte, Minorități |
| 6 | Public Administration, Territorial Planning | Administrație Publică, Amenajarea Teritoriului |
| 7 | Labour and Social Protection | Muncă și Protecție Socială |
| 8 | Health and Family | Sănătate și Familie |
| 9 | Education, Science, Youth, Sports | Educație, Știință, Tineret, Sport |
| 10 | Culture, Arts, Mass Media | Cultură, Arte, Mass Media |
| 11 | Legal, Discipline, Immunities | Afaceri Juridice, Disciplină, Imunități |
| 12 | Defense, Public Order, National Security | Apărare, Ordine Publică, Securitate Națională |
| 13 | Foreign Policy | Politică Externă |
| 14 | Abuse, Corruption, Petitions | Abuz, Corupție, Petiții |
| 15 | Standing Orders | Regulamente |
| 16 | Information Technology | Tehnologia Informației |
| 17 | Equal Opportunities | Egalitate de Șanse |

## Joint Parliamentary Committees

| # | Committee Name | Purpose |
|---|---------------|---------|
| 1 | Intelligence Services Control | Parliamentary oversight of SRI, SIE |
| 2 | December 1989 Revolutionaries | Research on 1989 revolution |
| 3 | Constitutional Revision | Draft constitution changes |
| 4 | European Integration with Moldova | EU-Moldova Relations |
| 5 | National Security | Security policy oversight |
| 6 | Court of Accounts Control | Financial oversight |
| 7 | Anti-Trafficking | Human trafficking prevention |
| 8 | Justice Legislation | Legal reform |
| 9 | OECD Accession | EU-OECD relations |
| 10 | Domestic Violence | Violence prevention |
| 11 | Environmental | Environmental policy |
| 12 | EU Funds | European funding oversight |

## Committee Membership Data Structure

For each MP profile, add:
```yaml
committees:
  - name: "Budget, Finance, Banking"
    code: "BUC"
    chamber: "senate"  # or "deputies" or "joint"
    role: "member"  # or "chair", "vice-chair", "secretary"
    start_date: "2024-12-21"
    end_date: null
```

---

## Usage in Vault

Track in MP profiles:
- `committees` field per parliamentarian
- Include: name, code, chamber, role, dates

Cross-reference in session data:
- Laws linked to committee of origin
- Committee meetings noted in transcripts

---

## References
- senat.ro - Senate committees
- cdep.ro - Chamber committees
- parliament Joint committees list

## Sensory Input

- **Source URL:** cdep.ro/senat.ro (committees)
- **Last Synced:** 2026-04-26 15:59:43
- **Meeting Schedule:** (from parliament calendar)

## Processing

- **Activity Score:** 0
- **Meeting Frequency:** monthly
- **Bills Reviewed:** (track from session data)

## Memory

### Members

### Meetings
- (Track meeting dates)

### Reports
- (Link published reports)

### Legislation Reviewed
- (Link laws)

## Action/Output

### Query Ready
```dataview
FROM "committees"
WHERE contains(name, "Parliamentary Committees")
```

### Member Attendance
- (Track from meetings)

### Bills Passed Through
- (Track laws)

### Activity Report
- Auto-generate
