# MPs by Party
query:: MPs grouped by political party

```dataview
TABLE WITHOUT ID
file.link as MP,
party,
chamber,
default(frontmatter.sessions_appeared, []) as Sessions,
length(frontmatter.sessions_appeared) as Appearances
FROM "politicians"
WHERE party
SORT party, appearances DESC
```

## Party Legend
- **PSD** - Partidul Social Democrat
- **PNL** - Partidul Național Liberal  
- **USR** - Uniunea Salvați România
- **AUR** - Alternativa pentru Demnitate și Adevăr
- **UDMR** - Uniunea Democrată Maghiară din România
- **SOS** - SOS România
- **POT** - Partidul Oamenilor Tineri

```dataview
LIST
FROM "politicians"
WHERE contains(party, "PSD")
SORT file.name
```