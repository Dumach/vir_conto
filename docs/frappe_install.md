## Table of Contents:

- **Step 1:** Server Setup
- **Step 2:** Install Required Packages
- **Step 3:** Configure MySQL Server
- **Step 4:** Install CURL, Node, NPM, Yarn
- **Step 5:** Install Frappe Bench
- **Step 6:** Install ERPNext and other Apps
- **Step 7:** Setup Production Server
- **Step 8:** Custom Domain & SSL Setup

This tutorial is made for installing the [[Frappe Framework]]

## 0. Pre-Requisites:

- Operating System: Linux Ubuntu 22.04 LTS
- Minimum Recommended Hardware: 2 CPU | 4 GB RAM | 20 GB Disk
- Root shell access to the server (via SSH)

## 1. Server Setup

---

### 1.1 Login to the server as root user

### 1.2 Setup correct date and timezone

Check the server’s current timezone

```bash
date
```

Set correct timezone as per your region

```bash
timedatectl set-timezone "Europe/Budapest"
```

### 1.3 Update & upgrade server packages

```bash
sudo apt-get update -y
sudo apt-get upgrade -y
```

### 1.4 Create a new user
We create this user as a security measure to prevent root user access.  
This user will be assigned admin permissions and will be used as the main Frappe Bench user

```bash
sudo adduser [frappe-user]
usermod -aG sudo [frappe-user]
su [frappe-user] 
cd /home/[frappe-user]/
```

Note: Replace [frappe-user] with your username. Eg. sudo adduser myname

For some cloud providers like AWS & Azure, you wont’t have root password access so you can simply run `sudo -i` when you login to the server using the default user (eg. ubuntu in AWS)

## 2. Install Required Packages

---

[[Frappe Bench]] and ERPNext requires many packages to run smoothly. In this step we will install all the required packages for the system to work correctly.

Note: During the installation of these packages the server might prompt you to confirm if you want to continue installing the package [Y/n]. Just hit “y” on your keyboard to continue.

### 2.1 Install GIT

```bash
sudo apt-get install git
```

Check if GIT is correctly installed by running `git --version`

### 2.2 Install Python

```bash
sudo apt-get install python3-dev python3.10-dev python3-setuptools python3-pip python3-distutils
```

### 2.3 Install Python Virtual Environment

```bash
sudo apt-get install python3.10-venv
```

Check if Python is correctly installed by running `python3 -V`

### 2.4 Install Software Properties Common

```bash
sudo apt-get install software-properties-common
```

### 2.5 Install MariaDB (MySQL server)

```bash
sudo apt install mariadb-server mariadb-client
```

Check if MariaDB is correctly installed by running `mariadb --version`

### 2.6 Install Redis Server

```bash
sudo apt-get install redis-server
```

### 2.7 Install other necessary packages (for fonts, PDFs, etc)

```bash
sudo apt-get install xvfb libfontconfig wkhtmltopdf
sudo apt-get install libmysqlclient-dev
```

## 3. Configure MySQL Server

---

### 3.1 Setup the server

```bash
sudo mysql_secure_installation
```

During the setup process, the server will prompt you with a few questions as given below. Follow the instructions to continue the setup;

- Enter current password for root: (Enter your SSH root user password)
- Switch to unix_socket authentication [Y/n]: Y
- Change the root password? [Y/n]: Y  
    It will ask you to set new MySQL root password at this step. This can be different from the SSH root user password.
- Remove anonymous users? [Y/n]: Y
- Disallow root login remotely? [Y/n]: N  
    This is set as N because we might want to access the database from a remote server for using business analytics software like Metabase / PowerBI / Tableau, etc.
- Remove test database and access to it? [Y/n]: Y
- Reload privilege tables now? [Y/n]: Y

### 3.2 Edit the MySQL default config file

```bash
sudo vim /etc/mysql/my.cnf
```

Add the below code block at the bottom of the file;

```ini
[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

[mysql]
default-character-set = utf8mb4
```

If you don’t know how to use VIM:

- Once the file is open, hit “i” key to start editing the file.
- After you’re done editing the file hit “Esc + :wq” to save the file

### 3.3 Restart the MySQL server (for the config to take effect)

```bash
sudo service mysql restart
```

## Instal CURL, Node, NPM and Yarn

---

### 4.1 Install CURL

```bash
sudo apt install curl
```

### 4.2 Install Node

```bash
curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash

source ~/.profile

nvm install 18
```

### 4.3 Install NPM

```bash
sudo apt-get install npm
```

### 4.4 Install Yarn

```bash
sudo npm install -g yarn
```

Check if Node is correctly installed by running `node --version`

## 5. Install Frappe Bench

---

### 5.1 Install Frappe Bench

```bash
sudo pip3 install frappe-bench
```

Check if Frappe Bench is correctly installed by running `bench --version`

### 5.2 Initialize Frappe Bench

```bash
bench init --frappe-branch version-15 frappe-bench
```

### 5.3 Go to Frappe Bench directory  
This will be the main directory from where we will be running all the commands.  
The full path of this directory will be: /home/[frappe-user]/frappe-bench/

```bash
cd frappe-bench/
```

### 5.4 Change user directory permissions  
This will allow execution permission to the home directory of the frappe user we created in step [[#1.4 Create a new user]]

```bash
chmod -R o+rx /home/[frappe-user]/
```

### 5.5 Create a New Site  
We will use this as the default site where ERPNext and other apps will be installed.

```bash
bench new-site site1.local
```

## 6. Install ERPNext and other Apps

---

Finally, we’re at the last stage of the installation process!

### 6.1 Download the necessary apps to our server  
Download the payments apps . This app is required during ERPNext installation

```bash
bench get-app payments
```

Download the main ERPNext app

```bash
bench get-app --branch version-15 erpnext
```

Download the HR & Payroll app (optional)

```bash
bench get-app hrms
```

Check if all the apps are correctly downloaded by running `bench version --format table`

### 6.2 Install all the Apps

Install the main ERPNext app

```bash
bench --site site1.local install-app erpnext
```

Install the HR & Payroll app (optional)

```bash
bench --site site1.local install-app hrms
```

Note: You might get some warnings / error messages while trying to install apps on the default site. These messages can be ignored and you can proceed further.

## 7. Setup Production Server

---

### 7.1 Enable scheduler service

```bash
bench --site site1.local enable-scheduler
```

### 7.2 Disable maintenance mode

```bash
bench --site site1.local set-maintenance-mode off
```

### 7.3 Setup production config

```bash
sudo bench setup production [frappe-user]
```

### 7.4 Setup NGINX web server

```bash
bench setup nginx
```

### 7.5 Setup Supervisord

Add *frappe* group to `/etc/supervisor/supervisord.conf`

```bash
; supervisor config file

[unix_http_server]
file=/var/run/supervisor.sock   ; (the path to the socket file)
chmod=0700                       ; sockef file mode (default 0700)

[group:frappe]
```

> If you forget adding it. You might get this error when restarting Frappe with `bench restart`:
```bash
"frappe: ERROR (no such group)"
```

### 7.6 Final server setup

```bash
sudo supervisorctl restart all
sudo bench setup production [frappe-user]
```

When prompted to save new/existing config files, hit “Y”

## 8. Ready to Go! 🎊

You can now go to your server **[IP-address]:80** and you will have a fresh new installation of ERPNext ready to be configured!

If you are facing any issues with the ports, make sure to enable all the necessary ports on your firewall using the below commands;

```bash
sudo ufw allow 22,25,143,80,443,3306,3022,8000/tcp
sudo ufw enable
```

## 9. Custom Domain & SSL Setup

For SSL configuration, you can run the following commands;

Before you begin, add an A record on your domain DNS and point it to the ERPNext server IP address.

```bash
cd /home/[frappe-user]/frappe-bench/

bench config dns_multitenant on

bench setup add-domain [subdomain.yourdomain.com] --site [site-name]

bench setup nginx 
sudo service nginx reload

sudo apt install certbot

sudo ln -s /snap/bin/certbot /usr/bin/certbot

sudo certbot --nginx
```

On terminal prompt, follow the instructions and select the correct site number and trying access your site on https:// from the custom domain you just added.

## 10. Troubleshoot
---
### 10.1 If pkg-config error during `bench init`

This happened with me during installation on Fedora 41:

```bash 
sudo apt-get install pkg-config python3-dev default-libmysqlclient-dev build-essential
```

### 10.2 Migrate Python Environment to newer version

Install specific Python version:

```bash
sudo apt install python3.12 python3.12-dev python3.12-distutils
```

Migrate Virtual Environment to desired Python Version:

```bash
bench migrate-env python3.12
```

Will migrate the virtual environment to the desired python version 

### 10.3 Redis cache server not running or Empty page

Only in Production:

If your Frappe site is running but you see an **empty page, showing "The site is under maintenance, it is probably not your problem"** or something like that. It probably yours.

Check if all your supervisor processes are running by trying:

```bash
sudo supervisorctl status
```

Output should look like this:

```bash
frappe-bench-redis:frappe-bench-redis-cache RUNNING    pid 6391, uptime 0:02:21
frappe-bench-redis:frappe-bench-redis-queue RUNNING    pid 6380, uptime 0:02:21
frappe-bench-redis:frappe-bench-redis-socketio RUNNING    pid 6395, uptime 0:02:21
frappe-bench-web:frappe-bench-frappe-web RUNNING    pid 6350, uptime 0:02:22
frappe-bench-web:frappe-bench-node-socketio RUNNING    pid 6420, uptime 0:02:20
frappe-bench-workers:frappe-bench-frappe-default-worker-0 RUNNING    pid 8828, uptime 0:00:01
frappe-bench-workers:frappe-bench-frappe-long-worker-0 STARTING
frappe-bench-workers:frappe-bench-frappe-schedule RUNNING    pid 8465, uptime 0:00:22
frappe-bench-workers:frappe-bench-frappe-short-worker-0 STARTING
```

If not, go to your supervisor config in `/etc/supervisord/conf.d` and check if the symlink with your `frappe-bench/config/supervisor.conf` is pointing to the correct location

---

You now have a fully production ready setup of Frappe & ERPNext on your server!

Thanks,  

Original Author: @Shashank

Extra: @Dumach
