from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key'

# Create required folders
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'responses', 'uploads')
EXCEL_PATH = os.path.join(BASE_DIR, 'responses', 'responses.xlsx')
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize Excel
if not os.path.exists(EXCEL_PATH):
    df = pd.DataFrame()
    df.to_excel(EXCEL_PATH, index=False)

@app.route('/')
def vendor_form():
    return render_template('vendor_form.html')

@app.route('/submit_vendor', methods=['POST'])
def submit_vendor():
    session['vendor_data'] = {
        'Company Name': request.form.get('company_name'),
        'Vendor Name': request.form.get('vendor_name'),
        'Address': request.form.get('address'),
        'GSTIN': request.form.get('gstin'),
        'Contact Name': request.form.get('contact_name'),
        'Contact No': request.form.get('contact_no'),
        'Mail Id': request.form.get('mail_id'),
        'Website': request.form.get('website'),
        'Payment Terms': request.form.get('payment_terms'),
        'Basis of Approval': request.form.get('basis_of_approval'),
        'Associated from': request.form.get('associated_from'),
        'Validity of Approval': request.form.get('validity_of_approval'),
        'Approved by': request.form.get('approved_by'),
        'Identification': request.form.get('identification'),
        'Feedback': request.form.get('feedback'),
        'Remarks': request.form.get('remarks'),
        'Enquired Part': request.form.get('enquired_part'),
        'Visited date': request.form.get('visited_date'),
        'NDA Signed': request.form.get('nda_signed'),
        'Detailed Evaluation': request.form.get('detailed_evaluation')
    }
    session['machine_entries'] = []
    return redirect(url_for('machine_entry'))

@app.route('/machine_entry')
def machine_entry():
    machines = ['Vertical Turning Turret', '5 Axis Milling', 'Turning Lathe', 'Spark EDM']
    sizes = ['S1', 'S2', 'M1', 'M2', 'L1', 'L2']
    return render_template('machine_entry.html', machines=machines, sizes=sizes)

@app.route('/submit_machine', methods=['POST'])
def submit_machine():
    machine = request.form.get('machine')
    size = request.form.get('size')
    hour_rate = request.form.get('hour_rate')

    # Handle image
    image_file = request.files.get('machine_image')
    img_path = ''
    if image_file and image_file.filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        folder = os.path.join(UPLOAD_DIR, secure_filename(machine))
        os.makedirs(folder, exist_ok=True)
        filename = f"{secure_filename(machine)}_{timestamp}_{secure_filename(image_file.filename)}"
        img_path = os.path.join(folder, filename)
        image_file.save(img_path)

    session['current_machine'] = {
        'Machine': machine,
        'Size': size,
        'Hour Rate': hour_rate,
        'Image Path': img_path
    }

    return redirect(url_for('specs_form'))

@app.route('/specs_form')
def specs_form():
    return render_template('specs_form.html', machine=session['current_machine']['Machine'], size=session['current_machine']['Size'])

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    specs = {
        'Make': request.form.get('make'),
        'Model/Year': request.form.get('model_year'),
        'Type': request.form.get('type'),
        'Axis Configuration': request.form.get('axis_config'),
        'Spindle Power': request.form.get('spindle_power'),
        'Controller': request.form.get('controller')
    }

    full_entry = {**session['vendor_data'], **session['current_machine'], **specs}
    session['machine_entries'].append(full_entry)

    if 'add_another' in request.form:
        return redirect(url_for('machine_entry'))
    else:
        return redirect(url_for('final_submit'))

@app.route('/final_submit')
def final_submit():
    machine_entries = session.get('machine_entries', [])
    if not machine_entries:
        return "❌ No machines submitted.", 400

    df_new = pd.DataFrame(machine_entries)

    if os.path.exists(EXCEL_PATH):
        df_old = pd.read_excel(EXCEL_PATH)
        df_combined = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_excel(EXCEL_PATH, index=False)

    session.clear()
    return "✅ Submission successful. Data & images saved."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)







