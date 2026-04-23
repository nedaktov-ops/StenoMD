---
id: {id}
date: {date}
date_display: {date_display}
chamber: {chamber}
chamber_display: {chamber_display}
title: {title}
source: {source}
source_url: "{source_url}"
laws_count: {laws_count}
speakers_count: {speakers_count}
statements: {statements}
word_count: {word_count}
topics: [{topics}]
is_complete: {is_complete}
extracted_at: {extracted_at}
synced_at: {synced_at}
---

# {title}

**Data:** {date_display} ({{date}})  
**Camera:** {chamber_display}  
**Sursa:** [{{source}}]({{source_url}})

## Sumar

{{summary}}

## Subiecte Discutate

{{#topics}}
- [[topics/{{.}}]]
{{/topics}}

## Legi Discutate

{{#laws}}
- [[laws/{{id}}]] ({{status}}){{#sponsors}} - initiat de [[politicians/{{.}}]]{{/sponsors}}
{{/laws}}

{{#laws_count}}
- Total: {laws_count} legi
{{/laws_count}}

## Participanti

{{#speakers}}
### [[politicians/{{slug}}]] ({{party}}) - {{role}}
> "{{excerpt}}"
{{/speakers}}

{{#presedinte}}
**Presedinte de sedinta:** [[politicians/{{slug}}]]
{{/presedinte}}

{{#secretari}}
**Secretari:** {{#secretari}}[[politicians/{{slug}}]]{{/secretari}}
{{/secretari}}

## Stenograma

{{transcript}}

---
*Extras: {extracted_at} | Sursa: {{source}}*