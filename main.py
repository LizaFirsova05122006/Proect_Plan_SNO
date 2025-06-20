import os
import smtplib
import random
import bcrypt
from flask import Flask, render_template, request, url_for, redirect
from webdav3.client import Client
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config as cfg
from data import db_session
from data.authorization import Authorization
from data.people import People
from data.contest import Contest
from data.olimped import Olimped
from data.award import Award
from data.profile import Profile
from data.project import Project
from data.article import Article
from data.scholarship import Scholarship
from data.champioship import Champioship
from data.requests import Requests
from data.faq import FAQ
from data.forgot import Forgot

app = Flask(__name__)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
options = {
    'webdav_hostname': "https://webdav.yandex.ru",
    'webdav_login': cfg.LOGIN,
    'webdav_password': cfg.PASSWORD_YANDEX
}
client = Client(options)


@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "GET":
        return render_template("home.html")
    elif request.method == "POST":
        session = db_session.create_session()
        email, passw = request.form["email"], request.form["password"]
        user = session.query(People).filter(People.email == email).first()
        if user is None:
            error = "Такого пользователя не существует или пароль не установлен"
            return render_template("home.html", error=error)
        else:
            valid = bcrypt.checkpw(passw.encode(), user.password)
            if valid:
                return redirect(url_for("profile", email=email))
            else:
                error = "Неверный пароль"
                return render_template("home.html", error=error)


@app.route("/forgot", methods=["POST", "GET"])
def forgot():
    msg = MIMEMultipart()
    msg["From"] = cfg.LOGIN
    if request.method == "GET":
        return render_template("forgot.html")
    elif request.method == "POST":
        session = db_session.create_session()
        email = request.form["email"]
        user = session.query(People).filter(People.email == email).first()
        if user is None:
            error = "Пользователя с таким email не существует"
            return render_template("forgot.html", error=error)
        else:
            str1, str2 = "1234567890", "qwertyuiopasdfghjklzxcvbnm"
            str3 = str2.upper()
            str4 = list(str1 + str2 + str3)
            random.shuffle(str4)
            psw = "".join([random.choice(str4) for x in range(12)])
            code = bcrypt.hashpw(psw.encode(), bcrypt.gensalt())
            forgot_password = session.query(Forgot).filter(Forgot.email == email).first()
            if forgot_password is None:
                new_user = Forgot(
                    email=email,
                    code=code,
                    used=0
                )
                session.add(new_user)
                session.commit()
            else:
                forgot_password.code = code
                forgot_password.used = 0
                session.commit()
            msg["Subject"] = f"Восстановление пароля"
            msg_body = (f"Для восстановления пароля перейдите по ссылке: http://127.0.0.1:5000/recovery\n"
                        f"Ваш код для восстановления: {psw}\n\n\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, email, msg.as_string())
            return redirect(url_for("recovery"))


@app.route("/recovery", methods=["POST", "GET"])
def recovery():
    if request.method == "GET":
        return render_template("recovery.html")
    elif request.method == "POST":
        session = db_session.create_session()
        email, rcode, password = request.form["email"], request.form["recovery"], request.form["password"]
        user = session.query(Forgot).filter(Forgot.email == email).first()
        if user is None:
            error = "Пользователя с таким email не существует"
            return render_template("recovery.html", error=error)
        else:
            if user.code == 0:
                valid = bcrypt.checkpw(rcode.encode(), user.password)
                if valid:
                    user_p = session.query(People).filter(People.email == email).first()
                    user_p.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                    session.commit()
                    user.used = 1
                    session.commit()
                    return redirect(url_for("home"))
                else:
                    error = "Неверный код восстановления"
                    return render_template("recovery.html", error=error)
            else:
                error = "Код восстановления устарел. Запросите, пожалуйста, "
                return render_template("recovery.html", error=error)


@app.route("/submit_request", methods=["POST", "GET"])
def submit_request():
    msg = MIMEMultipart()
    msg["From"] = cfg.LOGIN
    if request.method == "GET":
        return render_template("submit_request.html")
    elif request.method == "POST":
        session = db_session.create_session()
        param = {}
        param["surname"], param["name"], param["s_name"], param["group"], param["email"] = request.form["surname"], \
            request.form["name"], request.form["s_name"], request.form["group"], request.form["email"]
        user_a = session.query(Authorization).filter(Authorization.email == param["email"]).first()
        if user_a is None:
            new_user = Authorization(
                surname=param["surname"],
                name=param["name"],
                s_name=param["s_name"],
                group=param["group"],
                email=param["email"]
            )
            session.add(new_user)
            session.commit()
            msg[
                "Subject"] = f"Новая заявка на вступление в СНО: {param["surname"]} {param["name"][0]}.{param["s_name"][0]}."
            msg_body = (f"Новая заявка на вступление в СНО кафедры О7\n"
                        f"ФИО: {param["surname"]} {param["name"]} {param["s_name"]}\n"
                        f"Группа: {param["group"]}\n"
                        f"Для подверждения перейдите на сайт: http://127.0.0.1:5000\n\n\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, cfg.ADMIN, msg.as_string())
        else:
            error = "Ваша заявка на рассмотрении"
            return render_template("submit_request.html", error=error)
        return render_template("submit_request.html")


@app.route("/confirm_request/<email>", methods=["POST", "GET"])
def confirm_request(email):
    msg = MIMEMultipart()
    msg["From"] = cfg.LOGIN
    session = db_session.create_session()
    if request.method == "GET":
        count = session.query(Authorization).count()
        auth = session.query(Authorization).all()
        return render_template("confirm_request.html", email=email, county=count, users=auth)
    elif request.method == "POST":
        user_id = request.form.get("item_index")
        if request.form.get("action") == "approve":
            return redirect(url_for("confirm_user_request", email=email, user_id=user_id))
        elif request.form.get("action") == "reject":
            user = session.query(Authorization).filter(Authorization.id == user_id).first()
            msg["Subject"] = f"Ваша заявка на вступление в СНО"
            msg_body = (f"Ваша заявка на вступление в СНО кафедры О7 отклонена\n"
                        f"Вы можете обратиться в чат поддержки для получения дополнительной информации и помощи.\n\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, user.email, msg.as_string())
            session.delete(user)
            session.commit()
            return redirect(url_for("confirm_request", email=email))


@app.route("/confirm_user_request/<email>/<user_id>", methods=["POST", "GET"])
def confirm_user_request(email, user_id):
    msg = MIMEMultipart()
    msg["From"] = cfg.LOGIN
    if request.method == "GET":
        session = db_session.create_session()
        auth = session.query(Authorization).filter(Authorization.id == str(user_id)).first()
        return render_template("confirm_user_request.html", user=auth)
    elif request.method == "POST":
        if request.form.get("action") == "approve":
            role_user = request.form.get("role")
            if len(role_user) == 0:
                error = "Выберите роль"
                session = db_session.create_session()
                auth = session.query(Authorization).filter(Authorization.id == str(user_id)).first()
                return render_template("confirm_user_request.html", user=auth, error=error)
            else:
                session = db_session.create_session()
                auth = session.query(Authorization).filter(Authorization.id == str(user_id)).first()
                new_person = People(
                    surname=auth.surname,
                    name=auth.name,
                    s_name=auth.s_name,
                    group=auth.group,
                    email=auth.email,
                    id_role=1 if role_user == "Администратор" else (2 if role_user == "Студент" else 3)
                )
                session.add(new_person)
                session.commit()
                client.mkdir(f"/{r[0][1]} {r[0][2]} {r[0][3]}")
                msg["Subject"] = f"Ваша заявка на вступление в СНО"
                msg_body = (f"Ваша заявка на вступление в СНО кафедры О7 одобрена\n"
                            f"Перейдите по ссылке для установления пароля и ввода даты рождения: http://127.0.0.1:5000/add_data_user\n\n"
                            f"--\n"
                            f"С уважением,\n"
                            f"Администрация Студенческого научного общества кафедры О7")
                msg.attach(MIMEText(msg_body, "plain"))
                server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
                server.login(cfg.LOGIN, cfg.PASSWORD)
                server.sendmail(cfg.LOGIN, auth.email, msg.as_string())
                session.delete(auth)
                session.commit()
                return redirect(url_for("confirm_request", email=email))
        elif request.form.get("action") == "back":
            return redirect(url_for("confirm_request"))


@app.route("/add_data_user", methods=["POST", "GET"])
def add_data_user():
    if request.method == "GET":
        return render_template("add_data_user.html")
    elif request.method == "POST":
        session = db_session.create_session()
        email, date, password = request.form["email"], request.form["date_bh"].split("-"), request.form["password"]
        date_bh = f"{date[2]}.{date[1]}.{date[0]}"
        passw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        user = session.query(People).filter(People.email == email).first()
        if user is None:
            error = "Пользователя с таким email не существует"
            return render_template("add_data_user.html", error=error)
        else:
            user.password = passw
            user.date_birth = date_bh
            user.email = email
            session.commit()
            return redirect(url_for("home"))


@app.route("/profile/<email>", methods=["POST", "GET"])
def profile(email):
    session = db_session.create_session()
    user = session.query(People).filter(People.email == str(email)).first()
    if user.id_role == 1 and request.method == "GET":
        photo = session.query(Profile).filter(Profile.email == str(email)).first()
        if photo is None:
            return render_template("profile_admin1.html", email=email, user=user)
        else:
            return render_template("profile_admin2.html", user=user, email=email, photo=photo.photo)
    elif user.id_role == 1 and request.method == "POST":
        filenames = []
        UPLOAD_FOLDER = f'static\\img\\profile\\{email}'
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
        files1 = request.files.getlist("file")
        for file in files1:
            filenames.append(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))
        pro_user = session.query(Profile).filter(Profile.email == str(email)).first()
        if pro_user is None:
            new_pro = Profile(
                email=email,
                photo="".join(filenames)
            )
            session.add(new_pro)
            session.commit()
        else:
            pro_user.photo = "".join(filenames)
            session.commit()
        return redirect(url_for("profile", email=email))


@app.route("/users/<email>", methods=["POST", "GET"])
def users(email):
    if request.method == "GET":
        session = db_session.create_session()
        user = session.query(People).order_by(People.surname, People.name, People.s_name).all()
        return render_template("users.html", user=user, email=email)
    elif request.method == "POST":
        user_id = request.form.get("item_index")
        if user_id:
            return redirect(url_for("users_change", email=email, id_user=user_id))
        return redirect(url_for("users", email=email))


@app.route("/users/change/<email>/<id_user>", methods=["POST", "GET"])
def users_change(email, id_user):
    if request.method == "GET":
        session = db_session.create_session()
        user = session.query(People).filter(People.id == str(id_user)).first()
        return render_template("users_change.html", email=email, user=user)
    elif request.method == "POST":
        session = db_session.create_session()
        user = session.query(People).filter(People.id == str(id_user)).first()
        if int(request.form["check"]):
            user.surname = request.form["surname"]
        if int(request.form["check2"]):
            user.name = request.form["name"]
        if int(request.form["check3"]):
            user.s_name = request.form["s_name"]
        if int(request.form["check4"]):
            user.group = request.form["group"]
        if int(request.form["check5"]):
            user.email = request.form["email"]
        if int(request.form["check6"]):
            rol = request.form["role"]
            user.id_role = 1 if rol == "Администратор" else (2 if rol == "Студент" else 3)
        if int(request.form["check7"]):
            d = request.form["date_bh"].split("-")
            user.date_birth = f"{d[2]}.{d[1]}.{d[0]}"
        session.commit()
        return redirect(url_for("users_change", email=email, id_user=id_user))


@app.route("/add/achievement/<email>", methods=["POST", "GET"])
def add_achievement(email):
    msg = MIMEMultipart()
    msg["From"] = cfg.LOGIN
    if request.method == "GET":
        return render_template("add_achievement.html", email=email)
    elif request.method == "POST":
        filenames = []
        session = db_session.create_session()
        user = session.query(People).filter(People.email == str(email)).first()
        event = request.form["event"]
        if event == "Мероприятие":
            name_event = request.form["name_event"]
            if not name_event:
                return render_template("add_achievement.html", email=email, error="Не введено название мероприятия")
            result = request.form["result"]
            if not result:
                return render_template("add_achievement.html", email=email, error="Не выбран результат")
            level = request.form["level"]
            if not level:
                return render_template("add_achievement.html", email=email, error="Не выбран уровень мероприятия")
            is_range = request.form.get("isRange")
            date = ""
            if is_range == "on":
                start_date = request.form["startDate"].split("-")
                end_date = request.form["endDate"].split("-")
                if start_date and end_date:
                    date += f"{start_date[2]}.{start_date[1]}.{start_date[0]}-{end_date[2]}.{end_date[1]}.{end_date[0]}"
                else:
                    return render_template("add_achievement.html", email=email, error="Не выбраны даты")
            if is_range != "on":
                s_date = request.form["singleDate"].split("-")
                if len("".join(s_date)) > 0:
                    date += f"{s_date[2]}.{s_date[1]}.{s_date[0]}"
                else:
                    return render_template("add_achievement.html", email=email, error="Не выбрана дата")
            f = request.files.get("file")
            if not(f and f.filename):
                return render_template("add_achievement.html", email=email, error="Не прикреплены подверждающие документы")
            UPLOAD_DIPLOMA = f"static\\files\\contest\\{email}\\{name_event}"
            os.makedirs(UPLOAD_DIPLOMA, exist_ok=True)
            app.config["UPLOAD_CONTEST"] = UPLOAD_DIPLOMA
            filenames.append(f.filename)
            f.save(os.path.join(UPLOAD_DIPLOMA, f.filename))
            show_notes = request.form.get("show_notes")
            notes = request.form["notes"] if show_notes else ""
            new_contest = Contest(
                id_person=user.id,
                name_event=name_event,
                result=result,
                level=level,
                date=date,
                diploma="".join(filenames),
                notes=notes,
                approved=0
            )
            session.add(new_contest)
            session.commit()
            msg["Subject"] = f"Пользователь {user.surname} {user.name[0]}.{user.s_name[0]}. добавил достижение"
            msg_body = (f"Пользователь {user.surname} {user.name} {user.s_name} добавил достижение:\n\n"
                        f"Тип: Мероприятие\n"
                        f"Название: {name_event}\n"
                        f"Результат: {result}\n"
                        f"Уровень мероприятия: {level}\n"
                        f"Дата: {date}\n"
                        f"Подверждающие документы: {''.join(filenames)}\n"
                        f"Примечания: {notes}\n\n"
                        f"Перейдите на сайт, чтобы подвердить достижение: http://127.0.0.1:5000\n\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            if os.path.exists(f"static/files/contest/{email}/{name_event}/{filenames[0]}"):
                with open(f"static/files/contest/{email}/{name_event}/{filenames[0]}", "rb") as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(filenames[0]))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filenames[0])}"'
                msg.attach(part)
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, cfg.ADMIN, msg.as_string())
            return redirect(url_for("add_achievement", email=email))
        if event == "Олимпиада":
            name_event = request.form["name_event"]
            if not name_event:
                return render_template("add_achievement.html", email=email, error="Не введено название олимпиады")
            result = request.form["result"]
            if not result:
                return render_template("add_achievement.html", email=email, error="Не выбран результат")
            level = request.form["level"]
            if not level:
                return render_template("add_achievement.html", email=email, error="Не выбран уровень олимпиады")
            is_range = request.form.get("isRange")
            date = ""
            if is_range == "on":
                start_date = request.form["startDate"].split("-")
                end_date = request.form["endDate"].split("-")
                if start_date and end_date:
                    date += f"{start_date[2]}.{start_date[1]}.{start_date[0]}-{end_date[2]}.{end_date[1]}.{end_date[0]}"
                else:
                    return render_template("add_achievement.html", email=email, error="Не выбраны даты")
            if is_range != "on":
                s_date = request.form["singleDate"].split("-")
                if len("".join(s_date)) > 0:
                    date += f"{s_date[2]}.{s_date[1]}.{s_date[0]}"
                else:
                    return render_template("add_achievement.html", email=email, error="Не выбрана дата")
            f = request.files.get("file")
            if not (f and f.filename):
                return render_template("add_achievement.html", email=email,
                                       error="Не прикреплены подверждающие документы")
            UPLOAD_OLIMPED = f"static\\files\\olimped\\{email}\\{name_event}"
            os.makedirs(UPLOAD_OLIMPED, exist_ok=True)
            app.config["UPLOAD_OLIMPED"] = UPLOAD_OLIMPED
            filenames.append(f.filename)
            f.save(os.path.join(UPLOAD_OLIMPED, f.filename))
            show_notes = request.form.get("show_notes")
            notes = request.form["notes"] if show_notes else ""
            new_olimped = Olimped(
                id_person=user.id,
                name_event=name_event,
                result=result,
                level=level,
                date=date,
                diploma="".join(filenames),
                notes=notes,
                approved=0
            )
            session.add(new_olimped)
            session.commit()
            msg["Subject"] = f"Пользователь {user.surname} {user.name[0]}.{user.s_name[0]}. добавил достижение"
            msg_body = (f"Пользователь {user.surname} {user.name} {user.s_name} добавил достижение:\n\n"
                        f"Тип: Олимпиада\n"
                        f"Название: {name_event}\n"
                        f"Результат: {result}\n"
                        f"Уровень олимпиады: {level}\n"
                        f"Дата: {date}\n"
                        f"Подверждающие документы: {''.join(filenames)}\n"
                        f"Примечания: {notes}\n\n"
                        f"Перейдите на сайт, чтобы подвердить достижение: http://127.0.0.1:5000\n\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            if os.path.exists(f"static/files/olimped/{email}/{name_event}/{filenames[0]}"):
                with open(f"static/files/olimped/{email}/{name_event}/{filenames[0]}", "rb") as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(filenames[0]))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filenames[0])}"'
                msg.attach(part)
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, cfg.ADMIN, msg.as_string())
            return redirect(url_for("add_achievement", email=email))
        if event == "Премия":
            name_event = request.form["name_event"]
            if not name_event:
                return render_template("add_achievement.html", email=email, error="Не введено название премии")
            result = request.form["result"]
            if not result:
                return render_template("add_achievement.html", email=email, error="Не выбран результат")
            is_range = request.form.get("isRange")
            date = ""
            if is_range == "on":
                start_date = request.form["startDate"].split("-")
                end_date = request.form["endDate"].split("-")
                if start_date and end_date:
                    date += f"{start_date[2]}.{start_date[1]}.{start_date[0]}-{end_date[2]}.{end_date[1]}.{end_date[0]}"
                else:
                    return render_template("add_achievement.html", email=email, error="Не выбраны даты")
            if is_range != "on":
                s_date = request.form["singleDate"].split("-")
                if len("".join(s_date)) > 0:
                    date += f"{s_date[2]}.{s_date[1]}.{s_date[0]}"
                else:
                    return render_template("add_achievement.html", email=email, error="Не выбрана дата")
            f = request.files.get("file")
            if not (f and f.filename):
                return render_template("add_achievement.html", email=email, error="Не прикреплены подверждающие документы")
            UPLOAD_AWARD = f"static\\files\\award\\{email}\\{name_event}"
            os.makedirs(UPLOAD_AWARD, exist_ok=True)
            app.config["UPLOAD_OLIMPED"] = UPLOAD_AWARD
            filenames.append(f.filename)
            f.save(os.path.join(UPLOAD_AWARD, f.filename))
            show_notes = request.form.get("show_notes")
            notes = request.form["notes"] if show_notes else ""
            new_award = Award(
                id_person=user.id,
                name_event=name_event,
                result=result,
                date=date,
                diploma="".join(filenames),
                notes=notes,
                approved=0
            )
            session.add(new_award)
            session.commit()
            msg["Subject"] = f"Пользователь {user.surname} {user.name[0]}.{user.s_name[0]}. добавил достижение"
            msg_body = (f"Пользователь {user.surname} {user.name} {user.s_name} добавил достижение:\n\n"
                        f"Тип: Премия\n"
                        f"Название: {name_event}\n"
                        f"Результат: {result}\n"
                        f"Дата: {date}\n"
                        f"Подверждающие документы: {''.join(filenames)}\n"
                        f"Примечания: {notes}\n\n"
                        f"Перейдите на сайт, чтобы подвердить достижение: http://127.0.0.1:5000\n\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            if os.path.exists(f"static/files/award/{email}/{name_event}/{filenames[0]}"):
                with open(f"static/files/award/{email}/{name_event}/{filenames[0]}", "rb") as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(filenames[0]))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filenames[0])}"'
                msg.attach(part)
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, cfg.ADMIN, msg.as_string())
            return redirect(url_for("add_achievement", email=email))
        if event == "Проект":
            name_event = request.form["name_event"]
            if not name_event:
                return render_template("add_achievement.html", email=email, error="Не введено название проекта")
            result = request.form["result"]
            if not result:
                return render_template("add_achievement.html", email=email, error="Не выбран результат")
            participation = request.form["participation"]
            if not participation:
                return render_template("add_achievement.html", email=email, error="Не выбран тип участия")
            f = request.files.get("file")
            if not (f and f.filename):
                return render_template("add_achievement.html", email=email,error="Не прикреплены подверждающие документы")
            UPLOAD_PROJECT = f"static\\files\\project\\{email}\\{name_event}"
            os.makedirs(UPLOAD_PROJECT, exist_ok=True)
            app.config["UPLOAD_PROJECT"] = UPLOAD_PROJECT
            filenames.append(f.filename)
            f.save(os.path.join(UPLOAD_PROJECT, f.filename))
            show_notes = request.form.get("show_notes")
            notes = request.form["notes"] if show_notes else ""
            new_project = Project(
                id_person=user.id,
                name_event=name_event,
                result=result,
                participation=participation,
                diploma="".join(filenames),
                notes=notes,
                approved=0
            )
            session.add(new_project)
            session.commit()
            msg["Subject"] = f"Пользователь {user.surname} {user.name[0]}.{user.s_name[0]}. добавил достижение"
            msg_body = (f"Пользователь {user.surname} {user.name} {user.s_name} добавил достижение:\n\n"
                        f"Тип: Проект\n"
                        f"Название: {name_event}\n"
                        f"Результат: {result}\n"
                        f"Тип участия: {participation}\n"
                        f"Подверждающие документы: {''.join(filenames)}\n"
                        f"Примечания: {notes}\n\n"
                        f"Перейдите на сайт, чтобы подвердить достижение: http://127.0.0.1:5000\n\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            if os.path.exists(f"static/files/project/{email}/{name_event}/{filenames[0]}"):
                with open(f"static/files/project/{email}/{name_event}/{filenames[0]}", "rb") as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(filenames[0]))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filenames[0])}"'
                msg.attach(part)
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, cfg.ADMIN, msg.as_string())
            return redirect(url_for("add_achievement", email=email))
        if event == "Статья":
            name_event = request.form["name_event"]
            if not name_event:
                return render_template("add_achievement.html", email=email, error="Не введено название статьи")
            co_authors = request.form["co-authors"]
            if len(co_authors) == 0:
                co_authors = ""
            f = request.files.get("file")
            if not (f and f.filename):
                return render_template("add_achievement.html", email=email,
                                       error="Не прикреплены подверждающие документы")
            UPLOAD_ARTICLE = f"static\\files\\article\\{email}\\{name_event}"
            os.makedirs(UPLOAD_ARTICLE, exist_ok=True)
            app.config["UPLOAD_ARTICLE"] = UPLOAD_ARTICLE
            filenames.append(f.filename)
            f.save(os.path.join(UPLOAD_ARTICLE, f.filename))
            show_notes = request.form.get("show_notes")
            notes = request.form["notes"] if show_notes else ""
            new_article = Article(
                id_person=user.id,
                name_event=name_event,
                co_authors=co_authors,
                diploma="".join(filenames),
                notes=notes,
                approved=0
            )
            session.add(new_article)
            session.commit()
            msg["Subject"] = f"Пользователь {user.surname} {user.name[0]}.{user.s_name[0]}. добавил достижение"
            msg_body = (f"Пользователь {user.surname} {user.name} {user.s_name} добавил достижение:\n\n"
                        f"Тип: Статья\n"
                        f"Название: {name_event}\n"
                        f"Соавторы: {co_authors}\n"
                        f"Подверждающие документы: {''.join(filenames)}\n"
                        f"Примечания: {notes}\n\n"
                        f"Перейдите на сайт, чтобы подвердить достижение: http://127.0.0.1:5000\n\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            if os.path.exists(f"static/files/article/{email}/{name_event}/{filenames[0]}"):
                with open(f"static/files/article/{email}/{name_event}/{filenames[0]}", "rb") as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(filenames[0]))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filenames[0])}"'
                msg.attach(part)
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, cfg.ADMIN, msg.as_string())
            return redirect(url_for("add_achievement", email=email))
        if event == "Стипендия":
            name_event = request.form["name_event"]
            if not name_event:
                return render_template("add_achievement.html", email=email, error="Не введено название стипендии")
            is_range = request.form.get("isRange")
            date = ""
            if is_range == "on":
                start_date = request.form["startDate"].split("-")
                end_date = request.form["endDate"].split("-")
                if start_date and end_date:
                    date += f"{start_date[2]}.{start_date[1]}.{start_date[0]}-{end_date[2]}.{end_date[1]}.{end_date[0]}"
                else:
                    return render_template("add_achievement.html", email=email, error="Не выбраны даты")
            if is_range != "on":
                s_date = request.form["singleDate"].split("-")
                if len("".join(s_date)) > 0:
                    date += f"{s_date[2]}.{s_date[1]}.{s_date[0]}"
                else:
                    return render_template("add_achievement.html", email=email, error="Не выбрана дата")
            f = request.files.get("file")
            if not (f and f.filename):
                return render_template("add_achievement.html", email=email,
                                       error="Не прикреплены подверждающие документы")
            UPLOAD_SCHOLARSHIP = f"static\\files\\scholarship\\{email}\\{name_event}"
            os.makedirs(UPLOAD_SCHOLARSHIP, exist_ok=True)
            app.config["UPLOAD_PROJECT"] = UPLOAD_SCHOLARSHIP
            filenames.append(f.filename)
            f.save(os.path.join(UPLOAD_SCHOLARSHIP, f.filename))
            show_notes = request.form.get("show_notes")
            notes = request.form["notes"] if show_notes else ""
            new_scholarship = Scholarship(
                id_person=user.id,
                name_event=name_event,
                date=date,
                diploma="".join(filenames),
                notes=notes,
                approved=0
            )
            session.add(new_scholarship)
            session.commit()
            msg["Subject"] = f"Пользователь {user.surname} {user.name[0]}.{user.s_name[0]}. добавил достижение"
            msg_body = (f"Пользователь {user.surname} {user.name} {user.s_name} добавил достижение:\n\n"
                        f"Тип: Стипендия\n"
                        f"Название: {name_event}\n"
                        f"Дата: {date}\n"
                        f"Подверждающие документы: {''.join(filenames)}\n"
                        f"Примечания: {notes}\n\n"
                        f"Перейдите на сайт, чтобы подвердить достижение: http://127.0.0.1:5000\n\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            if os.path.exists(f"static/files/scholarship/{email}/{name_event}/{filenames[0]}"):
                with open(f"static/files/scholarship/{email}/{name_event}/{filenames[0]}", "rb") as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(filenames[0]))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filenames[0])}"'
                msg.attach(part)
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, cfg.ADMIN, msg.as_string())
            return redirect(url_for("add_achievement", email=email))
        if event == "Чемпионат":
            name_event = request.form["name_event"]
            if not name_event:
                return render_template("add_achievement.html", email=email, error="Не введено название чемпионата")
            result = request.form["result"]
            if not result:
                return render_template("add_achievement.html", email=email, error="Не выбран результат")
            level = request.form["level"]
            if not level:
                return render_template("add_achievement.html", email=email, error="Не выбран уровень чемпионата")
            is_range = request.form.get("isRange")
            date = ""
            if is_range == "on":
                start_date = request.form["startDate"].split("-")
                end_date = request.form["endDate"].split("-")
                if start_date and end_date:
                    date += f"{start_date[2]}.{start_date[1]}.{start_date[0]}-{end_date[2]}.{end_date[1]}.{end_date[0]}"
                else:
                    return render_template("add_achievement.html", email=email, error="Не выбраны даты")
            if is_range != "on":
                s_date = request.form["singleDate"].split("-")
                if len("".join(s_date)) > 0:
                    date += f"{s_date[2]}.{s_date[1]}.{s_date[0]}"
                else:
                    return render_template("add_achievement.html", email=email, error="Не выбрана дата")
            f = request.files.get("file")
            if not (f and f.filename):
                return render_template("add_achievement.html", email=email,
                                       error="Не прикреплены подверждающие документы")
            UPLOAD_CHAMPIOSHIP = f"static\\files\\champioship\\{email}\\{name_event}"
            os.makedirs(UPLOAD_CHAMPIOSHIP, exist_ok=True)
            app.config["UPLOAD_OLIMPED"] = UPLOAD_CHAMPIOSHIP
            filenames.append(f.filename)
            f.save(os.path.join(UPLOAD_CHAMPIOSHIP, f.filename))
            show_notes = request.form.get("show_notes")
            notes = request.form["notes"] if show_notes else ""
            new_champioship = Champioship(
                id_person=user.id,
                name_event=name_event,
                result=result,
                level=level,
                date=date,
                diploma="".join(filenames),
                notes=notes,
                approved=0
            )
            session.add(new_champioship)
            session.commit()
            msg["Subject"] = f"Пользователь {user.surname} {user.name[0]}.{user.s_name[0]}. добавил достижение"
            msg_body = (f"Пользователь {user.surname} {user.name} {user.s_name} добавил достижение:\n\n"
                        f"Тип: Чемпионат\n"
                        f"Название: {name_event}\n"
                        f"Результат: {result}\n"
                        f"Уровень чемпионата: {level}\n"
                        f"Дата: {date}\n"
                        f"Подверждающие документы: {''.join(filenames)}\n"
                        f"Примечания: {notes}\n\n"
                        f"Перейдите на сайт, чтобы подвердить достижение: http://127.0.0.1:5000\n\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            if os.path.exists(f"static/files/champioship/{email}/{name_event}/{filenames[0]}"):
                with open(f"static/files/champioship/{email}/{name_event}/{filenames[0]}", "rb") as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(filenames[0]))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filenames[0])}"'
                msg.attach(part)
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, cfg.ADMIN, msg.as_string())
            return redirect(url_for("add_achievement", email=email))
    return render_template("add_achievement.html", email=email)


@app.route("/view/achievement/<email>", methods=["GET", "POST"])
def view_achievement(email):
    msg = MIMEMultipart()
    msg["From"] = cfg.LOGIN
    if request.method == "GET":
        session = db_session.create_session()
        contest = session.query(Contest).all()
        return render_template("view_achievement.html", email=email, contest=contest)
    elif request.method == "POST":
        user_id = request.form.get("item_index")
        session = db_session.create_session()
        contest_user = session.query(Contest).filter(Contest.id == str(user_id)).first()
        if request.form.get("action") == "confirm":
            contest_user.approved = 1
            session.commit()
            msg["Subject"] = f"Администратор подтвердил Ваше достижение"
            msg_body = (f"Администратор подвердил Ваше достижение:\n\n"
                        f"Тип: Мероприятие\n"
                        f"Название: {contest_user.name_event}\n"
                        f"Результат: {contest_user.result}\n"
                        f"Уровень: {contest_user.level}\n"
                        f"Дата: {contest_user.date}\n\n"
                        f"Вы можете его посмотреть в своем личном кабинете: http://127.0.0.1:5000\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, contest_user.people.email, msg.as_string())
            base_path = f"{contest_user.people.surname} {contest_user.people.name} {contest_user.people.s_name}/Мероприятия"
            event_path = f"{base_path}/{contest_user.name_event}"
            local_file_path = f"static/files/contest/{contest_user.people.email}/{contest_user.name_event}/{contest_user.diploma}"
            remote_file_path = f"{event_path}/{contest_user.diploma}"
            if not client.check(base_path):
                client.mkdir(base_path)
            if not client.check(event_path):
                client.mkdir(event_path)
            try:
                if os.path.exists(local_file_path):
                    client.upload_sync(remote_path=remote_file_path, local_path=local_file_path)
            except Exception as e:
                os.remove(local_file_path)
                return redirect(url_for("view_achievement", email=email))
            os.remove(local_file_path)
            return redirect(url_for("view_achievement", email=email))
        if request.form.get("action") == "reject":
            comment = request.form.get("reject_comment")
            msg["Subject"] = f"Администратор отклонил Ваше достижение"
            msg_body = (f"Администратор отклонил Ваше достижение с комментарием:\n\n"
                        f"Здравствуйте, {contest_user.people.name} {contest_user.people.s_name}!\n"
                        f"Ваше достижение: Мероприятие {contest_user.name_event} отклонено по причине: {comment}.\n"
                        f"Вы можете обратиться в чат поддержки для получения дополнительной информации и помощи.\n\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, contest_user.people.email, msg.as_string())
            session.delete(contest_user)
            session.commit()
            local_file_path = f"static/files/olimped/{contest_user.people.email}/{contest_user.name_event}/{contest_user.diploma}"
            os.remove(local_file_path)
            return redirect(url_for("view_achievement", email=email))


@app.route("/view/olimpied/<email>", methods=["POST", "GET"])
def view_olimped(email):
    msg = MIMEMultipart()
    msg["From"] = cfg.LOGIN
    if request.method == "GET":
        session = db_session.create_session()
        contest = session.query(Olimped).all()
        return render_template("view_olimped.html", email=email, contest=contest)
    elif request.method == "POST":
        print("Y")
        user_id = request.form.get("item_index")
        print(user_id)
        session = db_session.create_session()
        olimped_user = session.query(Olimped).filter(Olimped.id == str(user_id)).first()
        action = request.form.get('action')
        if action == "confirm":
            print("f")
            olimped_user.approved = 1
            session.commit()
            msg["Subject"] = f"Администратор подтвердил Ваше достижение"
            msg_body = (f"Администратор подвердил Ваше достижение:\n\n"
                        f"Тип: Олимпиада\n"
                        f"Название: {olimped_user.name_event}\n"
                        f"Результат: {olimped_user.result}\n"
                        f"Уровень: {olimped_user.level}\n"
                        f"Дата: {olimped_user.date}\n\n"
                        f"Вы можете его посмотреть в своем личном кабинете: http://127.0.0.1:5000\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, olimped_user.people.email, msg.as_string())
            base_path = f"{olimped_user.people.surname} {olimped_user.people.name} {olimped_user.people.s_name}/Олимпиады"
            event_path = f"{base_path}/{olimped_user.name_event}"
            local_file_path = f"static/files/olimped/{olimped_user.people.email}/{olimped_user.name_event}/{olimped_user.diploma}"
            remote_file_path = f"{event_path}/{olimped_user.diploma}"
            if not client.check(base_path):
                client.mkdir(base_path)
            if not client.check(event_path):
                client.mkdir(event_path)
            try:
                if os.path.exists(local_file_path):
                    client.upload_sync(remote_path=remote_file_path, local_path=local_file_path)
            except Exception as e:
                os.remove(local_file_path)
                return redirect(url_for("view_olimped", email=email))
            os.remove(local_file_path)
            return redirect(url_for("view_olimped", email=email))
        if action == "reject":
            comment = request.form.get("reject_comment")
            msg["Subject"] = f"Администратор отклонил Ваше достижение"
            msg_body = (f"Администратор отклонил Ваше достижение с комментарием:\n\n"
                        f"Здравствуйте, {olimped_user.people.name} {olimped_user.people.s_name}!\n"
                        f"Ваше достижение: Олимпиада {olimped_user.name_event} отклонено по причине: {comment}.\n"
                        f"Вы можете обратиться в чат поддержки для получения дополнительной информации и помощи.\n\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, olimped_user.people.email, msg.as_string())
            session.delete(olimped_user)
            session.commit()
            local_file_path = f"static/files/olimped/{olimped_user.people.email}/{olimped_user.name_event}/{olimped_user.diploma}"
            os.remove(local_file_path)
            return redirect(url_for("view_olimped", email=email))


@app.route("/view/award/<email>", methods=["GET", "POST"])
def view_award(email):
    msg = MIMEMultipart()
    msg["From"] = cfg.LOGIN
    if request.method == "GET":
        session = db_session.create_session()
        award = session.query(Award).all()
        return render_template("view_award.html", email=email, award=award)
    elif request.method == "POST":
        user_id = request.form.get("item_index")
        session = db_session.create_session()
        award_user = session.query(Award).filter(Award.id == str(user_id)).first()
        if request.form.get("action") == "confirm":
            award_user.approved = 1
            session.commit()
            msg["Subject"] = f"Администратор подвердил Ваше достижение"
            msg_body = (f"Администратор подтвердил Ваше достижение:\n\n"
                        f"Тип: Премия\n"
                        f"Название: {award_user.name_event}\n"
                        f"Результат: {award_user.result}\n"
                        f"Дата: {award_user.date}\n\n"
                        f"Вы можете его посмотреть в своем личном кабинете: http://127.0.0.1:5000\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, award_user.people.email, msg.as_string())
            base_path = f"{award_user.people.surname} {award_user.people.name} {award_user.people.s_name}/Премии"
            event_path = f"{base_path}/{award_user.name_event}"
            local_file_path = f"static/files/award/{award_user.people.email}/{award_user.name_event}/{award_user.diploma}"
            remote_file_path = f"{event_path}/{award_user.diploma}"
            if not client.check(base_path):
                client.mkdir(base_path)
            if not client.check(event_path):
                client.mkdir(event_path)
            try:
                if os.path.exists(local_file_path):
                    client.upload_sync(remote_path=remote_file_path, local_path=local_file_path)
            except Exception as e:
                os.remove(local_file_path)
                return redirect(url_for("view_award", email=email))
            os.remove(local_file_path)
            return redirect(url_for("view_award", email=email))
        if request.form.get("action") == "reject":
            comment = request.form.get("reject_comment")
            msg["Subject"] = f"Администратор отклонил Ваше достижение"
            msg_body = (f"Администратор отклонил Ваше достижение с комментарием:\n\n"
                        f"Здравствуйте, {award_user.people.name} {award_user.people.s_name}!\n"
                        f"Ваше достижение: Премия {award_user.name_event} отклонено по причине: {comment}.\n"
                        f"Вы можете обратиться в чат поддержки для получения дополнительной информации и помощи.\n\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, award_user.people.email, msg.as_string())
            session.delete(award_user)
            session.commit()
            local_file_path = f"static/files/award/{award_user.people.email}/{award_user.name_event}/{award_user.diploma}"
            os.remove(local_file_path)
            return redirect(url_for("view_award", email=email))


@app.route("/view/project/<email>", methods=["POST", "GET"])
def view_project(email):
    msg = MIMEMultipart()
    msg["From"] = cfg.LOGIN
    if request.method == "GET":
        session = db_session.create_session()
        project = session.query(Project).all()
        return render_template("view_project.html", email=email, project=project)
    elif request.method == "POST":
        user_id = request.form.get("item_index")
        session = db_session.create_session()
        project_user = session.query(Project).filter(Project.id == str(user_id)).first()
        if request.form.get("action") == "confirm":
            project_user.approved = 1
            session.commit()
            msg["Subject"] = f"Администратор подтвердил Ваше достижение"
            msg_body = (f"Администратор подвердил Ваше достижение:\n\n"
                        f"Тип: Проект\n"
                        f"Название: {project_user.name_event}\n"
                        f"Результат: {project_user.result}\n"
                        f"Тип участия: {project_user.participation}\n\n"
                        f"Вы можете его посмотреть в своем личном кабинете: http://127.0.0.1:5000\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, project_user.people.email, msg.as_string())
            base_path = f"{project_user.people.surname} {project_user.people.name} {project_user.people.s_name}/Проекты"
            event_path = f"{base_path}/{project_user.name_event}"
            local_file_path = f"static/files/project/{project_user.people.email}/{project_user.name_event}/{project_user.diploma}"
            remote_file_path = f"{event_path}/{project_user.diploma}"
            if not client.check(base_path):
                client.mkdir(base_path)
            if not client.check(event_path):
                client.mkdir(event_path)
            try:
                if os.path.exists(local_file_path):
                    client.upload_sync(remote_path=remote_file_path, local_path=local_file_path)
            except Exception as e:
                os.remove(local_file_path)
                return redirect(url_for("view_project", email=email))
            os.remove(local_file_path)
            return redirect(url_for("view_project", email=email))
        if request.form.get("action") == "reject":
            comment = request.form.get("reject_comment")
            msg["Subject"] = f"Администратор отклонил Ваше достижение"
            msg_body = (f"Администратор отклонил Ваше достижение с комментарием:\n\n"
                        f"Здравствуйте, {project_user.people.name} {project_user.people.s_name}!\n"
                        f"Ваше достижение: Проект {project_user.name_event} отклонено по причине: {comment}.\n"
                        f"Вы можете обратиться в чат поддержки для получения дополнительной информации и помощи.\n\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, project_user.people.email, msg.as_string())
            session.delete(project_user)
            session.commit()
            local_file_path = f"static/files/project/{project_user.people.email}/{project_user.name_event}/{project_user.diploma}"
            os.remove(local_file_path)
            return redirect(url_for("view_project", email=email))


@app.route("/view/article/<email>", methods=["POST", "GET"])
def view_article(email):
    msg = MIMEMultipart()
    msg["From"] = cfg.LOGIN
    if request.method == "GET":
        session = db_session.create_session()
        article = session.query(Article).all()
        return render_template("view_article.html", email=email, article=article)
    elif request.method == "POST":
        user_id = request.form.get("item_index")
        session = db_session.create_session()
        article_user = session.query(Article).filter(Article.id == str(user_id)).first()
        if request.form.get("action") == "confirm":
            article_user.approved = 1
            session.commit()
            msg["Subject"] = f"Администратор подтвердил Ваше достижение"
            msg_body = (f"Администратор подвердил Ваше достижение:\n\n"
                        f"Тип: Статья\n"
                        f"Название: {article_user.name_event}\n"
                        f"Соавторы: {article_user.co_authors}\n"
                        f"Вы можете его посмотреть в своем личном кабинете: http://127.0.0.1:5000\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, article_user.people.email, msg.as_string())
            base_path = f"{article_user.people.surname} {article_user.people.name} {article_user.people.s_name}/Статьи"
            event_path = f"{base_path}/{article_user.name_event}"
            local_file_path = f"static/files/article/{article_user.people.email}/{article_user.name_event}/{article_user.diploma}"
            remote_file_path = f"{event_path}/{article_user.diploma}"
            if not client.check(base_path):
                client.mkdir(base_path)
            if not client.check(event_path):
                client.mkdir(event_path)
            try:
                if os.path.exists(local_file_path):
                    client.upload_sync(remote_path=remote_file_path, local_path=local_file_path)
            except Exception as e:
                os.remove(local_file_path)
                return redirect(url_for("view_article", email=email))
            os.remove(local_file_path)
            return redirect(url_for("view_article", email=email))
        if request.form.get("action") == "reject":
            comment = request.form.get("reject_comment")
            msg["Subject"] = f"Администратор отклонил Ваше достижение"
            msg_body = (f"Администратор отклонил Ваше достижение с комментарием:\n\n"
                        f"Здравствуйте, {article_user.people.name} {article_user.people.s_name}!\n"
                        f"Ваше достижение: Статья {article_user.name_event} отклонено по причине: {comment}.\n"
                        f"Вы можете обратиться в чат поддержки для получения дополнительной информации и помощи.\n\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, article_user.people.email, msg.as_string())
            session.delete(article_user)
            session.commit()
            local_file_path = f"static/files/article/{article_user.people.email}/{article_user.name_event}/{article_user.diploma}"
            os.remove(local_file_path)
            return redirect(url_for("view_article", email=email))


@app.route("/view/scholarship/<email>", methods=["POST", "GET"])
def view_scholarship(email):
    msg = MIMEMultipart()
    msg["From"] = cfg.LOGIN
    if request.method == "GET":
        session = db_session.create_session()
        scholarship = session.query(Scholarship).all()
        return render_template("view_scholarship.html", email=email, scholarship=scholarship)
    elif request.method == "POST":
        user_id = request.form.get("item_index")
        session = db_session.create_session()
        s_user = session.query(Scholarship).filter(Scholarship.id == str(user_id)).first()
        if request.form.get("action") == "confirm":
            s_user.approved = 1
            session.commit()
            msg["Subject"] = f"Администратор подвердил Ваше достижение"
            msg_body = (f"Администратор подтвердил Ваше достижение:\n\n"
                        f"Тип: Стипендия\n"
                        f"Название: {s_user.name_event}\n"
                        f"Дата: {s_user.date}\n\n"
                        f"Вы можете его посмотреть в своем личном кабинете: http://127.0.0.1:5000\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, s_user.people.email, msg.as_string())
            base_path = f"{s_user.people.surname} {s_user.people.name} {s_user.people.s_name}/Стипендии"
            event_path = f"{base_path}/{s_user.name_event}"
            local_file_path = f"static/files/scholarship/{s_user.people.email}/{s_user.name_event}/{s_user.diploma}"
            remote_file_path = f"{event_path}/{s_user.diploma}"
            if not client.check(base_path):
                client.mkdir(base_path)
            if not client.check(event_path):
                client.mkdir(event_path)
            try:
                if os.path.exists(local_file_path):
                    client.upload_sync(remote_path=remote_file_path, local_path=local_file_path)
            except Exception as e:
                os.remove(local_file_path)
                return redirect(url_for("view_scholarship", email=email))
            os.remove(local_file_path)
            return redirect(url_for("view_scholarship", email=email))
        if request.form.get("action") == "reject":
            comment = request.form.get("reject_comment")
            msg["Subject"] = f"Администратор отклонил Ваше достижение"
            msg_body = (f"Администратор отклонил Ваше достижение с комментарием:\n\n"
                        f"Здравствуйте, {s_user.people.name} {s_user.people.s_name}!\n"
                        f"Ваше достижение: Стипендия {s_user.name_event} отклонено по причине: {comment}.\n"
                        f"Вы можете обратиться в чат поддержки для получения дополнительной информации и помощи.\n\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, s_user.people.email, msg.as_string())
            session.delete(s_user)
            session.commit()
            local_file_path = f"static/files/scholarship/{s_user.people.email}/{s_user.name_event}/{s_user.diploma}"
            os.remove(local_file_path)
            return redirect(url_for("view_award", email=email))


@app.route("/view/championship/<email>", methods=["POST", "GET"])
def view_championship(email):
    msg = MIMEMultipart()
    msg["From"] = cfg.LOGIN
    if request.method == "GET":
        session = db_session.create_session()
        champ = session.query(Champioship).all()
        return render_template("view_championship.html", email=email, champ=champ)
    elif request.method == "POST":
        user_id = request.form.get("item_index")
        session = db_session.create_session()
        c_user = session.query(Champioship).filter(Champioship.id == str(user_id)).first()
        if request.form.get("action") == "confirm":
            c_user.approved = 1
            session.commit()
            msg["Subject"] = f"Администратор подтвердил Ваше достижение"
            msg_body = (f"Администратор подвердил Ваше достижение:\n\n"
                        f"Тип: Чемпионат\n"
                        f"Название: {c_user.name_event}\n"
                        f"Результат: {c_user.result}\n"
                        f"Уровень: {c_user.level}\n"
                        f"Дата: {c_user.date}\n\n"
                        f"Вы можете его посмотреть в своем личном кабинете: http://127.0.0.1:5000\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, c_user.people.email, msg.as_string())
            base_path = f"{c_user.people.surname} {c_user.people.name} {c_user.people.s_name}/Чемпионаты"
            event_path = f"{base_path}/{c_user.name_event}"
            local_file_path = f"static/files/champioship/{c_user.people.email}/{c_user.name_event}/{c_user.diploma}"
            remote_file_path = f"{event_path}/{c_user.diploma}"
            if not client.check(base_path):
                client.mkdir(base_path)
            if not client.check(event_path):
                client.mkdir(event_path)
            try:
                if os.path.exists(local_file_path):
                    client.upload_sync(remote_path=remote_file_path, local_path=local_file_path)
            except Exception as e:
                os.remove(local_file_path)
                return redirect(url_for("view_championship", email=email))
            os.remove(local_file_path)
            return redirect(url_for("view_championship", email=email))
        if request.form.get("action") == "reject":
            comment = request.form.get("reject_comment")
            msg["Subject"] = f"Администратор отклонил Ваше достижение"
            msg_body = (f"Администратор отклонил Ваше достижение с комментарием:\n\n"
                        f"Здравствуйте, {c_user.people.name} {c_user.people.s_name}!\n"
                        f"Ваше достижение: Чемпионат {c_user.name_event} отклонено по причине: {comment}.\n"
                        f"Вы можете обратиться в чат поддержки для получения дополнительной информации и помощи.\n\n"
                        f"--\n"
                        f"С уважением,\n"
                        f"Администрация Студенческого научного общества кафедры О7")
            msg.attach(MIMEText(msg_body, "plain"))
            server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
            server.login(cfg.LOGIN, cfg.PASSWORD)
            server.sendmail(cfg.LOGIN, c_user.people.email, msg.as_string())
            session.delete(c_user)
            session.commit()
            local_file_path = f"static/files/champioship/{c_user.people.email}/{c_user.name_event}/{c_user.diploma}"
            os.remove(local_file_path)
            return redirect(url_for("view_championship", email=email))


@app.route("/chat/help", methods=["POST", "GET"])
def chat_help():
    msg = MIMEMultipart()
    msg["From"] = cfg.LOGIN
    if request.method == "GET":
        return render_template("chat_help.html")
    elif request.method == "POST":
        session = db_session.create_session()
        email = request.form["email"]
        if not email:
            return render_template("chat_help.html", error="Не введен адрес электронной почты")
        name = request.form["name"]
        if not name:
            return render_template("chat_help.html", error="Не введено имя")
        message = request.form["message"]
        if not message:
            return render_template("chat_help.html", error="Не введено обращение")
        user = session.query(Requests).filter(Requests.email == str(email)).first()
        if not(user is None):
            return render_template("chat_help.html", error="Дождитесь ответа на предыдущее обращение")
        new_user = Requests(
            email=email,
            name=name,
            message=message
        )
        session.add(new_user)
        session.commit()
        msg["Subject"] = f"Новое обращение от пользователя {name}"
        msg_body = (f"В службу поддержки поступило новое обращение\n\n"
                    f"дрес электронной почты: {email}\n"
                    f"Имя: {name}\n"
                    f"Обращение: {message}\n\n"
                    f"Перейдите на сайт, чтобы ответить: http:/127.0.0.1:5000\n"
                    f"--\n"
                    f"С уважением,\n"
                    f"Администрация Студенческого научного общества кафедры О7")
        msg.attach(MIMEText(msg_body, "plain"))
        server = smtplib.SMTP_SSL("smtp.yandex.com: 465")
        server.login(cfg.LOGIN, cfg.PASSWORD)
        server.sendmail(cfg.LOGIN, cfg.ADMIN, msg.as_string())
        return redirect(url_for("chat_help"))


@app.route("/chat/help/user/<email>", methods=["POST", "GET"])
def chat_help_user(email):
    session = db_session.create_session()
    user = session.query(People).filter(People.email == str(email)).first()
    if user.id == 1 and request.method == "GET":
        faq = session.query(FAQ).order_by(FAQ.question).all()
        return render_template("chat_help_user.html", email=email, faq=faq, user=user.id)
    elif user.id == 1 and request.method == "POST":
        pass


@app.route("/chat/help/user/add/<email>", methods=["POST", "GET"])
def chat_help_user_add(email):
    session = db_session.create_session()
    if request.method == "GET":
        return render_template("chat_help_user_add.html", email=email)
    elif request.method == "POST":
        question = request.form["question"]
        if not question:
            return render_template("chat_help_user_add.html", email=email, error="Не введен вопрос")
        answer = request.form["answer"]
        if not answer:
            return render_template("chat_help_user_add.html", email=email, error="Не введен ответ")
        new_question = FAQ(
            question=question,
            answer=answer
        )
        session.add(new_question)
        session.commit()
        return redirect(url_for("chat_help_user", email=email))


@app.route("/chat/help/user/edit/<email>", methods=["POST", "GET"])
def chat_help_user_requests(email):
    session = db_session.create_session()
    if request.method == "GET":
        faq = session.query(FAQ).order_by(FAQ.question).all()
        return render_template("chat_help_user_requests.html", email=email, faq=faq)
    elif request.method == "POST":
        action = request.form.get("action")
        if action.startswith("delete_"):
            q_id = action.split("_")[1]
            ques = session.query(FAQ).filter(FAQ.id == str(q_id)).first()
            session.delete(ques)
            session.commit()
            return redirect(url_for("chat_help_user_requests", email=email))
        elif action.startswith("save_"):
            q_id = action.split("_")[1]
            ques = session.query(FAQ).filter(FAQ.id == str(q_id)).first()
            c1 = request.form.get(f"check_{q_id}")
            c2 = request.form.get(f"check2_{q_id}")
            if c1 == "1":
                ques.question = request.form.get(f"question_{q_id}")
            if c2 == "1":
                ques.answer = request.form.get(f"answer_{q_id}")
            session.commit()
            return redirect(url_for("chat_help_user_requests", email=email))


if __name__ == "__main__":
    db_session.global_init("db/planner.db")
    app.run()
