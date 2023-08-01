# 🐦 Warbler

Welcome to Warbler - a Twitter-inspired social media app built with love and Python. 🐍❤️🐦

## 📑 Overview

Warbler is a Flask-based web application that lets users sign up, log in, follow other users, post messages, and like messages. It's a playground for Pythonistas, database buffs, and social media enthusiasts! 😃

## 🌟 Features

### 🕵️‍♀️ User Authentication
Users can sign up and log in. User data is securely stored using hashed passwords.

### 🥳 Social Interactions
Users can follow/unfollow other users, much like on Twitter. See what your friends are posting and keep up to date with their activity.

### 💌 Posting Messages
Feeling chatty? Post messages to share your thoughts with the world. Messages are displayed on user profiles and on the home page.

### 💖 Liking Messages
See a post you love? Show your appreciation by liking it! You can also view all the posts you've liked on your profile page.

### 🔑 Account Management
Users can update their profiles, change their passwords, and even delete their accounts.

## 💻 Tech Stack
- Backend: Python with Flask
- ORM: SQLAlchemy
- Database: PostgreSQL
- Frontend: HTML, CSS, Bootstrap

## 🚀 Getting Started
To get Warbler up and running, you'll need Python, pip, PostgreSQL, and a virtual environment (like venv or conda), and a Google Locations API key. Follow these steps:

1. Clone the repo: git clone https://github.com/yourusername/warbler.git
2. Change to the app directory: cd warbler
3. Create and activate a virtual environment
4. Install requirements: pip install -r requirements.txt
5. Create a secrets.py file in the root of the project. This will be used to store your Google Locations API key: touch secret.py
6. Open the secret.py file and add your Google Locations API key: GOOGLE_API_KEY = 'your_api_key_here'
Make sure to replace your_api_key_here with your actual API key.
1. Create a database: createdb warbler
2. Run the app: flask run
3. Now, navigate to localhost:5000 in your browser to see Warbler in action!

Don't forget to add secret.py to your .gitignore file to prevent it from being committed to your Git repository. This way, each user can have their own secret.py file locally, but it won't be included in the repository when you push changes to GitHub.




.
