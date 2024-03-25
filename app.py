import os
from dotenv import load_dotenv
from chainlit import action_callback, Action, user_session, on_chat_start, on_message, Message, AskUserMessage, AsyncLangchainCallbackHandler, on_logout, on_chat_end, on_stop
from langchain import HuggingFaceHub, LLMChain
from fastapi import Request, Response
from langchain.memory.buffer import ConversationBufferMemory
import time
from prompts import general_prompt, factors_prompt, aspects_prompt
#from langchain_community.chat_models import ChatOpenAI
#from langchain.prompts import ChatPromptTemplate
#from langchain.schema import StrOutputParser
#from langchain.schema.runnable import Runnable
#from langchain.schema.runnable.config import RunnableConfig

#! reads file to set factors/aspects -> edit template -> chat
#! fix template file
#! fix model/ai output
#! fix template global variable
#! fix stop button
#! action button
#! deploy as website: https://ankushgarg.super.site/how-to-deploy-your-chatgpt-like-app-with-chainlit-and-aws-ecs

load_dotenv()
HUGGINGFACEHUB_API_TOKEN = os.environ['HUGGINGFACEHUB_API_TOKEN']

# Default prompt is both factors and aspects
prompt = general_prompt

@on_chat_start
async def main():
  #time.sleep(5)

  # Options to set template
  # actions = [
  #   Action(name="chat_mode", value="Chat Mode", description="Click me to chat!", collapsed=False),
  #   Action(name="get_factors", value="Factors Mode", description="Click me for factors mode!"), # choose factors template
  #   Action(name="get_aspects", value="Aspects Mode", description="Click me for aspects mode!") # choose aspects template
  # ]

  # await Message(content="Choose your multimodal social analysis mode", actions=actions).send()

  model_id = "gpt2-medium"
  conv_model = HuggingFaceHub(
      huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
      repo_id=model_id,
      model_kwargs={
          "temperature": 0.5,
          "max_new_tokens": 150
      }
  )
  conversation_memory = ConversationBufferMemory(memory_key="chat_history", max_len=50, return_messages=True)

  conv_chain = LLMChain(
    llm=conv_model,
    prompt=prompt,
    memory=conversation_memory,
    verbose=True
  )

  user_session.set("llm_chain", conv_chain)

  # Reads file to get factors or aspects
  factors = ""
  aspects = ""

@on_message
async def on_message(message: Message):
  llm_chain = user_session.get("llm_chain")

  res = await llm_chain.acall(message.content, callbacks=[AsyncLangchainCallbackHandler()]) # use the template to ask question
  query = res["query"] # user input
  text = res["text"] # bot output

  msg = Message(content=text)

  await msg.send()

@action_callback("chat_mode")
async def on_action(action: Action):
  global prompt

  prompt = ""

  return "Chat Mode"

@action_callback("get_factors")
def on_action(action: Action):
  global prompt

  prompt = ""

  return "Factors Mode"

@action_callback("get_aspects")
async def on_action(action: Action):
  global prompt

  prompt = ""

  return "Aspects Mode"

def file():
  return

@on_stop
def on_stop():
  print("The user wants to stop the task!")

@on_chat_end
def end():
  print("goodbye!", user_session.get("id"))

@on_logout
def logout(request: Request, response: Response):
  response.delete_cookie("my_cookie")

if __name__ == '__main__':
  main()
