"""My Python module.

This module contains functions and classes for performing various tasks.
"""

#from cmd import PROMPT
#import sys
import fitz
from flask import Flask, render_template, request
from flask import jsonify
import tempfile
import openai

app = Flask(__name__, template_folder='templates')

# Use your own API key
openai.api_key = "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"

# Initialize an empty list to store the extracted text
extracted_text = []

# Initialize an empty list to store the extracted text
extracting_text = []

user_input = []


chatbot_response = None
page_number = None
@app.route('/', methods=['GET', 'POST'])
def extract_pdf_text():
    """
    Extracts text from specific pages of a PDF file and returns it as a string.

    Args:
        pdf_file (FileStorage): The uploaded PDF file.
        page_numbers (list): A list of integers representing the page numbers to extract.

    Returns:
        str: The extracted text.
    """
    if request.method == 'POST':
        global page_number

        # Get the uploaded PDF file and page numbers from the form data
        pdf_file = request.files['pdf_file']

        
        # Save the PDF file to a temporary location on the filesystem
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = f"{temp_dir}/temp.pdf"
            pdf_file.save(pdf_path)
    
            # Open the PDF file using PyMuPDF
            pdf_doc = fitz.Document(pdf_path)

        # Iterate through all pages in the PDF document
        for page_number in range(pdf_doc.page_count):
            # Load the page from the PDF document
            #global page_number
            page = pdf_doc.load_page(page_number)
            # Extract the text from the page
            
            text = page.get_text()
            # Add the extracted text and page number to the list
            extracting_text.append((text, page_number))


        page_numbers = request.form['page_numbers']
        # Split the page numbers by comma and convert them to integers
        page_numbers = [int(x) for x in page_numbers.split(',')]


        # Iterate through the specified page numbers
        for page_number in page_numbers:
            # Make sure the page number is within the range of the PDF
            if page_number > 0 and page_number <= pdf_doc.page_count:
                # Load the page from the PDF document
                page = pdf_doc.load_page(page_number - 1)
                # Extract the text from the page
                text = page.get_text()
                # Add the extracted text to the list
                extracted_text.append(text)
            else:
                # Add an error message to the list if the page number is out of range
                extracted_text.append(f"Page {page_number} is not a valid page number.")

    else:
        # Render the HTML template for the GET request
        return render_template('frontend.html')
        
    # Send the extracted text to ChatGPT and get the response
    user_input = request.form['user_input']
    model = "text-davinci-003"
    prompt = user_input + '\n' + '\n'.join(extracted_text)
        
    response = openai.Completion.create(
            engine=model,
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
            presence_penalty=1.0,
            top_p=1.0,
        )

    global chatbot_response
    chatbot_response = response.choices[0].text
    return render_template('frontend.html', summary=chatbot_response,)


# Define the maximum number of characters per API request
max_chars = 2500

# Split the text into chunks
chunks = [extracting_text[i:i+max_chars] for i in range(0, len(extracting_text), max_chars)]
num_chunks = len(chunks)
print(num_chunks)
# Initialize an empty list to store the API responses


@app.route('/conversation', methods=['POST'])
def handle_conversation():
    global chun
    ks
    global chatbot_response
    global page_number
    global user_input
    # Engage in a conversation with the user about the summarized text
    #prompt = f"Here is a summary of the text:\n{chatbot_response}\n\nWhat would you like to know more about?"

    responses = []
    for chunk in chunks:
        user_input = request.form['user_input']
        prompt = f"From {chunk}. {user_input} please specify the page or pages you got the answer. if the answer is not in the book tell me your answer and specify that the answer isn't in the book"

        # Use GPT-3 to generate a response based on the user's input
        completions = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            stop=["You:"]
        )
        bot_response = completions.choices[0].text

        responses.append(bot_response)

    # Concatenate the responses together to get the complete answer
    complete_answer = "".join(responses)

    return render_template('frontend.html', bot_response = complete_answer)



if __name__ == '__main__':
    app.run(debug=True)