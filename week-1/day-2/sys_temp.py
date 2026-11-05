import os 
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
  raise ValueError("Api Erro Occurr")

client = Groq(api_key=my_api_key)

# creating message 
model = "openai/gpt-oss-20b"
role = "user"
prompt = "Suggest a name for my food company"

message = {
  "role":role,
  "content":prompt
}

message_system = {
  "role" : "system",
  "content" : "You are a brand manager who suggest name for my food company. Name should be in one word, suggest only one word"
}
messages = [message_system, message]

response = client.chat.completions.create(model=model,messages=messages,temperature=2)
answer = response.choices[0].message.content
print(answer)