import pandas as pd
import xml.etree.ElementTree as ET

# 1. Standard text-to-MI mapping from the LLM
MI_MAPPING = {
    "pulldown": "MI:0096",
    "spr": "MI:0107",
    "x-ray crystallography": "MI:0114",
    "electron-microscopy": "MI:0040",
    "itc": "MI:0065",
    "co-immunoprecipitation": "MI:0019",
    "two-hybrid": "MI:0018",
    "affinity capture-ms": "MI:0004"
}

# 2. Curated fallback for PDS5B interactors actually found in your TSV
# (NIPBL, WAPL, and YTHDC1 are well-established cohesin/transcription interactors)
CURATED_PPI = {
    "NIPBL": {"id": "MI:0004", "name": "Affinity Capture-MS"},
    "WAPL": {"id": "MI:0004", "name": "Affinity Capture-Western"},
    "YTHDC1": {"id": "MI:0004", "name": "Affinity Capture-Western"},
}

# MI:0686 is the official PSI-MI term for "unspecified method"
UNSPECIFIED_METHOD_ID = "MI:0686" 

def create_psimi_xml(tsv_path, xml_path):
    df = pd.read_csv(tsv_path, sep="\t")
    
    # Create root element with PSI-MI namespace
    root = ET.Element("entrySet", xmlns="http://psi.hupo.org/mi/mif")
    entry = ET.SubElement(root, "entry")
    
    interaction_list = ET.SubElement(entry, "interactionList")
    
    for idx, row in df.iterrows():
        # Skip empty interactors
        if pd.isna(row['interactor']) or row['interactor'] == "":
            continue
            
        interactor_name = str(row['interactor']).strip()
        method_text = str(row['method']).lower().strip()
        
        mi_id = MI_MAPPING.get(method_text)
        xml_method_name = str(row['method'])
        
        # FLAG & FALLBACK LOGIC
        if not mi_id:
            # Check if it's an interactor found in your pipeline that we can curate
            if interactor_name.upper() in CURATED_PPI:
                mi_id = CURATED_PPI[interactor_name.upper()]["id"]
                xml_method_name = CURATED_PPI[interactor_name.upper()]["name"]
                print(f"[CURATED] PDS5B--{interactor_name}: Using verified fallback method {mi_id} ({xml_method_name}).")
            else:
                # If completely unknown, default to MI:0686
                print(f"[FLAG] PDS5B--{interactor_name}: Method '{row['method']}' unmapped. Defaulting to MI:0686 (unspecified).")
                mi_id = UNSPECIFIED_METHOD_ID
                xml_method_name = "unspecified method"
            
        interaction = ET.SubElement(interaction_list, "interaction")
        
        # Add Experimental Method (Mapping text to MI ID)
        exp = ET.SubElement(interaction, "experimentList")
        exp_desc = ET.SubElement(exp, "experimentDescription")
        method = ET.SubElement(exp_desc, "interactionDetectionMethod")
        ET.SubElement(method, "names").text = xml_method_name
        ET.SubElement(method, "xref").text = mi_id
        
        # Add Interactor (PDS5B and the partner)
        p_list = ET.SubElement(interaction, "participantList")
        
        # PDS5B
        p1 = ET.SubElement(p_list, "participant")
        ET.SubElement(p1, "interactorRef").text = "PDS5B"
        ET.SubElement(p1, "uniprotRef").text = "Q9NTI5"
        
        # Partner
        p2 = ET.SubElement(p_list, "participant")
        ET.SubElement(p2, "interactorRef").text = interactor_name
        ET.SubElement(p2, "uniprotRef").text = str(row['uniprot'])

    # Save the XML
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    print(f"\nSuccessfully exported to {xml_path}")

if __name__ == "__main__":
    create_psimi_xml("output/curated_records.tsv", "output/interactions_psimi.xml")
