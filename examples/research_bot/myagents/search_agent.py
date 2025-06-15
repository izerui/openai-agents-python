from agents import Agent, WebSearchTool
from agents.model_settings import ModelSettings
from examples.models import get_agent_chat_model

INSTRUCTIONS = (
    "You are a research assistant. Given a search term, you search the web for that term and "
    "produce a concise summary of the results. The summary must be 2-3 paragraphs and less than 300 "
    "words. Capture the main points. Write succinctly, no need to have complete sentences or good "
    "grammar. This will be consumed by someone synthesizing a report, so its vital you capture the "
    "essence and ignore any fluff. Do not include any additional commentary other than the summary "
    "itself."
)

gpt = get_agent_chat_model('gpt')

search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool()],
    model=gpt,
    model_settings=ModelSettings(tool_choice="required"),
)
