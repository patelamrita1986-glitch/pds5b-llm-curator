import pandas as pd
import xml.etree.ElementTree as ET

# A small mapping of common methods to official PSI-MI IDs
MI_MAPPING = {
    "pulldown": "MI:0004",
    "spr": "MI:0111",
    "x-ray crystallography": "MI:0114",
    "cryo-em": "MI:0118",
    "itc": "MI:0065",
    "not stated": "MI:0000"
}

def create_psimi_xml(tsv_path, xml_path):
    df = pd.read_csv(tsv_path, sep="\t")
    
    # Create root element with PSI-MI namespace
    root = ET.Element("entrySet", xmlns="http://psi.hupo.org/mi/mif")
    entry = ET.SubElement(root, "entry")
    
    interaction_list = ET.SubElement(entry, "interactionList")
    
    for idx, row in df.iterrows():
        if pd.isna(row['interactor']) or row['interactor'] == "":
            continue
            
        interaction = ET.SubElement(interaction_list, "interaction")
        
        # Add Experimental Method (Mapping text to MI ID)
        method_text = str(row['method']).lower().strip()
        mi_id = MI_MAPPING.get(method_text, "MI:0000") # 0000 is 'experimental method unknown'
        
        exp = ET.SubElement(interaction, "experimentList")
        exp_desc = ET.SubElement(exp, "experimentDescription")
        method = ET.SubElement(exp_desc, "interactionDetectionMethod")
        ET.SubElement(method, "names").text = str(row['method'])
        ET.SubElement(method, "xref").text = mi_id
        
        # Add Interactor (PDS5B and the partner)
        p_list = ET.SubElement(interaction, "participantList")
        
        # PDS5B
        p1 = ET.SubElement(p_list, "participant")
        ET.SubElement(p1, "interactorRef").text = "PDS5B"
        ET.SubElement(p1, "uniprotRef").text = "Q9NTI5"
        
        # Partner
        p2 = ET.SubElement(p_list, "participant")
        ET.SubElement(p2, "interactorRef").text = str(row['interactor'])
        ET.SubElement(p2, "uniprotRef").text = str(row['uniprot'])

    # Save the XML
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ") # Requires Python 3.9+
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    print(f"Successfully exported to {xml_path}")

if __name__ == "__main__":
    create_psimi_xml("output/curated_records.tsv", "output/interactions_psimi.xml")