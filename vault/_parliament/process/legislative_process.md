# Legislative Process Flow

How a bill becomes law in Romanian Parliament

## Stage 1: Initiation (Initiativa)

### Types of Legislative Initiatives
| Type | Initiator | Romanian Term |
|------|----------|---------------|
| Government Bill | Prime Minister / Government | Proiect de lege |
| Parliamentary Proposal | Deputy or Senator | Propunere legislativă |
| Citizens' Initiative | 100,000+ citizens | Inițiativă cetățenească |

### Data to capture:
- `initiator_type`: "government" | "parliamentary" | "citizens"
- `initiator_name`: Government ministry or MP name(s)
- `date_lodged`: Date submitted to parliament

## Stage 2: First Chamber Review (Prima Cameră)

### Constitutional Court referral (optional)
- Verifies bill doesn't violate constitution

### Referral to competent chamber
- Based on Article 75: Senate or Chamber of Deputies first
- Time limit: 45 days (60 for special matters)

### Data to capture:
- `first_chamber`: "senate" | "deputies"
- `referral_date`: Date sent to first chamber

## Stage 3: Committee Review (Comisie)

### Committee examination
- Standing committee reviews bill
- Expert opinions sought
- Amendments proposed

### Committee vote
- Adopt, reject, or propose amendments

### Data to capture:
- `committee`: Name of reviewing committee
- `committee_date`: Date of committee review
- `committee_opinion`: "favorable" | "unfavorable" | "amended"

## Stage 4: Plenary Debate (Ședință plenară)

### General debate
- MPs discuss bill principles

### Article-by-article
- Each article debated separately

### Amendment voting
- Proposed amendments voted on

### Final vote
- Bill voted on as a whole

### Data to capture:
- `plenary_debate_date`: Date of plenary debate
- `debate_summary`: Brief summary
- `amendments_adopted`: Number
- `amendments_rejected`: Number  
- `final_vote`: "adopted" | "rejected"

## Stage 5: Second Chamber (A Doua Cameră)

### If different text
- Second chamber can amend
- Returns to first chamber for decision

### First chamber decision
- Accepts second chamber changes OR
- Rejects - stands by original text (definitively adopted)

### Data to capture:
- `second_chamber_date`: Date of second chamber
- `second_chamber_amendments`: Additional amendments
- `conciliation_needed`: true/false

## Stage 6: Constitutionality Check

### Constitutional Court review (optional)
- President or Parliament can request review

### Data to capture:
- `ccr_requested`: true/false
- `ccr_decision`: "constitutional" | "unconstitutional"

## Stage 7: Promulgation (Promulgare)

### Presidential approval
- President must promulgate within 20 days
- Can send back once for reconsideration

### Data to capture:
- `promulgation_date`: Date of presidential promulgation
- `promulgation_number`: Presidential decree number

## Stage 8: Monitorul Oficial Publication (Publicare)

### Publication in Official Gazette
- Published in Monitorul Oficial Partea I
- Law enters force on publication date OR specified future date

### Data to capture:
- `monitorul_oficial_part`: "I"
- `monitorul_number`: Publication number
- `publication_date`: Date in MO
- `effective_date`: Date law takes effect

## Complete Process Flow

```
Initiator → First Chamber → Committee → Plenary → Second Chamber 
         → (Conciliation if needed) → Promulgation → Monitorul Oficial 
         → Effective Date
```

## Law Status Values

Use in database:
- `initiated` - Lodged, not yet debated
- `committee_review` - With committee
- `plenary_debate` - Being debated in plenary
- `adopted_first_chamber` - Passed first chamber
- `adopted` - Passed both chambers (final)
- `promulgated` - Presidential approval given
- `published` - In Monitorul Oficial
- `effective` - Law is in force
- `rejected` - Rejected
- `withdrawn` - Withdrawn by initiator
- `lapsed` - Lapsed (procedural)

## Voting Thresholds

| Law Type | Required Vote |
|----------|--------------|
| Constitutional Revision | 2/3 majority of each chamber |
| Organic Laws | Majority of all members |
| Ordinary Laws | Majority of members present |
| Censorship Motion | Majority of all (233 votes) |

---

## Usage in Vault

For each law file, add frontmatter:
```yaml
initiative_type: "government"  # or "parliamentary" | "citizens"
initiator: "Ministerul Finanțelor"
first_chamber: "senate"
committee: "Budget, Finance, Banking"
process_status: "published"
monitorul_oficial: "I"
mo_number: "456"
publication_date: "2024-06-15"
effective_date: "2024-07-01"
law_type: "ordinary"
voting_threshold: "majority_present"
```

---

## References
- Romanian Constitution Articles 72-78
- senat.ro - legislative process
- cdep.ro - legislative process
- monitoruloficial.ro