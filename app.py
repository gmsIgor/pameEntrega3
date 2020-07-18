from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
# from flask_mail import Mail, Message
import bcrypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data-dev.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JSON_SORT_KEYS"] = False

# app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USERNAME'] = 'apikey'
# app.config['MAIL_PASSWORD'] = 'e-pass'
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False


db = SQLAlchemy(app)
# mail = Mail(app)


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    idade = db.Column(db.Integer, default=0)

    password_hash = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, default=False)

    def json(self):
        user_json = {'id': self.id,
                     'name': self.name,
                     'email': self.email,
                     'idade': self.idade}
        return user_json


@app.route('/users/', methods=['POST'])
def create():

    data = request.json

    name = data.get('name')
    email = data.get('email')
    idade = data.get('idade')
    password = data.get('password')

    if not name or not email or not password:
        return {'error': 'Dados insuficientes'}, 400

    user_check = User.query.filter_by(email=email).first()

    if user_check:
        return {'error': 'Usuario já cadastrado'}, 400

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    user = User(name=name, email=email, idade=idade,
                password_hash=password_hash)

    db.session.add(user)
    db.session.commit()

    # msg = Message(sender='fluxo.cce@gmail.com',
    #               recipients=[email],
    #               subject='Bem Vindo!',
    #               body='texto do email aqui')

    # mail.send(msg)

    return user.json(), 200


@app.route('/users/', methods=['GET'])
def index():

    data = request.args

    idade = data.get('idade')

    if not idade:
        users = User.query.all()
    else:

        idade = idade.split('-')

        if len(idade) == 1:

            users = User.query.filter_by(idade=idade[0])
        else:

            users = User.query.filter(
                db.and_(User.idade >= idade[0], User.idade <= idade[1]))

    return jsonify([user.json() for user in users]), 200


@app.route('/users/<int:id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def user_detail(id):

    user = User.query.get_or_404(id)

    if request.method == 'GET':
        return user.json(), 200

    if request.method == 'PUT':

        data = request.json

        if not data:
            return {'error': 'Requisição precisa de body'}, 400

        name = data.get('name')
        email = data.get('email')

        if not name or not email:
            return {'error': 'Dados insuficientes'}, 400

        if User.query.filter_by(email=email).first() and email != user.email:
            return {'error': 'Email já cadastrado'}, 400

        user.name = name
        user.email = email

        db.session.add(user)
        db.session.commit()

        return user.json(), 200

    if request.method == 'PATCH':

        data = request.json

        if not data:
            return {'error': 'Requisição precisa de body'}, 400

        email = data.get('email')

        if User.query.filter_by(email=email).first() and email != user.email:
            return {'error': 'Email já cadastrado'}, 400

        user.name = data.get('name', user.name)
        user.email = data.get('email', user.email)
        user.idade = data.get('idade', user.idade)

        db.session.add(user)
        db.session.commit()

        return user.json(), 200

    if request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()

        return {}, 204

@app.route('/users/login', methods=['POST'])
def user_auth():
    data = request.json
    
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email = email).first()

    if bcrypt.checkpw(password.encode(), user.password_hash):
        return {"msg":"usuário logado"}, 200
    else:
        return {"msg":"email ou senha inválidos"}, 400




if __name__ == '__main__':
    app.run(debug=True)
