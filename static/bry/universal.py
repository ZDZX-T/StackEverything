from browser import document, window, html, timer, ajax # type: ignore
from i18n import i18n
import sys
import json
sys.path.insert(0, '../../')
# sys.path.append('../../')
import config  # ../../config

# 告警
alert_num = 0
success_num = 0


def my_alert(msg, show=3000):
    global alert_num
    alert_num += 1
    alert_id = f'alert{alert_num}'

    new_div = html.DIV()
    new_div.attrs['id'] = alert_id
    new_div.attrs['role'] = 'alert'
    new_div.class_name = 'container-fluid fixed-top justify-content-md-center mt-4 fade show'
    new_div.style = {
        'z-index': 1100,
        'pointer-events': 'none'
    }
    document <= new_div

    document[alert_id].html = f"""
        <div class="row justify-content-center">
            <div class="col-4 col-xl-3 alert alert-danger alert-dismissible" role="alert" style="pointer-events: auto;">
                {msg}
                <button type="button"class="btn-close" id="btn_{alert_id}">
            </div>
        </div>
    """
    document[f'btn_{alert_id}'].bind('click', lambda ev: remove_alert(alert_id))
    timer.set_timeout(remove_alert, show, alert_id)


def remove_alert(alert_id):
    try:
        document[alert_id].classList.remove('show')
        timer.set_timeout(document[alert_id].remove, 500)
    except KeyError:
        pass


def my_success(msg, show=2000):
    global success_num
    success_num += 1
    success_id = f'success{success_num}'

    new_div = html.DIV()
    new_div.attrs['id'] = success_id
    new_div.attrs['role'] = 'alert'
    new_div.class_name = 'container-fluid fixed-top justify-content-md-center mt-4 fade show'
    new_div.style = {
        'z-index': 1100,
        'pointer-events': 'none'
    }
    document <= new_div

    document[success_id].html = f"""
        <div class="row justify-content-center">
            <div class="col-4 col-xl-3 alert alert-success alert-dismissible" role="alert" style="pointer-events: auto;">
                {msg}
                <button type="button"class="btn-close" id="btn_{success_id}">
            </div>
        </div>
    """
    document[f'btn_{success_id}'].bind('click', lambda ev: remove_success(success_id))
    timer.set_timeout(remove_success, show, success_id)


def remove_success(success_id):
    try:
        document[success_id].classList.remove('show')
        timer.set_timeout(document[success_id].remove, 500)
    except KeyError:
        pass


# 可交互性控制（其实没啥用）
def add_is_invalid(target):
    document[target].classList.add('is-invalid')


def remove_is_invalid(target):
    document[target].classList.remove('is-invalid') if 'is-invalid' in document[target].classList else None


def add_disabled(target):
    document[target].disabled = True


def remove_disabled(target):
    document[target].disabled = False


def disable_selection():
    # 禁用选择
    document.body.style.userSelect = "none"
    document.body.style.webkitUserSelect = "none"
    document.body.style.mozUserSelect = "none"
    document.body.style.msUserSelect = "none"


def enable_selection():
    # 启用选择
    document.body.style.userSelect = ""
    document.body.style.webkitUserSelect = ""
    document.body.style.mozUserSelect = ""
    document.body.style.msUserSelect = ""


# 同步执行
class Promise:
    def __init__(self, executor):
        self.on_resolve = None
        self.on_reject = None
        executor(self.resolve, self.reject)

    def resolve(self, value):
        if self.on_resolve:
            self.on_resolve(value)

    def reject(self, reason):
        if self.on_reject:
            self.on_reject(reason)

    def then(self, on_resolve):
        self.on_resolve = on_resolve
        return self

    def catch(self, on_reject):
        self.on_reject = on_reject
        return self


# i18n
def load_i18n():
    document.documentElement.lang = config.LANGUAGE
    missing_i18n_list = []
    for elem in document.select('[data-i18n]'):
        keys = elem.attrs['data-i18n']
        if keys == '':  # 有data-i18n没参数，可能在调试
            missing_i18n_list.append(keys)
            continue
        for key in keys.split(','):
            if key not in i18n:
                missing_i18n_list.append(key)
                continue
            if key[-1] == 'S':  # src
                elem.src = i18n[key]
            elif key[-1] == 'V':  # value
                elem.value = i18n[key]
            elif key[-1] == 'P':  # placeholder
                elem.placeholder = i18n[key]
            elif key[-1] == 'C':  # textContent
                elem.textContent = i18n[key]
            else:  # text
                elem.text = i18n[key]
    if len(missing_i18n_list):  # 提醒有data-i18n参数缺失
        my_alert(i18n['missing_i18n'] + str(missing_i18n_list))
load_i18n()