from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory

from werkzeug.security import generate_password_hash, check_password_hash
import razorpay
from datetime import datetime
import random



app = Flask(__name__)




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

#coin root
@app.route('/coin')
def coin():
    return render_template("coin.html", user=session.get('username', None))
@app.route('/keno')
def keno():
    return render_template("keno.html", user=session.get('username', None))
@app.route('/odd_even')
def odd_even():
    return render_template("odd-even.html", user=session.get('username', None))

@app.route('/color-game')
def color():
    return render_template("color.html", user=session.get('username', None))
@app.route('/color-prediction')
def color_prediction():
    return render_template("color_game.html", user=session.get('username', None))

@app.route('/plinko')
def plinko():
    return render_template("plinko.html", user=session.get('username', None))



if __name__ == '__main__':
    app.run(debug=True)
