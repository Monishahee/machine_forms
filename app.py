from flask import Flask, render_template, request, redirect, send_from_directory
from werkzeug.utils import secure_filename
from tinydb import TinyDB
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'
DB_FILE = os.path.join(DATA_FOLDER, 'responses.json')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

db = TinyDB(DB_FILE)
session_data = {}

@app.route('/')
def index():
    return render_template('vendor_form.html')

@app.route('/submit_vendor', methods=['POST'])
def submit_vendor():
    session_data['company_name'] = request.form.get('company_name', '')
    session_data['vendor_name'] = request.form.get('vendor_name', '')
    # ... other fields ...
    image = request.files.get('board_image')
    if image and image.filename:
        filename = secure_filename(image.filename)
        image.save(os.path.join(UPLOAD_FOLDER, filename))
        session_data['company_image'] = filename
    else:
        session_data['company_image'] = ''
    return redirect('/machine_entry')

@app.route('/machine_entry', methods=['GET', 'POST'])
def machine_entry():
    if request.method == 'POST':
        session_data['machine'] = request.form.get('machine', '')
        session_data['size'] = request.form.get('size', '')
        session_data['hour_rate'] = request.form.get('hour_rate', '')
        return redirect('/specs_form')
    return render_template('machine_entry.html')

@app.route('/specs_form')
def specs_form():
    return render_template('specs_form.html', machine=session_data.get('machine'), size=session_data.get('size'))

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    fields = [
        'make', 'model_year', 'type', 'axis_config', 'x_travel', 'y_travel', 'z_travel',
        # ... other fields ...
    ]
    for field in fields:
        session_data[field] = request.form.get(field, '')
    
    db.insert(session_data.copy())  # Save to JSON DB

    action = request.form.get('action')
    if action == 'add':
        return redirect('/machine_entry')
    elif action == 'submit':
        return redirect('/final_submit')

@app.route('/final_submit')
def final_submit():
    return render_template('final_submit.html')

@app.route('/view_responses')
def view_responses():
    records = db.all()
    return render_template('view_responses.html', records=records)

@app.route('/download_json')
def download_json():
    return send_from_directory(DATA_FOLDER, 'responses.json', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)













