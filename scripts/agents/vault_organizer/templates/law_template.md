---
id: {id}
number: {number}
number_display: {number_display}
number_short: {number_short}
year: {year}
legislature: {legislature}
title: {title}
title_short: {title_short}
topic: {topic}
status: {status}
discussions_count: {discussions_count}
is_complete: {is_complete}
created_at: {created_at}
updated_at: {updated_at}
---

# {number_display}: {title_short}

**Numar:** {number_display}  
**An:** {year}  
**Subiect:** [[topics/{{topic}}]]  
**Status:** {status}

{{#title}}
## Descriere

{title}
{{/title}}

## Sedinte unde a fost Discutata ({{discussions_count}})

{{#sessions}}
- [[sessions/{chamber_folder}/{{date}}]] ({{date}}) - {{reference}}
{{/sessions}}

{{#sponsors}}
## Initiatori

- {{#sponsors}}[[politicians/{{.}}]]{{/sponsors}}
{{/sponsors}}

## Istoric Status

| Data | Status | Sedinta |
|------|--------|--------|
{{#history}}
| {{date}} | {{status}} | [[sessions/{chamber_folder}/{{session}}]] |
{{/history}}

---
*Creata: {created_at} | Actualizata: {updated_at}*