import random
import pandas as pd
from flask import Flask, request, send_file, render_template
import os

app = Flask(__name__)

def load_csv(file):
    return pd.read_csv(file)

def secret_santa_assignment(employees, previous_assignments=None):
    employee_names = employees['Employee_Name'].tolist()
    
    
    remaining = employee_names.copy()
    assignments = {}

    for _, row in employees.iterrows():
        giver_name = row['Employee_Name']
        giver_email = row['Employee_EmailID']
        
      
        available_children = [e for e in remaining if e != giver_name]

        
        if previous_assignments is not None:
            last_year_child = previous_assignments.get(giver_name, None)
            available_children = [e for e in available_children if e != last_year_child]
        
        
        secret_child_name = random.choice(available_children)
        remaining.remove(secret_child_name)

        
        secret_child_row = employees[employees['Employee_Name'] == secret_child_name].iloc[0]
        secret_child_email = secret_child_row['Employee_EmailID']

        
        assignments[giver_name] = {
            'Employee_Name': giver_name,
            'Employee_EmailID': giver_email,
            'Secret_Child_Name': secret_child_name,
            'Secret_Child_EmailID': secret_child_email
        }

    return pd.DataFrame(assignments.values())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    current_employees_file = request.files['current_employees']
    previous_assignments_file = request.files.get('previous_assignments')

    employees = load_csv(current_employees_file)

    previous_assignments = None
    if previous_assignments_file:
        previous_df = load_csv(previous_assignments_file)
        previous_assignments = dict(zip(previous_df['Employee_Name'], previous_df['Secret_Child_Name']))

    assignments_df = secret_santa_assignment(employees, previous_assignments)
    output_filename = 'secret_santa_assignments.csv'
    assignments_df.to_csv(output_filename, index=False)

    return send_file(output_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
