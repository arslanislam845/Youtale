from flask import Flask, render_template, request, jsonify, session, redirect
from flask_wtf.csrf import CSRFProtect
from transformers import pipeline
from datetime import timedelta
import math

import utility
app = Flask(__name__)
csrf = CSRFProtect(app)
app.secret_key ="youtale"


@csrf.exempt
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=300)
    session.modified = True
@csrf.exempt
@app.route('/',methods=['GET','POST'])
def index():
  if 'email' in session:
     return render_template('index.html',status="Log Out",link="/logout")
  return render_template('index.html',status="Log in",link="/login")
@csrf.exempt
@app.route('/login',methods=['GET','POST'])
def login():
  if 'email' in session:
     return redirect('/home')
  return render_template('login.html',response='')
@csrf.exempt
@app.route('/logout',methods=['GET','POST'])
def logout():
  if 'email' in session:
  # remove the username from the session if it's there
      session.pop('email', None)
  if 'password' in session:
  # remove the password from the session if it's there
      session.pop('password', None)
  return redirect('/login')
@csrf.exempt
@app.route('/signup',methods=['GET','POST'])
def signup():
  if 'email' in session:
     return redirect('/home')
  return render_template('signup.html',response='')


@csrf.exempt
@app.route('/signup_credentials',methods=['GET','POST'])
def signup_credentials():
  if request.method=="POST":
    collection = utility.get_mongodb_collection()
    name = request.form['name'] 
    email = request.form['email'] 
    password = request.form['password'] 
    cpassword = request.form['Cpassword'] 
    if password==cpassword:
      collection.insert_one({"name":name,"email":email,"password":password})
      return redirect('/login')
    else:
      return render_template("signup.html",response='Password doesnot match')
  else:
      return redirect('/signup')
     
@csrf.exempt
@app.route('/transcribe',methods=['GET','POST'])
def transcribe():
  if 'email' in session:
     return render_template('transcribe.html')
  return redirect('/login')
@csrf.exempt
@app.route('/home',methods=['GET','POST'])
def home():
  if 'email' in session:
     return render_template('home.html')
  if request.method =='POST':
    collection=utility.get_mongodb_collection()
    email = request.form['email'] 
    password = request.form['password'] 
    try:
      collection.find({"email": email})[0]
      collection.find({"password": password})[0]
      session['email'] = email
      session['password'] = password
      return render_template('home.html')
    except Exception:
       return render_template("login.html",response="Invalid Username and Password")
  return redirect('/login')


@csrf.exempt
@app.route('/result.html', methods=['GET', 'POST'])
def result():
  if 'email' in session:
    return render_template('result.html')
  return redirect('/login')


@csrf.exempt
@app.route('/submit',methods=['GET','POST'])
def submit():
    # try:
      if 'email' in session:
        try:
            video_url=request.form["video_url"]
        except Exception:
          return redirect('/transcribe')
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
            
            # text_splitter = RecursiveCharacterTextSplitter(
            #     chunk_size=1000, chunk_overlap=0)
            # docs = text_splitter.split_documents(transcript)
            # result = ', '.join([str(doc).split("metadata={'source':")[0][14:-2].replace('[Music]', "" ) for doc in docs])
            return str(transcript[0]).split("metadata={'")[0][14:-2]

        # video_url = "https://www.youtube.com/watch?v=bgiPTUy2RqI"
        # video_url = "https://youtu.be/4xG2aJa6UyY"
        # video_url = "https://www.youtube.com/watch?v=L_Guz73e6fw"
        docs=create_db_from_youtube_video_url(video_url)
        print(docs)
        return render_template("result.html",docs=docs,url=url)
      return redirect('/')
@csrf.exempt
@app.route('/get_summary', methods=['GET', 'POST'])
def get_summary():
    # try:
      if request.method=="POST":
        try:
          docs=request.get_json(force=True)['docs']
          summarizer = pipeline(
              "summarization", model="philschmid/bart-large-cnn-samsum")
          length=math.ceil(len(docs)/5000)
          print("@@@@@@@@",length)
          start_window=0
          end_window=0
          summary=''
          for i in range(0,length):
            end_window=end_window+5000
            summary=summarizer(docs[start_window:end_window])[0]['summary_text']+summary
            start_window=end_window
            print(summary)
          return jsonify({"status":200,"summary":summary})
        except Exception as e:
          print("Error is",e)
          return jsonify({"status":400})
 
if __name__ == '__main__':
  app.run(debug=True)
  
  
  # docs="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."