from flask import Flask, render_template, request, redirect, session
import os
import pandas as pd
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Upload folders
UPLOAD_FOLDER = 'uploads'
COMPANY_IMG_FOLDER = os.path.join(UPLOAD_FOLDER, 'company_board')
MACHINE_IMG_FOLDER = os.path.join(UPLOAD_FOLDER, 'machine_images')
EXCEL_PATH = 'data/responses.xlsx'

# Create directories
os.makedirs(COMPANY_IMG_FOLDER, exist_ok=True)
os.makedirs(MACHINE_IMG_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)

# If Excel doesn't exist, create with headers
if not os.path.exists(EXCEL_PATH):
    df = pd.DataFrame(columns=[
        "Timestamp", "Company Name", "Vendor Manager", "Address", "Email", "Phone Number",
        "GSTIN", "Contact Name", "Contact No", "Mail ID", "Website", "Payment Terms",
        "Board Image", "Machine Name", "Machine Size", "Machine Image", "Specs"
    ])
    df.to_excel(EXCEL_PATH, index=False)


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

    # Fix: match the name in HTML
    board_img = request.files.get('company_image')
    if board_img:
        filename = datetime.now().strftime("%Y%m%d_%H%M%S_") + board_img.filename
        board_img_path = os.path.join(COMPANY_IMG_FOLDER, filename)
        board_img.save(board_img_path)
        vendor_data['company_image'] = board_img_path
    else:
        vendor_data['company_image'] = ''

    session['vendor_data'] = vendor_data
    session['machine_entries'] = []
    return redirect('/machine_entry')

    board_img = request.files.get('board_image')
    if board_img:
        filename = datetime.now().strftime("%Y%m%d_%H%M%S_") + board_img.filename
        board_img_path = os.path.join(COMPANY_IMG_FOLDER, filename)
        board_img.save(board_img_path)
        vendor_data['board_image'] = board_img_path
    else:
        vendor_data['board_image'] = ''

    session['vendor_data'] = vendor_data
    session['machine_entries'] = []  # clear previous
    return redirect('/machine_entry')


@app.route('/machine_entry', methods=['GET', 'POST'])
def machine_entry():
    if request.method == 'POST':
        machine_name = request.form.get('machine_name')
        machine_size = request.form.get('machine_size')
        machine_img = request.files.get('machine_image')

        if not machine_name or not machine_size:
            return "Missing machine name or size", 400

        filename = ''
        if machine_img:
            filename = datetime.now().strftime("%Y%m%d_%H%M%S_") + machine_img.filename
            img_path = os.path.join(UPLOAD_FOLDER, filename)
            machine_img.save(img_path)

        entry = {
            'name': machine_name,
            'size': machine_size,
            'image': filename,
            'specs': {}
        }

        machine_entries = session.get('machine_entries', [])
        machine_entries.append(entry)
        session['machine_entries'] = machine_entries

        return redirect(f'/specs_form?machine={machine_name}&size={machine_size}')

    return render_template('machine_entry.html')



@app.route('/submit_machine', methods=['POST'])
def submit_machine():
    machine = request.form.get('machine')
    size = request.form.get('size')

    if not machine or not size:
        return "Bad Request: Missing data", 400

    return redirect(url_for('specs_form', machine=machine, size=size))



@app.route('/specs_form', methods=['GET'])
def specs_form():
    return render_template('specs_form.html',
                           machine=session['current_machine']['name'],
                           size=session['current_machine']['size'])


@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    specs = {key: request.form[key] for key in request.form}

    machine_img = request.files.get('machine_image')
    img_path = ''
    if machine_img:
        filename = datetime.now().strftime("%Y%m%d_%H%M%S_") + machine_img.filename
        img_path = os.path.join(MACHINE_IMG_FOLDER, filename)
        machine_img.save(img_path)

    machine_data = {
        'name': session['current_machine']['name'],
        'size': session['current_machine']['size'],
        'specs': specs,
        'image': img_path
    }

    session['machine_entries'].append(machine_data)
    return redirect('/machine_entry')  # allow adding more

@app.route('/final_submit', methods=['POST'])
def final_submit():
    try:
        # Get existing session data
        customer_data = session.get('customer_data', {})
        machine_entries = session.get('machine_entries', [])

        # Combine everything into one dictionary
        final_data = {
            'customer_details': customer_data,
            'machines': machine_entries
        }

        # Save to Excel file
        df_customer = pd.DataFrame([customer_data])
        df_machines = pd.DataFrame(machine_entries)

        file_path = os.path.join(DATA_FOLDER, 'responses.xlsx')
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a' if os.path.exists(file_path) else 'w') as writer:
            df_customer.to_excel(writer, sheet_name='Customer', index=False)
            df_machines.to_excel(writer, sheet_name='Machines', index=False)

        return render_template('final_submit.html')

    except Exception as e:
        return f"An error occurred: {str(e)}", 400


    vendor = session['vendor_data']
    machines = session['machine_entries']
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    all_rows = []
    for m in machines:
        row = {
            "Timestamp": timestamp,
            "Company Name": vendor['company_name'],
            "Vendor Manager": vendor['vendor_name'],
            "Address": vendor['address'],
            "Email": vendor['email'],
            "Phone Number": vendor['phone'],
            "GSTIN": vendor['gstin'],
            "Website": vendor['website'],
            "Payment Terms": vendor['payment_terms'],
            "Associated From": vendor['associated_from'],
            "Validity of Approval": vendor['validity'],
            "Approved By": vendor['approved_by'],
            "Identification": vendor['identification'],
            "Feedback": vendor['feedback'],
            "Remarks": vendor['remarks'],
            "Enquired Part": vendor['enquired_part'],
            "Visited Date": vendor['visited_date'],
            "NDA Signed": vendor['nda_signed'],
            "Detailed Evaluation": vendor['detailed_evaluation'],
            "Board Image": vendor['company_image'],
            "Machine Name": m['name'],
            "Machine Size": m['size'],
            "Machine Image": m['image'],
           "Specs": json.dumps(m['specs'])
}

        all_rows.append(row)

    # Append to Excel
    existing_df = pd.read_excel(EXCEL_PATH)
    new_df = pd.DataFrame(all_rows)
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    combined_df.to_excel(EXCEL_PATH, index=False)

    return render_template('final_submit.html', vendor=vendor, machines=machines)

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use Render's assigned port or 5000 locally
    app.run(host='0.0.0.0', port=port)










