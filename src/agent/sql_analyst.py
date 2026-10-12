import os
import sys
from utils.llm_pick import pick_llm
from Models.schema import AgentSchema
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#AI agent code

def curate_ques(state: AgentSchema)-> AgentSchema:
    user_question=state.user_question
    llm=pick_llm("low")
    response=llm.invoke(f"Curate the following question: {user_question}")

    state.curated_ques=response
    return state

def prompt_query_context(state: AgentSchema)-> AgentSchema:
    curated_question=state.curated_ques
    llm=pick_llm("low")
    response=llm.invoke(f"Curate the following question: {user_question}")

    state.curated_ques=response
    return state


