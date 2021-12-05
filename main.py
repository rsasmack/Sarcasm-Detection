from flask import *
import sqlite3
import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

con=sqlite3.connect("newsarcastic.db")
cur=con.cursor()
cur.execute('create table if not exists register(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL,email TEXT NOT NULL, password TEXT NOT NULL)')
cur.execute('CREATE TABLE IF NOT EXISTS textresult(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,name TEXT NOT NULL,data TEXT NOT NULL, emotion TEXT NOT NULL,polarity TEXT NOT NULL)')

df= pd.read_csv("Sarcastic1.csv")
df_data = df[["Tweet","Class"]]
# Features and Labels
df_x = df_data['Tweet']
df_y = df_data.Class
# Extract Feature With CountVectorizer
corpus = df_x
cv = CountVectorizer()
X = cv.fit_transform(corpus)
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, df_y, test_size=0.33, random_state=42)
#Naive Bayes Classifier
from sklearn.naive_bayes import MultinomialNB
clf = MultinomialNB()
clf.fit(X_train,y_train)
clf.score(X_test,y_test)

data1=pd.read_csv("Twitter_Data.csv")
data1.isnull().sum()
data1["input"]=data1["clean_text"].fillna("hi")
data1["output"]=data1["category"].fillna(0.0)
X1 = data1['input']
y1 = data1['output']
X1_train,X1_test,y1train,y1test=train_test_split(X1,y1,test_size=0.10,random_state=42)
vectorizer1 = TfidfVectorizer( max_df= 0.9).fit(X1_train)
X1_train = vectorizer1.transform(X1_train)
X1_test = vectorizer1.transform(X1_test)
encoder1 = LabelEncoder().fit(y1train)
y1_train = encoder1.transform(y1train)
y1_test = encoder1.transform(y1test)
model1 = LogisticRegression(C=.1, class_weight='balanced')
model1.fit(X1_train,y1_train)
y1_pred_train = model1.predict(X1_train)
y1_pred_test = model1.predict(X1_test)
print("Training Accuracy : ", accuracy_score(y1_train, y1_pred_train))
print("Testing Accuracy  : ", accuracy_score(y1_test, y1_pred_test))



app=Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict',methods=['POST'])
def saveemotion():
    if request.method=="POST":
        a=request.form['txt']
        data=[a]
        vect = cv.transform(data).toarray()
        my_prediction = clf.predict(vect)
        tfidf1 = vectorizer1.transform([a])
        preds1 = model1.predict_proba(tfidf1)[0]    
        preds1=list(preds1)
        re1=preds1.index(max(preds1))

        d={0:'NEGATIVE',1:'NEUTRAL',2:'POSITIVE'}
        re1=d[re1]
        re1=str(re1)

        if my_prediction[0]==0:
            result="NOT SARCASM"
            result1=re1
            finalresult="emotion={0} and polarity={1}".format(result,result1)
            con=sqlite3.connect('newsarcastic.db')
            cur=con.cursor()
            cur.execute('select * from register where username=?',(session['username'],))
            row=cur.fetchone()
            username=row[1]
            cur.execute('insert into textresult(name,data,emotion,polarity) values(?,?,?,?)',(session['username'],a,result,result1))
            con.commit()
            return render_template('result.html',temp=result,temp1=result1)
        elif my_prediction[0]==1:
            result="SARCASM"
            result1=re1
            finalresult="emotion={0}  and polarity={1}  and mail={2}  and data={3}".format(result,result1,session['email'],data[0])
            con=sqlite3.connect('newsarcastic.db')
            cur=con.cursor()
            cur.execute('select * from register where username=?',(session['username'],))
            row=cur.fetchone()
            username=row[1]
            cur.execute('insert into textresult(name,data,emotion,polarity) values(?,?,?,?)',(session['username'],a,result,result1))
            con.commit()
            return render_template('result.html',temp=result,temp1=result1)
        else:
            pass
@app.route('/register.html')
def registration():
    return render_template('register.html')


@app.route('/registrationpagedetails',methods=['POST'])
def saveregvalues():
    if request.method == "POST":
        username=request.form['a']
        phnumber=request.form['b']
        password=request.form['c']
        password1=request.form['d']
        if(password1==password):
            with sqlite3.connect("newsarcastic.db") as con:  
                cur = con.cursor()  
                cur.execute("insert into register(username,phnumber,password)values(?,?,?)",(username,phnumber,password))
                con.commit()
                return redirect('register1.html')
        else:
            return render_template('register.html')
    else:
        
        return render_template('register.html')


@app.route('/userlogindetails',methods=['POST','GET'])

def saveloginvalues():

    if request.method == "POST":
        loginusername=request.form['11']
        loginpassword=request.form['13']
        with sqlite3.connect("newsarcastic.db") as con:
            cur = con.cursor()  
            cur.execute("select * from register where username=?",(loginusername,))
            
            rows = cur.fetchone()  
        
            u1=rows[1]
            u2=rows[3]
            u3=rows[2]
            
            
            if((loginusername ==u1 ) and (loginpassword == u2)):
                session['username']=u1
                session['email']=u3
                return redirect('post.html')
            else:
                return render_template('register1.html')

    return render_template('register.html')



@app.route('/post.html')
def postvalue():
    return render_template('post.html')

@app.route('/register1.html')
def newloginpage():
    return render_template('register1.html')

@app.route('/FAQS.html')
def Faqs():
    return render_template('FAQS.html')


@app.route('/about_us.html')
def about():
    return render_template('about_us.html')

if __name__=='__main__':
    app.secret_key = 'myworld'
    app.run(debug=True)
