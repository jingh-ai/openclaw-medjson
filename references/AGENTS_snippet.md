# Medical Records Reference

## Medical Records

Structured medical test results (blood tests, imaging reports, vaccination records, etc.)
are saved as JSON files in:

```
memory/medical_records/
```

- **File naming**: `{YYYY-MM-DD}_{category}_{seq:02d}.json` (e.g., `2024-03-15_blood_routine_01.json`)
- **Vaccination record**: `vaccination_record.json` (single accumulative file)

These files contain the user's historical health data extracted from medical reports.

**When providing health advice, medical suggestions, or answering health-related questions,
always check and reference these records first.** Read the relevant JSON files to understand
the user's health history, identify trends, and provide informed recommendations based on
actual test results.
