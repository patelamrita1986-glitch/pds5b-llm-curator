import requests, json, os, sys

def fetch_abstract(pmid: str) -> dict:
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": f"EXT_ID:{pmid} AND SRC:MED",
        "format": "json",
        "resultType": "core",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    hits = r.json().get("resultList", {}).get("result", [])
    if not hits:
        raise ValueError(f"No record found for PMID {pmid}")
    hit = hits[0]
    return {
        "pmid": pmid,
        "title": hit.get("title", ""),
        "abstract": hit.get("abstractText", ""),
    }

if __name__ == "__main__":
    pmid = sys.argv[1]
    data = fetch_abstract(pmid)
    os.makedirs("data/abstracts", exist_ok=True)
    with open(f"data/abstracts/{pmid}.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved PMID {pmid}: {data['title'][:80]}")