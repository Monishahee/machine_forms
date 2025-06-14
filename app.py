from flask import Flask, render_template, request, redirect, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'macreq_secret_key'

# Create data folder if not exists
if not os.path.exists('data'):
    os.makedirs('data')

excel_file = 'data/responses.xlsx'

# Special spec machines
SPECIAL = ['Spark Erosion Drill', 'Spark Electrical Discharge Machining', 'Wire Electrical Discharge Machining']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_customer', methods=['POST'])
def set_customer():
    session['customer'] = {
        'company': request.form['company'],
        'vendor': request.form['vendor'],
        'address': request.form['address']
    }
    return redirect('/specs_form')

@app.route('/specs_form')
def specs_form():
    if 'customer' not in session:
        return redirect('/')
    return render_template('specs_form.html', machine="", size="", special=False)

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    cust = session.get('customer', {})
    machine = request.form.get('machine', '')
    size = request.form.get('size', '')
    rate = request.form.get('rate', '')

    specs = request.form.to_dict()
    specs.pop('rate', None)  # remove rate from specs, it's added separately

    row_data = {
        'Company Name': cust.get('company', ''),
from flask import Flask, render_template, request, redirect, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'macreq_secret_key'

# Make sure data folder exists
if not os.path.exists('data'):
    os.makedirs('data')

excel_file = 'data/responses.xlsx'

# Machines with special EDM specs
SPECIAL = ['Spark Erosion Drill', 'Spark Electrical Discharge Machining', 'Wire Electrical Discharge Machining']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/specs_form', methods=['POST'])
def specs_form():
    # Save customer details once
    if 'cust' not in session:
        session['cust'] = {
            'company_name': request.form['company_name'],
            'vendor_name': request.form['vendor_name'],
            'address': request.form['address'],
            'rate': request.form['rate']
        }

    # Save machine and size for current entry
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

    # Append to Excel
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file)
        df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
    else:
        df = pd.DataFrame([row_data])

    df.to_excel(excel_file, index=False)

    # Ask user if they want to add more or finish
    return render_template('success.html')

@app.route('/finish')
def finish():
    session.clear()
    return "✅ All machine entries have been saved successfully."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)













