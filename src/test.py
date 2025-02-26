
from google.generativeai import GenerativeModel, configure  # type: ignore

configure(api_key="AIzaSyCtJYKNLMkn8DpsvWDyR3UQX_jCzHxiAnY")

model = GenerativeModel("gemini-1.5-flash")
response = model.generate_content("what is a good name for my cat rocky?")

print(response.text)
