import os
import sys
from utils.llm_pick import pick_llm
from utils.database import DatabaseUtil
from models.schema import AgentSchema,JudgeSchema
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



# Greate SQL Query Node 
def generate_sql(state:AgentSchema)-> AgentSchema:
    prompt=state.prompt_query_context

    llm=pick_llm("medium")
    generated_sql_query=llm.invoke(prompt)

    state.generated_sql_query=generated_sql_query

    return state


# is safe node
def is_safe_sql(state: AgentSchema) -> AgentSchema:
    sql_query=state.generated_sql_query

    llm=pick_llm("medium")
    llm_judge=llm.with_structured_output(JudgeSchema)


    prompt=f"""
    You are an SQL Judge for data security. Your task is to determine whether the SQL query is 
    safe or not. The SQL query should only be used for data retrieval and should not modify the 
    database in any way. Neither the SQL query nor the prompt should contain any SQL commands that can modify the 
    database, such as INSERT,UPDATE,DELETE, DROP, ALTER, TRUNCATE, CREATE, or any other commands that can change
    the structure or content of the database. If the SQL query is safe, respond with ' Yes' otherwise respond with 
    'No'. Additionally, provide comments explaining your decision.
    Here's the SQL query to evaluate:
    {sql_query}
            """
    response=llm_judge.invoke(prompt).model_dump()
    state.is_safe_sql_response=response['answer']
    state.comments=response['comments']

    return state
    

def canceled_sql(state:AgentSchema)->AgentSchema:
    comments=state.state.comments
    state.final_answer=f"The generated SQL query was deemed unsafe to execute. The reason provided by the judge is:{comments}. Therefore, the SQL query will not be executed."
    return state

#Execute SQL Query node
def execute_sql(state:AgentSchema)->AgentSchema:
    sql_query=state.generated_sql_query

    conn_details={
        "host":os.environ['host'],
        "port":os.environ["port"],
        "user":os.environ["user"],
        "password":os.environ["password"],
        "dbname":os.environ['dbname']
    }
    obj=DatabaseUtil(conn_details)
    execute_result=obj.execute_sql(sql_query)
    state.sql_query_execution_result=execute_result

    return state