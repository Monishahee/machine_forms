from flask import Flask, render_template, request, redirect, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'macreq_secret_key'

# Create data folder if not exists
if not os.path.exists('data'):
    os.makedirs('data')

excel_file = 'data/responses.xlsx'

# Special spec machines (last 3)
SPECIAL = ['Spark Erosion Drill', 'Spark Electrical Discharge Machining', 'Wire Electrical Discharge Machining']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/specs_form', methods=['POST'])
def specs_form():
    session['cust'] = {
        'company_name': request.form['company_name'],
        'vendor_name': request.form['vendor_name'],
        'address': request.form['address'],
        'rate': request.form['rate']
    }
    session['machine'] = request.form['machine']
    session['size'] = request.form['size']
    return render_template('specs_form.html',
                           machine=session['machine'],
                           size=session['size'],
                           special=session['machine'] in SPECIAL)

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    cust = session.get('cust', {})
    machine = session.get('machine', '')
    size = session.get('size', '')

    specs = request.form.to_dict()
    row_data = {
        'Company Name': cust.get('company_name', ''),
        'Vendor Name': cust.get('vendor_name', ''),
        'Address': cust.get('address', ''),
        'Rate per Hour': cust.get('rate', ''),
        'Machine': machine,
        'Size': size
    }
    row_data.update(specs)

    # Save to Excel
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file)
        df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
    else:
        df = pd.DataFrame([row_data])

    df.to_excel(excel_file, index=False)

    return redirect('/success')

@app.route('/success')
def success():
    return "✅ Your machine specifications have been submitted successfully!"

if __name__ == '__main__':
    # For Render: Bind to 0.0.0.0
    app.run(host='0.0.0.0', port=5000)











