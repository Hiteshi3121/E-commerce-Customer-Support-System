from langchain_core.tools import tool
from backend.rag.vectorstore import get_vectorstore
import os
from dotenv import load_dotenv
load_dotenv()


@tool
def company_info_tool(query: str) -> str:
    """
    Use this tool to answer questions about the company.
    """
    retriever = get_vectorstore().as_retriever(
        search_type="mmr",
        search_kwargs={"k": 3, "fetch_k": 8}
    )
    docs = retriever.invoke(query)

    if not docs:
        return ""

    return "\n".join(d.page_content for d in docs)
