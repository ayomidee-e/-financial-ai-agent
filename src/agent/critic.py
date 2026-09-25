from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate


class Critique(BaseModel):
    is_accurate: bool = Field(description="Does the analysis match the source data?")
    feedback: str = Field(description="Specific corrections needed")

critic_llm = ChatOpenAI(model="gpt-4o", temperature=0).with_structured_output(Critique)

CRITIC_PROMPT = """You are an Auditor. Review the Analyst's report against the Source Documents.
Check for:
1. Mathematical errors (verify all sums).
2. Fabricated numbers (numbers not found in sources).
3. Missing context (cherry-picking data).
If any error exists, set is_accurate=False and provide specific feedback."""

def audit_analysis(analysis: str, source_docs: str) -> Critique:
    chain = ChatPromptTemplate.from_messages([
        ("system", CRITIC_PROMPT),
        ("user", "Source Documents: {source_docs}\n\nAnalyst Report: {analysis}")
    ]) | critic_llm
    return chain.invoke({"analysis": analysis, "source_docs": source_docs})