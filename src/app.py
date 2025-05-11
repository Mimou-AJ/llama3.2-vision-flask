from flask import Flask, request, jsonify, render_template,send_file
from flask_weasyprint import HTML, render_pdf
import pandas as pd
import glob
from pathlib import Path
import os
import zipfile
from wtforms import FileField, SubmitField
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired
from werkzeug.utils import secure_filename
from utils.OCR_processor import make_response, find_closest_match
from flask_httpauth import HTTPBasicAuth
from utils.configuration import env
import datetime



auth = HTTPBasicAuth()

app = Flask(__name__)


app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = ''

class UploadFileForm(FlaskForm):
    file = FileField("File",  validators=[InputRequired(), FileAllowed(['pdf'], 'PDF files only!')])
    submit = SubmitField("Upload File")

@auth.verify_password
def verify_password(username, password):
    if username == env["PYTHON_API_USERNAME"] and password == env["PYTHON_API_PASSWORD"]:
        return True
    return False


@app.route('/api/v1/OCR/image2text/confirm', methods=['POST'])
def confirm():
    insurance_companies_df = pd.read_pickle('insurance_companies.pkl')
    insurance_companies_df.rename({'name': 'name_insurance_company'}, axis=1, inplace=True)

    form_keys = request.form.keys()
    
    number_of_images = len(set(key.split('_')[-1] for key in form_keys if key.startswith('ocr_insurance_company')))
    
    updated_records = []

    current_date = datetime.date.today()
    formatted_date = current_date.strftime("%d.%m.%Y")
    
    # Retrieve the corrected values for each image
    for i in range(number_of_images):
        include_key = f'include_{i}'
        if include_key in request.form:
            ocr_insurance_company = request.form.get(f'ocr_insurance_company_{i}')  # Corrected value
            
            # Find the closest match
            closest_match = find_closest_match(ocr_insurance_company, insurance_companies_df)

            # Retrieve address based on the closest match
            address = None
            if closest_match:
                matched_row = insurance_companies_df[insurance_companies_df['name_insurance_company'] == closest_match]
                if not matched_row.empty:
                    address = matched_row['address'].values[0]

            record = {
                "name": request.form.get(f'name_{i}'),
                "insurance_number": request.form.get(f'insurance_number_{i}'),
                "insurance_company": closest_match,  # Updated closest match
                "address": address,  # Updated address
                "processed_image": request.form.get(f'processed_image_{i}'),
            }
        try: 
            # Render the final letter with the corrected data
            html = render_template('PDF_template_export.html', corrected_data=record,current_date_formatted=formatted_date)
            render_pdf(HTML(string=html).write_pdf((record['insurance_number'])+'.pdf')) ##convert html--> pdf
        except: pass    
    listFileNames=glob.glob("*.pdf")
    try:
        with zipfile.ZipFile( 'OCR_result.zip',mode='w', compression=zipfile.ZIP_DEFLATED ) as myzip:
            for f in listFileNames:
                myzip.write(f)
        return app.send_static_file(myzip)
    except : pass
    try:
        path = Path('/app/OCR_result.zip')
    except : pass
    try:
        for i in listFileNames:
            path1=Path ("/app/" + str(i))
            os.remove(path1)
    except:pass
    return (send_file(path, as_attachment=True), os.remove(path))



@app.route('/api/v1/OCR/image2text/upload', methods=["GET","POST"])
@app.route('/home', methods=['GET',"POST"])
@auth.login_required
def upload_image():
    form = UploadFileForm()

    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filename)
        try: 
            result,base64_image_list = make_response(filepath)
        
            os.remove(filepath)
            if result:
                return render_template('ocr_results.html', processed_response=result,images=base64_image_list), 200
            else:
                return jsonify({"error": "OCR failed"}), 500
        except Exception as e:
            os.remove(filepath)
            return jsonify({'error': 'An error occurred: {}'.format(e)}), 400    
    return render_template('upload_pdf.html', form=form)


if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0", port=5000)