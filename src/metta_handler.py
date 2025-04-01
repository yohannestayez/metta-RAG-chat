import subprocess
import json
from hyperon import MeTTa
import logging

metta=MeTTa()


def execute_metta_query(query):
    """Execute a MeTTa query and return results."""
    result= metta.run(query)
    return result

def assert_fact(fact, file_path="metta/knowledge_base.metta"):
    """Append a fact to a MeTTa file."""
    with open(file_path, "a") as f:
        f.write(f"\n{fact}")

def add_to_knowledge_base(json_data):
  try:
    for data in json_data:
        for entity in data["entities"]:
            node_name=entity["name"]
            node_type=entity["type"]
            node_description= entity["description"]  
            node_query = f"!(add-atom &kb (({node_name}) ({node_type}) ({node_description})))"
            assert_fact(node_query)
        logging.info("node data added into the atomspace")
        for relation in data["relationships"]:
            source=relation["source"]
            target=relation["target"]
            edge=relation["type"]
            edge_content= relation["context"]
            edge_query=f"!(add-atom &kb (({source}) ({edge}) ({target})))"
            assert_fact(edge_query)
            edges_content= f"!(add-atom &kb (({edge}) ({edge_content})))"
            assert_fact(edges_content)
        logging.info("edge data added into the atomspace")
        logging.info("Knowledge added into atomspace")
  except Exception as e:
      logging.error(f'{e}')
            
    
def add_user_interaction(user_id, query, response, timestamp):
    """Add user interaction to long-term memory."""
    fact = f"(user_query {user_id} \"{query}\" \"{response}\" \"{timestamp}\")"
    assert_fact(fact, "data/user_memory.metta")

