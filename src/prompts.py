PDF_TO_JSON_PROMPT = """
You are a knowledge extraction expert. Extract knowledge in the form of entities and relationships from the following text and represent them in a structured JSON format.  

### **Requirements**:  
#### **1. Entities Extraction**  
Identify and extract all significant entities from the text, including but not limited to:  
- **People** (e.g., individuals, historical figures, professionals)  
- **Organizations** (e.g., companies, institutions, government bodies)  
- **Locations** (e.g., cities, countries, landmarks)  
- **Concepts & Events** (e.g., theories, methodologies, conferences, significant occurrences)  
- **Objects & Products** (e.g., software, tools, technologies, publications)  
- **Other relevant terms** that play a key role in the text  

Each entity should be represented with:  
- **name**: The exact entity name as mentioned in the text  
- **type**: The category it belongs to (e.g., Person, Organization, Location, Concept, Product)  
- **description**: A concise definition or contextual explanation based on its role in the text  

#### **2. Relationship Extraction**  
Identify meaningful relationships between entities, ensuring:  
- **source**: The originating entity  
- **target**: The related entity  
- **type**: The nature of the relationship (e.g., "works at", "founded", "is a subsidiary of", "developed", "authored", "located in")  
- **context**: A sentence or short explanation that provides clarity on the relationship  

### **Guidelines for Accuracy & Consistency**  
1. **Faithful Representation**: Extracted data must stay true to the original text, avoiding assumptions or hallucinations.  
2. **Entity Consistency**: Ensure that all entities referenced in relationships are also included in the entities list.  
3. **Comprehensive Coverage**: Capture as much structured knowledge as possible while maintaining precision.  

### **Output Format**  
```json
{{
  "entities": [
    {{
      "name": "Entity Name",
      "type": "EntityType",
      "description": "Definition or contextual explanation"
    }}
  ],
  "relationships": [
    {{
      "source": "Entity Name",
      "target": "Entity Name",
      "type": "RelationshipType",
      "context": "Sentence or explanation providing context"
    }}
  ]
}}
```

#### **Text Input**:  

"""

SCHEMA_BUILDER="""

From the following structured JSON data, extract a schema in the form of a list where:  

### **Requirements**  
#### **1. Relationship Extraction**  
Extract all relationships from the `"relationships"` section and structure them as follows:  
- **nodes**: Contains `"source"` and `"target"` entity names.  
- **relationships**: Specifies the `"type"` of relationship between the entities.  

#### **2. Output Format**  
```json
[
  {
    "nodes": {
      "source": "SourceEntity",
      "target": "TargetEntity"
    },
    "relationships": "RelationshipType"
  }
]
```

### **Guidelines for Accuracy & Consistency**  
1. **Complete Relationship Mapping**: Ensure all relationships from the `"relationships"` section are extracted.  
2. **No Duplicate Entries**: Avoid repeated relationships between the same entities unless they have different `"type"` values.  
3. **Data Integrity**: Maintain fidelity to the original JSON data, ensuring `"source"`, `"target"`, and `"type"` are accurately mapped.  
4. **Handle Missing or Ambiguous Data**: If `"source"`, `"target"`, or `"type"` is missing, mark the `"relationships"` field as `"Unknown"` with `"context": "Requires clarification"`.  

### **Input JSON Data**  

"""

query_rewriter = lambda history, query, long_term: f"""

Rewrite the given question with full contextual information, but only if it:

- Lacks necessary details that can be fulfilled by the provided context.
- Is related to the context; otherwise, leave it unchanged.

Ensure that the rewritten question:
- Maintains the original intent.
- Is direct and precise, while incorporating relevant context for clarity.
- Makes explicit references to previously discussed concepts where applicable.
NOTE: just respond with only the question nothing else.
Input:
long term memory:
{long_term}

History:
{history}

Original Question:
{query}

Output:
Contextualized Question:
"""
def query_parser(schema, query):
    prompt= f"""
            Convert the following natural language query into an annotation query using the provided schema.  

            ### **Schema:**  
            {schema}

            ### **Requirements:**  
            1. **Match Against Schema**: The output JSON must conform to the schema. If part of the query matches an existing relationship in the schema but another part does not, the unmatched part should be set to `None`.  
            2. **Structured Representation**: Convert the query into the following format:  
              ```json
              {{
                "source": "source_entity",
                "target": "target_entity",
                "edge": "relationship_type"
              }}
              ```
            3. **Handle Missing or Unknown Data**:  
              - If the query references an unknown entity or relationship not found in the schema, replace it with `None`.

            ### **Examples:**  

            #### **Schema Example:**  
            ```json
            [
              {{
                "nodes": {{
                  "source": "Company A",
                  "target": "Person X"
                }},
                "relationships": "employs"
              }},
              {{
                "nodes": {{
                  "source": "University Y",
                  "target": "Person Z"
                }},
                "relationships": "graduated from"
              }}
            ]
            ```

            #### **Input Query Example 1:**  
            *"Who does Company A employ?"*  

            #### **Expected Output:**  
            ```json
            {{
              "source": "Company A",
              "target": "None",
              "edge": "employs"
            }}
            ```

            #### **Input Query Example 2:**  
            *"Where did Person Z graduate from?"*  

            #### **Expected Output:**  
            ```json
            {{
              "source": "Person Z",
              "target": "None",
              "edge": "graduated from"
            }}
            ```

            #### **Input Query Example 3 (Unknown Relationship):**  
            *"Who is the CEO of Company A?"*  

            #### **Expected Output:**  
            ```json
            {{
              "source": "Company A",
              "target": "None",
              "edge": "None"
            }}
            ```

            ### **Natural Language Query:**  
            {query}  
          """
    return prompt

def metta_graph_response(retrieved_content, query):
    prompt= f"""
              You are tasked with answering the user's query based solely on the provided information. 

              Query: {query}.

              Information: {retrieved_content}.

              Instructions:
              1. Evaluate the provided information for relevance, accuracy, and usefulness to the query.
              2. If the information is sufficient, provide a clear and concise answer directly addressing the query.
              3. Do not mention or refer to "retrieved results" or the source of the information in your response.
              4. If the information is empty, irrelevant, or unhelpful, respond with: "I can't help with your question."

              Provide only the answer, and avoid any unnecessary references or disclaimers.
              """
    return prompt