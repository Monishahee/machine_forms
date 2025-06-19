from flask import Flask, render_template, request, redirect, send_from_directory, url_for
from werkzeug.utils import secure_filename
import firebase_admin
from firebase_admin import credentials, firestore, storage
import pandas as pd
import uuid
import os

# ----- Firebase Setup -----
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': '<YOUR_PROJECT_ID>.appspot.com'
})
db = firestore.client()
bucket = storage.bucket()

# ----- Flask App Setup -----
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

# Temporary storage across forms
session_data = {}

# ----- Helpers -----
def upload_image(file_storage, folder):
    if file_storage and file_storage.filename:
        filename = secure_filename(file_storage.filename)
        local_path = os.path.join(UPLOAD_FOLDER, filename)
        file_storage.save(local_path)
        blob = bucket.blob(f"{folder}/{filename}")
        blob.upload_from_filename(local_path)
        blob.make_public()
        return blob.public_url
    return ""

def save_to_firestore(data):
    data['timestamp'] = firestore.SERVER_TIMESTAMP
    doc_id = str(uuid.uuid4())
    db.collection('vendor_forms').document(doc_id).set(data)

# ----- Routes -----
@app.route('/')
def index():
    return render_template('vendor_form.html')

@app.route('/submit_vendor', methods=['POST'])
def submit_vendor():
    # Save vendor details
    for field in ['company_name','vendor_name','address','email','phone','gstin',
                  'website','payment_terms','associated_from','validity',
                  'approved_by','identification','feedback','remarks',
                  'enquired_part','visited_date','nda_signed','detailed_evaluation']:
        session_data[field] = request.form.get(field,"")

    # Upload company image
    session_data['company_image_url'] = upload_image(request.files.get('company_image'), 'company_images')
    return redirect(url_for('machine_entry'))

@app.route('/machine_entry', methods=['GET','POST'])
def machine_entry():
    if request.method == 'POST':
        session_data['machine'] = request.form['machine']
        session_data['size'] = request.form['size']
        session_data['hour_rate'] = request.form['hour_rate']
        images = request.files.getlist('machine_images')
        session_data['machine_images_urls'] = [upload_image(img, 'machine_images') for img in images]
        return redirect(url_for('specs_form'))
    return render_template('machine_entry.html')

@app.route('/specs_form', methods=['GET','POST'])
def specs_form():
    if request.method == 'POST':
        for key, val in request.form.items():
            if key not in ['action']:
                session_data[key] = val
        if request.form['action'] == 'add':
            save_to_firestore(session_data.copy())
            session_data.clear()
            return redirect(url_for('machine_entry'))
        else:
            save_to_firestore(session_data.copy())
            session_data.clear()
            return redirect(url_for('final_submit'))
    return render_template('specs_form.html',
        machine=session_data.get('machine'),
        size=session_data.get('size')
    )

@app.route('/final_submit')
def final_submit():
    return render_template('final_submit.html')

@app.route('/view_responses')
def view_responses():
    docs = db.collection('vendor_forms').order_by('timestamp').stream()
    data = [doc.to_dict() for doc in docs]
    if not data:
        return "<h3>No responses yet!</h3>"
    df = pd.DataFrame(data).drop(columns='_key_', errors='ignore')
    df['timestamp'] = df['timestamp'].apply(lambda t: t.strftime("%Y-%m-%d %H:%M:%S") if t else "")
    return render_template('view_responses.html',
                           tables=[df.to_html(classes="table table-striped", index=False)],
                           titles=df.columns.values)

@app.route('/download_excel')
def download_excel():
    docs = db.collection('vendor_forms').order_by('timestamp').stream()
    data = [doc.to_dict() for doc in docs]
    if not data:
        return "No data to download.", 404
    df = pd.DataFrame(data).drop(columns='_key_', errors='ignore')
    df['timestamp'] = df['timestamp'].apply(lambda t: t.strftime("%Y-%m-%d %H:%M:%S") if t else "")
    path = os.path.join(DATA_FOLDER, 'responses.xlsx')
    df.to_excel(path, index=False, engine='openpyxl')
    return send_from_directory(DATA_FOLDER, 'responses.xlsx', as_attachment=True)

# Entry point
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)












