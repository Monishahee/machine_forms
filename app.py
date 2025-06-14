from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'macreq123'  # Required to use session

EXCEL_PATH = 'data/responses.xlsx'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/specs_form', methods=['POST'])
def specs_form():
    # Store customer info once in session
    session['customer'] = {
        'company_name': request.form['company_name'],
        'vendor_name': request.form['vendor_name'],
        'address': request.form['address']
    }
    machine_name = request.form['machine']
    machine_size = request.form['size']
    return render_template('specs_form.html', machine=machine_name, size=machine_size)

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    machine = request.form['machine']
    size = request.form['size']
    specs = dict(request.form)
    specs.pop('machine')
    specs.pop('size')

    # Combine customer + machine + specs
    final_data = {
        'Company Name': session['customer']['company_name'],
        'Vendor Name': session['customer']['vendor_name'],
        'Address': session['customer']['address'],
        'Machine': machine,
        'Size': size
    }
    final_data.update(specs)

    # Save to Excel
    df_new = pd.DataFrame([final_data])

    if os.path.exists(EXCEL_PATH):
        df_existing = pd.read_excel(EXCEL_PATH)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_excel(EXCEL_PATH, index=False)

    return redirect(url_for('index'))  # Return to index to submit next machine

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)










