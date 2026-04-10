---
name: medical-report-to-json
description: >
  Use this skill when the user sends medical test reports (blood tests, urine tests,
  imaging reports, pathology results, vaccination records, etc.) as images or PDFs
  and wants to extract the health data into structured JSON files. Also use this skill
  when the user asks to review, list, query, or compare previously saved medical records.
version: 1.0.0
---

# Medical Report to JSON

Extract structured health data from medical report images or PDFs and save as JSON files
in the agent's workspace memory for future reference.

---

## When to Trigger

Activate this skill when:

- The user sends an **image or PDF** of a medical test report and asks to process/save it.
- The user mentions keywords like: test results, lab report, blood test, checkup, medical report,
  health record, vaccination, imaging report, or similar.
- The user asks to **list, query, compare, or summarize** previously saved medical records.

---

## Privacy Reminder

**ALWAYS** remind the user on first interaction:

> ⚠️ Before sending medical reports, please ensure you have **removed or redacted all personal
> information** (name, date of birth, ID numbers, address, insurance info, etc.) from the
> images. I will only extract health-related test data. Once redacted, you can safely send
> the report images.

Do NOT extract or store any personally identifiable information, even if visible.

---

## Step 1: Receive & Identify the Input

### Image Input
If the user sends an image (PNG, JPG, WebP):
1. Analyze the image using your vision capability.
2. Identify the **report type** (blood test, urine test, imaging, etc.).
3. Identify the **report date** (look for date fields on the report).
4. Identify the **language** (Chinese, German, English, etc.).
5. Proceed to Step 2.

### PDF Input
If the user sends a PDF file:
1. Run the PDF-to-image converter script included with this skill:
   ```bash
   python3 <skill_directory>/scripts/pdf_to_images.py "<pdf_path>" "<output_directory>"
   ```
   - If `pymupdf` is not installed, first run: `pip3 install pymupdf`
   - The script will output one PNG per page to `<output_directory>`.
2. Analyze **each generated PNG** using your vision capability.
3. Combine the data from all pages into a single report extraction.
4. Proceed to Step 2.

---

## Step 2: Multi-Image Handling

A single medical report may span **multiple images** sent across separate messages.

### Collection Phase
- When the user sends a report image, check if they indicate more pages are coming
  (e.g., "page 1 of 3", "more coming", "first part").
- If more pages are expected:
  1. Analyze the current image and note the extracted data in your context.
  2. Respond: "✅ Received page N. Send the next page when ready."
  3. Wait for the next image.
- Repeat until either:
  - The user says "that's all", "last one", "done", "no more", or similar.
  - The user indicates the page count and all pages have been received (e.g., "page 3 of 3").

### Processing Phase
- Once all images are received, consolidate all extracted data.
- Remove duplicates (items appearing on overlapping pages).
- Proceed to Step 3.

If only **one image** is sent with no indication of more pages, proceed directly to Step 3.

---

## Step 3: Extract Data

### What to Extract
Focus ONLY on clinically relevant information:

- **Test item name** — use standard English abbreviations (e.g., WBC, HGB, ALT, TSH)
- **Test value** — numeric when possible, string for qualitative results (e.g., "positive", "negative")
- **Unit** — as printed on the report
- **Reference range** — as printed on the report
- **Flag** — determine based on value vs reference range

### What to IGNORE
- Patient personal information (name, age, gender, ID, address)
- Hospital/lab name and address
- Doctor name and signature
- Specimen type and collection method details
- Barcode, QR code, and page numbers
- Administrative details (order numbers, billing info)

### Translation Rules
- **Always output item names in English**, regardless of source language.
- Use internationally recognized abbreviations where they exist:
  - 白细胞 / Leukozyten → WBC
  - 血红蛋白 / Hämoglobin → HGB
  - 谷丙转氨酶 / GPT → ALT
  - 促甲状腺激素 / TSH → TSH
- For items without standard abbreviations, use a concise English name.
- Keep units in their original standard form (do not convert units).

### Flag Values
Assign one of the following flags based on the value relative to the reference range:
- `"normal"` — within reference range
- `"high"` — above upper limit
- `"low"` — below lower limit
- `"critical_high"` — significantly above upper limit (if marked as critical on report)
- `"critical_low"` — significantly below lower limit (if marked as critical on report)
- `"abnormal"` — outside range but direction not applicable
- `"positive"` — for qualitative tests with positive result
- `"negative"` — for qualitative tests with negative result

---

## Step 4: Categorize & Split

### Category Assignment
Assign each extracted item to one of these standardized categories:

| Category | Covers |
|---|---|
| `blood_routine` | CBC, complete blood count |
| `blood_chemistry` | Metabolic panel, CMP, BMP |
| `liver_function` | ALT, AST, bilirubin, albumin |
| `kidney_function` | Creatinine, BUN, GFR, uric acid |
| `lipid_panel` | Cholesterol, triglycerides, LDL, HDL |
| `blood_glucose` | Fasting glucose, HbA1c, OGTT |
| `thyroid_function` | TSH, FT3, FT4 |
| `urine_routine` | Urinalysis |
| `coagulation` | PT, INR, APTT, fibrinogen |
| `tumor_markers` | AFP, CEA, PSA, CA-125 |
| `hormone_panel` | Testosterone, estrogen, cortisol |
| `immune_panel` | IgG, IgM, complement, ANA |
| `infection_markers` | CRP, PCT, ESR |
| `imaging_report` | X-ray, CT, MRI, ultrasound |
| `ecg` | Electrocardiogram |
| `pathology` | Biopsy, cytology |
| `vaccination_record` | Vaccination records (see special handling below) |
| `other` | Anything not fitting above |

### Multi-Category Splitting
If a single report contains items from **multiple categories**:
- **Split** the items into separate groups by category.
- Create **one JSON file per category**.
- Each file contains only the items belonging to that category.

---

## Step 5: Build JSON

### Standard Report Schema

For each category group, build a JSON object:

```json
{
  "id": "{date}_{category}_{seq}",
  "category": "{category}",
  "date": "{YYYY-MM-DD}",
  "items": [
    {
      "name": "{standard_abbreviation}",
      "value": 7.2,
      "unit": "{unit}",
      "ref_range": "{lower}-{upper}",
      "flag": "normal"
    }
  ],
  "findings": "Brief clinical summary if abnormalities exist."
}
```

**Field rules:**
- `id`: Composite of date, category, and sequence number (e.g., `"2024-03-15_blood_routine_01"`)
- `category`: Must be one of the standardized category slugs from Step 4
- `date`: Report date in `YYYY-MM-DD` format. If the date is unclear, ask the user
- `items`: Array of test items. `value` should be numeric when possible
- `items[].ref_range`: Omit this field if no reference range is given on the report
- `findings`: Include ONLY if there are notable abnormalities. Write in English. Keep it brief
  (1-2 sentences). Focus on clinically significant deviations

Refer to the example file at `references/schema_example.json` in this skill directory.

### Vaccination Record Schema (Special)

Vaccination records use a **different schema** and are **accumulative** — all entries go
into a single file that grows over time:

```json
{
  "id": "vaccination_record",
  "category": "vaccination_record",
  "last_updated": "{YYYY-MM-DD}",
  "items": [
    {
      "vaccine": "COVID-19 mRNA (Pfizer-BioNTech) Dose 1",
      "date": "2021-06-15"
    }
  ]
}
```

**Vaccination-specific rules:**
- Only two fields per item: `vaccine` (vaccine name/type/dose) and `date`
- When adding new vaccination records, **read the existing file first**, append new
  entries, then write back. Do NOT overwrite existing entries
- Update `last_updated` to today's date
- Avoid duplicate entries (same vaccine + same date = duplicate)

---

## Step 6: File Naming & Save

### Storage Location
Save all JSON files to:
```
memory/medical_records/
```
This path is relative to the agent workspace root. Create the directory if it does not exist:
```bash
mkdir -p memory/medical_records
```

### Naming Convention

**Standard reports:**
```
{YYYY-MM-DD}_{category}_{seq:02d}.json
```
- Date: From the report itself (NOT the upload date)
- Category: Standardized slug from Step 4
- Sequence: `01`, `02`, `03`... Auto-increment if a file with the same date+category exists

**Examples:**
- `2024-03-15_blood_routine_01.json`
- `2024-03-15_blood_routine_02.json` (second blood test same day)
- `2024-06-20_liver_function_01.json`

**Vaccination records:**
```
vaccination_record.json
```
Fixed filename, no date prefix, no sequence number.

### Sequence Number Logic
Before saving, check for existing files:
```bash
ls memory/medical_records/{date}_{category}_*.json
```
- If no files match: use `01`
- If files exist: use the next available number (e.g., if `_01` and `_02` exist, use `_03`)

---

## Step 7: Confirm & Summarize

After saving, report back to the user with:

1. **File saved**: Full filename and path
2. **Category**: What type of report was processed
3. **Date**: Report date
4. **Item count**: How many test items were extracted
5. **Abnormal findings**: Highlight any items flagged as high/low/critical/abnormal
6. **Summary**: The `findings` field content

**Example response:**
```
✅ Report saved: memory/medical_records/2024-03-15_blood_routine_01.json

📋 Blood Routine | 2024-03-15 | 18 items extracted

⚠️ Abnormal findings:
  • HGB: 105 g/L (ref: 130-175) — LOW
  • PLT: 95 ×10^9/L (ref: 125-350) — LOW

📝 Summary: Hemoglobin and platelet count are below the reference range.
   Consider follow-up testing.
```

---

## Querying Saved Records

When the user asks about their medical records:

### List all records
```bash
ls -la memory/medical_records/
```
Present as a formatted table with date, category, and file size.

### Read a specific record
Read the JSON file and present the data in a readable table format, highlighting
any abnormal values.

### Compare records over time
If the user asks to compare or track trends:
1. Read multiple JSON files of the same category across different dates.
2. Show how specific values have changed over time.
3. Highlight improving or worsening trends.

### Search by category or date
Filter files by parsing filenames:
- By date: `ls memory/medical_records/2024-03-*`
- By category: `ls memory/medical_records/*_blood_routine_*`

---

## Memory Awareness

On first successful save, add a note to the workspace `MEMORY.md` (if it exists)
or create a section noting:

```
## Medical Records
Structured medical test results are saved as JSON files in:
  memory/medical_records/
File naming: {YYYY-MM-DD}_{category}_{seq:02d}.json
I can read these files anytime to answer health-related questions.
```

This ensures awareness persists across conversation sessions.
