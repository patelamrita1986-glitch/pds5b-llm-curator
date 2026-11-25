import pandas as pd
import os

def evaluate_against_intact(intact_file, pipeline_file):
    if not os.path.exists(intact_file):
        print(f"Error: {intact_file} not found. Please download and extract it from IntAct FTP.")
        return
    if not os.path.exists(pipeline_file):
        print(f"Error: {pipeline_file} not found. Run pipeline.py first.")
        return

    # --- 1. Parse the IntAct MITAB file ---
    print("Parsing large IntAct file... (this may take a moment)")
    # PSI-MITAB is tab-delimited. We only need a few key columns.
    # Column 1: Interactor A ID, Column 2: Interactor B ID, Column 6: Publication ID, Column 7: Method
    intact_df = pd.read_csv(
        intact_file,
        sep='\t',
        header=None,
        usecols=[0, 1, 6, 7], # Use only columns A, B, PubID, Method
        names=['id_a', 'id_b', 'pmid', 'method'],
        dtype=str
    )

    # --- 2. Filter for PDS5B (UniProt: Q9NTI5) ---
    # The IDs in IntAct look like "uniprotkb:Q9NTI5".
    pds5b_id = "uniprotkb:Q9NTI5"
    pds5b_interactions = intact_df[
        (intact_df['id_a'].str.contains(pds5b_id, na=False)) |
        (intact_df['id_b'].str.contains(pds5b_id, na=False))
    ].copy()

    # Clean up the PMID (e.g., "pubmed:12345678" -> "12345678")
    pds5b_interactions['pmid'] = pds5b_interactions['pmid'].str.replace('pubmed:', '', regex=False)

    # --- 3. Parse your Pipeline Output ---
    pred_df = pd.read_csv(pipeline_file, sep='\t')

    # --- 4. Create Keys for Matching ---
    # We will match on PMID + Interactor Name. For IntAct, we need to extract the partner's ID.
    def get_partner(row):
        # If interactor A is PDS5B, return interactor B's ID, and vice versa.
        if pds5b_id in str(row['id_a']):
            return str(row['id_b'])
        else:
            return str(row['id_a'])

    pds5b_interactions['partner_id'] = pds5b_interactions.apply(get_partner, axis=1)

    # Clean up IntAct IDs (e.g., "uniprotkb:P12345" -> "P12345")
    pds5b_interactions['partner_id_clean'] = pds5b_interactions['partner_id'].str.replace('uniprotkb:', '', regex=False)

    # Create a matching key (PMID + Partner UniProt ID)
    intact_keys = set(pds5b_interactions['pmid'] + "_" + pds5b_interactions['partner_id_clean'])

    # Your pipeline outputs interactor names and UniProt IDs.
    # To match reliably, we'll use the UniProt ID if available, otherwise the name.
    pred_df['key'] = pred_df['pmid'].astype(str) + "_" + pred_df['uniprot'].astype(str).str.upper().str.strip()

    # --- 5. Calculate Metrics ---
    tp = 0
    fp = 0
    # For simplicity, we'll just check how many of your predictions are in IntAct.
    # A full evaluation would also check for false negatives (what IntAct has that you missed).
    
    for key in pred_df['key']:
        if key in intact_keys:
            tp += 1
        else:
            fp += 1

    total_preds = len(pred_df)
    precision = tp / total_preds if total_preds > 0 else 0.0

    # To calculate recall, we'd need to know how many total interactions exist for these PMIDs in IntAct.
    # This is a simplified version for demonstration.
    
    print("\n--- Evaluation vs. IntAct Database ---")
    print(f"Total Predictions from Pipeline: {total_preds}")
    print(f"True Positives (Matches found in IntAct): {tp}")
    print(f"False Positives (Not found in IntAct): {fp}")
    print(f"Precision (TP / Total): {precision:.2f}")
    print("---------------------------------------")
    print("Note: Recall is not calculated here, as it requires knowing all possible interactions in IntAct for the given papers.")

if __name__ == "__main__":
    # The default name for the extracted IntAct file is often 'intact.txt'
    # You may need to change this to the actual filename you extracted.
    evaluate_against_intact('intact.txt', 'output/curated_records.tsv')
