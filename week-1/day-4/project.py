# improting Liabraries 

import os 
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel 

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

# checking if the key doesnt work 

if not my_api_key:
  raise ValueError("Invalid Api key")

# create a client

client = Groq(api_key=my_api_key)

# creating model 

model = "openai/gpt-oss-20b"

# Creating a structured ouputing using pydantic 

class Ticket(BaseModel):
  name:str
  email:str
  issue:str

scheama = Ticket.model_json_schema()
response_format = {
  "type":"json_object"
}

# making a system prompt 

system_promt = f"""Extract the Person information from the ticket strictly based on the Json schema . {scheama}"""

# creating a system role 

message_system = {
  "role":"system",
  "content":system_promt
}

# creating a user problem and user role 

text = "Hello my name is Piyush . I have an iphone which is not wroking at all. My email is abc@gmail.com. My contact is 82134"
prompt = f"""Read the user problem from the text and extract personal information from the text.{text}"""

message_user ={
  "role":"user",
  "content":prompt
}

# collecting the messages 

messages = [message_system,message_user]

# generating response 

response = client.chat.completions.create(model=model,messages=messages,response_format=response_format)
answer = response.choices[0].message.content

# {"name":"Piyush","email":"abc@gmail.com","issue":"I have an iphone which is not wroking at all."}

# converin into json 

import json

raw_json = answer
data_file = json.loads(raw_json)
ticket = Ticket(**data_file)

print(ticket.name)
print(ticket.email)
print(ticket.issue)