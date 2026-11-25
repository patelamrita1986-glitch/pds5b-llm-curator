import os
import pandas as pd
from fetch_papers import fetch_abstract
from extract import extract
from map_uniprot import map_name_to_uniprot

# Replace these with 3 PDS5B PMIDs you verify in PubMed (see D10)
PMIDS = ["29217591", "35986423", "40591192", "28343965", "40437074", "27924011"]

rows = []
for pmid in PMIDS:
    print(f"Processing PMID {pmid}...")
    try:
        paper = fetch_abstract(pmid)
    except Exception as e:
        print(f"  skipped: {e}")
        continue

    result = extract(paper["abstract"])
    interactors = result.get("interactors", [])

    if not interactors:
        rows.append({
            "pmid": pmid,
            "interactor": "",
            "uniprot": "",
            "mapping_status": "no_interaction_extracted",
            "method": result.get("method", ""),
            "stoichiometry": result.get("stoichiometry", ""),
            "evidence_sentence": result.get("evidence_sentence", ""),
            "confidence": result.get("confidence", ""),
            "needs_review": True,
        })
        continue

    for it in interactors:
        name = it.get("name", "")
        mapping = map_name_to_uniprot(name) if name else {"uniprot": None, "status": "no_name"}
        rows.append({
            "pmid": pmid,
            "interactor": name,
            "uniprot": mapping.get("uniprot") or "",
            "mapping_status": mapping.get("status", ""),
            "method": result.get("method", ""),
            "stoichiometry": result.get("stoichiometry", ""),
            "evidence_sentence": result.get("evidence_sentence", ""),
            "confidence": result.get("confidence", ""),
            "needs_review": True,
        })

os.makedirs("output", exist_ok=True)
df = pd.DataFrame(rows)
df.to_csv("output/curated_records.tsv", sep="\t", index=False)
print(f"\nWrote {len(df)} rows to output/curated_records.tsv")
