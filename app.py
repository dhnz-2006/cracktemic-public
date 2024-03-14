from flask import *
from flask_sqlalchemy import SQLAlchemy as _BaseSQLAlchemy
from flask_migrate import Migrate
from models import db
import os
import pathlib
import psycopg2
import re
import requests
from werkzeug.exceptions import BadRequestKeyError,RequestEntityTooLarge
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from werkzeug.utils import secure_filename
import datetime
from psycopg2.errors import *

app = Flask(__name__)

app.secret_key = 'afhodhbsnbdals'
app.static_folder='static'
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
app.config['UPLOAD_FOLDER'] = 'UPLOAD_FOLDER/'
app.config['DOWNLOAD_FOLDER'] = 'DOWNLOAD_FOLDER/'
app.config['MAX_CONTENT_LENGTH'] = 10*1024*1024 #100mb

migrate = Migrate()
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://dhnz2006:PwmQsVGZ0Rb3@ep-green-sound-a1aw4vjb.ap-southeast-1.aws.neon.tech/crackthemic'

db.init_app(app)
conn = psycopg2.connect(database="crackthemic", user="dhnz2006", 
                        password="PwmQsVGZ0Rb3", host="ep-green-sound-a1aw4vjb.ap-southeast-1.aws.neon.tech", port="5432") 


client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
GOOGLE_CLIENT_ID = '409001498988-jdb3erqtuhn844mi9ihvt19s9hkctsdq.apps.googleusercontent.com'
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)


auth=[]


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401) 
        else:
            return function()

    return wrapper

@app.errorhandler(404)  
def not_found(e): 
  return render_template("404.html")

def tupleit(val):
    listval=[]
    for i in val:
        for j in i:
            listval.append(j)
    return listval

@app.route("/login", methods=['POST','GET'])
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback", methods=['POST','GET'])
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    auth.append(1)
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
        )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/indexpage")


@app.route("/logout", methods=['POST','GET'])
def logout():
    session.clear()
    auth.clear()
    return redirect("/")


@app.route('/',methods=['post','get'])
def applogin():
    return render_template('template_login.html')

@app.route('/indexpage',methods=['post','get'])
def index():
    if 1 in auth:
        cursor=conn.cursor()
        cursor.execute('''select langname_str from tbl_language_master; ''')
        langs = cursor.fetchall()
        cursor.execute('''select user_id from tbl_user_master; ''')
        uids = cursor.fetchall()
        #cursor.close()
        if session['google_id'] not in tupleit(uids):
            try:
                now = datetime.datetime.utcnow()
                cursor=conn.cursor()
                cursor.execute(''' insert into tbl_user_master(user_id,username_str,role_str,created_dt) values('{0}','{1}','USER','{2}')'''.format(session['google_id'],session['name'],now))
                conn.commit()
                cursor.close()
            except InFailedSqlTransaction:
                return redirect('/')
        if request.method=='POST':
            lang = request.form.get('lang')
            return redirect('/homepage/'+lang)
    else:
        cursor.close()
        return redirect('/')
    return render_template("template_index.html",languages = tupleit(langs))

@app.route('/homepage/<lang>',methods=['post','get'])
def homepage(lang):
    cursor = conn.cursor()
    cursor.execute('''SELECT dialouge_file_link FROM tbl_dialouge_master where lang = '{0}' ORDER BY RANDOM() OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY;'''.format(lang))
    global mp3_path
    mp3_path = cursor.fetchone()
    cursor.execute('''select lang_id from tbl_language_master where langname_str = '{0}' '''.format(lang))
    langid = cursor.fetchone()
    cursor.execute('''select dialouge_id from tbl_dialouge_master where dialouge_file_link = '{0}' '''.format(mp3_path[0]))
    did=cursor.fetchone()
    print(mp3_path[0].split('/')[1])
    cursor.close()
    if request.method=='POST':
        if 'audio' in request.files:
            file = request.files['audio']
            file.filename=session['name']+"_"+(mp3_path[0].split('/')[1])+'.mp3'
            try:
                
                if file:
                    cursor = conn.cursor()
                    file.save(app.static_folder+'/'+app.config['UPLOAD_FOLDER']+secure_filename(file.filename))
                    

                    now=datetime.datetime.now()
                    cursor.execute('''insert into tbl_file_master(filelink_str,user_id,lang_id,dialouge_id,created_dt) values('{0}','{1}','{2}','{3}','{4}')'''.format(app.config['UPLOAD_FOLDER']+secure_filename(file.filename),session['google_id'],langid[0],did[0],now))
                    conn.commit()
                    cursor.close()
            except RequestEntityTooLarge:
                flash('File too Large')
            
        else:
            return redirect('/')
    return render_template('template_homepage.html',langz=lang,mp3path=mp3_path[0])

@app.route('/admin/dialougecreater',methods=['post','get'])
def dialouge():
    cursor=conn.cursor()
    cursor.execute(''' select role_str from tbl_user_master where user_id = '{0}' '''.format(session['google_id']))
    userrole = cursor.fetchone()
    cursor.close()
    now = datetime.datetime.utcnow()
    cursor=conn.cursor()
    cursor.execute('''select langname_str from tbl_language_master; ''')
    langs = cursor.fetchall()
    cursor.close()
    if request.method=='POST':
        try:
            lang = request.form.get('lang')
            file = request.files['dialougefile']
            if file:
                file.save(app.static_folder+'/'+app.config['DOWNLOAD_FOLDER']+secure_filename(file.filename))
                cursor = conn.cursor()
                cursor.execute('''insert into tbl_dialouge_master (lang,dialouge_file_link,created_dt) values('{0}','{1}','{2}')'''.format(lang,app.config['DOWNLOAD_FOLDER']+secure_filename(file.filename),now))
                conn.commit()
        except RequestEntityTooLarge:
            flash('File is Larger than 10MB Limit')

    return render_template('template_new_dialouge.html',languages = tupleit(langs))


if __name__ == '__main__':
    with app.app_context():
        migrate.init_app(app,db)
        db.create_all()
        app.run(host="0.0.0.0")
