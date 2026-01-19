---
description: Generate B14 Blurbs Requested - ONLY explicit blurb requests (outputs JSONL)
tags:
  - meeting-intelligence
  - block-generation
  - b14
  - blurbs
tool: true
---
# Generate B14: Blurbs Requested

**PURPOSE:** Detect EXPLICIT blurb requests made during the meeting. Output structured JSONL metadata for automated generation.

**CRITICAL:** This is ONLY for blurbs that were EXPLICITLY requested. If no blurbs requested, output empty result.

---

## What Is a Blurb?

**Definition:**
A SHORT, pithy piece of text (35-250 words) describing a person, product, company, or concept for a specific purpose.

**Characteristics:**
- **SHORT** - Not a strategy doc, not a presentation, not an article
- **DISCRETE** - Single text artifact, not multi-part campaign
- **SPECIFIC SUBJECT** - About ONE thing (Danny's bio, YOUR_COMPANY product description, etc.)
- **CLEAR PURPOSE** - For a specific use (email intro, website copy, pitch deck)
- **DELIVERABLE** - Someone will write/send THIS specific text

**Examples of REAL blurbs:**
- "Can you write a 75-word bio of Danny for the partnership announcement?"
- "I need a short product description for YOUR_COMPANY - 100 words max for the homepage"
- "Draft me a 3-sentence pitch for the investor deck"
- "Write a brief intro about yourself for the speaker bio"

**What is NOT a blurb:**
- Strategic messaging frameworks
- Campaign planning ("develop social media strategy")
- Presentation content ("create slides about X")
- Talking points or soundbites
- Multi-document initiatives
- Broad communications work

---

## Detection Framework

### Semantic Validation (4 Questions)

For EVERY potential blurb, ask:

**1. Is there a discrete text artifact?**
- ✅ Yes: "Write me a bio", "Draft product description"
- ❌ No: "Develop messaging", "Create campaign materials"

**2. Is the length SHORT (under 300 words)?**
- ✅ Yes: Blurb request
- ❌ No: Likely presentation, article, or strategy doc

**3. Was it EXPLICITLY requested?**
- ✅ Yes: "Can you write...", "I need...", "Draft me..."
- ❌ No: Implied need, strategic discussion

**4. Is there ONE specific subject?**
- ✅ Yes: About Danny, about YOUR_COMPANY, about the workshop
- ❌ No: Multiple topics, broad initiative

**MUST answer YES to all 4. If ANY is NO → Not a blurb.**

---

## Output Format: JSONL

**Schema:** `file 'N5/schemas/B14_BLURBS_REQUESTED.schema.json'`

### Structure (One JSON Object Per Line)

```jsonl
{"id": "BLB-001", "subject": "V", "type": "short", "recipient": "David", "audience_context": "Investor pitch deck", "purpose": "Speaker bio for partnership announcement", "key_points": ["Career coach background", "YOUR_COMPANY founder", "Non-technical but curious"], "status": "pending"}
{"id": "BLB-002", "subject": "YOUR_COMPANY", "type": "email", "recipient": "Ilya", "audience_context": "University career services directors", "purpose": "Product overview for partnership discussions", "key_points": ["AI-powered matching", "Free for universities", "Employer subscription model"], "status": "pending"}
```

### Required Fields

```json
{
  "id": "BLB-XXX",              // BLB-001, BLB-002, etc. (sequential)
  "subject": "V|YOUR_COMPANY|Other",
  "subject_detail": "string",   // If subject=Other, specify what
  "type": "short|email",        // short=50-80 words, email=150-250 words
  "recipient": "string",        // Who requested it / who will use it
  "audience_context": "string", // Who recipient will share with
  "purpose": "string",          // Why needed (specific use case)
  "key_points": ["array"],      // Important details to include
  "status": "pending"           // Always "pending" at detection
}
```

---

## Examples - What to Capture vs Omit

### ✅ CAPTURE THESE:

**Example 1:**
> V: "Can you send me a 75-word bio of Danny for the departure announcement?"

**Output:**
```jsonl
{"id": "BLB-001", "subject": "Other", "subject_detail": "Danny's bio", "type": "short", "recipient": "V", "audience_context": "Team / stakeholders", "purpose": "Departure announcement", "key_points": ["Role at YOUR_COMPANY", "Key contributions", "Next steps"], "status": "pending"}
```

**Example 2:**
> David: "I need a product description for the homepage - about 100 words explaining what we do"

**Output:**
```jsonl
{"id": "BLB-001", "subject": "YOUR_COMPANY", "type": "short", "recipient": "David", "audience_context": "Website visitors", "purpose": "Homepage product description", "key_points": ["AI-powered matching", "University partnerships", "Employer benefits"], "status": "pending"}
```

### ❌ DO NOT CAPTURE:

**Example 1:**
> "We need to develop messaging for the social media campaign"

**Why omit:** Broad initiative, not discrete text artifact

**Example 2:**
> "Let's create presentation slides about our competitive advantage"

**Why omit:** Presentation content, not a blurb

**Example 3:**
> "We should probably have better positioning for enterprise clients"

**Why omit:** Strategic need, not explicit request

**Example 4:**
> "The GTM deck needs updating with our new value prop"

**Why omit:** Multi-part project, not single blurb

---

## Context Sources

**ALWAYS check these for subject context:**

1. **Knowledge base:** `file 'Knowledge/'` subdirectories
   - Look for existing bios, product descriptions, company info
   - Reference these in `key_points` if relevant

2. **Related blocks:**
   - **B01 (Detailed Recap)** - Full meeting context
   - **B02 (Commitments)** - Related commitments made
   - **B08 (Stakeholder Intelligence)** - Background on people
   - **B21 (Key Moments)** - Memorable details to include
   - **B25 (Deliverables)** - Related deliverables

---

## Execution Steps

1. **Read full transcript** - Understand complete conversation
2. **Scan for explicit requests** - Look for "write", "draft", "need", "can you"
3. **Apply 4-question validation** - Verify each is actually a blurb
4. **Check Knowledge base** - Gather subject context
5. **Generate JSONL entries** - One object per line, sequential IDs
6. **Write output file** - `B14_BLURBS_REQUESTED.jsonl` in meeting folder

---

## Output Handling

### If Blurbs Requested:
**Write file:** `B14_BLURBS_REQUESTED.jsonl`  
**Format:** One JSON object per line (no commas between lines)  
**Validation:** Each object must match schema

### If NO Blurbs Requested:
**Write file:** `B14_BLURBS_REQUESTED.jsonl`  
**Content:** Single comment line:
```
# No blurbs requested in this meeting
```

---

## Quality Standards

**Before outputting, verify:**
- ✅ Each entry passes 4-question validation
- ✅ Only EXPLICIT requests captured
- ✅ `key_points` references Knowledge base when relevant
- ✅ `purpose` is specific (not vague like "communications")
- ✅ JSONL is valid (one object per line, proper JSON syntax)
- ✅ IDs are sequential (BLB-001, BLB-002, etc.)

**If uncertain about a request:**
- Apply 4-question framework strictly
- When in doubt, OMIT (better false negative than false positive)
- V will explicitly request if truly needed

---

**Generate B14 now using the meeting transcript provided in this conversation.**

