from metta_handler import execute_metta_query, add_user_interaction
from gemini import GeminiModel
from datetime import datetime
from extractor import process_pdf
from prompts import query_parser, metta_graph_response
import logging
import json

llm=GeminiModel()



def parse_query(query):
    """Convert natural language query to MeTTa query."""
    with open('schema.txt', 'r') as f:
        schema=f.read()
    prompt= query_parser(schema=schema, query=query)
    parsed_query=llm.generate(prompt= prompt)
    print(type(parsed_query))
    logging.info(f"Parsed query: {parsed_query}")
    
    return parsed_query
def generate_metta_query(parsed_query):
    source= '$x' if parsed_query["source"]=="None" else parsed_query["source"]
    target= '$y'if parsed_query["target"] == "None" else parsed_query["target"]
    edge= '$z' if parsed_query["edge"]=="None" else parsed_query["edge"]
    metta_query= f"""
         !(match &kb (({source}) ({edge}) ({target}))  (({source}) ({edge}) ({target})))
         !(match &kb (({source}) ({edge}) ({target}))  (match &kb (({source}) $type $description) (({source}) $type $description)))
         !(match &kb (({source}) ({edge}) ({target}))  (match &kb (({target}) $type $description) (({target}) $type $description)))
         !(match &kb (({source}) ({edge}) ({target}))  (match &kb (({edge}) $context) $context))
            """
    return metta_query

def generate_response(metta_query, query):
    """Generate a response based on MeTTa query results."""
    with open("metta/knowledge_base.metta", "r") as f:
        KG=f.read()
    results = execute_metta_query(f"{KG} \n {metta_query}")
    logging.info(f"returned result: {results}")
    if results:
        prompt=metta_graph_response(retrieved_content=results, query=query)
        logging.info("Generating response from info retreived from atomspace")
        response= llm.generate(prompt=prompt)
        return response
        
    return "I don’t know."


if __name__ == "__main__":
    query= "who is the younger brother? can you explain in detail"
    parsed_query= parse_query(query)
    metta_query=generate_metta_query(parsed_query)
    response=generate_response(metta_query=metta_query, query=query)
    print(response)
    

