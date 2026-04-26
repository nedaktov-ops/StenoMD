# Romanian Legislatures Reference

## Related Sections

- [[politicians/deputies|Deputies]] - Browse all deputies
- [[politicians/senators|Senators]] - Browse all senators

## Current Legislature

### Legislature 2024-2028 (Legislatura LVII)
- **Election Date**: December 1, 2024
- **Start Date**: December 21, 2024 (when Parliament convened)
- **End Date**: Expected December 2028
- **Senate Seats**: 136 (2 vacant - 134 active)
- **Chamber Seats**: 330 (331 after diaspora adjustment)

### Previous Legislatures

### Legislature 2020-2024 (Legislatura LVI)
- **Election Date**: December 6, 2020
- **Dissolved**: December 2024
- **Senate Seats**: 136
- **Chamber Seats**: 332

### Legislature 2016-2020 (Legislatura LV)
- **Election Date**: December 11, 2016
- **Dissolved**: December 2020
- **Senate Seats**: 136
- **Chamber Seats**: 329

### Legislature 2012-2016 (Legislatura LIV)
- **Election Date**: December 9, 2012
- **Dissolved**: December 2016
- **Senate Seats**: 176 (reduced to 168 in 2015)
- **Chamber Seats**: 412 (reduced to 399 in 2015)

### Legislature 2008-2012 (Legislatura LIII)
- **Election Date**: November 30, 2008
- **Dissolved**: December 2012
- **Senate Seats**: 137
- **Chamber Seats**: 411

### Legislature 2004-2008 (Legislatura LII)
- **Election Date**: November 2004
- **Dissolved**: December 2008
- **Senate Seats**: 137
- **Chamber Seats**: 411

### Legislature 2000-2004 (Legislatura LI)
- **Election Date**: November 2000
- **Dissolved**: December 2004
- **Senate Seats**: 140
- **Chamber Seats**: 345

### Legislature 1996-2000 (Legislatura L)
- **Election Date**: November 1996
- **Dissolved**: November 2000
- **Senate Seats**: 143
- **Chamber Seats**: 343

### Legislature 1992-1996 (Legislatura XLIX)
- **Election Date**: September 1992
- **Dissolved**: November 1996
- **Senate Seats**: 143
- **Chamber Seats**: 341

### Legislature 1990-1992 (Legislatura XLVIII)
- **Election Date**: May 20, 1990
- **Dissolved**: September 1992
- **Senate Seats**: 119
- **Chamber Seats**: 395

## Data Structure for Tracking

```yaml
legislature: "2024-2028"
election_date: "2024-12-01"
start_date: "2024-12-21"
end_date: null  # ongoing
chamber: "both"
seats:
  senate: 136
  chamber: 330
status: "active"  # or "completed"
```

## Multi-Legislature Profile Example

For tracking same person across legislatures:
```yaml
name: "John Smith"
stable_id: "john-smith-1975-bucharest"

legislative_history:
  - legislature: "2012-2016"
    chamber: "deputies"
    party: "PDL"
    constituency: "București"
    
  - legislature: "2016-2020"
    chamber: "deputies"  
    party: "PNL"
    constituency: "București"
    
  - legislature: "2020-2024"
    chamber: "senate"
    party: "PNL"
    constituency: "București"
    
  - legislature: "2024-2028"
    chamber: "senate"
    party: "PNL"
    constituency: "București"
    status: "active"
```

## Usage in Vault

1. **For each legislature**: Create reference file
2. **For each MP**: Track parliamentary history across legislatures  
3. **For sessions**: Link to legislature in date
4. **For laws**: Include legislature reference

---

## References
- IPU Parline (data.ipu.org)
- Romanian Parliament archives
- Wikipedia - List of Romanian legislatures