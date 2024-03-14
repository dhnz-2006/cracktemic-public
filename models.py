from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()


class usermaster(db.Model):
    __tablename__='tbl_user_master'
    user_id = db.Column(db.String(40),primary_key=True)
    username_str = db.Column(db.String(40))
    role_str = db.Column(db.String(40))
    created_dt = db.Column(db.DateTime, default=datetime.datetime.utcnow())


    def __init__(self,user_id,username_str,role_str,created_dt):
        self.user_id = user_id
        self.username_str=username_str
        self.role_str = role_str
        self.created_dt = created_dt


class langmaster(db.Model):
    __tablename__='tbl_language_master'
    lang_id = db.Column(db.String(40),primary_key=True)
    langname_str = db.Column(db.String(40))
    created_dt = db.Column(db.DateTime, default=datetime.datetime.utcnow())


    def __init__(self,lang_id,langname_str,created_dt):
        self.lang_id = lang_id
        self.langname_str=langname_str
        self.created_dt = created_dt

class dialougemaster(db.Model):
    __tablename__='tbl_dialouge_master'
    dialouge_id = db.Column(db.Integer(),primary_key=True,autoincrement = True)
    lang = db.Column(db.String(50))
    dialouge_file_link = db.Column(db.String(400))
    created_dt = db.Column(db.DateTime, default=datetime.datetime.utcnow())


    def __init__(self,dialouge_id,lang,dialouge_file_link,created_dt):
        self.dialouge_id = dialouge_id
        self.lang=lang
        self.dialouge_file_link = dialouge_file_link
        self.created_dt = created_dt

class filemaster(db.Model):
    __tablename__='tbl_file_master'
    file_id = db.Column(db.Integer(),primary_key=True,autoincrement = True)
    filelink_str = db.Column(db.String(400))
    user_id = db.Column(db.String(400))
    lang_id = db.Column(db.String(400))
    dialouge_id = db.Column(db.String(400))
    created_dt = db.Column(db.DateTime, default=datetime.datetime.utcnow())


    def __init__(self,file_id,filelink_str,user_id,lang_id,dialouge_id,created_dt):
        self.file_id = file_id
        self.filelink_str = filelink_str
        self.user_id = user_id
        self.lang_id = lang_id
        self.dialouge_id = dialouge_id
        self.created_dt = created_dt


