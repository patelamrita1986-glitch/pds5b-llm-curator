# PDS5B LLM-assisted interaction curator

A small prototype that extracts PDS5B molecular-interaction information from
scientific abstracts using a free LLM (Groq), maps interactors to UniProt, and
outputs a review-ready TSV with evidence sentences and provenance flags.

**Anchor protein:** PDS5B (APRIN/AS3), UniProt ambiguous / unmapped / 

## Why

AI-assisted curation must be transparent and human-verified. This prototype
shows a minimal, honest workflow: fetch abstract → LLM extraction → UniProt
mapping → flag for expert review.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

## Evaluation Benchmark & Error Analysis

To validate the pipeline, we provide a script (`evaluate_intact.py`) that benchmarks the LLM's output against the gold-standard **IntAct database** (PSI-MITAB format).

**Initial Findings:**
When tested on a set of randomly selected PDS5B PubMed IDs, the pipeline yielded a Precision of **0.00** (0 True Positives out of 4 predictions).

**Why is Precision low? (Biocuration Insights):**
This 0.00 result reveals a critical truth about AI-assisted curation and validates why human curators are still necessary:
1. **Abstract vs. Full-text:** The LLM extracts interactions mentioned in the abstract (e.g., as background context), whereas IntAct curators require specific experimental evidence from the full text.
2. **Database Coverage:** Not every published PDS5B paper has been curated by IntAct yet.
3. **Entity Disambiguation:** If the LLM outputs an ambiguous protein name, the UniProt mapping fails, causing a mismatch against the database.

**Next Steps for Improvement:**
To improve precision, the pipeline must move beyond abstracts to full-text XML parsing and include a more robust Named Entity Recognition (NER) step before UniProt mapping. 
pip install -r requirements.txt
# add GROQ_API_KEY to .env
python pipeline.py

****## PSI-MI XML Export****

To demonstrate interoperability with standard biocuration workflows, the repository includes `export_psimi.py`. This script maps the extracted tabular data (interactors, UniProt IDs, and experimental methods) into a simplified PSI-MI XML format, utilizing standard MI ontology IDs (e.g., `MI:0000` for unknown methods). An example output can be found in `example_output_psimi.xml`.
