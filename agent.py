import glob
import json
import os

# load chat history if exist or create a new one
# just a single chat
import random
import uuid
from datetime import datetime

from langchain.agents import create_agent
from langchain.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_aws import ChatBedrockConverse
from pandas import DataFrame

import config
import db_utils as db
from tools import calc, get_weather, transl

random.seed(123)


def exec_agent(h_msg: str, chat_id: uuid.UUID, engine):
    chat_history = db.get_messages_per_id(engine, chat_id)

    db.add_message(engine, chat_id, "user", h_msg)
    history_for_ai = [
        {"role": msg.role, "content": msg.content} for msg in chat_history
    ]

    history_for_ai.append({"role": "user", "content": h_msg})

    # model = ChatBedrockConverse(
    #    model=config.MODEL_NAME,
    #    region_name=config.AWS_REGION,
    #    credentials_profile_name=config.AWS_PROFILE,
    #    temperature=config.TEMPERATURE,
    #    max_tokens=config.MAX_TOKENS,
    # )
    #
    # agent = create_agent(
    #    model,
    #    tools=[transl, calc, get_weather],
    # )

    start_message = [{"role": "system", "content": "You are my personal assistant."}]
    start_message.extend(history_for_ai)
    # --- BLOCCO CHIAMATA AI ---    #
    # model = ChatBedrockConverse(...)
    # agent = create_agent(...)
    # response = agent.invoke({"messages": start_message})
    # final_response_text = response["messages"][-1].content
    final_response_text = "ciao"
    db.add_message(engine, chat_id, "ai", final_response_text)
    return {"content": final_response_text}
