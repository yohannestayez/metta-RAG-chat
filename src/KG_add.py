# Add to src/chatbot.py or create a separate update script
from extractor import process_knowledge
from metta_handler import add_to_knowledge_base
import logging
from pprint import pprint



def update_knowledge_base(pdf_path):
    """Process a new PDF and update the knowledge graph."""
    try:
        json_data = process_knowledge(pdf_path)
        if not json_data:
            logging.info("Failed to process PDF.")
            return
    
        add_to_knowledge_base(json_data)
        print(f"Knowledge base updated with {pdf_path}")
    except Exception as e:
        print(f"Invalid data extracted from PDF. {e}")

