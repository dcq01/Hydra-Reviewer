from langchain_openai.chat_models import ChatOpenAI


def get_generate_llm():
    generate_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return generate_llm


def get_llm():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return llm


def get_reflection_times():
    return 3 * 2
