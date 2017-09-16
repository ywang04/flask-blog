What is Yuora?
===

Yuora is created with Python Flask Framework from scratch. Front end uses HTML, CSS, Bootstrap and jQuery. The purpose of it is to store information we are interested in and share interesting things with other people. 
Please feel free to contact Yuora Admin via email yang.wang04@gmail.com if you have any issues. Any feedback is welcome.

Yuora Deployment Guide
===

Since this process can be difficult, as there are a number of moving pieces, we'll look at this in multiple parts, starting with the most basic configuration and working our way up:

#### Part 1: Setting up the basic configuration

#### Part 2: nginx configuration

#### Part 3: Insert data into MySQL database

#### Part 4: Start your project

---
We'll specifically be using:

1. Ubuntu 14.04.5 x64 (DigitalOcean)
2. nginx 1.4.6
3. gunicorn 19.6.0
4. Python 2.7.6
5. pip 1.5.4
6. virtualenv 1.11.4
7. Flask 0.10.1

Assuming you already have a VPS running an Ubuntu operating system, we'll use nginx as our web server. Since a web server cannot communicate directly with Flask (Python), we’ll use gunicorn to act as a medium between the server and Python/Flask.

Think if gunicorn as the application web server that will be running behind nginx – the front facing web server. gunicorn is WSGI compatible. It can talk to other applications that support WSGI, like Flask or Django.

The end goal: HTTP requests are routed from the web server to Flask, which Flask handles appropriately, and the responses are then sent right back to the web server and finally back to the end user. Properly implementing a Web Server Gateway Interface (WSGI) will be paramount to our success.


#### Part 1 – Setup
Let’s get the basic configuration setup.


##### Add a new User
SSH to the server as the ‘root’ user, run-

```  
$ useradd newuser -m -s /bin/bash
$ passwd newuser
$ adduser newuser sudo
$ su - newuser
```
-to create a new user with 'sudo' privileges.


##### Install the Requirements
SSH into the server with the new user, and then install the following packages:

```
$ sudo apt-get update
$ sudo apt-get install -y python python-pip python-virtualenv python-dev nginx git
```

##### Set up the basic configuration
Start by creating a new directory, "/home/www", to store the project:

```
$ sudo mkdir /home/www && cd /home/
$ sudo chown -R newuser:newuser www 
$ cd www
```

##### Download source code from your github:

```
$ git clone https://github.com/ywang04/flask-blog.git
```

Then create and activate a virtualenv:

```
$ sudo virtualenv env
$ source env/bin/activate
```

Install the requirements:
```
(venv) $ pip install -r requirements/common.txt 
(venv) $ pip install gunicorn
```

Configure MySQL:
```
(venv) $ sudo apt-get install mysql-server python-mysqldb libmysqlclient-dev 
(venv) $ pip install mysql-python
(venv) $ mysql -u root -p 
mysql> CREATE DATABASE data CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';
mysql> exit
```

Configure environment variables in ~/.bash_profile under newuser:
```
export MAIL_USERNAME="*****@gmail.com"
export MAIL_PASSWORD="*****"
export FLASK_ADMIN="*****@gmail.com"
export DATABASE_URL="mysql://root:*****@localhost/<your database name>"
export FLASK_CONFIG="production"
export SECRET_KEY="*****"
```

####Part 2 – Now set up nginx:

```
$ sudo /etc/init.d/nginx start
$ sudo rm /etc/nginx/sites-enabled/default
$ sudo touch /etc/nginx/sites-available/flask-blog
$ sudo ln -s /etc/nginx/sites-available/flask-blog /etc/nginx/sites-enabled/flask-blog
```

Edit nginx configuration file:

```
(venv) $ sudo vim /etc/nginx/sites-enabled/flask-blog
```

Add following into nginx configuration file:

```
server { 
    location / { 
        proxy_pass http://localhost:8000; 
        proxy_set_header Host $host; 
        proxy_set_header X-Real-IP $remote_addr; 
    }
    location /static { 
        alias /home/www/flask-blog/app/static/; 
    } 
}
```

location /static means the static path of your project, here I use /home/www/flask-blog/app/static/.

Restart nginx:

```
(venv) $ sudo /etc/init.d/nginx restart 
```

#### Part 3 - Insert data into your MySQL database:

```
(venv) $ python manage.py shell 
>>> db.create_all() 
>>> Role.insert_roles() 
>>> exit() 
```

#### Part4 - Start your project now:

```
(venv) $ cd /home/www/flask-blog/ 
(venv) $ gunicorn manage:app -b localhost:8000 (or)
(venv) $ gunicorn manage:app -b localhost:8000 &
```

The second way is to run command at the background. 

Finally, you can access your website using real name.
