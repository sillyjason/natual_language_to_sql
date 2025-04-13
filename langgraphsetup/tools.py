from langgraphsetup.llm import model
from langchain.tools import tool
from langgraphsetup.prompts.tableSelection import table_selection_prompt
from langgraphsetup.prompts.queryGeneration import query_generation_prompt
from langchain.prompts import PromptTemplate
import os 
import requests
from dotenv import load_dotenv

# load the environment variables
load_dotenv()


@tool
def select_tables(message: str) -> dict:
    """Based on the exact user messag, select the relevant Couchbase collection or set of collections for SQL generation in subsequent steps"""
    prompt = PromptTemplate(template=table_selection_prompt, input_variables=["question"])
    response = model.invoke(prompt.format(question=message))
    return response.content



@tool
def retrieve_schemas(tables: list) -> str:
    """Retrieve the schema of the selected Couchbase collection or set of collections"""
    
    if len(tables) == 0:
        return "None"
    
    schema_dir = "langgraphsetup/schemas"
    schema_contents = []
    
    for table in tables:
        schema_path = os.path.join(schema_dir, f"{table}.txt")
        if os.path.exists(schema_path):
            with open(schema_path, "r") as file:
                schema_contents.append(file.read())
        else:
            schema_contents.append(f"Schema for {table} not found.")
    
    return "\n\n".join(schema_contents)
        

@tool
def generate_sql(message: str, concatenated_schemas: str) -> str:
    """Based on the exact user message along with the concatenated schemas, generate SQL++ query that can be run in Couchbase"""
    
    prompt = PromptTemplate(template=query_generation_prompt, input_variables=["question", "concat_schemas"])
    response = model.invoke(prompt.format(question=message, concat_schemas=concatenated_schemas))
    
    # post processing, remove the leading and training ``` characters
    sql = response.content.strip()
    sql = sql.replace("```", "")
    
    # post processing, if the response starts with "sql", remove it   
    if sql.lower().startswith("sql"):
        sql = sql[3:].strip()
    
    return sql



@tool
def run_sql(sql: str) -> dict:
    """Run the SQL++ query against the Couchbase database"""

    url = "http://localhost:8093/query/service"  # Couchbase Query Service endpoint
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "statement": sql  # The SQL++ query to execute
    }
    
    try:
        user = os.getenv("CB_USERNAME")
        password = os.getenv("CB_PASSWORD")
        
        response = requests.post(url, json=payload, headers=headers, auth=(user, password))  # Replace with your Couchbase credentials
        response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
        
        request_result = response.json()  # Return the JSON response from Couchbase
        
        result = request_result.get("results", [])
        return str(result) 
        
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}