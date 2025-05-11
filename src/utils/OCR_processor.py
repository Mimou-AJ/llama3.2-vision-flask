import numpy as np
from .pdf import DocumentFile
import pandas as pd 
import json
from thefuzz import fuzz, process
from PIL import Image
import base64
from io import BytesIO
import re
import requests


SYSTEM_PROMPT = """Act as an OCR assistant. Analyze the provided doctor receipt, in german language, containing sensitive patient's data and:
1. Determine the correct rotation angle of the input image (doctor receipt) to ensure that text is read in the proper orientation.
2. Focus solely on the large square in the upper left section of the receipt. This region contains the key data.
3. From within the ROI, extract only the following fields: "Krankenkasse bzw Kostenträger": which represents the name of the insurance company (located at the top of the square), "Name Vorname des Versicherten": only the name and surname of the patient and the "Versicherten-Nr.": which is the insurance_number, a 10-character number that always starts with an alphabet letter followed by 9 numbers (located below the word Versicherten-Nr.).
4. Recognize all to be extracted text in the image as accurately as possible.
Your answer should only and strictly be the following JSON format without any additional text or comments: {"ocr_insurance_company": "<your guess>", "name": "<your guess>", "insurance_number": "<your guess>"}
"""


def read_PDF_images(image_path):
    images = DocumentFile.from_pdf(image_path)
    return images
    
def numpy_image_to_base64(np_image):
    # Convert the numpy array to an image using PIL
    image = Image.fromarray(np_image)
    
    # Save the image to a BytesIO object
    buffered = BytesIO()
    image.save(buffered, format="PNG")  # You can change the format if needed
    
    # Encode the image to base64
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return img_base64

#  # Function to get the closest match
def find_closest_match(ocr_name, df1):
    if ocr_name is None or not isinstance(ocr_name, str):
        return None
    
    choices = df1['name_insurance_company'].tolist()
    # Use a token-based scorer to match based on significant word overlap
    closest_match, score = process.extractOne(ocr_name, choices, scorer=fuzz.partial_ratio)
    
    return closest_match


def perform_ocr(base64_image): 

    response = requests.post(
        "http://localhost:11434/api/chat",  # Ollama API endpoint.
        json={
            "model": "llama3.2-vision",
            "messages": [
                {
                    "role": "user",
                    "content": SYSTEM_PROMPT,
                    "images": [base64_image],
                },
            ],
        }
    )

    if response.status_code == 200:
        full_response = ""
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                content = json_response.get("message", {}).get("content", "")
                full_response += content
        
        json_match = re.search(r'\{.*\}', full_response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                result_json = json.loads(json_str)
                return result_json
            except json.JSONDecodeError as e:
                print("JSON decoding error:", e)
                return None
        else:
            print("No JSON found in OCR result")
            return None
    else:
        print("Error:", response.status_code, response.text)
        return None

def make_response(file): 
    insurance_companies_df = pd.read_pickle('insurance_companies.pkl')
    insurance_companies_df.rename({'name': 'name_insurance_company'}, axis=1, inplace=True)

    np_images=read_PDF_images(file)
    base64_image_list=[]
    result= []
    for i in np_images: 
        base64_images = numpy_image_to_base64 (i)
        base64_image_list.append(base64_images)
        ocr_result = perform_ocr(base64_images)
        if ocr_result:
            result.append(ocr_result)
    
    if not result:
        return {"error": "No valid OCR data found"}, []

    ocr_df= pd.DataFrame(result)

    if not ocr_df.empty:
        if 'ocr_insurance_company' in ocr_df.columns: 
            ocr_df['Closest_Match'] = ocr_df['ocr_insurance_company'].apply(lambda x: find_closest_match(x, insurance_companies_df))

            ocr_df = ocr_df.merge(insurance_companies_df[['name_insurance_company', 'address']], 
                        left_on='Closest_Match', 
                        right_on='name_insurance_company', 
                        how='left')
            # # Drop the extra 'name' column from the merge
            # ocr_df.drop('name_insurance_company', axis=1, inplace=True)

    return json.loads(json.dumps(ocr_df.to_dict('records'))),base64_image_list