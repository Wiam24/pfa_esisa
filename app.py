from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import pickle
import os

# Load the pickled ensemble model
with open("ensemble_model.pkl", "rb") as model_file:
    ensemble_model = pickle.load(model_file)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)  # Or set to a fixed string: app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

# Create the database
with app.app_context():
    db.create_all()

# Load and preprocess the data
df = pd.read_csv("Clean_Input_Data.csv")
# ... Preprocessing steps ..

@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/team', methods=['GET'])
def team():
    return render_template('team.html')

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # Clear the session data
    session.clear()
    # Redirect the user to the login page
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username  # Store username in session
            return redirect(url_for('index'))  # Redirect to the home page after login
        else:
            flash('Invalid username or password', 'error')  # Adding category 'error'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')  # Adding category 'error'
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful', 'success')  # Adding category 'success'
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/get_data', methods=['GET'])
def get_data():
    cust_id = request.args.get('cust_id')
    customer_data = df[df['CUST_ID'] == cust_id]
    data = customer_data.to_dict(orient='records')[0]
    return jsonify(data)

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    
    username = session['username']
    if request.method == 'POST':
        cust_id = request.form['cust_id']
        balance = float(request.form['balance'])
        balance_frequency = float(request.form['balance_frequency'])
        purchases = float(request.form['purchases'])
        oneoff_purchases = float(request.form['oneoff_purchases'])
        installments_purchases = float(request.form['installments_purchases'])
        cash_advance = float(request.form['cash_advance'])
        purchases_frequency = float(request.form['purchases_frequency'])
        oneoff_purchases_frequency = float(request.form['oneoff_purchases_frequency'])
        purchases_installments_frequency = float(request.form['purchases_installments_frequency'])
        cash_advance_frequency = float(request.form['cash_advance_frequency'])
        cash_advance_trx = float(request.form['cash_advance_trx'])
        purchases_trx = float(request.form['purchases_trx'])
        credit_limit = float(request.form['credit_limit'])
        payments = float(request.form['payments'])
        minimum_payments = float(request.form['minimum_payments'])
        prc_full_payment = float(request.form['prc_full_payment'])
        tenure = float(request.form['tenure'])

        input_data = pd.DataFrame({
            'CUST_ID': [cust_id],
            'BALANCE': [balance],
            'BALANCE_FREQUENCY': [balance_frequency],
            'PURCHASES': [purchases],
            'ONEOFF_PURCHASES': [oneoff_purchases],
            'INSTALLMENTS_PURCHASES': [installments_purchases],
            'CASH_ADVANCE': [cash_advance],
            'PURCHASES_FREQUENCY': [purchases_frequency],
            'ONEOFF_PURCHASES_FREQUENCY': [oneoff_purchases_frequency],
            'PURCHASES_INSTALLMENTS_FREQUENCY': [purchases_installments_frequency],
            'CASH_ADVANCE_FREQUENCY': [cash_advance_frequency],
            'CASH_ADVANCE_TRX': [cash_advance_trx],
            'PURCHASES_TRX': [purchases_trx],
            'CREDIT_LIMIT': [credit_limit],
            'PAYMENTS': [payments],
            'MINIMUM_PAYMENTS': [minimum_payments],
            'PRC_FULL_PAYMENT': [prc_full_payment],
            'TENURE': [tenure]
        })

        # Apply preprocessing steps to the input data (e.g., one-hot encoding)
        # Make sure to apply the same preprocessing as you did when loading the data
        # ...

        prediction = ensemble_model.predict(input_data)
        print("Data retrieved and predicted successfully")

        return render_template('home.html', prediction=prediction, df=df, username=username)

    return render_template('home.html', prediction=None, df=df, username=username)

# Import and create the dashboard
from dashboard import create_dash_app
dash_app = create_dash_app(app)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
