import os
import json
import uuid
import sys
from flask import Flask, render_template, request, jsonify

# Ensure the parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.extractors import extract_from_csv, extract_from_pdf, extract_from_github
from src.merger import merge_records
from src.projector import project_output

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'files' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
        
    files = request.files.getlist('files')
    github_url = request.form.get('github_url', '').strip()
    
    # Load config
    config_filename = request.form.get('config', 'default_config.json')
    # Basic security check to prevent directory traversal
    if config_filename not in ['default_config.json', 'custom_config.json']:
        config_filename = 'default_config.json'
        
    config_path = os.path.join(os.getcwd(), config_filename)
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    all_extracted = []
    warning_messages = []
    
    # Handle GitHub URL
    if github_url:
        if "github.com" in github_url:
            all_extracted.extend(extract_from_github(github_url))
            
    # Process uploaded files
    for file in files:
        if file.filename == '':
            continue
            
        ext = file.filename.split('.')[-1].lower()
        if ext not in ['csv', 'pdf']:
            continue
            
        # Save temp file securely
        temp_filename = f"{uuid.uuid4()}_{file.filename}"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        file.save(temp_path)
        
        # Extract based on file type
        try:
            if ext == 'csv':
                all_extracted.extend(extract_from_csv(temp_path))
            elif ext == 'pdf':
                all_extracted.extend(extract_from_pdf(temp_path))
        except Exception as e:
            warning_messages.append(f"{file.filename} could not be processed.")
        finally:
            # Always clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    # Merge and project
    canonical_profiles = merge_records(all_extracted)
    
    final_output = []
    for profile in canonical_profiles:
        projected = project_output(profile, config)
        final_output.append(projected)
        
    # Calculate stats before returning
    processed_count = len(all_extracted)
    merged_count = 0
    
    for profile in final_output:
        # Count unique sources in provenance to see if it was merged
        prov_list = profile.get("provenance", [])
        unique_sources = set(p.get("source") for p in prov_list)
        if len(unique_sources) > 1:
            merged_count += 1
            
    duplicates_resolved = processed_count - len(final_output)

    return jsonify({
        "profiles": final_output,
        "stats": {
            "processed": processed_count,
            "merged": merged_count,
            "duplicates_resolved": duplicates_resolved,
            "warnings": warning_messages
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
