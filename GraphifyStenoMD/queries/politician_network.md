# Politician Network Query

**Trigger:** `/stenomd xquery network`
**Purpose:** Show politician connections and network

---

## Usage

```
/stenomd xquery network "NAME"
/stenomd xquery network "NAME" --depth 2
```

---

## Example

```
/stenomd xquery network "TANASESCU"

=== Network: TĂNĂSESCU Alina-Elena ===

Direct connections (1 hop):
- session-20241221 (speaks in)
- session-20250115 (speaks in)
- PSD (member of)
- 38-2026 (proposes)
- Dolj (represents)

Network size:
- 1 hop: 5 connections
- 2 hops: 23 connections

Key bridge nodes:
- session-20241221 (connects to 87 politicians)
```