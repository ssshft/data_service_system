import os
import re
from datetime import datetime
from threading import Lock
import threading

from flask import Flask, url_for, request, render_template, jsonify
from flask_login import LoginManager, login_user, login_required
from gevent import pywsgi
from werkzeug.utils import redirect, secure_filename
import pandas as pd
from flask_socketio import SocketIO


from dataevent.DataQueue import data_queue
from model.models import query_user, User
from service.DataService import data_service
from tools.Utility import get_program_path

app = Flask(__name__)

app.secret_key = 'data_service'
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Access denied.'
login_manager.init_app(app)

socketio = SocketIO(app)

global thread, client_num, close
thread = None
thread_lock = Lock()
client_num = 0
close = True


@login_manager.user_loader
def load_user(user_id):
    if query_user(user_id) is not None:
        curr_user = User()
        curr_user.id = user_id
        return curr_user

@app.route('/')
@login_required
def root_dir():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user')
        user = query_user(user_id)
        if user is not None and request.form['password'] == user['password']:
            curr_user = User()
            curr_user.id = user_id
            login_user(curr_user)
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/index')
@login_required
def index():
    return render_template('base.html')


@app.route('/max_loan')
@login_required
def max_loan():
    return render_template('max_loan.html')


@app.route('/funding_rate')
@login_required
def funding_rate():
    return render_template('funding_rate.html')


@app.route('/contract_info')
@login_required
def contract_info():
    return render_template('contract_info.html')


@app.route('/kline')
@login_required
def kline():
    return render_template('kline.html')


@app.route('/contract_open_interest')
@login_required
def contract_open_interest():
    return render_template('contract_open_interest.html')


@app.route('/account_monitor')
@login_required
def account_monitor():
    return render_template('account_monitor.html')


@app.route('/account_detail/<account_id>')
@login_required
def account_detail(account_id):
    return render_template('account_detail.html', account_id=account_id)


@app.route('/get_gateio_market_max_loan')
@login_required
def get_gateio_market_max_loan():
    market_max_loan = data_service.get_gateio_market_max_loan()
    return jsonify({"value": market_max_loan})


@app.route('/get_gateio_max_loan')
@login_required
def get_gateio_max_loan():
    account_name = request.args['account']
    max_loan = data_service.get_gateio_max_loan(account_name)
    return jsonify({"value": max_loan})


@app.route('/get_okx_max_loan')
@login_required
def get_okx_max_loan():
    account_name = request.args['account']
    main_contract_list = data_service.get_okx_max_loan(account_name)
    return jsonify({"value": main_contract_list})


@app.route('/get_binance_funding_rate')
@login_required
def get_binance_funding_rate():
    start_date = request.args['start']
    end_date = request.args['end']
    funding_rate_data = data_service.get_binance_funding_rate(start_date, end_date)
    return jsonify({"value": funding_rate_data})


@app.route('/get_gateio_funding_rate')
@login_required
def get_gateio_funding_rate():
    start_date = request.args['start']
    end_date = request.args['end']
    funding_rate_data = data_service.get_gateio_funding_rate(start_date, end_date)
    return jsonify({"value": funding_rate_data})


@app.route('/get_bybit_funding_rate')
@login_required
def get_bybit_funding_rate():
    start_date = request.args['start']
    end_date = request.args['end']
    funding_rate_data = data_service.get_bybit_funding_rate(start_date, end_date)
    return jsonify({"value": funding_rate_data})


@app.route('/get_okx_funding_rate')
@login_required
def get_okx_funding_rate():
    start_date = request.args['start']
    end_date = request.args['end']
    funding_rate_data = data_service.get_okx_funding_rate(start_date, end_date)
    return jsonify({"value": funding_rate_data})


@app.route('/get_binance_contract_info')
@login_required
def get_binance_contract_info():
    contract_info = data_service.get_binance_contract_info()
    return jsonify({"value": contract_info})


@app.route('/get_gateio_contract_info')
@login_required
def get_gateio_contract_info():
    contract_info = data_service.get_gateio_contract_info()
    return jsonify({"value": contract_info})


@app.route('/get_bybit_contract_info')
@login_required
def get_bybit_contract_info():
    contract_info = data_service.get_bybit_contract_info()
    return jsonify({"value": contract_info})


@app.route('/get_okx_contract_info')
@login_required
def get_okx_contract_info():
    contract_info = data_service.get_okx_contract_info()
    return jsonify({"value": contract_info})


@app.route('/get_binance_contract_open_interest')
@login_required
def get_binance_contract_open_interest():
    start_date = request.args['start']
    end_date = request.args['end']
    open_interest_data = data_service.get_binance_contract_open_interest(start_date, end_date)
    return jsonify({"value": open_interest_data})


@app.route('/get_gateio_contract_open_interest')
@login_required
def get_gateio_contract_open_interest():
    start_date = request.args['start']
    end_date = request.args['end']
    open_interest_data = data_service.get_gateio_contract_open_interest(start_date, end_date)
    return jsonify({"value": open_interest_data})


@app.route('/get_bybit_contract_open_interest')
@login_required
def get_bybit_contract_open_interest():
    start_date = request.args['start']
    end_date = request.args['end']
    open_interest_data = data_service.get_bybit_contract_open_interest(start_date, end_date)
    return jsonify({"value": open_interest_data})


@app.route('/get_binance_kline')
@login_required
def get_binance_kline():
    start_date = request.args['start']
    end_date = request.args['end']
    kline_data = data_service.get_binance_kline(start_date, end_date)
    return jsonify({"value": kline_data})


@app.route('/get_gateio_kline')
@login_required
def get_gateio_kline():
    start_date = request.args['start']
    end_date = request.args['end']
    kline_data = data_service.get_gateio_kline(start_date, end_date)
    return jsonify({"value": kline_data})


@app.route('/get_bybit_kline')
@login_required
def get_bybit_kline():
    start_date = request.args['start']
    end_date = request.args['end']
    kline_data = data_service.get_bybit_kline(start_date, end_date)
    return jsonify({"value": kline_data})


@socketio.on('connect', namespace='/account_info')
def connect():
    global thread, close
    with thread_lock:
        if thread is None:
            close = False
            thread = socketio.start_background_task(target=background_thread)


def background_thread():
    while not close:
        view_data = data_queue.get_view_data()
        if view_data:
            socketio.emit('account_info_view', {'text': view_data}, namespace='/account_info')

        detail_data = data_queue.get_detail_data()
        if detail_data:
            socketio.emit('account_info_detail', {'text': detail_data}, namespace='/account_info')
            
        socketio.sleep(10)


@socketio.on('disconnect', namespace="/account_info")
def disconnect():
    pass


if __name__ == '__main__':
    # app.run(port=8000)
    # app.run(host='0.0.0.0', port=8020, debug=False)
    socketio.run(app, host='0.0.0.0', port=8020)
    # server = pywsgi.WSGIServer(('0.0.0.0', 8000), app)
    # server.serve_forever()
