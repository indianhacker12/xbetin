from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory

from werkzeug.security import generate_password_hash, check_password_hash
import razorpay
from datetime import datetime
import random



app = Flask(__name__)


# User model



# OddEvenGameResult model to store bets and results for the Odd/Even game
# class OddEvenGameResult(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     prediction = db.Column(db.String(50), nullable=False)
#     result = db.Column(db.String(50), nullable=False)
#     bet_amount = db.Column(db.Float, nullable=False)
#     win = db.Column(db.Boolean, nullable=False)
#     timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
#     user = db.relationship('User', backref='odd_even_game_results')

# class ColorGameResult(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     prediction = db.Column(db.String(50), nullable=False)
#     result = db.Column(db.String(50), nullable=False)
#     bet_amount = db.Column(db.Float, nullable=False)
#     win = db.Column(db.Boolean, nullable=False)
#     timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
#     user = db.relationship('User', backref='ColorGameResult')

# Home route
@app.route('/')
def main():
    return redirect(url_for('home'))

# Login route

# Signup route



# Wallet route


# Privacy, Terms, and About routes
@app.route('/home')
def home():
    return render_template('home.html')
@app.route('/privacy')
def privacy_policy():
    return render_template('privacy.html')

@app.route('/security')
def security():
    return render_template('security.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Contact route
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        flash('Your message has been sent!', 'success')
    return render_template('contact.html')



if __name__ == '__main__':
    app.run(debug=True)
