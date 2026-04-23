---
id: {id}
name: {name}
name_first: {name_first}
name_last: {name_last}
slug: {slug}
chamber: {chamber}
chamber_display: {chamber_display}
role: {role}
party: {party}
party_display: {party_display}
legislature: {legislature}
statements_total: {statements_total}
positions_count: {positions_count}
is_complete: {is_complete}
created_at: {created_at}
updated_at: {updated_at}
---

# {name}

**Camera:** {chamber_display}  
**Partid:** [[parties/{{party}}]]  
**Legislatura:** {legislature}

{{#role}}
**Functie:** {role}
{{/role}}

## Activitate

### Sedinte ({{sessions_count}})

{{#sessions}}
- [[sessions/{chamber_folder}/{{date}}]] ({{date}}) - {{role}} - {{statement_count}} declaratii
{{/sessions}}

### Statistici

- **Total declaratii:** {statements_total}
- **Sedinte active:** {{sessions_count}}

## Pozitii pe Subiecte

{{#positions}}
### [[topics/{{topic}}]]
> **Pozitie:** {position}
> **Sedinta:** [[sessions/{chamber_folder}/{{session}}]]
> **Context:** "{context}"
{{/positions}}

{{#committees}}
## Comisii

- [[committees/{{name}}]] - {{role}}
{{/committees}}

## Note

*Senator/ Deputat in Parlamentul Romaniei*

---
*Creat: {created_at} | Actualizat: {updated_at}*