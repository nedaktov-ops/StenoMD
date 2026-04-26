# Session Search Query

**Trigger:** `/stenomd xquery session`
**Purpose:** Find sessions by various criteria

---

## Usage

```
/stenomd xquery session DATE
/stenomd xquery session --chamber cdep
/stenomd xquery session --year 2024
/stenomd xquery session --month 2024-12
/stenomd xquery session --laws
```

---

## Examples

### By Date
```
/stenomd xquery session 2024-12-21

=== Session 2024-12-21 ===
Date: 21 December 2024
Chamber: Chamber of Deputies
Legislature: 2024-2028
Speakers: 87
Laws discussed: 4
```

### By Chamber
```
/stenomd xquery session --chamber cdep

=== Chamber of Deputies Sessions ===
Total: 1890 sessions
Date range: 1998-2025

Top 5 by speeches:
1. 2025-09-17 (87 speakers)
2. 2025-09-10 (72 speakers)
...
```

### By Year
```
/stenomd xquery session --year 2024

=== 2024 Sessions ===
Total: 234 sessions
Most active: November 2024
Top law: Law 38/2026
```

### Laws Discussed
```
/stenomd xquery session --laws

=== Laws by Discussion Frequency ===
1. 38/2026 (23 sessions)
2. 52/2026 (18 sessions)
3. 448/2006 (12 sessions)
```