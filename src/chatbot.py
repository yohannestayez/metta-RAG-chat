import json
import logging
from datetime import datetime
from langchain.memory import ChatMessageHistory
from metta_handler import execute_metta_query, assert_fact
from gemini import GeminiModel
from prompts import query_parser, metta_graph_response, query_rewriter

# Define history file path
HISTORY_FILE = "chat_history.json"

# Initialize the language model
llm = GeminiModel()

def summarize_questions_and_answers(messages):
    """Summarizes user questions and AI responses separately."""
    user_questions = []
    ai_responses = []

    for msg in messages:
        if msg["type"] == "human":
            user_questions.append(msg["content"])
        elif msg["type"] == "ai":
            ai_responses.append(msg["content"])

    if not user_questions and not ai_responses:
        return

    # Construct prompts for LLM summarization
    question_prompt = f"""
            Summarize the following user questions into a concise paragraph, 
            capturing only the key topics and recurring themes. The summary should strictly 
            include only the most valuable information, focusing on the main topics and highlights.
            Do not add anything other than the summary.

            Input: {user_questions}
            """

    answer_prompt = f"""
            Summarize the following AI responses into a concise paragraph, 
            capturing only the main explanations, solutions, and recommendations given. 
            The summary should strictly include only the most valuable information. 
            Do not add anything other than the summary.

            Input: {ai_responses}
            """

    # Generate summaries using LLM
    question_summary = llm.generate(prompt=question_prompt).strip()
    answer_summary = llm.generate(prompt=answer_prompt).strip()
    time= str(datetime.now().isoformat)

    summary = f"(user ({question_summary}) ({answer_summary}) ({time}))"
    return summary

def load_history():
    """Load chat history from a file."""
    try:
        with open(HISTORY_FILE, "r") as f:
            messages = json.load(f)
            chat_history = ChatMessageHistory()
            for msg in messages:
                if msg["type"] == "human":
                    chat_history.add_user_message(msg["content"])
                else:
                    chat_history.add_ai_message(msg["content"])
            if len(messages) % 10 == 0:
                if len(messages) == 0:
                    return chat_history
                long_term = summarize_questions_and_answers(messages=messages[:10])
                assert_fact(fact=long_term, file_path="metta/user_memory.metta")
            return chat_history
    except FileNotFoundError:
        return ChatMessageHistory()

def save_history(memory):
    """Save chat history to a file."""
    messages = [{"type": msg.type, "content": msg.content} for msg in memory.messages]
    with open(HISTORY_FILE, "w") as f:
        json.dump(messages, f, indent=4)

# Load chat history on startup
memory = load_history()

def parse_query(query):
    """Convert natural language query to MeTTa query."""
    with open('schema.txt', 'r') as f:
        schema = f.read()
    prompt = query_parser(schema=schema, query=query)
    parsed_query = llm.generate(prompt=prompt)
    logging.info(f"Parsed query: {parsed_query}")
    return parsed_query

def generate_metta_query(parsed_query):
    """Generate a MeTTa query from the parsed query."""
    source = '$x' if parsed_query["source"] == "None" else parsed_query["source"]
    target = '$y' if parsed_query["target"] == "None" else parsed_query["target"]
    edge = '$z' if parsed_query["edge"] == "None" else parsed_query["edge"]

    logging.info(f'{source}, {target}, {edge}')
    metta_query = f"""
         !(match &self (({source}) ({edge}) ({target}))  (({source}) ({edge}) ({target})))
         !(match &self (({target}) ({edge}) ({source}))  (({target}) ({edge}) ({source})))
         !(match &self (({source}) ({edge}) ({target}))  (match &self (({source}) $type1 $description1) (({source}) $type1 $description1)))
         !(match &self (({source}) ({edge}) ({target}))  (match &self (({target}) $type2 $description2) (({target}) $type2 $description2)))
         !(match &self (({target}) ({edge}) ({source}))  (match &self (({source}) $type3 $description3) (({source}) $type3 $description3)))
         !(match &self (({target}) ({edge}) ({source}))  (match &self (({target}) $type4 $description4) (({target}) $type4 $description4)))
         !(match &self (({source}) ({edge}) ({target}))  (match &self (({edge}) $context1) $context1))
         !(match &self (({target}) ({edge}) ({source}))  (match &self (({edge}) $context2) $context2))
            """
    return metta_query

def generate_response(metta_query, query):
    """Generate a response based on MeTTa query results."""
    with open("metta/knowledge_base.metta", "r") as f:
        KG = f.read()
    results = execute_metta_query(f"{KG} \n {metta_query}")
    logging.info(f"Returned result: {results}")
    if results:
        prompt = metta_graph_response(retrieved_content=results, query=query)
        logging.info("Generating response from info retrieved from atomspace")
        response = llm.generate(prompt=prompt)
        return response
    return "I don’t know."

def _refine_query_with_context(user_query):
    """Use conversation history to add context to the current query."""

    with open("metta/user_memory.metta", "r") as f:
        long_term= f.read()
    if not memory.messages:
        return user_query
        
    conversation_history = "\n".join(
        [f"{msg.type.capitalize()}: {msg.content}" for msg in memory.messages]
    )
    
    prompt = query_rewriter(
        history=conversation_history[:10],
        query=user_query, 
        long_term=long_term
    )
    
    refined_query = llm.generate(prompt=prompt)
    logging.info(f"Refined query: {refined_query}")
    return refined_query.strip('"')

def _generate_response(query):
    """Process the user query and generate a response while maintaining history."""
    # Add user message to memory
    memory.add_user_message(query)
    
    # Refine query with contextual memory
    contextual_query = _refine_query_with_context(query)
    
    # Process refined query through pipeline
    parsed_query = parse_query(contextual_query)
    metta_query = generate_metta_query(parsed_query)
    response = generate_response(metta_query=metta_query, query=contextual_query)
    
    # Add system response to memory
    memory.add_ai_message(response)
    save_history(memory)  # Save updated chat history
    
    print(response)
    return response