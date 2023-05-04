import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from flask import Flask,render_template,request,redirect,session,url_for,flash
from tensorflow.keras.models import load_model
import sqlite3
app=Flask(__name__)
app.secret_key="123"
model=load_model('crude_oil.h5',)
name1=input();

con=sqlite3.connect("database.db")
con.execute("create table if not exists customer(pid integer primary key,name text,mobile integer,password text)")
con.execute("create table if not exists price(name text,price decimal(2,10))")
con.close()

@app.route('/')
def home():
    return render_template("index.html")
@app.route('/about')
def home1():
    return render_template("index.html")
@app.route('/predict')
def home2():
    return render_template("web.html")


@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        try:
            name=request.form['name'] 
            mobile=request.form['mobile']
            password=request.form['password']
            con=sqlite3.connect("database.db")
            cur=con.cursor()
            cur.execute("insert into customer(name,mobile,password)values(?,?,?)",(name,mobile,password))
            con.commit()    
            flash("Record Added Successfully","success")
        except:
            flash("Error in Insert Operations","danger")
        finally:
            return render_template("index.html")
            con.close()
    return render_template("register.html")



@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        
        name=request.form['name'] 
        session["name1"]=request.form['name'] 
        password=request.form['password']
        con=sqlite3.connect("database.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("select * from customer where name=? and password=?",(name,password))
        data=cur.fetchone()
        if data:
            session["name"]=data["name"]
            return render_template("web.html")
        else:
            flash("Usernaem and Password Mismatch","danger")
            return redirect("login")

    return render_template("login.html")

@app.route('/prediction',methods=['POST'])
def prediction():
    x_input=str(request.form['year'])
    x_input=x_input.split(',')
    print(x_input)
    for i in range(0,len(x_input)):
        x_input[i]=float(x_input[i])
    print(x_input)
    x_input=np.array(x_input).reshape(1,-1)
    temp_input=list(x_input)
    temp_input=temp_input[0].tolist()
    lst_output=[]
    n_steps=10
    i=0
    while(i<1):
        if(len(temp_input)>10):
            x_input=np.array(temp_input[1:])
            print("{} day input {}".format(i,x_input))
            x_input=x_input.reshape(1,-1)
            x_input=x_input.reshape((1,n_steps,1))

            yhat=model.predict(x_input,verbose=0)
            print("{} day output {}".format(i,yhat))
            temp_input.extend(yhat[0].tolist())
            temp_input=temp_input[1:]

            lst_output.extend(yhat.tolist())
            i=i+1

        else:
            x_input=x_input.reshape((1,n_steps,1))
            yhat=model.predict(x_input,verbose=0)
            print(yhat[0])
            temp_input.extend(yhat[0].tolist())
            print(len(temp_input))
            lst_output.extend(yhat.tolist())
            i=i+1

        print(lst_output)
        con=sqlite3.connect("database.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        name1=session["name"]
        price=str(lst_output[0][0])
        cur.execute("insert into price(name,price) values(?,?)",(name1,price,))
        
        con.commit()   
        cur.execute("select * from")
        return render_template("web.html",showcase='The next day predicted value is:'+str(lst_output[0][0]))


if __name__=='__main__':
    app.run(debug=True,port=5000)