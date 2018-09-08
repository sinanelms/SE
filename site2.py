from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps
import pandas as pd
import random


# Kullanıcı Giriş Decorator'ı
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapın.","danger")
            return redirect(url_for("login"))

    return decorated_function
# Kullanıcı Kayıt Formu
class RegisterForm(Form):
    name = StringField("İsim Soyisim",validators=[validators.Length(min = 4,max = 25)])
    username = StringField("Kullanıcı Adı",validators=[validators.Length(min = 5,max = 35)])
    email = StringField("Email Adresi",validators=[validators.Email(message = "Lütfen Geçerli Bir Email Adresi Girin...")])
    password = PasswordField("Parola:",validators=[
        validators.DataRequired(message = "Lütfen bir parola belirleyin"),
        validators.EqualTo(fieldname = "confirm",message="Parolanız Uyuşmuyor...")
    ])
    confirm = PasswordField("Parola Doğrula")
class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")

app = Flask(__name__,static_folder='static')
app.secret_key= "ybblog"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "ybblog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)
#Anasayfa
@app.route("/")
def index():
    cursor = mysql.connection.cursor()
    sorgu = "SELECT * FROM site2 WHERE ID = (SELECT MAX(ID) FROM site2)"
    
    result = cursor.execute(sorgu) 
    if result > 0:
        articles = cursor.fetchone()
        
        return render_template("site.html",articles = articles)
    else:
        return render_template("site.html")
    cursor.close()


    
#Haritalar
@app.route("/maps")
def about():
    return render_template("maps.html")
#Atama Url
@app.route("/sonuc",methods=["GET","POST"])
def sonuc():      
    cursor = mysql.connection.cursor()
    sorgu = "Select * From site"
    result = cursor.execute(sorgu)    
    if result >0:
        articles = cursor.fetchall()
        cursor.execute("DELETE FROM site")
        mysql.connection.commit()
        cursor.close()
        return render_template("sonuc.html",articles= articles)
    else:
        cursor.execute("DELETE FROM site")
        mysql.connection.commit()
        cursor.close()
        return render_template("site.html")
    cursor.execute("DELETE FROM site")
    mysql.connection.commit()
    cursor.close()
 #mysql kaydetme
#bilgi
@app.route("/bilgi",methods=["GET","POST"])
def bilgi():
    keyword = request.form.get("keyword")
    isimler = keyword.split("\r")     
    if request.method == "POST" and (len(keyword) >= 3):
        yer = pd.read_excel("yerler.xlsx")        
               
        
        for isim in isimler:
            if (len(isim) >= 3) :
                rastgele = random.randint(1,592)
                yeniYer = yer.iloc[rastgele]                    
                cursor = mysql.connection.cursor()    
                sorgu = "Insert into site(yerler,bolge,teskilati,ACM,ili,isim) VALUES(%s,%s,%s,%s,%s,%s)"
                cursor.execute(sorgu,(yeniYer["yerler"],yeniYer["bolge"],yeniYer["teskilati"],yeniYer["ACM"],yeniYer["ili"],isim))
                sorgu2 = "Insert into site2(isim) VALUES(%s)"
                cursor.execute(sorgu2,(isim,))
                mysql.connection.commit()
            elif  len(isim) == 1:
                continue                                             
            else:
                flash("Lütfen isimleri düzgün giriniz...","danger")
                return render_template("site.html")

        cursor.close()
            
        flash("Başarılı...","success")
        return redirect(url_for("sonuc")) #sonuca yönlendir
    else:
        flash("İsim(ler) girmeyi unuttunuz...","danger")
        return render_template("site.html")
#Son giriş zamanını öğrenme
@app.route("/ekip")
@login_required
def dashboard():
    cursor = mysql.connection.cursor()

    sorgu = "Select * From site2"

    result = cursor.execute(sorgu)
    
    if result > 0:
        articles = cursor.fetchall()
        return render_template("ekip.html",articles = articles)
    else:
        return render_template("ekip.html")

    
#Kayıt Olma

# Login İşlemi
@app.route("/login",methods =["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
       username = form.username.data
       password_entered = form.password.data

       cursor = mysql.connection.cursor()

       sorgu = "Select * From users where username = %s"

       result = cursor.execute(sorgu,(username,))

       if result > 0:
           data = cursor.fetchone()
           real_password = data["password"]
           if sha256_crypt.verify(password_entered,real_password):
               flash("Başarıyla Giriş Yaptınız...","success")

               session["logged_in"] = True
               session["username"] = username

               return redirect(url_for("index"))
           else:
               flash("Parolanızı Yanlış Girdiniz...","danger")
               return redirect(url_for("login")) 

       else:
           flash("Böyle bir kullanıcı bulunmuyor...","danger")
           return redirect(url_for("login"))

    
    return render_template("login.html",form = form)

# Logout İşlemi
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))



#iletişim
@app.route("/iletisim")
def iletisim():
    return render_template("call.html")

#resimler
@app.route("/resimler")
def resim():
    return render_template("resim.html")


if __name__ == "__main__":
    app.run(debug=True)