#!/usr/bin/env python3
"""
🧬 Bio-Forge Adapter v1.0
━━━━━━━━━━━━━━━━━━━━━━━━
Convertit les protéines du Bio-Compiler (fichiers .cs générés) 
en format "Kata" compatible avec CodeForge (InGeN-Blackproject).

Usage:
    python bio_to_codeforge_adapter.py --config proteome_config_949.json --slot ./slot --output bio_library.json
"""

import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

# ══════════════════════════════════════════════════════════════════════════════
# NETTOYEUR DE JSON (Tolérant aux espaces parasites)
# ══════════════════════════════════════════════════════════════════════════════
def clean_json_keys(obj: Any) -> Any:
    """Supprime récursivement les espaces en début/fin des clés JSON."""
    if isinstance(obj, dict):
        return {k.strip(): clean_json_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_json_keys(elem) for elem in obj]
    return obj

# ══════════════════════════════════════════════════════════════════════════════
# EXTRACTEUR DE CODE C#
# ══════════════════════════════════════════════════════════════════════════════
def extract_constructor_body(cs_code: str) -> str:
    """
    Extrait le corps du constructeur 'public BioProgram()' 
    qui contient le code de la protéine généré.
    Gère les accolades imbriquées.
    """
    # Chercher le début du constructeur
    match = re.search(r"public\s+BioProgram\s*\(\s*\)\s*\{", cs_code)
    if not match:
        return "// Erreur: Constructeur BioProgram() introuvable."
    
    start_idx = match.end()
    brace_count = 1
    i = start_idx
    
    # Parcourir jusqu'à trouver l'accolade fermante correspondante
    while i < len(cs_code) and brace_count > 0:
        if cs_code[i] == '{':
            brace_count += 1
        elif cs_code[i] == '}':
            brace_count -= 1
        i += 1
    
    if brace_count != 0:
        return "// Erreur: Accolades déséquilibrées."
    
    # Extraire et nettoyer le contenu
    body = cs_code[start_idx:i-1]
    
    # Supprimer l'indentation excessive (souvent 8 espaces au premier niveau)
    lines = body.split('\n')
    cleaned_lines = []
    for line in lines:
        # Retirer jusqu'à 8 espaces en début de ligne
        if line.startswith("        "):
            cleaned_lines.append(line[8:])
        elif line.startswith("    "):
            cleaned_lines.append(line[4:])
        else:
            cleaned_lines.append(line)
            
    return '\n'.join(cleaned_lines).strip()

# ══════════════════════════════════════════════════════════════════════════════
# MAPPING DES FAMILLES (Opérons -> Catégories CodeForge)
# ══════════════════════════════════════════════════════════════════════════════
OPERON_MAPPING = {
    "OP_STRESS": "Biologie / Stress & Réparation",
    "OP_GROWTH": "Biologie / Métabolisme & Croissance",
    "OP_REPLICATION": "Biologie / Cycle Cellulaire & Mitose",
    "OP_APOPTOSIS": "Biologie / Mort Cellulaire (Apoptose)",
    "OP_CIRCADIAN": "Biologie / Rythmes Circadiens",
    "OP_MEMORY": "Biologie / Mémoire Épigénétique",
    "OP_IO": "Système / Entrées-Sorties",
    "OP_CRYPTO": "Système / Cryptographie",
    "OP_NETWORK": "Système / Réseau",
    "OP_APPLICATIONS": "Système / Ordonnancement",
    "OP_SECURITY": "Système / Sécurité",
    "OP_METABOLISM": "Système / Métabolisme de base"
}

def get_family(prot_id: str, operons: List[Dict]) -> str:
    """Détermine la famille de la protéine selon son opéron."""
    for op in operons:
        genes = op.get("genes", [])
        if prot_id in genes:
            op_id = op.get("id", "")
            return OPERON_MAPPING.get(op_id, f"Biologie / {op_id}")
    return "Biologie / Générale"

def get_tags(prot_def: Dict, operons: List[Dict]) -> List[str]:
    """Génère les tags pour CodeForge."""
    tags = ["bio-compiler", "cellular-automata"]
    
    # Tags épigénétiques
    markers = prot_def.get("epigenetic_markers", [])
    tags.extend([f"epi:{m}" for m in markers[:3]]) # Limiter à 3 pour ne pas surcharger
    
    # Tags opéron
    for op in operons:
        if prot_def["id"] in op.get("genes", []):
            tags.append(f"operon:{op['id']}")
            break
            
    # Tags phase cellulaire
    phase = prot_def.get("meta", {}).get("cell_phase", "")
    if phase:
        tags.append(f"phase:{phase}")
        
    return list(set(tags)) # Dédupliquer

# ══════════════════════════════════════════════════════════════════════════════
# GÉNÉRATEUR PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
def generate_library(config_path: str, slot_dir: str, output_path: str):
    print(f"🧬 Bio-Forge Adapter v1.0")
    print(f"   Config: {config_path}")
    print(f"   Slot:   {slot_dir}")
    print(f"   Output: {output_path}")
    print("━" * 50)

    # 1. Charger et nettoyer la config
    try:
        raw_config = json.loads(Path(config_path).read_text(encoding="utf-8"))
        config = clean_json_keys(raw_config)
    except Exception as e:
        print(f"❌ Erreur chargement config: {e}")
        return

    proteins = config.get("proteins", [])
    operons = config.get("operons", [])
    slot_path = Path(slot_dir)
    
    library = []
    generated_count = 0

    # 2. Itérer sur les protéines
    for prot in proteins:
        prot_id = prot.get("id", "unknown")
        filename = prot.get("filename", f"{prot_id}.cs")
        
        # Trouver le fichier généré
        cs_file = slot_path / filename
        if not cs_file.exists():
            print(f"⚠️  [{prot_id}] Fichier introuvable: {cs_file} (Ignoré)")
            continue

        # 3. Extraire le code
        try:
            cs_content = cs_file.read_text(encoding="utf-8")
            code_body = extract_constructor_body(cs_content)
        except Exception as e:
            print(f"❌ [{prot_id}] Erreur lecture/parsing: {e}")
            continue

        # 4. Construire l'objet Kata CodeForge
        meta = prot.get("meta", {})
        description = meta.get("docstring", prot.get("description", ""))
        # Nettoyer la description (enlever les balises XML C# pour la lisibilité)
        description = re.sub(r"///\s*<summary>|///\s*</summary>|///", "", description).strip()
        
        kata = {
            "id": f"bio_{prot_id}",
            "type": "function",
            "name": prot_id.replace("_", " ").title(), # Ex: "heatshock" -> "Heatshock"
            "language": "CSharp",
            "famille": get_family(prot_id, operons),
            "description": description,
            "parameters": [], # Les protéines utilisent l'état global
            "returns": {
                "datatype": "void",
                "description": "Modifie l'état cellulaire global (_cellularState)."
            },
            "source": code_body,
            "tags": get_tags(prot, operons)
        }
        
        library.append(kata)
        generated_count += 1
        print(f"✅ [{prot_id}] Converti -> {kata['famille']}")

    # 5. Écrire le JSON final
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(library, f, indent=2, ensure_ascii=False)
        print("━" * 50)
        print(f"🏆 Succès ! {generated_count} protéines converties.")
        print(f"👉 Importez '{output_path}' dans CodeForge.")
    except Exception as e:
        print(f"❌ Erreur écriture JSON: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Bio-Compiler proteins to CodeForge library.")
    parser.add_argument("--config", required=True, help="Path to proteome_config.json")
    parser.add_argument("--slot", default="./slot", help="Directory containing generated .cs files")
    parser.add_argument("--output", default="bio_library.json", help="Output JSON path for CodeForge")
    args = parser.parse_args()

    generate_library(args.config, args.slot, args.output)