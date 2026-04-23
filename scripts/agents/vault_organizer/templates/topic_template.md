---
id: {id}
name: {name}
name_display: {name_display}
category: {category}
category_display: {category_display}
keywords_primary: [{keywords_primary}]
keywords_secondary: [{keywords_secondary}]
sessions_count: {sessions_count}
politicians_count: {politicians_count}
created_at: {created_at}
updated_at: {updated_at}
---

# {name_display}

**Categoria:** [[categories/{category}]]  
**Cuvinte cheie:** {{keywords_primary}}

## Descriere

{keywords_secondary}

## Legi pe Acest Subiect

{{#laws}}
- [[laws/{{.}}]]
{{/laws}}

## Sedinte Relevante ({{sessions_count}})

{{#sessions}}
- [[sessions/{chamber_folder}/{{date}}]] ({{date}})
{{/sessions}}

## Politicieni Activi ({{politicians_count}})

{{#politicians}}
- [[politicians/{{slug}}]]
{{/politicians}}

## Subiecte Inrudite

{{#subtopics}}
- [[topics/{{.}}]]
{{/subtopics}}

{{^subtopics}}
{{#category_topics}}
- [[topics/{{.}}]]
{{/category_topics}}
{{/subtopics}}

---
*Creat: {created_at} | Actualizata: {updated_at}*