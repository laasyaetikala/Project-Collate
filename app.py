from flask import Flask, render_template,flash,redirect,url_for,session,logging,request,jsonify
from flask_wtf import FlaskForm
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, FileField, SelectField, SubmitField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import smtplib
from flask_mail import Mail, Message


app=Flask(__name__)
mail= Mail(app)
#config Mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'projectcollate@gmail.com'
app.config['MAIL_PASSWORD'] = 'ehwpygtoeifzrzeb'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

#config MySQL
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='mini_project'
app.config['MYSQL_CURSORCLASS']='DictCursor'

#init MySQL
mysql=MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')


class StudentForm(FlaskForm):
    name=StringField("name",[validators.Length(min=1,max=200)])
    rollno=StringField("rollno",[validators.Length(min=10,max=10)])
    email=StringField("email",[validators.Length(min=1,max=200)])
    passout=StringField("passout",[validators.Length(min=4,max=4)])
    batchno=StringField("batchno",[validators.Length(min=1,max=2)])
    password=PasswordField("password",[
        validators.DataRequired(),
        validators.Length(min=1,max=200),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm=PasswordField('confirm')
    s_submit=SubmitField('studentsubmit')

class FacultyForm(FlaskForm):
    name=StringField("name",[validators.Length(min=1,max=200)])
    id=StringField("rollno",[validators.Length(min=10,max=10)])
    email=StringField("email",[validators.Length(min=1,max=200)])
    domains=StringField("domains",[validators.Length(min=1,max=200)])
    password=PasswordField("password",[
        validators.DataRequired(),
        validators.Length(min=1,max=200),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm=PasswordField('confirm')
    f_submit=SubmitField('facultysubmit')


@app.route('/register', methods=['GET','POST'])
def register():
    s_form=StudentForm(request.form)
    f_form=FacultyForm(request.form)
    print('take form')
    print(request.method)
    print(s_form.s_submit.data)
    #print(s_form.validate_on_submit())
    if request.method=='POST': #and s_form.s_submit.data and s_form.validate():
        print(s_form.validate())
        if request.form['submit']=='student':# and s_form.validate():
            print('in stu')
            name=request.form['name']
            rollno=request.form['rollno']
            email=request.form['email']
            passout=request.form['passout']
            batchno=request.form['batchno']
            password = sha256_crypt.encrypt(str(request.form['password']))
            print('before insert')
            cur=mysql.connection.cursor()
            cur.execute("INSERT INTO student(name,roll_no,email,passout_year,batch_no,password) VALUES(%s,%s,%s,%s,%s,%s)",(name,rollno,email,passout,batchno,password))
            #commit to DB
            mysql.connection.commit()
            #close connection 
            cur.close()
            #flash('Details Submitted')
            msg = 'Details Submitted'
            #return redirect(url_for('index'))
            return render_template('register.html', msg=msg)

        elif request.form['submit']=='faculty': #and f_form.f_submit.data and f_form.validate():
            print('in fac')
            name=request.form['name']
            id=request.form['id']
            email=request.form['email']
            domain=request.form['domains']
            print(domain)
            password = sha256_crypt.encrypt(str(request.form['password']))
            cur=mysql.connection.cursor()
            print(name,id)
            r1=cur.execute("INSERT INTO faculty(name,faculty_id,email,domain,password) VALUES(%s,%s,%s,%s,%s)",(name,id,email,domain,password))
            print(r1,'fac')
            #for i in domains:
            r2=cur.execute("INSERT INTO domains(faculty_id,domain) VALUES(%s,%s)",(id,domain))
            print(r2,'dom')
            mysql.connection.commit()
            cur.close()
            #flash('Details Submitted')
            msg = 'Details Submitted'
            #return redirect(url_for('index'),msg=msg)
            return render_template('register.html',msg=msg)

    return render_template('register.html',s_form=s_form,f_form=f_form)

class Login(FlaskForm):
    username=StringField('Username',[validators.Length(min=5)])
    password=PasswordField('Password',[validators.Length(min=5)])

#user login
@app.route('/login',methods=['POST','GET'])
def login():    
    form=Login(request.form)
    if request.method=='POST':
        if request.form['submit']=='student':
            username=request.form['username']
            password_candidate=request.form['password'] 
            cur=mysql.connection.cursor()
            result=cur.execute("SELECT * FROM student WHERE roll_no=%s",[username])
            print(result)
            if result>0:
                #get stored hash
                data=cur.fetchone()
                password=data['password']
            
                #compare passwords
                if sha256_crypt.verify(password_candidate,password):
                    #passed
                    print('in if')
                    session['logged_in']=True
                    cur.execute("SELECT name FROM student WHERE roll_no=%s",[username])
                    data=cur.fetchone()
                    session['username']=username
                    session['name']=data['name']
                    # app.logger.info('PASSWORD MATCHED ')
                    print('registered')
                    print(session['username'])
                    return redirect(url_for('index'))
                else:
                    error="Invalid Login"
                    # app.logger.info('PASSWORD NOT MATCHED')
                    # flash('Invalid login','danger')
                    return render_template('login.html',error=error)
            else:
                #app.logger.info('no user')   
                error="Username not found"
                return render_template('login.html',error=error)

        elif request.form['submit']=='faculty':
            username=request.form['username']
            password_candidate=request.form['password'] 
            cur=mysql.connection.cursor()
            result=cur.execute("SELECT * FROM faculty WHERE faculty_id=%s",[username])
            if result>0:
                #get stored hash
                data=cur.fetchone()
                password=data['password']
            
                #compare passwords
                if sha256_crypt.verify(password_candidate,password):
                    #passed
                    print('in if')
                    session['logged_in']=True
                    res=cur.execute("SELECT name FROM faculty WHERE faculty_id=%s",[username])
                    print(res)
                    data=cur.fetchone()
                    session['username']=username
                    session['name']=data['name']
                    # app.logger.info('PASSWORD MATCHED ')
                    print('registered')
                    print(session['username'])
                    return render_template('index.html',form=form)
                else:
                    error="Invalid Login"
                    # app.logger.info('PASSWORD NOT MATCHED')
                    # flash('Invalid login','danger')
                    return render_template('login.html',error=error)
            else:
                app.logger.info('no user')   
                error="username not found"
                return render_template('login.html',error=error)
            
    return render_template('login.html')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            #flash('Unauthorized, Please login','danger')
            return redirect(url_for('login')) 
    return wrap


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    return redirect(url_for('index'))


class UploadProject(FlaskForm):
    title=StringField('title')
    domain=StringField('domain')
    abstract=TextAreaField('abstract')
    techstack=TextAreaField('techstack')
    source_code=TextAreaField('code')
    team=TextAreaField('details')

@app.route('/upload',methods=['GET','POST'])
@is_logged_in
def upload():
    form=UploadProject(request.form)
    if request.method=='POST':
        print('in upload')
        title=request.form['title']
        domain=request.form['domain']
        abstract=request.form['abstract']
        techstack=request.form['techstack']
        source_code=request.form['code']
        team=request.form['details']
        cur=mysql.connection.cursor()
        res=cur.execute("SELECT batch_no,passout_year FROM student WHERE roll_no=%s",[session['username']])
        data=cur.fetchone()
        print(data['batch_no'])
        id=str(data['passout_year'])+'_'+str(data['batch_no'])
        print(id)
        cur.execute("INSERT INTO project(id,title,domain,tech_stack,abstract,source_code,team_details) VALUES(%s,%s,%s,%s,%s,%s,%s)",(id,title,domain,techstack,abstract,source_code,team))
        mysql.connection.commit()
        cur.close()

        flash('Uploaded Project Details','success')
        return redirect(url_for('dashboard'))

    return render_template('upload.html',form=form)

class Search(FlaskForm):
    title=StringField('search')

@app.route('/dashboard',methods=['GET'])
@is_logged_in
def dashboard():
    form=Search(request.form)
    cur=mysql.connection.cursor()
    if request.args.get('search')=='search_title':
        print("post for livesearch")
        search = request.args.get('searchtitle')
        title = "%{}%".format(search)
        print(search)
        cur=mysql.connection.cursor()
        res=cur.execute("SELECT * FROM project WHERE title LIKE '{}%' order by title".format(title))
        filtered=cur.fetchall()
        print(filtered)
        res=cur.execute("SELECT * FROM project")
        projects=cur.fetchall()
        return render_template('dashboard.html',projects=filtered)
    else:
        cur=mysql.connection.cursor()
        res=cur.execute("SELECT * FROM project")
        projects=cur.fetchall()
        if res>0:
            return render_template('dashboard.html',projects=projects)
        else:
            msg='No Projects Available'
            return render_template('dashboard.html',msg=msg)
    return render_template('dashboard.html',form=form)

@app.route('/viewproject/<string:title>')
@is_logged_in
def display_project(title):
    cur=mysql.connection.cursor()
    res=cur.execute("SELECT * FROM project WHERE title=%s",[title])
    project=cur.fetchone()
    res=cur.execute("SELECT * FROM comments WHERE title=%s",[title])
    comments=cur.fetchall()
    print(comments)
    session['ptitle']=title
    return render_template('project.html',project=project,comments=comments)

@app.route('/selectDomain/<domain>',methods=['POST','GET'])
@is_logged_in
def selectDomain(domain):
    cur=mysql.connection.cursor()
    res=cur.execute("SELECT * FROM project WHERE domain=%s",[domain])
    filtered=cur.fetchall()
    print(filtered)
    return render_template('dashboard.html',projects=filtered)

class Comment(Form):
    comment=TextAreaField('comment')

@app.route('/comments',methods=['POST'])
@is_logged_in
def comment():
    form=Comment(request.form)
    print('in comm*****')
    cur=mysql.connection.cursor()
    title=session['ptitle']
    res=cur.execute("SELECT * FROM project WHERE title=%s",[title])
    project=cur.fetchone()
    res=cur.execute("SELECT * FROM comments WHERE title=%s",[title])
    comments=cur.fetchall()
    if request.method=='POST':
        print('hiii*******')
        c=request.form['comment']
        print(c) 
        print(type(c))      
        res=cur.execute("INSERT INTO comments(title,name,comment) VALUES(%s,%s,%s)",(session['ptitle'],session['name'],c))
        mysql.connection.commit()        
        cur.close()
        return render_template('project.html',project=project,comments=comments)
    return render_template('project.html',form=form,project=project,comments=comments)

def send_mail(to,body):
    '''msg=EmailMessage()
    msg.set_content(body)
    msg['subject']='Project Support from Project Collate'
    msg['to']=to'''
    subj='Project Support from Project Collate'
    froms='projectcollate@gmail.com'
    password='zetjcyxbxaolnkxi'

    #msg['from']=froms
    msg="Subject: {}\n\n{}".format(subj,body)
    server=smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(froms,password)
    #server.send_message(msg)
    print(froms)
    server.sendmail(froms,to,msg)
    server.close()


@app.route('/mail')
def mail():
    cur=mysql.connection.cursor()
    res=cur.execute("SELECT * FROM faculty")
    faculty=cur.fetchall()
    print(faculty)
    res=cur.execute("SELECT * FROM student")
    students=cur.fetchall()
    return render_template('mail.html',faculty=faculty,students=students)

@app.route('/mail/<string:name>')
def mailto(name):
    cur=mysql.connection.cursor()
    if len(session['username'])==10:
        res=cur.execute("SELECT email FROM student WHERE roll_no=%s",[session['username']])
        s_email=cur.fetchone()
        res=cur.execute("SELECT email FROM faculty WHERE name=%s",[name])
        r_email=cur.fetchone()
    else:
        res=cur.execute("SELECT email FROM faculty WHERE faculty_id=%s",[session['username']])
        s_email=cur.fetchone()
        res=cur.execute("SELECT email FROM student WHERE name=%s",[name])
        r_email=cur.fetchone()
    print(r_email)
    print(s_email,'****')
    msg = Message('Project Support from Project Collate', sender = 'projectcollate@gmail.com', recipients = [r_email['email']])
    body = "Hello "+str(name)+"! This is from Project Collate support.\n"+str(session['name'])+" has some queries on a project\nCould you please reach out to the below mail.\n"+s_email['email']+"\nThank You!"
    send_mail(r_email['email'],body)
    #mail.send(msg)
    return render_template('mailsent.html')


if __name__=='__main__':
    app.secret_key='1234'
    app.run(debug=True)