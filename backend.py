from flask import Flask, render_template, request
import PyPDF2
import pytesseract
import openai

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = "YOUR_API_KEY"

@app.route('/', methods=['GET', 'POST'])
def extract_text():
    if request.method == 'POST':
        # Get the uploaded PDF file and page numbers from the form data
        file = request.files['file']
        page_numbers = request.form['page_numbers']
        # Split the page numbers by comma and convert them to integers
        page_numbers = [int(x) for x in page_numbers.split(',')]

        # Create a PDF object from the uploaded file
        pdf = PyPDF2.PdfFileReader(file)
        # Get the number of pages in the PDF
        num_pages = pdf.getNumPages()

        # Create an empty list to store the extracted text
        extracted_text = []

        # Iterate through the specified page numbers
        for page_number in page_numbers:
            # Make sure the page number is within the range of the PDF
            if page_number > 0 and page_number <= num_pages:
                # Extract the text from the page
                text = pytesseract.image_to_string(pdf.getPage(page_number - 1), lang='eng', options='--psm 6')
                # Add the extracted text to the list
                extracted_text.append(text)
            else:
                # Add an error message to the list if the page number is out of range
                extracted_text.append(f"Page {page_number} is not a valid page number.")

        # Send the extracted text to ChatGPT and get the response
        model = "chatbot"
        prompt = "\n".join(extracted_text)
        response = openai.Completion.create(
            engine=model,
            prompt=prompt,
            max_tokens=200,
            n=1,
            stop=None,
            temperature=0.5,
            presence_penalty=1.0,
            top_p=1.0,
        )
        chatbot_response = response.text

        # Render the HTML template with the extracted text and ChatGPT response
        return render_template('index.html', extracted_text=extracted_text, chatbot_response=chatbot_response)
    else:
        # Render the HTML template for the GET request
        return render_template('index.html')

if __name__ == '__main__':
    app.run()
