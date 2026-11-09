import os 
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
  raise ValueError("Api Erro Occurr")

client = Groq(api_key=my_api_key)

# creating message 
model = "openai/gpt-oss-20b"
role = "user"


# structured output 

class Ticket(BaseModel):
  name:str
  email:str
  issue:str

schema = Ticket.model_json_schema()
response_format = {
  "type":"json_object"
}

system_promt = f"""Extract the personal information from the ticket strictly based n this JSON format schema.{schema} """

message_system = {
  "role":"system",
  "content":system_promt
}
text = "Hello my name is Piyush . I have an iphone which is not wroking at all. My email is abc@gmail.com. My contact is 82134"
prompt = f""" This is a customer ticeket. Please extract the personal information from this {text}"""

message = {
  "role":role,
  "content":prompt
}

messages = [message_system,message]

response = client.chat.completions.create(model=model,messages=messages,response_format=response_format)
answer = response.choices[0].message.content
# print(answer)

# how to read this 
import json

raw_json = answer
data_file = json.loads(raw_json)
ticket  = Ticket(**data_file)

print(ticket.name)
print(ticket.email)
print(ticket.issue)
print(ticket)