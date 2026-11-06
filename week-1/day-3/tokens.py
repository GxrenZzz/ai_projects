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
# 3 Prmpts 

prompt1  = "hi "
prompt2  = "Explain time trave in detail "
prompt3  = "Write a 1000 words an essay on Machine Learning? "

prompts = [prompt1,prompt2,prompt3]
for prompt in prompts:
  message = {
  "role":role,
  "content":prompt}
  messages = [message]

  response = client.chat.completions.create(model=model,messages=messages,max_tokens=100)
  usage = response.usage
  print(f"Prompt: {prompt} -> your tokens :{usage.prompt_tokens} completion_tokens:{usage.completion_tokens} total_tokens:{usage.total_tokens} Finish_Reason:{response.choices[0].finish_reason}")
# answer = response.choices[0].message.content
# print(answer)