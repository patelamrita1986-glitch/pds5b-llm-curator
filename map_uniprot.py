import requests

def _query(query: str) -> list:
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": query,
        "format": "json",
        "size": 5,  # fetch a few to check for ambiguity
        "fields": "accession,protein_name,gene_names,reviewed",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("results", [])

def map_name_to_uniprot(name: str, organism_id: int = 9606) -> dict:
    # 1) Try exact gene name among *reviewed* (Swiss-Prot) entries
    results = _query(f'(gene_exact:"{name}") AND (organism_id:{organism_id}) AND (reviewed:true)')
    if len(results) == 1:
        return {"uniprot": results[0]["primaryAccession"], "status": "mapped_gene_reviewed"}
    if len(results) > 1:
        # If multiple reviewed entries, return all candidates for human review
        return {
            "uniprot": None,
            "status": "ambiguous_reviewed_gene",
            "candidates": [x["primaryAccession"] for x in results],
        }

    # 2) Fall back to protein name among *reviewed* entries
    results = _query(f'(protein_name:"{name}") AND (organism_id:{organism_id}) AND (reviewed:true)')
    if len(results) == 1:
        return {"uniprot": results[0]["primaryAccession"], "status": "mapped_protein_reviewed"}
    if len(results) > 1:
        return {
            "uniprot": None,
            "status": "ambiguous_reviewed_protein",
            "candidates": [x["primaryAccession"] for x in results],
        }

    # 3) Last resort: exact gene name in unreviewed entries (TrEMBL)
    results = _query(f'(gene_exact:"{name}") AND (organism_id:{organism_id})')
    if len(results) == 1:
        return {"uniprot": results[0]["primaryAccession"], "status": "mapped_gene_unreviewed"}
    if len(results) > 1:
        return {
            "uniprot": None,
            "status": "ambiguous_gene_unreviewed",
            "candidates": [x["primaryAccession"] for x in results],
        }

    return {"uniprot": None, "status": "unmapped"}