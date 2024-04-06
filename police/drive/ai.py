import pymysql
import PyPDF2

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        pdf = PyPDF2.PdfFileReader(file)
        for page_num in range(pdf.numPages):
            page = pdf.getPage(page_num)
            text += page.extract_text()
    return text

# Function to store words in a MySQL database
def store_words_in_database(words):
    # Connect to MySQL database
    connection = pymysql.connect(host='localhost',
                                 user='your_username',
                                 password='your_password',
                                 database='your_database_name')
    
    # Create a cursor object using cursor() method
    cursor = connection.cursor()

    # Split text into words
    word_list = words.split()

    # Insert each word into the database
    for word in word_list:
        sql = "INSERT INTO words (word) VALUES (%s)"
        cursor.execute(sql, (word,))
    
    # Commit changes
    connection.commit()

    # Close cursor and connection
    cursor.close()
    connection.close()

# PDF file path
pdf_path = 'example.pdf'

# Extract text from PDF
pdf_text = extract_text_from_pdf(pdf_path)

# Store words in the database
store_words_in_database(pdf_text)

print("Words stored in the database successfully!")
