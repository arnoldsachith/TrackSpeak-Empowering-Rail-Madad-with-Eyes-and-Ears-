import requests
from flask import Flask, render_template, request, session
import json
import os
from datetime import datetime

import google.generativeai as genai
import PIL

genai.configure(api_key="*****yDcIkhhBY7Y1gc4Z8nD7ymsfCETXm*****")


##GOOGLE GEMINI MODEL
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")


# Create or cleanup existing extracted image frames directory.
FRAME_EXTRACTION_DIRECTORY = "/content/frames"
FRAME_PREFIX = "_frame"


def create_frame_output_dir(output_dir):
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)
  else:
    shutil.rmtree(output_dir)
    os.makedirs(output_dir)

def extract_frame_from_video(video_file_path): ##CODE FOR EXTRACTING FRAMES FROM VIDEO
  print(f"Extracting {video_file_path} at 1 frame per second. This might take a bit...")
  create_frame_output_dir(FRAME_EXTRACTION_DIRECTORY)
  vidcap = cv2.VideoCapture(video_file_path)
  fps = vidcap.get(cv2.CAP_PROP_FPS)
  frame_duration = 1 / fps  # Time interval between frames (in seconds)
  output_file_prefix = os.path.basename(video_file_path).replace('.', '_')
  frame_count = 0
  count = 0
  while vidcap.isOpened():
      success, frame = vidcap.read()
      if not success: # End of video
          break
      if int(count / fps) == frame_count: # Extract a frame every second
          min = frame_count // 60
          sec = frame_count % 60
          time_string = f"{min:02d}:{sec:02d}"
          image_name = f"{output_file_prefix}{FRAME_PREFIX}{time_string}.jpg"
          output_filename = os.path.join(FRAME_EXTRACTION_DIRECTORY, image_name)
          cv2.imwrite(output_filename, frame)
          frame_count += 1
      count += 1
  vidcap.release() # Release the capture object\n",
  print(f"Completed video frame extraction!\n\nExtracted: {frame_count} frames")
  
class File:
  def __init__(self, file_path: str, display_name: str = None):
    self.file_path = file_path
    if display_name:
      self.display_name = display_name
    self.timestamp = get_timestamp(file_path)

  def set_file_response(self, response):
    self.response = response

def get_timestamp(filename):
  """Extracts the frame count (as an integer) from a filename with the format
     'output_file_prefix_frame00:00.jpg'.
  """
  parts = filename.split(FRAME_PREFIX)
  if len(parts) != 2:
      return None  # Indicates the filename might be incorrectly formatted
  return parts[1].split('.')[0]
  
# Make GenerateContent request with the structure described above.
def make_request(prompt, files):
  request_1 = [prompt]
  for file in files:
    request_1.append(file.timestamp)
    request_1.append(file.response)
  return request_1
        
        
@app.route('/PNR_OCR',methods=["POST"])
def PNR_OCR():

  file = request.files["pnr_image_file"]
  image_path = "pnr_images/"+current_dateTime+".png"
  ticket = PIL.Image.open(image_path)
  print(image_path)
  prompt = """Identify the PNR number from the image, return the output in JSON schema {"PNR_number":}"""

  response = model.generate_content([prompt, ticket], generation_config = {
    'response_mime_type': 'application/json'
    })
  print(response)
  res = json.loads(response.text)
  print(res)
  
  return res
    
@app.route('/audio_process',methods=["POST","GET"])

def Audio_based_Transcript_and_Intent(): # FUNCTION OUTLINES THE AUDIO BASED TRANSCRIPT, INTENT RECOGNITION USING GEMINI PRO

    print(request.files)
    file = request.files["audio_file"]
    pnr = request.form["pnr"]
    print(file.filename)
    
    torchaudio.save(filename,resampled_waveform,resample_rate)

    session["filename"] = filename
    print(filename)
    your_file = genai.upload_file(path=filename)

    # Configure JSON response and safety settings
    generation_config = {
        'response_mime_type': 'application/json'  # Add this line for JSON response
    }
    
    prompt = 'Listen carefully to the following audio file. Provide the transcription in their respective native language. Remove the entities like person name, station name from the given text. Also bucket the text into one of the categories = Staff-Behaviour_Staff-Behaviour,Security_Smoking/Drinking_Alcohol/Narcotics, Security_Theft_of_Passengers_Belongings/Snatching, Security_Harassment, Coach-Cleanliness_Toilets, Coach-Cleanliness_Cockroach/Rodents, Coach-Cleanliness_Coach-Interior, Electrical-Equipment_AC, Electrical-Equipment_Fans, Electrical-Equipment_Lights, Corruption/Bribery_Corruption/Bribery. Return the response in JSON schema = {"Transcription": <String>,"Intent Category":,"Entity_person_name":,"Entity_station_name":}. If there are no entities or if the sentence does not belong to any intent category return NA'
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
    
    response = model.generate_content([prompt, your_file], generation_config=generation_config)
    
    print(response)
    res = json.loads(response.text)
    print(res)
    if isinstance(res,list):
      res = res[0]
      transcript = res['Transcription']
      category = res['Intent Category']
      category = category.split("_")
      category_fin = category[0]
      sub_category_fin = category[1]
    else:
      transcript = res['Transcription']
      category = res['Intent Category']
      category = category.split("_")
      category_fin = category[0]
      sub_category_fin = category[1]
      
    
    return {"message":"success","transcription": transcript, 'category':category_fin, 'sub-category':sub_category_fin, "org_audio":blob_dat_org}
    
    
@app.route('/video_process',methods=["POST","GET"])

def Video_Process(): #GEMINI BASDE VIDEO + TEXT ANALYSIS

    print(request.files)
    file = request.files["video_file"]
    pnr = request.form["pnr"]
    filename_vd = "videos/" + pnr+"_"+lang+"_"+current_dateTime+".mp4"

    filename = "audios/" + pnr+"_"+lang+"_"+current_dateTime+".wav"

    file.save(filename_vd)

    session["filename"] = filename
    p = subprocess.Popen(['ffmpeg',"-i", filename_vd,"-ac",'1',"-ar",'16000',"-vn","-acodec","pcm_s16le",filename], stdout = subprocess.PIPE)
    (output, err) = p.communicate()
    p_status = p.wait()

    
    your_file = genai.upload_file(path=filename)

    # Configure JSON response and safety settings
    generation_config = {
        'response_mime_type': 'application/json'  # Add this line for JSON response
    }
    
    prompt = 'Listen carefully to the following audio file. Provide the transcription in their respective native language. Remove the entities like person name, station name from the given text. Also bucket the text into one of the categories = Staff-Behaviour_Staff-Behaviour,Security_Smoking/Drinking_Alcohol/Narcotics, Security_Theft_of_Passengers_Belongings/Snatching, Security_Harassment, Coach-Cleanliness_Toilets, Coach-Cleanliness_Cockroach/Rodents, Coach-Cleanliness_Coach-Interior, Electrical-Equipment_AC, Electrical-Equipment_Fans, Electrical-Equipment_Lights, Corruption/Bribery_Corruption/Bribery. Return the response in JSON schema {"Transcription": <String>,"Intent Category":,"Entity_person_name":,"Entity_station_name":}. If there are no entities or if the sentence does not belong to any intent category return NA'
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
    
    response = model.generate_content([prompt, your_file], generation_config=generation_config)
    
    print(response)
    res = json.loads(response.text)
    print(res)
    if isinstance(res,list):
      res = res[0]
      transcript = res['Transcription']
      category = res['Intent Category']
      category = category.split("_")
      category_fin = category[0]
      sub_category_fin = category[1]
    else:
      transcript = res['Transcription']
      category = res['Intent Category']
      category = category.split("_")
      category_fin = category[0]
      sub_category_fin = category[1]
      
    
    video_file_name = filename_vd
    extract_frame_from_video(video_file_name)
    # Process each frame in the output directory
    files = os.listdir(FRAME_EXTRACTION_DIRECTORY)
    files = sorted(files)
    files_to_upload = []
    for file in files:
      files_to_upload.append(
          File(file_path=os.path.join(FRAME_EXTRACTION_DIRECTORY, file)))
    
    # Upload the files to the API
    # Only upload a 10 second slice of files to reduce upload time.
    # Change full_video to True to upload the whole video.
    full_video = True
    
    uploaded_files = []
    print(f'Uploading {len(files_to_upload) if full_video else 10} files. This might take a bit...')
    
    for file in files_to_upload if full_video else files_to_upload[40:50]:
      print(f'Uploading: {file.file_path}...')
      response = genai.upload_file(path=file.file_path)
      file.set_file_response(response)
      uploaded_files.append(file)
    
    print(f"Completed file uploads!\n\nUploaded: {len(uploaded_files)} files")
    
    # Create the prompt.
    prompt = """Go through the video and transcription, compare and tell me if video and whatever user has spoken matches the video content, also give reason why?.Provide the detailed video analysis as well. return the output in JSON schema :{"Matching_Percentage": ,"reason":,"Video_Analysis":} """ + "transcription :" + transcript
    
    # Make the LLM request.
    request_2 = make_request(prompt, uploaded_files)
    response = model.generate_content(request_2,
                                      request_options={"timeout": 600}, generation_config = {
        'response_mime_type': 'application/json'  # Add this line for JSON response
    })
    
    
    res = json.loads(response.text)
    print(res)

    
    return {"message":"success","transcription": transcript, 'category':category_fin, 'sub-category':sub_category_fin}

