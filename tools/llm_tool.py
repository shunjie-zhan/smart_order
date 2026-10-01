"""
se encarga de invocar llm

"""
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
load_dotenv()


def call_llm(query: str, system_instruction: str):
    """
    :param query: pregunta
    :param system_instruction: para cambiar modelo de negocio
    :return:
    """

    # 1. instancia de modelo llm
    api_key = os.getenv("DASHSCOPE_API_KEY")
    api_base = os.getenv("DASHSCOPE_API_BASE")
    model_name = os.getenv("LLM_MODE")
    if not api_key or not api_base or not model_name:
        raise ValueError("API key and API base are not set")
    llm = ChatOpenAI(model_name=model_name, openai_api_key=api_key, openai_api_base=api_base)

    # 2. propt template
    chat_promt_template = ChatPromptTemplate.from_messages([
        ("system", "{system_instruction}"),
        ("human", "{query}")
    ])
    # chat_promt.from_template(query=query, system_instruction=system_instruction)

    # 3. definicion de chain "|"
    chain = chat_promt_template | llm

    # 4. ejeucion de chain
    response = chain.invoke({"system_instruction": system_instruction, "query": query})

    # 5. return resultado
    return response.content

if __name__ == '__main__':
    result=call_llm("como esta el mercado de empleo de agent AI", "eres un experto de empleo en Spain")
    print(result)