import openai
import json
import boto3

# Set your API key
openai.api_key = 'api_key'


def summarize_text(text, max_tokens=100):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=text,
        max_tokens=max_tokens,
        temperature=0.7, 
        top_p=1.0, 
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response.choices[0].text.strip()


def read_text_from_json(file_path): 
    with open(file_path, 'r') as file:
        data = json.load(file)
        transcripts = data['results']['transcripts']
        text = ""
        for transcript in transcripts:
            text += transcript['transcript']
        return text

# Path to your JSON file
json_file_path = 'testaudio.json'

# Read text from JSON file
input_text = read_text_from_json(json_file_path)

prompt = f"Please generate a detailed summary of the following text:\n{input_text}"

# Summarize the text
detailed_summary = summarize_text(prompt, max_tokens=100)

output_file_path = 'detailed_summary.txt'
with open(output_file_path, 'w') as file:
    file.write(detailed_summary)

print(f"Detailed summary written to {output_file_path}")

s3 = boto3.client('s3', 
  aws_access_key_id = "access_key_id",
                            aws_secret_access_key = "secret_access_key",
region_name = "us-east-1")
s3.upload_file("C:\\Users\\lavdr\\codefest-2024\\detailed_summary.txt", "finalnotes", "detailed_summary.txt")

