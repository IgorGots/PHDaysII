import libs.logger as logger
from operator import itemgetter

from langchain_core.messages import AIMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain.tools.render import render_text_description

from libs.llm import tools
from libs.prompts import chat
from libs.llm import mygpt


log = logger.setup_applevel_logger()

ALL_TOOLS = [tools.chat, tools.alert_answer]


def tool_chain(model_output: str):
    tool_map = {tool.name: tool for tool in ALL_TOOLS}
    chosen_tool = tool_map[model_output["name"]]
    return itemgetter("arguments") | chosen_tool


def soc_brain(message: str) -> AIMessage:

    chain = chat.brain_prompt | mygpt.BIG_LLM | JsonOutputParser() | tool_chain

    answer = chain.invoke({
        "rendered_tools": render_text_description(ALL_TOOLS),
        "input": message
    })

    return answer
