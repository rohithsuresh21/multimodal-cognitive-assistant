import json
import ollama

resp = ollama.chat(
model='mistral:7b-instruct-q4_K_M',
format='json',
messages=[{
'role': 'user',
'content': 'Return JSON with keys: internal_monologue, verbal_response'
}]
)
data = json.loads(resp['message']['content'])
print(data) 