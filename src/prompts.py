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