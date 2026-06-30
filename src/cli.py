import argparse
import json
import os
from src.extractors import extract_from_csv, extract_from_pdf, extract_from_github
from src.merger import merge_records
from src.projector import project_output

def main():
    parser = argparse.ArgumentParser(description="Multi-Source Candidate Data Transformer")
    parser.add_argument("--inputs", nargs="+", help="Paths to input files (CSV, PDF)", required=True)
    parser.add_argument("--config", help="Path to runtime JSON config", required=True)
    parser.add_argument("--output", help="Path to save output JSON", required=False)
    
    args = parser.parse_args()
    
    # 1. Load config
    with open(args.config, 'r') as f:
        config = json.load(f)
        
    # 2. Extract
    all_extracted = []
    for input_val in args.inputs:
        if input_val.startswith("http://") or input_val.startswith("https://"):
            if "github.com" in input_val or "api.github.com" in input_val:
                all_extracted.extend(extract_from_github(input_val))
            else:
                print(f"Warning: Unsupported URL {input_val}")
            continue

        filepath = input_val
        if not os.path.exists(filepath):
            print(f"Warning: File not found {filepath}")
            continue
            
        ext = filepath.split('.')[-1].lower()
        if ext == 'csv':
            all_extracted.extend(extract_from_csv(filepath))
        elif ext == 'pdf':
            all_extracted.extend(extract_from_pdf(filepath))
        else:
            print(f"Warning: Unsupported file type for {filepath}")
            
    # 3. Merge
    canonical_profiles = merge_records(all_extracted)
    
    # 4. Project
    final_output = []
    for profile in canonical_profiles:
        projected = project_output(profile, config)
        final_output.append(projected)
        
    # 5. Output
    final_json = json.dumps(final_output, indent=2)
    print(final_json)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(final_json)
        print(f"\nSaved output to {args.output}")
        
if __name__ == "__main__":
    main()
