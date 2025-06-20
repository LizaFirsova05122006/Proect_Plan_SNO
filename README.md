<h1 align="center">Автоматизация мониторинга активности участников СНО Вуза</h1>
<br>
<nav>
  <h2>Содержание</h2>
  <ol>
    <li><a href="#id1">Использованные технологии</a></li>
    <ul type="disc">
      <li><a href="#id1.1">Backend</a></li>
      <ul type="circle">
        <li><a href=#id1.1.1">Python</a></li>
        <li><a href="#id1.1.2">Flask</a></li>
        <li><a href="#id1.1.3">SQLAlchemy</a></li>
        <li><a href="#id1.1.4">Модели данных</a></li>
        <li><a href="#id1.1.5">Bcrypt</a></li>
        <li><a href="#id1.1.6">SMTP (smtplib, email.mime)</a></li>
        <li><a href="#id1.1.7">WebDav (webdav3.client)</a></li>
        <li><a href="#id1.1.8">OS</a></li>
      </ul>
      <li><a href="#id1.2">Frontend</a></li>
      <ul type="circle">
        <li><a href="#id1.2.1">HTML, CSS, Java Script</a></li>
        <li><a href="#id1.2.2">Jinja2</a></li>
      </ul>
      <li><a href="#id1.3">База данных</a></li>
      <ul type="circle">
        <li><a href="#id1.3.1">SQLite</a></li>
      </ul>
    </ul>
    <li><a href="#id2">Рекомендации по запуску кода</a></li>
  </ol>
</nav>
<br><br>
<h2 id="id1">Использованные технологии</h2>
<ol type="1">
  <h3 id="id1.1"><li>Backend</li></h3>
  <ul type="disc">
    <h3 id="id1.1.1"><li>Python - основной язык программирования для серверной части</li></h3>
    <h3 id="id1.1.2"><li>Flask - микрофреймворк для создания веб-приложений</li></h3>
    <h3 id="id1.1.3"><li>SQLAlchemy - ORM для взаимодействия с БД</li></h3>
    <h3 id="id1.1.4"><li>Модели данных:</li></h3>
    <ul type="circle">
      <h4><li>Article, Authorization, Award, Champioship, Contest, Event, Faq, Forgot, Olimped, People, Profile, Project, Requests, Roles, Scholarship</li></h4>
    </ul>
    <h3 id="id1.1.5"><li>Bcrypt - алгоритм на Python для хэширования паролей</li></h3>
    <h3 id="id1.1.6"><li>SMTP (smtplib, email.mime) - отправка элекронных писем</li></h3>
    <h3 id="id1.1.7"><li>WebDav (webdav3.client) - взаимодействие с облочным хранилищем</li></h3>
    <h3 id="id1.1.8"><li>OS - бибилиотека, используется для работы с файловой системой, доступа к переменным окружения</li></h3>
  </ul>
  <h3 id="id1.2"><li>Fortend</li></h3>
  <ul type="disc">
    <h3 id="id1.2.1"><li>HTML, CSS, Java Script - базовая вёрстка</li></h3>
    <h3 id="id1.2.2"><li>Jinja2 - встроенный в Flask движок рендеринга HTML</li></h3>
  </ul>
  <h3 id="id1.3"><li>База данных</li></h3>
  <ul type="disc">
    <h3 id="id1.3.1"><li>SQLite - встроенная реляционная база данных, которая не требует отдельного сервера. Подходит для проекта с запросами около ~300 тыс. штук в день</li>
  </ul>
</ol>
<br><br>
<h2 id="id2">Рекомендации по запуску кода</h2>
<ol type="1">
  <h3><li>Убедитесь, что у Вас установлен Git. Проверить можно, выполнив программу:</li></h3>
  <pre><code>git --version</code></pre>
  <h3>Если Git не установлен, скачайте и установите его с официального сайта</h3>
  <h3><li>Откройте терминал или командную строку</li></h3>
  <h3><li>Перейдите в папку, куда Вы хотите клонировать репозиторий, с помощью комманды cd:</li></h3>
  <pre><code>cd путь/к/Вашей/папке</code></pre>
  <h3><li>Используйте следующую команду, чтобы клонировать репозиторий:</li></h3>
  <pre><code>git clone https://github.com/LizaFirsova05122006/Proect_Plan_SNO.git</code></pre>
  <h3><li>Создайте аккаунт в Яндекс Почта. В приложении Необходимо создать пароль приложений для почты. Чтобы все работало в настройках необходимо поставить галочки:</li></h3>
  <a href='https://postimages.org/' target='_blank'><img src='https://i.postimg.cc/TPkcN47Q/2024-07-10-17-31-28.png' border='0' alt='2024-07-10-17-31-28'/></a>
  <h3><li>В файле config.py для переменной LOGIN вместо EMAIL вставьте адрес электронной почты</li></h3>
  <h3><li>В файле config.py для переменной PASSWORD вместо PASSWORD вставьте полученный пароль приложений</li></h3>
  <h3><li>Создайте пароль приложений для файлов</li></h3>
  <h3><li>В файле config.py для переменной PASSWORD_YANDEX вместо PASSWORD вставьте полученный пароль приложений</li></h3>
  <h3><li>В файле config.py для переменной ADMIN вместо EMAIL2 вставьте адрес электронной почты, который принадлежит админу</li></h3>
  <h3><li>Установите зависимости:</li></h3>
  <pre><code>pip install -r requirements.txt</code></pre>
  <h3><li>Откройте IDE с интерпретатором Python и запустите main.py</li></h3>
  <h3><li>Или в командной строке (в папке, куда был склонирован репозиторий) введите команду:</li></h3>
  <pre><code>python main.py</code></pre>
</ol>
