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
pip install -r requirements.txt
# add GROQ_API_KEY to .env
python src/pipeline.py

****## PSI-MI XML Export****

To demonstrate interoperability with standard biocuration workflows, the repository includes `export_psimi.py`. This script maps the extracted tabular data (interactors, UniProt IDs, and experimental methods) into a simplified PSI-MI XML format, utilizing standard MI ontology IDs (e.g., `MI:0000` for unknown methods). An example output can be found in `example_output_psimi.xml`.
