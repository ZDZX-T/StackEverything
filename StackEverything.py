from flask import Flask, render_template, request, jsonify, send_from_directory
import SQL
import config
import os
import logging
from logging.handlers import TimedRotatingFileHandler

from static.py.operating_area import operating_area
from static.py.view_items import view_items
from static.py.manage_attributes import manage_attributes

__log_handler = None


def setup_logging():  # 自定义日志行为
    global __log_handler
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'app.log')
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    # 创建TimedRotatingFileHandler
    __log_handler = TimedRotatingFileHandler(log_file_path, when='D', interval=1, backupCount=config.LOG_RETENTION_TIME, encoding='utf-8')
    __log_handler.setLevel(logging.INFO)
    # 设置日志格式
    formatter = logging.Formatter(
        '%(message)s [in %(pathname)s:%(lineno)d]'
    )
    __log_handler.setFormatter(formatter)
    # 获取Flask的默认日志记录器并移除所有默认处理器
    # logger = logging.getLogger('werkzeug')
    # logger.handlers = []
    # 添加自定义处理器到根记录器
    root_logger = logging.getLogger()
    root_logger.addHandler(__log_handler)
    root_logger.setLevel(logging.INFO)
    # print(f'日志存放路径:{log_file_path}')
# 在创建Flask应用对象之前调用日志配置函数
setup_logging()


app = Flask(__name__)
app.register_blueprint(operating_area)
app.register_blueprint(view_items)
app.register_blueprint(manage_attributes)


# 日志记录POST请求报文，以及拦截非POST与GET请求
@app.before_request
def log_request_info():
    if request.method == "POST":
        # 捕获POST请求的内容
        # app.logger.info(f"Request URL: {request.url}")
        # app.logger.info(f"Request Method: {request.method}")
        # app.logger.info(f"Request Headers: {dict(request.headers)}")
        app.logger.info(f"↓below POST Body: {request.get_data(as_text=True)[:config.SINGLE_LOG_MAX_LEN]}")
    elif request.method != "GET":
        return jsonify({
            "error": "Method Not Allowed",
            "message": f"The method {request.method} is not allowed. Only GET and POST are supported."
        }), 405


@app.route('/')  # 主页
def main_page():
    return render_template('index.html')


@app.route('/config.py')  # 使得config.py在下层文件夹也可访问
def config_available():
    return send_from_directory('./', 'config.py')


@app.route('/i18n/<who_cares>')  # 加载语言包
def load_i18n(who_cares):
    return send_from_directory('./i18n/', f'{config.LANGUAGE}.json')


@app.route('/uploaded_pic/<filename>')  # 动态加载图片
def uploaded_pic(filename):
    return send_from_directory(config.PIC_PATH, filename)


@app.route('/doRollover')  # 手动触发日志轮转
def doRollover():
    __log_handler.doRollover()  # 同一天内反复调用，只会把未轮转的日志追加到已轮转的日志的后面去
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    __log_handler.doRollover()  # 每次启动都尝试轮转，防止有人仅在需要时运行
    app.run(host=config.SERVER_HOST, port=config.SERVER_PORT, debug=config.SERVER_DEBUG)
