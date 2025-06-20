# app.py
from flask import (Flask, render_template, request, redirect, url_for,
                   send_from_directory, flash)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os, pandas as pd, base64, requests
from datetime import datetime

app = Flask(__name__)
app.config.update(
    SECRET_KEY='your-secret-key',
    UPLOAD_FOLDER='uploads',
    SQLALCHEMY_DATABASE_URI='sqlite:///app.db',
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16 MB limit
)
db = SQLAlchemy(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    company_name = db.Column(db.String(200))
    vendor_name = db.Column(db.String(200))
    address = db.Column(db.String(300))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(100))
    gstin = db.Column(db.String(100))
    website = db.Column(db.String(200))
    payment_terms = db.Column(db.String(200))
    associated_from = db.Column(db.String(100))
    validity = db.Column(db.String(100))
    approved_by = db.Column(db.String(200))
    identification = db.Column(db.String(200))
    feedback = db.Column(db.String(200))
    remarks = db.Column(db.String(300))
    enquired_part = db.Column(db.String(200))
    visited_date = db.Column(db.String(100))
    contact_name = db.Column(db.String(200))
    contact_no = db.Column(db.String(100))
    contact_email = db.Column(db.String(200))
    nda_signed = db.Column(db.String(10))
    detailed_evaluation = db.Column(db.String(300))
    company_image = db.Column(db.String(300))

    # Machine Entry Fields
    machine = db.Column(db.String(200))
    size = db.Column(db.String(100))
    hour_rate = db.Column(db.String(50))
    machine_images = db.Column(db.Text)

    # Specs Fields (flattened if needed)
    make = db.Column(db.String(200))
    model_year = db.Column(db.String(100))
    type = db.Column(db.String(100))
    axis_config = db.Column(db.String(100))
    x_travel = db.Column(db.String(100))
    y_travel = db.Column(db.String(100))
    z_travel = db.Column(db.String(100))
    a_travel = db.Column(db.String(100))
    b_travel = db.Column(db.String(100))
    c_travel = db.Column(db.String(100))
    max_part_size = db.Column(db.String(100))
    max_part_height = db.Column(db.String(100))
    spindle_taper = db.Column(db.String(100))
    spindle_power = db.Column(db.String(100))
    spindle_torque = db.Column(db.String(100))
    main_spindle_rpm = db.Column(db.String(100))
    aux_spindle_rpm = db.Column(db.String(100))
    max_table_load = db.Column(db.String(100))
    coolant_pressure = db.Column(db.String(100))
    pallet_type = db.Column(db.String(100))
    tolerance_standard = db.Column(db.String(100))
    accuracy_xyz = db.Column(db.String(100))
    accuracy_abc = db.Column(db.String(100))
    accuracy_table = db.Column(db.String(100))
    angle_head = db.Column(db.String(100))
    controller = db.Column(db.String(100))
    cad_software = db.Column(db.String(100))
    cam_software = db.Column(db.String(100))
    wire_diameter = db.Column(db.String(100))
    taper_degree = db.Column(db.String(100))
    max_cutting_thickness = db.Column(db.String(100))
    surface_finish = db.Column(db.String(100))
    electrode_diameter = db.Column(db.String(100))
    spindle_stroke = db.Column(db.String(100))
    table_size = db.Column(db.String(100))
    sink_size = db.Column(db.String(100))

with app.app_context():
    db.create_all()


# Google Apps Script endpoint (replace with your actual URL)
GAS_URL = "https://script.google.com/macros/s/AKfycbyyFHjwHkZP1Ljkxh8fM4_uPQviaCpttByQnj2jt4voWKRD21Q_IGEwdGMTSn3J0pRd/exec"

@app.route('/')
def vendor_form():
    return render_template('vendor_form.html')

@app.route('/submit_vendor', methods=['POST'])
def submit_vendor():
    data = request.form.to_dict()
    img = request.files.get('board_image')
    data['company_image'] = ""
    if img and img.filename:
        fn = secure_filename(img.filename)
        img.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
        data['company_image'] = fn
    entry = Entry(**data)
    db.session.add(entry)
    db.session.commit()
    return redirect(url_for('machine_entry', entry_id=entry.id))

@app.route('/machine_entry/<int:entry_id>', methods=['GET', 'POST'])
def machine_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    if request.method == 'POST':
        machine = request.form['machine']
        size = request.form['size']
        hr = request.form['hour_rate']
        fnames = []
        for img in request.files.getlist('machine_images'):
            if img and img.filename:
                fn = secure_filename(img.filename)
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                fnames.append(fn)
        entry.machine = machine
        entry.size = size
        entry.hour_rate = hr
        entry.machine_images = ",".join(fnames)
        db.session.commit()
        return redirect(url_for('specs_form', entry_id=entry.id))
    return render_template('machine_entry.html', entry=entry)

@app.route('/specs_form/<int:entry_id>', methods=['GET', 'POST'])
def specs_form(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    if request.method == 'POST':
        specs = request.form.to_dict()
        entry.specs = str(specs)
        db.session.commit()
        # Optional: send to Google Sheets
        send_to_gas(entry)
        flash('✅ Submission complete! We saved everything.')
        return redirect(url_for('view_responses'))
    return render_template('specs_form.html', entry=entry)

def send_to_gas(entry):
    data = {
        'company_name': entry.company_name,
        'vendor_name': entry.vendor_name,
        'address': entry.address,
        'email': entry.email,
        'phone': entry.phone,
        'gstin': entry.gstin,
        'machine': entry.machine,
        'size': entry.size,
        'hour_rate': entry.hour_rate,
        'specs': entry.specs
    }
    # Attach images as base64
    for field, fn in [('company_image', entry.company_image)] + \
                     [(f'machine_img{i+1}', fn) for i, fn in enumerate(entry.machine_images.split(','))]:
        path = os.path.join(app.config['UPLOAD_FOLDER'], fn)
        if fn and os.path.exists(path):
            with open(path, 'rb') as f:
                data[field] = base64.b64encode(f.read()).decode('utf-8')
                data[field + '_name'] = fn
    requests.post(GAS_URL, json=data)

@app.route('/view_responses')
def view_responses():
    entries = Entry.query.order_by(Entry.timestamp.desc()).all()
    return render_template('view_responses.html', entries=entries)

@app.route('/download_excel')
def download_excel():
    df = pd.DataFrame([
        {
            'Timestamp': e.timestamp,
            'Company': e.company_name,
            'Vendor': e.vendor_name,
            'Machine': e.machine,
            'Size': e.size,
            'Hour Rate': e.hour_rate,
            'Specs': e.specs
        } for e in Entry.query.all()
    ])
    os.makedirs('data', exist_ok=True)
    out = 'data/responses.xlsx'
    df.to_excel(out, index=False, engine='openpyxl')
    return send_from_directory('data', 'responses.xlsx', as_attachment=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
print("Registered Routes:")
for rule in app.url_map.iter_rules():
    print(rule.endpoint, rule)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)


















