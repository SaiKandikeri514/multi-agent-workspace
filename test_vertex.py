import os
from dotenv import load_dotenv
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage

load_dotenv()

project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "test-project")
print(f"Project ID: {project_id}")

try:
    llm = ChatVertexAI(model="gemini-1.5-flash", project=project_id, max_retries=1)
    res = llm.invoke("Hi")
    print(f"gemini-1.5-flash success: {res.content}")
except Exception as e:
    print(f"gemini-1.5-flash error: {e}")

try:
    llm2 = ChatVertexAI(model="gemini-2.5-flash", project=project_id, max_retries=1)
    res2 = llm2.invoke("Hi")
    print(f"gemini-2.5-flash success: {res2.content}")
except Exception as e:
    print(f"gemini-2.5-flash error: {e}")
