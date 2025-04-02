import PyPDF2
import json
from gemini import GeminiModel
from prompts import PDF_TO_JSON_PROMPT, SCHEMA_BUILDER  
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


llm = GeminiModel()


def process_pdf(text: str) -> list[dict]:
    logging.info("Processing book text...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        separators=["\n\nChapter ", "\n\nSection ", "\n\n", "\n", ".", " "]
    )
    if not isinstance(text, str) or not text.strip():
        logging.error("Invalid input: Book text must be a non-empty string")
        raise ValueError("Book text must be a non-empty string")
    
    logging.info("Splitting text into chunks")
    chunks = splitter.split_text(text)
    
    logging.info(f"Successfully split text into {len(chunks)} chunks")
    print(chunks)
    return chunks

def extract_pdf_text(pdf_file):
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
    return text

def summarize_text(text):
  summarization= llm.generate(prompt=f"Summarize the following: {text}")
  logging.info(f'Summarization generated')
  return summarization

def extract_entities_and_relationships(text):
    """Convert summary to JSON with entities and relationships using LLM."""
    json_str=llm.generate(prompt=f'{PDF_TO_JSON_PROMPT} \n{text}')
    logging.info(f"extracted info: {json.dumps(json_str)}")
    return json_str
def extract_schema(input):
    schema= llm.generate(prompt=f'{SCHEMA_BUILDER} \n{input}')
    logging.info(f'schema extracted')
    with open('schema.txt', 'w') as f:
        f.write(str(schema))


def process_knowledge(pdf_path):
    """Full PDF processing pipeline."""
    text = extract_pdf_text(pdf_path)
    json_list=[]
    contents=process_pdf(text=text)
    for content in contents:
        json_data = extract_entities_and_relationships(text)
        json_list.append(json_data)
    extract_schema(str(json_list))
    logging.info("annotation query generated")
    return json_list


if __name__ == '__main__':

    process_knowledge("metta/input_data/short_story.pdf")