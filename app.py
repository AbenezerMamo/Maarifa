from flask import Flask
from flask.ext.restless import APIManager
from flask.ext.sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Maarifa.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Text, primary_key=True, unique=True)
    current_math = db.Column(db.Integer, default=0)
    current_english = db.Column(db.Integer, default=0)
    current_science = db.Column(db.Integer, default=0)


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    lesson_subject = db.Column(db.Text)
    lesson_level = db.Column(db.Integer)
    lesson_content = db.Column(db.Text)
    lesson_id = db.Column(db.Integer)


db.create_all()

api_manager = APIManager(app, flask_sqlalchemy_db=db)
api_manager.create_api(User, methods=['GET', 'POST', 'DELETE', 'PUT'])
api_manager.create_api(Lesson, methods=['GET', 'POST', 'DELETE', 'PUT'])


def request_data(subject, lesson_id):
    r = requests.get('http://maarifa.herokuapp.com/api/lesson')
    data = r.json()
    for lessons in data['objects']:
        if subject in lessons.values():
            if lessons["lesson_id"] == lesson_id:
                return lessons["lesson_content"]


@app.route("/", methods=['GET', 'POST'])
def message_handling():
    resp = twilio.twiml.Response()
    body = request.values.get('Body', None).lower()
    from_number = request.values.get('From', None)
    users = requests.get('http://maarifa.herokuapp.com/api/user')
    user_data = users.json()
    for user in user_data['objects']:
        if from_number in user.values():
            if body == 'math':
                content = request_data('math', user['current_math'])
                resp.message(content)
            elif body == 'science':
                content = request_data('science', user['current_science'])
                resp.message(content)
            elif body == 'english':
                content = request_data('english', user['current_english'])
                resp.message(content)
            else:
                resp.message('Subject currently not supported!')
        else:
            headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
            sign_up = {'id': '+1415655674583'}  # , 'current_math': 0, 'current_english': 0, 'current_science': 0}
            print("####################################")
            print(sign_up)
            requests.post(url="http://maarifa.herokuapp.com/api/lesson", json=sign_up)
            resp.message("Welcome to TextLessons!")
    return str(resp)



if __name__ == "__main__":
    app.run(port=3000)
