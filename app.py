import pandas as pd
import numpy as np
from flask import Flask,render_template,request,session,redirect, Response, url_for, flash
import pickle
import uuid
import mysql.connector
from werkzeug.security import generate_password_hash
from hashlib import sha256





#creating object for class flask
app=Flask(__name__)
app.secret_key = "ashhdb"


#loading the model 
with open("ipl_model.pkl","rb") as f:
    model=pickle.load(f)


# connecting the db
db_config={
    'host':'localhost',
    'user':'root',
    'password':'',
    'database':'ipl'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def hash_password(password):
    return sha256(password.encode()).hexdigest()

#prediction 
def predict_score(batting_team='Chennai Super Kings', bowling_team='Mumbai Indians', 
                  overs=5.1, runs=50, wickets=0, runs_in_prev_5=50,
                    wickets_in_prev_5=0):
    temp_array=list()
    if batting_team == 'Chennai Super Kings':
        temp_array = temp_array + [1,0,0,0,0,0,0,0]
    elif batting_team == 'Delhi Daredevils':
        temp_array = temp_array + [0,1,0,0,0,0,0,0]
    elif batting_team == 'Kings XI Punjab':
        temp_array = temp_array + [0,0,1,0,0,0,0,0]
    elif batting_team == 'Kolkata Knight Riders':
        temp_array = temp_array + [0,0,0,1,0,0,0,0]
    elif batting_team == 'Mumbai Indians':
        temp_array = temp_array + [0,0,0,0,1,0,0,0]
    elif batting_team == 'Rajasthan Royals':
        temp_array = temp_array + [0,0,0,0,0,1,0,0]
    elif batting_team == 'Royal Challengers Bangalore':
        temp_array = temp_array + [0,0,0,0,0,0,1,0]
    elif batting_team == 'Sunrisers Hyderabad':
        temp_array = temp_array + [0,0,0,0,0,0,0,1]

    # Bowling Team
    if bowling_team == 'Chennai Super Kings':
        temp_array = temp_array + [1,0,0,0,0,0,0,0]
    elif bowling_team == 'Delhi Daredevils':
        temp_array = temp_array + [0,1,0,0,0,0,0,0]
    elif bowling_team == 'Kings XI Punjab':
        temp_array = temp_array + [0,0,1,0,0,0,0,0]
    elif bowling_team == 'Kolkata Knight Riders':
        temp_array = temp_array + [0,0,0,1,0,0,0,0]
    elif bowling_team == 'Mumbai Indians':
        temp_array = temp_array + [0,0,0,0,1,0,0,0]
    elif bowling_team == 'Rajasthan Royals':
        temp_array = temp_array + [0,0,0,0,0,1,0,0]
    elif bowling_team == 'Royal Challengers Bangalore':
        temp_array = temp_array + [0,0,0,0,0,0,1,0]
    elif bowling_team == 'Sunrisers Hyderabad':
        temp_array = temp_array + [0,0,0,0,0,0,0,1]

    temp_array = temp_array + [overs, runs, wickets, runs_in_prev_5, wickets_in_prev_5]

  # Converting into numpy array
    temp_array = np.array([temp_array])
    print(temp_array)

    # Prediction
    return int(model.predict(temp_array))

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/predict',methods=['POST','GET'])
def predict():
    if request.method=='POST':
        batting_team=request.form.get('batting_team')
        bowling_team=request.form.get('bowling_team')
        overs=float(request.form.get('overs'))
        runs=int(request.form.get('runs'))
        wickets=int(request.form.get('wickets'))
        runs_in_prev_5=int(request.form.get('runs_in_prev_5'))
        wickets_in_prev_5=int(request.form.get('wickets_in_prev_5'))
        score=predict_score(batting_team=batting_team, bowling_team=bowling_team, 
                  overs=overs, runs=runs, wickets=wickets, runs_in_prev_5=runs_in_prev_5,
                    wickets_in_prev_5=wickets_in_prev_5)
        return render_template('predict.html',prediction=score)


    return render_template('predict.html')

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method=='POST':
        username=request.form['name']
        email=request.form['email']
        password=request.form['password']

        conn=get_db_connection()
        cursor=conn.cursor()

        #check if email already exists
        cursor.execute("SELECT * FROM user where email=%s",(email,))
        if cursor.fetchone():
            conn.close()
            flash("Email already exists!.Please Choose another email","error")
            return redirect(url_for("register"))
        
        #inserting new user
        hashed=hash_password(password)
        cursor.execute("INSERT INTO user (uname,email,password) VALUES(%s,%s,%s)",
                       (username,email,hashed))
        conn.commit()
        conn.close()
        flash("Registration Successfull!. Please Login","success")
        return redirect(url_for("login"))
    

    return render_template("register.html")


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form["email"]
        password=request.form["password"]
        conn=get_db_connection()
        cursor=conn.cursor(dictionary=True)
        cursor.execute("SELECT * from user where email=%s",(email,))
        user=cursor.fetchone()

        if user and hash_password(password)==user['password']:
            session['user_id']= user["u_id"]
            session['username']= user["uname"]
            session['uemail']= user["email"]
            flash("Login successfull!","success")
            return redirect(url_for("index"))
        else:
            flash("Invalid Email or Password!!","error")
            return(redirect(url_for("login")))
            

    return render_template("login.html")


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfull!!","success")
    return redirect(url_for("login"))

#to create a main function
if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0',port=7000)
