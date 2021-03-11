from flask import Flask, request, render_template, redirect, url_for, flash
import sys

import requests
from flask_sqlalchemy import SQLAlchemy
import datetime
# ..
app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.sqlite3'
app.config['SECRET_KEY'] = 'super secret key'

db = SQLAlchemy(app)


class Weather(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable = False, unique=True)
    state = db.Column(db.String(50),nullable = False)
    degree = db.Column(db.Integer)
    time = db.Column(db.String(50),nullable = False)

    def __repr__(self):
        return 'City=%r' % self.name

db.create_all()

def get_weather(city):
    params = dict(q=city, appid='2cd86366483c364e6f43b5c9ae79fbac', units='metric')
    r = requests.get(f'https://api.openweathermap.org/data/2.5/weather', params=params).json()
    print(r['id'])
    time = (datetime.datetime.utcnow() + datetime.timedelta(seconds=r['timezone'])).hour
    if (8 <= time <= 11) or (20 <= time <= 23): background_class = 'evening-morning'
    elif 12 <= time <= 19: background_class = 'day'
    elif 0 <= time <= 7: background_class = 'night'
    else: background_class = 'evening-morning'

    dict_with_weather_info = { 'city': r['name'].upper(),
        'degree': int(r['main']['temp']),
        'state': r['weather'][0]['description'],
        'time': background_class   }

    return dict_with_weather_info


@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    city = Weather.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/',methods=['GET','POST', 'PUT'])
def index():
    print('KIND', request.method)
    if request.method == 'POST':
        try:
            act = list(request.form.keys())[0]
            if act =='delete':
                del_ths_city = list(request.form.values())[0]
                return redirect('/delete/'+del_ths_city)
        except:
            pass

        try:
            city = request.form['city_name']
            dict_with_weather = get_weather(city)
            #flash("This city does exist!!!!")
        except Exception:
            flash("The city doesn't exist!")
            return redirect('/')

        weather = Weather(name=dict_with_weather['city'],
                          state=dict_with_weather['state'],
                          degree=dict_with_weather['degree'],
                          time=dict_with_weather['time'])

        try:  # Добавляем новый город, если такой уже есть бросаем исключение
            db.session.add(weather)
            db.session.commit()
            dict_with_weather = Weather.query.all()

        except Exception as e:
            db.session.rollback()
            dict_with_weather = Weather.query.all()
            flash("The city has already been added to the list!")

        print(dict_with_weather)
        return render_template('index.html', weather=dict_with_weather)

    db.session.rollback()
    dict_with_weather = Weather.query.all()
    print(dict_with_weather)
    return render_template('index.html', weather=dict_with_weather)


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else: app.run()
