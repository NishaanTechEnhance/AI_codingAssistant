import os
import re
import time
from flask import Flask, render_template, request
from openai import AzureOpenAI
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv("DEPLOYMENT_NAME")

client = AzureOpenAI(
    api_key=api_key,
    api_version="2024-02-01",
    azure_endpoint=azure_endpoint
)

criteria_options = [
    "Code optimization",
    "Code generation",
    "Code debugging",
    "Code testing"
]

criteria_descriptions = {
    "Code optimization": "Improve the performance, readability, and maintainability of the code.",
    "Code generation": "Generate detailed correct code according to the prompt.",
    "Code debugging": "Identify and fix errors in the code, and provide suggestions for improvement.",
    "Code testing": "Provide suggestions for writing and executing unit tests and testing strategies."
}

prompts = {
    "Code optimization": "Analyze the existing code to improve its performance, readability, and maintainability.",
    "Code generation": "Analyze the given prompt and generate detailed correct code according to the prompt.",
    "Code debugging": "Identify and fix errors in the code, and provide suggestions for improvement.",
    "Code testing": "Provide suggestions for writing and executing unit tests, as well as testing strategies."
}

def remove_comments(code):
    code = re.sub(r'//.*', '', code)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    return code.strip()

def call_openai_chat_completion(model, messages):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error while calling OpenAI API: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        code_input = request.form.get('code_input', '')
        criteria_selected = request.form.get('criteria_selected')
        uploaded_file = request.files.get('uploaded_file')
        
        if uploaded_file and uploaded_file.filename:
            code_input = uploaded_file.read().decode("utf-8")
        
        code_input = remove_comments(code_input)
        prompt = prompts.get(criteria_selected, "")
        messages = [
            {"role": "system", "content": "You are a helpful coding assistant."},
            {"role": "user", "content": f"User provided code:\n{code_input}"},
            {"role": "assistant", "content": prompt}
        ]
        
        output = call_openai_chat_completion(deployment_name, messages)
        time.sleep(2)
        
        if output:
            return render_template('index.html', criteria_options=criteria_options, criteria_descriptions=criteria_descriptions, output=output)
        else:
            return "Error occurred while generating response. Please try again later."
    
    return render_template('index.html', criteria_options=criteria_options, criteria_descriptions=criteria_descriptions)

if __name__ == "__main__":
    app.run(debug=True)
