from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
from sqlalchemy import text
from sqlalchemy.orm import relationship
import datetime
from datetime import datetime
from sqlalchemy import ForeignKey



#my DB connection
local_server=True
#initialising the application of flask
app=Flask(__name__)

app.secret_key='Sumanth' #optional


#this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='Login'
@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))

#app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/databas_table_name'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/csms'#data base url this is used for hosting the particular database(one time only)
db=SQLAlchemy(app)

#here we will create DB models that is tables
#Test first letter should be capital
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))

class User(UserMixin,db.Model):
   id=db.Column(db.Integer,primary_key=True)
   username=db.Column(db.String(50))
   email=db.Column(db.String(50),unique=True)
   password=db.Column(db.String(1000))

class Customer(db.Model):
    cid=db.Column(db.Integer,primary_key=True)
    fname=db.Column(db.String(50))
    lname=db.Column(db.String(50))
    dob=db.Column(db.String(50),nullable=False)
    gender=db.Column(db.String(50))
    email=db.Column(db.String(50))
    phnumber=db.Column(db.String(50))
    address=db.Column(db.String(10000))


class Products(db.Model):
   id=db.Column(db.Integer,primary_key=True)
   prname=db.Column(db.String(50))
   description=db.Column(db.Text)
   price=db.Column(db.Integer)
   prid=db.Column(db.String(50),unique=True)
   ratings=db.Column(db.Integer)
   image=db.Column(db.String(100))

class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    offer_id = db.Column(db.Integer)
    discount_percentage = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    # Add more attributes as needed

    # Define relationship with Products table
    product = db.relationship('Products', backref=db.backref('offers', lazy=True))


class Order(db.Model):
   order_id = db.Column(db.Integer, primary_key=True)
   customer_id = db.Column(db.Integer, db.ForeignKey('customer.cid'),nullable=False)
   product_id = db.Column(db.Integer, db.ForeignKey('products.id'),nullable=False)
   email=db.Column(db.String(50))
   product_name = db.Column(db.String(50))
   size = db.Column(db.String(50))
   quantity = db.Column(db.Integer)
   offer = db.Column(db.Integer)
   discount = db.Column(db.Float)
   order_date = db.Column(db.DateTime, default=datetime.utcnow)
   address=db.Column(db.String(10000))
   price=db.Column(db.Integer)
   total=db.Column(db.Float)
   
   
    # Relationships
   product = relationship("Products")
   customer = relationship("Customer") 




#route is a end point that means i run this program i get ip  address
@app.route("/")
def index():
   return render_template('index.html') 
@app.route("/Customer_details",methods=['POST','GET'])
@login_required
def Customer_details():
   if request.method == "GET":
        # Assuming you have access to the current user's email address
        email = current_user.email
        
        # Check if the customer with the provided email already exists in the database
        cust = Customer.query.filter_by(email=email).first()
        
        if cust:
            # If customer exists, redirect to pd.html page
            return render_template('pd.html',custdata=cust)
   if request.method=="POST":
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        dob=request.form.get('dob')
        gender=request.form.get('gender')
        email=request.form.get('email')
        phnumber=request.form.get('phnumber')
        address=request.form.get('address')
        query=Customer(fname=fname,lname=lname,dob=dob,gender=gender,email=email,phnumber=phnumber,address=address)
        db.session.add(query)
        db.session.commit()
        return redirect(url_for('Customer_details'))

   return render_template('Customer.html') 
@app.route("/Product")
def Product():
   
   return render_template('Product.html') 
  
 
@app.route("/Offers")
@login_required
def Offers():
   all_offers = Offer.query.all()
   return render_template('Offer.html', offers=all_offers) 
@app.route("/Login",methods=['POST','GET'])
def Login():
   if request.method=="POST":
      email=request.form.get('email')
      password=request.form.get('password')
      user=User.query.filter_by(email=email).first()

      if user and check_password_hash(user.password,password):
         login_user(user)
         flash("Login Success","primary")
         return redirect(url_for('index'))
      else:
         flash("invalid credentials","danger")
         return render_template('login.html')
      

   return render_template('login.html') 
@app.route("/Signup",methods=['POST','GET'])
def Signup():
   if request.method=="POST":
      username=request.form.get('username')
      email=request.form.get('email')
      password=request.form.get('password')
      user=User.query.filter_by(email=email).first()
      if user:
         flash("email already exists","warning")
         return render_template('signup.html')
      encpassword=generate_password_hash(password)
      #new_user=db.engine.execute(f"INSERT INTO 'user' ('username','email','password') VALUES('{username}','{email}','{encpassword}')")
      newuser=User(username=username,email=email,password=encpassword)
      db.session.add(newuser)
      db.session.commit()
      flash("Signup success please Login","success")
      return render_template('login.html')
   return render_template('signup.html') 
    #a=Test.query.all()
@app.route("/Logout")
@login_required
def Logout():
   logout_user()
   flash("Logout Success","warning")
   return redirect(url_for('Login')) 

@app.route("/Products/Mens")
@login_required
def Mens():
   product_ids = ['TS100', 'SH101','KT102','LU103']
   all_data = Products.query.filter(Products.prid.in_(product_ids)).all()
   return render_template('Mens.html',employees=all_data) 
@app.route("/Products/Womens")
@login_required
def Womens():
   product_ids1 = ['SA104', 'TO105','CH106','JE107']
   all_womens = Products.query.filter(Products.prid.in_(product_ids1)).all()
   return render_template('Womens.html',category2=all_womens) 
@app.route("/Products/Kids")
@login_required
def Kids():
   product_ids2 = ['UM108', 'CS110','BTS111','BCP112']
   all_kids = Products.query.filter(Products.prid.in_(product_ids2)).all()
   return render_template('Kids.html',category3=all_kids) 
    #print(a)
    #return render_template('index.html')                   
    #try:
    #    Test.query.all()
    #    return 'My Data Base is Connected'
    #except:
    #    return 'My DB is not connected'
@app.route("/Purchase_History")
@login_required
def Purchase_History():
   orders = Order.query.filter(Order.email == current_user.email).all()

   return render_template('Purchase_history.html',orders=orders) 
@app.route("/view_cart",methods=["POST","GET"])
def view_cart():
   if request.method == "POST":
        viewid = request.form.get("product_id")
        quant = request.form.get("quantity")
        siz = request.form.get("size")
        # Fetch product details from the database based on product_id
        cart1 = Products.query.filter_by(id=viewid).first()
        return render_template('viewcart.html',cart=cart1,quantity1=quant,size1=siz)
   return redirect(url_for('Product'))

@app.route("/Orders",methods=['POST','GET'])
@login_required
def Orders():
  
   if request.method == "POST":
        product_id = request.form.get("product_id")
        quantity = request.form.get("quantity")
        size = request.form.get("size")
        
        email = current_user.email

        # Fetch product details based on product_id
        product = Products.query.filter_by(id=product_id).first()
        offercode = Offer.query.filter_by(product_id=product_id).first()
        cust = Customer.query.filter_by(email=email).first()
        
        # Check if the customer with the provided email already exists in the database
        
       

        # Create an order and store it in the database
        order = Order(
            customer_id=current_user.id,
            product_id=product.id,
            email=current_user.email,
            product_name=product.prname,
            size=size,
            quantity=quantity,
            offer=offercode.id,
            discount=offercode.discount_percentage,
            order_date=datetime.utcnow(),
            address=cust.address,
            price=product.price,
            total=product.price*(1-offercode.discount_percentage/100)

            
         )
        db.session.add(order)
        db.session.commit()

        flash("Order placed successfully!", "success")
        return redirect(url_for('Orders'))  # Redirect to the orders page after placing the order

   return redirect(url_for('index'))




   #The render_template function used to render HTML templates. It takes the template's filename as its first argument and a set of variables as the second argument.

#@app.route('/test') in webpage when we click on test at that time we get https://some.in/test
#To Run the application
app.run(debug=True)
#username=current_user.username