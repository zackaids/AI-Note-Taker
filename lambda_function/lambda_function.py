import json
import pandas as pd
import boto3
import time
import openai
import urllib.parse

def lambda_handler(event, context):
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    data = amazon_transcribe(key, transcribe)
    input_text = read_text_from_json(data)

    prompt = f"Please generate a detailed summary of the following text:\n{input_text}"
    
    detailed_summary = summarize_text(prompt, max_tokens=100)
    
    output_file_path = 'detailed_summary.txt'
    with open(output_file_path, 'w') as file:
        file.write(detailed_summary)

    s3 = boto3.client(  's3', 
                            aws_access_key_id = "access_key_id",
                            aws_secret_access_key = "secret_access_key",
                            region_name = "us-east-1")
    s3.upload_file("./detailed_summary.txt", "finalnotes", "detailed_summary.txt")
    
    

transcribe = boto3.client(  'transcribe',
                            aws_access_key_id = "access_key_id",
                            aws_secret_access_key = "secret_access_key",
                            region_name = "us-east-1")

def check_job_name(job_name):
    job_verification = True

    # all the transcriptions
    existed_jobs = transcribe.list_transcription_jobs()

    for job in existed_jobs['TranscriptionJobSummaries']:
        if job_name == job['TranscriptionJobName']:
            job_verification = False
            break

    if job_verification == False:
        command = input(job_name + " has existed. \nDo you want to override the existed job (Y/N): ")
        if command.lower() == "y" or command.lower() == "yes":
            transcribe.delete_transcription_job(TranscriptionJobName=job_name)
        elif command.lower() == "n" or command.lower() == "no":
            job_name = input("Insert new job name? ")
            check_job_name(job_name)
        else: 
            print("Input can only be (Y/N)")
            command = input(job_name + " has existed. \nDo you want to override the existed job (Y/N): ")
    return job_name


def amazon_transcribe(audio_file_name, transcribe):
    job_uri = "s3://audioinputs/" + audio_file_name
    job_name = (audio_file_name.split('.')[0]).replace(" ", "")  
    # file format  
    file_format = audio_file_name.split('.')[1]
  
    # check if name is taken or not
    job_name = check_job_name(job_name)
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat=file_format,
        LanguageCode='en-US')
  
    while True:
        result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if result['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        time.sleep(15)
        
    if result['TranscriptionJob']['TranscriptionJobStatus'] == "COMPLETED":
        data_uri = result['TranscriptionJob']['Transcript']['TranscriptFileUri']
        print(data_uri)
        data = pd.read_json(data_uri).to_json()
        return data
    else:
        return None

def summarize_text(text, max_tokens=100):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=text,
        max_tokens=max_tokens,
        temperature=0.7,  # Adjust temperature for more creative outputs
        top_p=1.0,  # Adjust top_p for more randomness in outputs
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response.choices[0].text.strip()


def read_text_from_json(data): 
    data = json.loads(data)
    transcripts = data['results']['transcripts']
    text = ""
    for transcript in transcripts:
        text += transcript['transcript']
    return text