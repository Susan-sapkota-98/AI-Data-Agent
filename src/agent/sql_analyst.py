import os
import sys
from utils.llm_pick import pick_llm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

llm_obj=pick_llm("low")
print(llm_obj.invoke("what is the capital of France?"))