from flask import Flask, render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user, login_required
from app.models import User
from flask_login import logout_user
from app.forms import RegistrationForm, PlatformForm
from app import db
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import statsmodels.api as sm
from math import sqrt
from sklearn.metrics import mean_squared_error
from datetime import datetime, timedelta
import pickle
from werkzeug.utils import secure_filename
import os


model = pickle.load(open('model.pkl', 'rb'))

app_root = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(businessname=form.businessname.data, businesstype=form.businesstype.data, email=form.email.data, number=form.number.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/platform', methods=['GET', 'POST'])
@login_required
def platform():
    form = PlatformForm()
    # profile = request.files['profile']
    # profile.save(os.path.join(uploads_dir, secure_filename(profile.filename)))
    target = os.path.join(app_root, 'static/uploads/')
    if not os.path.isdir(target):
        os.makedirs(target)
    if request.method == 'POST':
        ...
        file = request.files['file']
        file_name = 'demfore_data.csv'
        destination = '/'.join([target, file_name])
        file.save(destination)

    # form = PlatformForm()
    # if form.validate_on_submit():
    #     days = form.days.data

    return render_template('platform.html',form=form)

# @app.route('/platform', methods=['GET', 'POST'])
# def platform():
#     # form = PostForm()
#     # if form.validate_on_submit():
#     # final_forecast=None
#     # days=0
#     # final_forecast_dates=None
#     # final_forecast_values=None
#     form = PlatformForm()
#     if form.validate_on_submit():
#         uploaded_file = request.files['file']
#         # filename = secure_filename(uploaded_file.filename)
#         if uploaded_file.filename != '':
#             # file_ext = os.path.splitext(filename)[1]
#             uploaded_file.save(os.path.join(
#             app.instance_path, 'static', filename))

#         # data_file = uploaded_file
#         # data = pd.read_csv(data_file, parse_dates=['date'],index_col='date')
#         # temp_date = pd.read_csv('Demfore_Data2.csv')
#         # y = data['sales']
#         # sarima = sm.tsa.statespace.SARIMAX(y,order=(1,1,1),seasonal_order=(1,1,0,12),
#         #                              enforce_stationarity=False, enforce_invertibility=False,).fit()
#         # pred = sarima.get_prediction(start=pd.to_datetime('2019-01-01'), dynamic=False)
#         # y_truth = y['2019-01-01':]
#         # y_pred = pred.predicted_mean
#         # mse = ((y_pred - y_truth) ** 2).mean()
        
#         # days = form.days.data
#         # results = round(sarima.forecast(steps = days), 2)

#         # future = []
#         # last_date = temp_date["date"].iloc[-1]
#         # last_date = datetime.strptime(last_date, '%d-%m-%y').date()
#         # t_d = last_date

#         # for i in range(days):
#         #     t_d = t_d + timedelta(days = 1)
#         #     future.append(t_d)
#         # forecasting = pd.DataFrame(future)
#         # forecasting.rename(columns = {forecasting.columns[0]: 'Future Dates'}, inplace = True)
#         # forecasting.insert(1, "Forecasted Sales", list(results))
#         # final_forecast_dates = []
#         # final_forecast_values = []
#         # for x in forecasting['Future Dates']:
#         #     final_forecast_dates.append(x.strftime("%m/%d/%Y"))

#         # for x in forecasting["Forecasted Sales"]:
#         #     final_forecast_values.append(x)

        
#         # final_forecast = forecasting.to_string(index=False)

#     return render_template('platform.html', form=form)

@app.route('/forecast', methods=['GET', 'POST'])
def forecast():

    form = PlatformForm()
    # if form.validate_on_submit():
    data_file = 'static/uploads/demfore_data.csv'
    data = pd.read_csv(data_file, parse_dates=['date'],index_col='date')
    temp_date = pd.read_csv(data_file)
    y = data['sales']
    sarima = sm.tsa.statespace.SARIMAX(y,order=(1,1,1),seasonal_order=(1,1,0,12),
                                 enforce_stationarity=False, enforce_invertibility=False,).fit()
    pred = sarima.get_prediction(start=pd.to_datetime('2019-01-01'), dynamic=False)
    y_truth = y['2019-01-01':]
    y_pred = pred.predicted_mean
    mse = ((y_pred - y_truth) ** 2).mean()
    
    stps = form.days.data
    results = round(sarima.forecast(steps = stps), 2)

    future = []
    last_date = temp_date["date"].iloc[-1]
    last_date = datetime.strptime(last_date, '%d-%m-%y').date()
    t_d = last_date

    for i in range(stps):
        t_d = t_d + timedelta(days = 1)
        future.append(t_d)
    forecasting = pd.DataFrame(future)
    forecasting.rename(columns = {forecasting.columns[0]: 'Future Dates'}, inplace = True)
    forecasting.insert(1, "Forecasted Sales", list(results))
    final_forecast_dates = []
    final_forecast_values = []
    for x in forecasting['Future Dates']:
        final_forecast_dates.append(x.strftime("%m/%d/%Y"))
    sales_sum=0
    for x in forecasting["Forecasted Sales"]:
        final_forecast_values.append(x)
        sales_sum += x
    sales_sum = int(round(sales_sum,0))
    final_forecast = forecasting.to_string(index=False)

    return render_template('forecast.html', stps=stps, final_forecast=final_forecast, final_forecast_dates=final_forecast_dates, final_forecast_values=final_forecast_values, sales_sum=sales_sum)


# @app.route('/forecast', methods=['GET', 'POST'])
# def forecast():
#     data_file = 'Demfore_Data2.csv'
#     data = pd.read_csv(data_file, parse_dates=['date'],index_col='date')
#     temp_date = pd.read_csv('Demfore_Data2.csv')
#     y = data['sales']
#     sarima = sm.tsa.statespace.SARIMAX(y,order=(1,1,1),seasonal_order=(1,1,0,12),
#                                  enforce_stationarity=False, enforce_invertibility=False,).fit()
#     pred = sarima.get_prediction(start=pd.to_datetime('2019-01-01'), dynamic=False)
#     y_truth = y['2019-01-01':]
#     y_pred = pred.predicted_mean
#     mse = ((y_pred - y_truth) ** 2).mean()
    
#     stps = 31
#     results = round(sarima.forecast(steps = stps), 2)

#     future = []
#     last_date = temp_date["date"].iloc[-1]
#     last_date = datetime.strptime(last_date, '%d-%m-%y').date()
#     t_d = last_date

#     for i in range(stps):
#         t_d = t_d + timedelta(days = 1)
#         future.append(t_d)
#     forecasting = pd.DataFrame(future)
#     forecasting.rename(columns = {forecasting.columns[0]: 'Future Dates'}, inplace = True)
#     forecasting.insert(1, "Forecasted Sales", list(results))
#     final_forecast_dates = []
#     final_forecast_values = []
#     for x in forecasting['Future Dates']:
#         final_forecast_dates.append(x.strftime("%m/%d/%Y"))

#     for x in forecasting["Forecasted Sales"]:
#         final_forecast_values.append(x)

#     final_forecast = forecasting.to_string(index=False)

#     return render_template('forecast.html', stps=stps, final_forecast=final_forecast, final_forecast_dates=final_forecast_dates, final_forecast_values=final_forecast_values)

