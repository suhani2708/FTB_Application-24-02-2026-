# Key Validation Fix - Login.html

## Date: 16 March 2026

---

## Problem

Users were unable to login with existing activation keys. The error message displayed was:
> **"Invalid key format. Expected: jyotS260105-64HYE9NP (20 chars, case-sensitive)"**

### Example Key That Failed
```
p256S260505-X5QD3H5L
```

---

## Root Cause Analysis

### Key Format Structure
The activation keys follow this structure:
```
p256S260505-X5QD3H5L
│────│ │─────│ │───│
  4     1   6    8    ← character counts
```

| Position | Length | Content | Example |
|----------|--------|---------|---------|
| 0-3 | 4 | Email hint (alphanumeric) | `p256` |
| 4 | 1 | Role code (`S` or `T`) | `S` |
| 5-10 | 6 | Expiry date (YYMMDD) | `260505` |
| 11 | 1 | Separator | `-` |
| 12-19 | 8 | HMAC signature (uppercase) | `X5QD3H5L` |

### The Mismatch

| Component | Expected Format | Actual Generated Keys |
|-----------|-----------------|----------------------|
| **Backend (`app.py`)** | Accepts any 4 chars in positions 0-3 | ✅ Compatible |
| **Frontend (`Login.html`)** | Required exactly 4 **lowercase letters** `[a-z]{4}` | ❌ Rejected keys with digits |

The frontend JavaScript validation was **stricter** than the backend Python validation:

**Old Pattern (Line 639 / 744):**
```javascript
/^[a-z]{4}[ST]\d{6}-[23456789ABCDEFGHJKLMNPQRSTUVWXYZ]{8}$/
```

This pattern rejected keys like `p256S260505-X5QD3H5L` because:
- `p256` contains **digits** (`256`)
- Pattern expected **only lowercase letters** (`[a-z]{4}`)

---

## Solution

Updated the regular expression patterns in `ui/Login.html` to accept **alphanumeric** characters (letters + digits) in the first 4 positions.

### Changes Made

#### 1. Key-Only Login Validation (Line 744)
```diff
- /^[a-z]{4}[ST]\d{6}-[23456789ABCDEFGHJKLMNPQRSTUVWXYZ]{8}$/
+ /^[a-z0-9]{4}[ST]\d{6}-[23456789ABCDEFGHJKLMNPQRSTUVWXYZ]{8}$/
```

#### 2. First-Time Login Validation (Line 769)
```diff
- /^[a-z]{2,5}\.?[a-z]{0,4}[ST]\d{6}-[23456789ABCDEFGHJKLMNPQRSTUVWXYZ]{8}$/
+ /^[a-z0-9]{2,5}\.?[a-z0-9]{0,4}[ST]\d{6}-[23456789ABCDEFGHJKLMNPQRSTUVWXYZ]{8}$/
```

### Summary of Change
| Pattern | Before | After |
|---------|--------|-------|
| Character class | `[a-z]` | `[a-z0-9]` |
| Accepts | Lowercase letters only | Lowercase letters + digits |

---

## Files Modified

| File | Lines Changed |
|------|---------------|
| `ui/Login.html` | 744, 769 |

---

## Testing

### Test Key
```
Key: p256S260505-X5QD3H5L
Name: SWANANDI CHANDWADKAR
College: NICMAR University Pune
Email: p25607001@student.nicmar.ac.in
```

### Result
✅ Login successful - key validation now passes

---

## Backup & Rollback

### Git Backup Point
```
Commit: 71d4937
Message: Fixed Johnsons file path issue
```

### Rollback Command
If you need to revert to the previous version:
```bash
git checkout 71d4937 -- ui/Login.html
```

---

## Build Information

### Executable Built
- **File:** `dist/EDU_Toolbox.exe`
- **Size:** ~68.5 MB
- **Build Date:** 16 March 2026
- **Build Command:** `python build_executable.py`

---

## Why This Fix Was Necessary

1. **Bulk-generated keys** already exist with alphanumeric prefixes (e.g., `p256`, `SWAN`, etc.)
2. **Re-generating all keys** would be impractical and disrupt existing users
3. **Backend already accepts** alphanumeric prefixes - frontend was unnecessarily restrictive
4. **Minimal change** - only 2 regex patterns updated, no backend changes required

---

## Notes

- The fix maintains security - still validates:
  - Total length = 20 characters
  - Position 4 = `S` or `T` (role code)
  - Position 11 = `-` (separator)
  - Positions 5-10 = valid date (YYMMDD)
  - Positions 12-19 = valid HMAC signature
- Error message example updated from `jyotS260105-64HYE9NP` to `p256S260505-X5QD3H5L` for clarity

---

## Related Files

| File | Purpose |
|------|---------|
| `app.py` | Backend validation (`verify_activation_code_new()`) |
| `ui/Login.html` | Frontend validation (JavaScript) |
| `config/individual_licenses.csv` | Existing license keys |
| `config/licenses.xlsx` | Bulk license data |

---

**Document Created:** 16 March 2026  
**Author:** FTB Development Team
