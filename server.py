from flask import Flask, render_template,request
import re
import pandas as pd
from jinja2 import Environment, filters
app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/login.html')
def login():
  return render_template('login.html')

@app.route('/signup.html')
def signup():
  return render_template('signup.html')

@app.route('/transcribe.html')
def transcribe():
  return render_template('transcribe.html')

@app.route('/home.html')
def home():
  return render_template('home.html')

@app.route('/result.html')
def result():
  return render_template('result.html')

@app.route('/submit',methods=['POST'])
def submit():
    # try:
      if request.method=="POST":
        video_url=request.form["video_url"]
        print(video_url)
        url=video_url[-11:]
        print(url)
        from langchain.document_loaders import YoutubeLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.embeddings.openai import OpenAIEmbeddings
        import openai
        import os

        openai.api_key = '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'
        
        def create_db_from_youtube_video_url(video_url):
            loader = YoutubeLoader.from_youtube_url(video_url)
            transcript = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=0)
            docs = text_splitter.split_documents(transcript)
            result = ', '.join([str(doc).split("metadata={'source':")[0][14:-2].replace('[Music]', "" ) for doc in docs])
            
            return result

        # video_url = "https://www.youtube.com/watch?v=bgiPTUy2RqI"
        # video_url = "https://youtu.be/4xG2aJa6UyY"
        # video_url = "https://www.youtube.com/watch?v=L_Guz73e6fw"
        docs=create_db_from_youtube_video_url(video_url)
        print(docs)

        return render_template("result.html",docs=docs,url=url)

 
if __name__ == '__main__':
  app.run(debug=True)
  
  
  # docs="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."