from flask import Flask, request, render_template, redirect, url_for, flash 
from models import User, db  
from config import Config    
import pickle                
import numpy as np         
from flask_login import LoginManager, login_user, login_required, logout_user 
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
db.init_app(app)

socketio = SocketIO(app)

#gọi người dùng từ csdl
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@socketio.on('user_message')
def handle_user_message(msg):
    print('User messeage: '+ msg)
    emit('new_question',msg, broadcast=True)

@socketio.on('teacher_response')
def  handle_teacher_response(response):
    print('Teacher response: '+ response)
    emit('response', response ,  broadcast=True)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Email đã tồn tại. Vui lòng chọn email khác.', 'danger')
            return redirect(url_for('signup'))

        new_user = User(
            username=username,
            email=email,
            password=password,
            )
        db.session.add(new_user)
        db.session.commit()
        flash('Đăng ký thành công! Bạn có thể đăng nhập.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.', 'danger')
    return render_template('login.html')

model = pickle.load(open('model.pkl', 'rb'))

@app.route('/teacher')
def teacher_page():
    return render_template('teacher.html')

@app.route('/main')
def home():
    return render_template('main.html')

@app.route('/predict', methods=['POST'])
def predict():
   
    
    input_features = [float(x) for x in request.form.values()]
    features = np.array([input_features])
    
    
    prediction_proba = model.predict_proba(features)
    
    prob_pass = prediction_proba[0][1] * 100
    prob_fail = 100 - prob_pass

    result = f'Xác suất đậu: {prob_pass:.2f}%, Xác suất rớt: {prob_fail:.2f}%'
    
    return render_template('main.html', logged_in=True, prediction_text=f'Kết quả: {result}', show_register=False)

if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(debug=True)

