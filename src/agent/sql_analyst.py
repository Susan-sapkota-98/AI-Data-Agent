import os
import sys
from utils.llm_pick import pick_llm
from utils.database import DatabaseUtil
from models.schema import AgentSchema
from langchain_core.messages import HumanMessage 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#AI agent code

def curate_ques(state: AgentSchema)-> AgentSchema:
    user_question=state.user_question
    llm=pick_llm("low")
    response=llm.invoke(f"Curate the following question: {user_question}")

    state.curated_ques=response
    state.messages += [HumanMessage(content=f"{response}")]
    return state

def prompt_query_context(state: AgentSchema)-> AgentSchema:
    curated_question=state.curated_ques

    conn_details={
        "host":os.environ['host'],
        "port":os.environ['port'],
        "user":os.environ['user'],
        "password":os.environ['password'],
        "dbname":os.environ['dbname']
    }
    obj=DatabaseUtil(conn_details)

    schema_info=obj.schema_details("public")

    prompt=f"""
    You are an SQL analyst agent. Your task is to convert the user's natural language
    query into postgres SQL query that can be executed on the database. You are provided with the
    user's original query and the schema details of the database, including table names, column
    names,data types, and sample data for each table so that you can understand the structure of the database and 
    generte an accurate SQL query. Unless user explicitely asks for specific number of rows,
    always limit the output to 10 rows. 
    Note - Just generate the SQL query without any explanation or addititonal text because this query will be executed directly on the database. 
    So, the output should be SQL ready to be executed without any modifications.

    User's Original Query: {curated_question}

    Database Schema Details:
    {schema_info}
    """

    state.prompt_query_context=prompt

    llm=pick_llm("medium")
    generated_sql_query=llm.invoke(prompt)

    state.generated_sql_query=generated_sql_query

    return state

