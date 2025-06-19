from flask import Flask, render_template, request, redirect, session, url_for
from flask_session import Session
import os
import json
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Upload folders
UPLOAD_FOLDER = 'uploads'
COMPANY_IMG_FOLDER = os.path.join(UPLOAD_FOLDER, 'company_board')
MACHINE_IMG_FOLDER = os.path.join(UPLOAD_FOLDER, 'machine_images')
os.makedirs(COMPANY_IMG_FOLDER, exist_ok=True)
os.makedirs(MACHINE_IMG_FOLDER, exist_ok=True)

# Google Sheets setup
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
client = gspread.authorize(CREDS)
SHEET_NAME = "MachineFormResponses"
worksheet = client.open(SHEET_NAME).sheet1

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_vendor', methods=['POST'])
def submit_vendor():
    vendor_data = {
        'company_name': request.form['company_name'],
        'vendor_name': request.form['vendor_name'],
        'address': request.form['address'],
        'email': request.form['email'],
        'phone': request.form['phone'],
        'gstin': request.form['gstin'],
        'website': request.form['website'],
        'payment_terms': request.form['payment_terms'],
        'associated_from': request.form['associated_from'],
        'validity': request.form['validity'],
        'approved_by': request.form['approved_by'],
        'identification': request.form['identification'],
        'feedback': request.form['feedback'],
        'remarks': request.form['remarks'],
        'enquired_part': request.form['enquired_part'],
        'visited_date': request.form['visited_date'],
        'nda_signed': request.form['nda_signed'],
        'detailed_evaluation': request.form['detailed_evaluation']
    }

    board_img = request.files.get('company_image')
    if board_img and board_img.filename != '':
        filename = datetime.now().strftime("%Y%m%d_%H%M%S_") + board_img.filename
        image_path = os.path.join(COMPANY_IMG_FOLDER, filename)
        board_img.save(image_path)
        vendor_data['company_image'] = image_path

    session['vendor_data'] = vendor_data
    return redirect('/machine_entry')

@app.route('/machine_entry', methods=['GET', 'POST'])
def machine_entry():
    if request.method == 'POST':
        machine_name = request.form.get('machine')
        machine_size = request.form.get('size')
        hour_rate = request.form.get('hour_rate')
        machine_imgs = request.files.getlist('machine_images')

        if not machine_name or not machine_size:
            return "Missing machine name or size", 400

        image_paths = []
        for img in machine_imgs:
            if img and img.filename != '':
                filename = datetime.now().strftime("%Y%m%d_%H%M%S_") + img.filename
                image_path = os.path.join(MACHINE_IMG_FOLDER, filename)
                img.save(image_path)
                image_paths.append(image_path)

        session['current_machine'] = {
            'name': machine_name,
            'size': machine_size,
            'hour_rate': hour_rate,
            'image': ','.join(image_paths)
        }

        return redirect(f'/specs_form?machine={machine_name}&size={machine_size}')

    return render_template('machine_entry.html')

@app.route('/specs_form')
def specs_form():
    machine = request.args.get('machine')
    size = request.args.get('size')
    return render_template('specs_form.html', machine=machine, size=size)

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    specs = {key: request.form[key] for key in request.form if key not in ['action', 'machine', 'size']}
    current_machine = session.get('current_machine', {})

    machine_entry = {
        'name': current_machine.get('name', ''),
        'size': current_machine.get('size', ''),
        'hour_rate': current_machine.get('hour_rate', ''),
        'image': current_machine.get('image', ''),
        'specs': specs
    }

    if 'machine_specs' not in session:
        session['machine_specs'] = []
    session['machine_specs'].append(machine_entry)

    action = request.form.get('action')
    if action == 'add':
        return redirect('/machine_entry')
    elif action == 'submit':
        return redirect('/final_submit')
    else:
        return "Invalid action", 400

@app.route('/final_submit')
def final_submit():
    vendor = session.get('vendor_data', {})
    machines = session.get('machine_specs', [])

    if not vendor or not machines:
        return "Missing vendor or machine data", 400

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for m in machines:
        row = [
            timestamp,
            vendor.get('company_name'),
            vendor.get('vendor_name'),
            vendor.get('address'),
            vendor.get('email'),
            vendor.get('phone'),
            vendor.get('gstin'),
            vendor.get('website'),
            vendor.get('payment_terms'),
            vendor.get('associated_from'),
            vendor.get('validity'),
            vendor.get('approved_by'),
            vendor.get('identification'),
            vendor.get('feedback'),
            vendor.get('remarks'),
            vendor.get('enquired_part'),
            vendor.get('visited_date'),
            vendor.get('nda_signed'),
            vendor.get('detailed_evaluation'),
            vendor.get('company_image'),
            m['name'],
            m['size'],
            m['image'],
            json.dumps(m['specs'])
        ]
        worksheet.append_row(row)

    session.pop('vendor_data', None)
    session.pop('machine_specs', None)

    return render_template('final_submit.html', vendor=vendor, machines=machines)

@app.route('/view_responses')
def view_responses():
    records = worksheet.get_all_records()
    return render_template('view_responses.html', records=records)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)












