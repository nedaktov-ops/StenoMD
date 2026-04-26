---
tags: [politician]
type: person
status: active
party: 
party_full: 
constituency: 
legislature: []
born: 
stable_id: 
original_elected_party: 
party_affiliations: []
committees: []
idm: 
source_url: 
last_synced: 
data_sources: []
activity_score: 0
collaboration_network: []
speeches_count: 0
voting_records: []
related_templates: [politician, law, session, committee]
---

# {{title}}

## Basic Info

| Related |
|---------|
| [[politicians/deputies|Deputies]] |
| [[politicians/senators|Senators]] |

| Field | Value |
|-------|-------|
| Name | {{title}} |
| Party | {{party}} |
| Constituency | {{constituency}} |
| Born | {{born}} |
| Stable ID | {{stable_id}} |
| IDM | {{idm}} |

## Sensory Input

- **Source URL:** {{source_url}}
- **Last Synced:** {{last_synced}}
- **Data Sources:** {{data_sources}}

## Processing

- **Activity Score:** {{activity_score}}
- **Collaboration Network:** {{collaboration_network}}

## Memory

### Proposals Sponsored

- [[proposals/|Browse Proposals]]

### Co-Sponsors

- (Track from proposals)

### Speeches

- [[sessions/deputies/|View Speeches]] · Total: {{speeches_count}}

### Voting Record

- [[sessions/|View Voting Records]] · {{voting_records.length || 0}} votes recorded 

## Action/Output

### Query Ready

```dataview
FROM "politicians"
WHERE idm = "{{idm}}"
```

### Alerts

- No alerts

## Parliamentary Activity

### Sessions Attended

- 

### Committees

- 

## Tags

#politician #romania