# Medical Report to JSON — OpenClaw Skill

Extract structured health data from medical report images or PDFs and save as JSON files
for long-term tracking and querying by your AI health assistant.

## Features

- 📷 **Image & PDF input** — supports PNG, JPG, WebP images and PDF files
- 🌍 **Multi-language** — handles Chinese, German, English, and other languages; all output in English
- 📑 **Multi-page reports** — send multiple images across messages for a single report
- 🔀 **Auto-categorization** — splits multi-category reports into separate JSON files
- 💉 **Vaccination booklet** — accumulative vaccination record in a single file
- 🔍 **Query & compare** — agent can list, read, and compare saved records across dates
- 🔒 **Privacy-first** — no PII extraction; user redacts before sending

## Installation

Copy the skill directory to your agent's workspace:

```bash
cp -r medical-report-to-json/ ~/.openclaw/workspace-<AGENT-ID>/skills/
```

Or for all agents:

```bash
cp -r medical-report-to-json/ ~/.openclaw/skills/
```

### PDF Support

The skill includes a Python helper for PDF conversion. Install the dependency:

```bash
pip3 install pymupdf
```

The agent will also prompt to install this automatically on first PDF encounter.

## Usage

### Sending a Report

1. Redact personal information from your report image/PDF.
2. Send the image to your OpenClaw agent.
3. The agent extracts the data and saves a JSON file.

**Single image:**
> "Here's my blood test from March 15th."

**Multi-page report:**
> "Blood test page 1 of 3" → send image
> "Page 2 of 3" → send image
> "Last page" → send image

**PDF file:**
> "Process this lab report PDF" → attach PDF

### Querying Records

> "List all my medical records"

> "What were my last blood test results?"

> "Compare my cholesterol levels over the past year"

> "Show my vaccination record"

## Output

### Storage Location

All records are saved to:

```
<workspace>/memory/medical_records/
```

### File Naming

| Type | Pattern | Example |
|---|---|---|
| Standard report | `{YYYY-MM-DD}_{category}_{seq:02d}.json` | `2024-03-15_blood_routine_01.json` |
| Vaccination record | `vaccination_record.json` | `vaccination_record.json` |

### Supported Categories

| Category | Description |
|---|---|
| `blood_routine` | CBC, complete blood count |
| `blood_chemistry` | Metabolic panel, CMP, BMP |
| `liver_function` | ALT, AST, bilirubin, albumin |
| `kidney_function` | Creatinine, BUN, GFR |
| `lipid_panel` | Cholesterol, triglycerides, LDL, HDL |
| `blood_glucose` | Fasting glucose, HbA1c |
| `thyroid_function` | TSH, FT3, FT4 |
| `urine_routine` | Urinalysis |
| `coagulation` | PT, INR, APTT |
| `tumor_markers` | AFP, CEA, PSA |
| `hormone_panel` | Testosterone, estrogen, cortisol |
| `immune_panel` | IgG, IgM, complement |
| `infection_markers` | CRP, PCT, ESR |
| `imaging_report` | X-ray, CT, MRI, ultrasound |
| `ecg` | Electrocardiogram |
| `pathology` | Biopsy, cytology |
| `vaccination_record` | Vaccination booklet (accumulative) |
| `other` | Anything not fitting above |

## JSON Schema

### Standard Report

```json
{
  "id": "2024-03-15_blood_routine_01",
  "category": "blood_routine",
  "date": "2024-03-15",
  "items": [
    {
      "name": "WBC",
      "value": 7.2,
      "unit": "10^9/L",
      "ref_range": "3.5-9.5",
      "flag": "normal"
    }
  ],
  "findings": "All values within normal range."
}
```

**Fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | ✅ | `{date}_{category}_{seq}` |
| `category` | string | ✅ | Category slug |
| `date` | string | ✅ | Report date `YYYY-MM-DD` |
| `items` | array | ✅ | Test result items |
| `items[].name` | string | ✅ | Standard English abbreviation |
| `items[].value` | number/string | ✅ | Numeric or qualitative |
| `items[].unit` | string | ✅ | Standard unit |
| `items[].ref_range` | string | ❌ | Reference range |
| `items[].flag` | string | ✅ | `normal`, `high`, `low`, `critical_high`, `critical_low`, `abnormal`, `positive`, `negative` |
| `findings` | string | ❌ | Brief summary of abnormalities |

### Vaccination Record

```json
{
  "id": "vaccination_record",
  "category": "vaccination_record",
  "last_updated": "2024-11-20",
  "items": [
    {
      "vaccine": "COVID-19 mRNA (Pfizer-BioNTech) Dose 1",
      "date": "2021-06-15"
    }
  ]
}
```

**Unique behavior:**
- Single accumulative file: `vaccination_record.json`
- New entries are **appended**, never overwritten
- Only `vaccine` (name/type) and `date` per entry

## Privacy

This skill is designed with privacy in mind:

- **User responsibility**: Redact PII before sending images to the agent
- **No PII extraction**: The skill instructions explicitly tell the agent to ignore personal information
- **Local storage only**: JSON files are stored locally in the agent's workspace
- **No external API calls**: Vision analysis uses the agent's built-in LLM capability

## Skill Structure

```
medical-report-to-json/
├── SKILL.md                    # Skill definition and instructions
├── scripts/
│   └── pdf_to_images.py        # PDF → PNG converter (PyMuPDF)
├── references/
│   └── schema_example.json     # JSON schema examples
└── README.md                   # This file
```

## License

MIT
