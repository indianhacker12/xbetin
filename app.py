from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import razorpay
from datetime import datetime, timedelta
import random
from razorpay_config import RAZORPAY_API_KEY, RAZORPAY_API_SECRET
import time
import math
from random import choice, shuffle
import itertools
import uuid
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from sqlalchemy import func

# Secret key
razorpay_client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET))
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://u483781610_yaswantpandey:Iamluciferhackerfrommankapur7398731184@mysql-79828-0.cloudclusters.net:3306/u483781610_xbetin'  # MySQL database connection
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Helper function to generate game ID
def generateGameId():
    return str(int(time.time())) + str(random.randint(1000, 9999))

# Global variable to store game state
game_state = {
    'current_round_id': generateGameId(),
    'round_end_time': time.time() + 30,  # 30 seconds from now
    'results': None,
    'last_update': time.time()
}

def get_remaining_time():
    """Get remaining time in current round"""
    current_time = time.time()
    remaining = max(0, game_state['round_end_time'] - current_time)
    
    # If time has elapsed, update the game state
    if remaining <= 0:
        check_and_update_round()
        remaining = max(0, game_state['round_end_time'] - current_time)
    
    return round(remaining, 1)  # Return with 1 decimal place for smoother updates

def generate_color_game_result(bet_type):
    """Generate a result for the color game based on bet type"""
    if bet_type == "Color":
        # Color probabilities: Red (45%), Green (45%), Violet (10%)
        colors = ["Red", "Green", "Violet"]
        weights = [0.45, 0.45, 0.1]
        winning_color = random.choices(colors, weights=weights, k=1)[0]
        
        # Win probability based on color
        if winning_color == "Violet":
            win_prob = 0.1  # Lower win chance for high multiplier
        else:
            win_prob = 0.4  # Normal win chance for Red/Green
            
        result = "win" if random.random() < win_prob else "lose"
        return result, winning_color
    
    elif bet_type == "Number":
        # Numbers 0-9 with equal probability
        winning_number = str(random.randint(0, 9))
        
        # 10% win probability for numbers (1/10 chance)
        result = "win" if random.random() < 0.1 else "lose"
        return result, winning_number
    
    elif bet_type == "BigSmall":
        # Big/Small with equal probability
        options = ["Big", "Small"]
        winning_option = random.choice(options)
        
        # 45% win probability for Big/Small
        result = "win" if random.random() < 0.45 else "lose"
        return result, winning_option
    
    # Default fallback
    return "lose", ""

def check_and_update_round():
    """Check if round has ended and update if needed"""
    global game_state
    current_time = time.time()
    
    # Only update if enough time has passed since last update
    if current_time - game_state['last_update'] >= 0.1:  # Update at most every 100ms
        if current_time >= game_state['round_end_time']:
            # Generate results for all three types
            _, color = generate_color_game_result("Color")
            _, number = generate_color_game_result("Number")
            _, bigSmall = generate_color_game_result("BigSmall")
            
            # Store results
            game_state['results'] = {
                'color': color,
                'number': number,
                'bigSmall': bigSmall
            }
            
            # Start new round
            game_state['current_round_id'] = generateGameId()
            game_state['round_end_time'] = current_time + 30  # 30 seconds for next round
            game_state['last_update'] = current_time

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    pass_hash = db.Column(db.String(200), nullable=False)  # Store hashed password
    wallet_balance = db.Column(db.Float, nullable=False, default=0.0)
    
    def get_id(self):
        return str(self.id)
    
    @property
    def wallet(self):
        return self.wallet_balance
    
    @wallet.setter
    def wallet(self, value):
        self.wallet_balance = value

# GameResult model for generic game results
class GameResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_name = db.Column(db.String(100), default='Dice Roll')
    result = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref='game_results')

class OddEvenGameResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    user_choice = db.Column(db.String(10), nullable=False)
    result = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref='odd_even_results')

class ColorGameResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    user_choice = db.Column(db.String(10), nullable=False)
    winning_color = db.Column(db.String(10), nullable=False)
    result = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref='color_game_results')

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

class GameHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_type = db.Column(db.String(50), nullable=False)
    result = db.Column(db.String(50), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    winnings = db.Column(db.Float, nullable=False)
    date_played = db.Column(db.DateTime, nullable=False)
    user = db.relationship('User', backref=db.backref('game_histories', lazy=True))

class RockPaperScissorsHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Integer, nullable=False)
    user_choice = db.Column(db.String(10), nullable=False)
    computer_choice = db.Column(db.String(10), nullable=False)
    result = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class OddEvenHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Integer, nullable=False)
    user_choice = db.Column(db.String(10), nullable=False)
    generated_number = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ColorPredictionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    user_choice = db.Column(db.String(10), nullable=False)
    winning_color = db.Column(db.String(10), nullable=False)
    result = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class KenoHistory(db.Model):
    __tablename__ = 'keno_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    bet_amount = db.Column(db.Numeric(10, 2), nullable=False)  # Add this line
    user_numbers = db.Column(db.JSON, nullable=False)
    generated_numbers = db.Column(db.JSON, nullable=False)
    matches = db.Column(db.Integer, nullable=False)
    winnings = db.Column(db.Numeric(10, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Add any other necessary fields


class PokerHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Integer, nullable=False)
    user_hand = db.Column(db.String(50), nullable=False)
    dealer_hand = db.Column(db.String(50), nullable=False)
    winner = db.Column(db.String(50), nullable=False)
    winnings = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class BetHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_type = db.Column(db.String(50), nullable=False)
    bet_value = db.Column(db.String(50), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    multiplier = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(20), nullable=True) 

class MineBettingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    grid_size = db.Column(db.Integer, nullable=False)  # e.g., 5x5
    mines_count = db.Column(db.Integer, nullable=False)  # Number of mines placed
    cells_revealed = db.Column(db.Integer, nullable=False)  # Number of cells revealed
    mine_positions = db.Column(db.JSON, nullable=False)  # Positions of mines
    revealed_positions = db.Column(db.JSON, nullable=False)  # Positions revealed by player
    multiplier_achieved = db.Column(db.Float, nullable=False)  # Final multiplier achieved
    result = db.Column(db.String(10), nullable=False)  # 'win' or 'lose'
    winnings = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='mine_betting_history')

class AviatorHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    multiplier = db.Column(db.Float, nullable=True)
    auto_cashout = db.Column(db.Float, nullable=True)
    winnings = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(10), nullable=False)  # 'win' or 'loss'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='aviator_history')

class DiceBettingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Integer, nullable=False)
    user_choice = db.Column(db.Integer, nullable=False)
    dice_roll = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class PlinkoHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_amount = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(10), nullable=False)  # 'low', 'medium', 'high'
    rows = db.Column(db.Integer, nullable=False)
    path = db.Column(db.String(100), nullable=False)  # Store the path as a string of L/R directions
    multiplier = db.Column(db.Float, nullable=False)
    winnings = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='plinko_history')

with app.app_context():
    db.create_all()


def get_winning_color():
    colors = ['red', 'green', 'blue']
    return random.choice(colors)

@app.route('/color-prediction', methods=['GET', 'POST'])
def color_prediction_game():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        bet_amount = float(request.form['bet_amount'])
        user_choice = request.form['color_choice']

        if bet_amount > user.wallet:
            flash("Insufficient Balance!", "danger")
            return redirect(url_for('color_prediction_game'))

        # Generate the winning color
        winning_color = get_winning_color()
        result = 'win' if user_choice == winning_color else 'lose'

        # Calculate winnings
        multiplier = 2  # 2x payout for correct color prediction
        winnings = bet_amount * multiplier if result == 'win' else 0
        
        # Update wallet balance
        if result == 'win':
            user.wallet += winnings - bet_amount
        else:
            user.wallet -= bet_amount

        # Save the game result to the database
        game = ColorPredictionHistory(
            user_id=user.id,
            bet_amount=bet_amount,
            user_choice=user_choice,
            winning_color=winning_color,
            result=result
        )
        db.session.add(game)
        db.session.commit()

        return render_template(
            'color_prediction_result.html',
            user_choice=user_choice,
            winning_color=winning_color,
            result=result,
            winnings=winnings,
            balance=user.wallet
        )

    return render_template('color_prediction_play.html', balance=user.wallet)

@app.route('/color-prediction/history')
def color_prediction_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Get bet history from BetHistory model
    bet_history = BetHistory.query.filter_by(
        user_id=session['user_id'], 
        bet_type='Color'
    ).order_by(BetHistory.id.desc()).all()
    
    # Convert to format expected by the template
    games = []
    for bet in bet_history:
        game = {
            'id': bet.id,
            'user_id': bet.user_id,
            'bet_amount': bet.bet_amount,
            'user_choice': bet.bet_value,
            'winning_color': bet.bet_value if bet.result == 'win' else get_different_color(bet.bet_value),
            'result': bet.result,
            'winnings': bet.bet_amount * bet.multiplier if bet.result == 'win' else 0,
            'timestamp': bet.id  # Using id as a proxy for timestamp since BetHistory might not have timestamp
        }
        games.append(game)
    
    return render_template('color_prediction_history.html', games=games)

def get_different_color(color):
    """Return a different color than the input color"""
    colors = ['red', 'green', 'blue']
    colors.remove(color.lower())
    return random.choice(colors)





# Helper function to generate random numbers
def generate_keno_numbers():
    return random.sample(range(1, 21), 5)  # Generate 5 random numbers from 1-20

@app.route('/keno', methods=['GET', 'POST'])
def keno_game():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        bet_amount = int(request.form['bet_amount'])
        user_numbers = request.form.getlist('user_numbers')

        if len(user_numbers) != 5:
            return jsonify({"error": "Please select exactly 5 numbers!"}), 400
        if bet_amount > user.wallet:
            return jsonify({"error": "Insufficient Balance!"}), 400

        user_numbers = list(map(int, user_numbers))
        generated_numbers = generate_keno_numbers()
        matches = len(set(user_numbers) & set(generated_numbers))

        # Improved payout multipliers
        multipliers = {0: 0, 1: 1, 2: 2, 3: 5, 4: 10, 5: 50}
        multiplier = multipliers.get(matches, 0)
        
        # Calculate winnings
        winnings = bet_amount * multiplier
        
        # Update wallet balance
        user.wallet = user.wallet - bet_amount + winnings

        # Save game history
        game = KenoHistory(
            user_id=user.id,
            bet_amount=bet_amount,
            user_numbers=user_numbers,  # Store as JSON
            generated_numbers=generated_numbers,  # Store as JSON
            matches=matches,
            winnings=winnings
        )
        db.session.add(game)
        db.session.commit()

        # Return JSON response for AJAX handling
        return jsonify({
            "success": True,
            "user_numbers": user_numbers,
            "generated_numbers": generated_numbers,
            "matches": matches,
            "winnings": winnings,
            "balance": user.wallet
        })

    return render_template('keno_play.html', balance=user.wallet)

@app.route('/keno/recent', methods=['GET'])
def keno_recent():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    # Get the 5 most recent games for the user
    recent_games = KenoHistory.query.filter_by(user_id=session['user_id']).order_by(KenoHistory.id.desc()).limit(5).all()
    
    games_data = []
    for game in recent_games:
        games_data.append({
            "user_numbers": game.user_numbers,
            "generated_numbers": game.generated_numbers,
            "matches": game.matches,
            "winnings": game.winnings,
            "bet_amount": game.bet_amount,
            "timestamp": game.timestamp.strftime("%Y-%m-%d %H:%M:%S") if hasattr(game.timestamp, 'strftime') else str(game.timestamp)
        })
    
    return jsonify({"games": games_data})

@app.route('/keno/history')
def keno_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    games = KenoHistory.query.filter_by(user_id=session['user_id']).order_by(KenoHistory.id.desc()).all()
    return render_template('keno_history.html', games=games)




# Helper function to generate a random number
def generate_number():
    return random.randint(1, 100)

# Helper functions for Rock Paper Scissors game
def get_computer_choice():
    choices = ['rock', 'paper', 'scissors']
    return random.choice(choices)

def determine_winner(user_choice, computer_choice):
    if user_choice == computer_choice:
        return 'tie'
    elif (user_choice == 'rock' and computer_choice == 'scissors') or \
         (user_choice == 'paper' and computer_choice == 'rock') or \
         (user_choice == 'scissors' and computer_choice == 'paper'):
        return 'win'
    else:
        return 'lose'

@app.route('/odd-even', methods=['GET', 'POST'])
def odd_even_play():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        bet_amount = int(request.form['bet_amount'])
        user_choice = request.form['user_choice']

        if bet_amount > user.wallet_balance:
            flash('Insufficient balance! Please add funds to your wallet.', 'danger')
            return redirect(url_for('odd_even_play'))

        # Set win probability to 10%
        win_probability = 0.1
        
        # Determine if user wins based on probability
        random_value = random.random()
        will_win = random_value < win_probability
        
        # Generate a number that matches the result
        generated_number = generate_number()
        
        if will_win:
            # User will win, make sure number matches their choice
            if user_choice == 'odd' and generated_number % 2 == 0:
                # User chose odd but number is even, generate a new odd number
                while generated_number % 2 == 0:
                    generated_number = generate_number()
            elif user_choice == 'even' and generated_number % 2 != 0:
                # User chose even but number is odd, generate a new even number
                while generated_number % 2 != 0:
                    generated_number = generate_number()
            result = 'win'
        else:
            # User will lose, make sure number doesn't match their choice
            if user_choice == 'odd' and generated_number % 2 != 0:
                # User chose odd and number is odd, generate a new even number
                while generated_number % 2 != 0:
                    generated_number = generate_number()
            elif user_choice == 'even' and generated_number % 2 == 0:
                # User chose even and number is even, generate a new odd number
                while generated_number % 2 == 0:
                    generated_number = generate_number()
            result = 'lose'

        # Update wallet balance
        if result == 'win':
            user.wallet_balance += bet_amount
        else:
            user.wallet_balance -= bet_amount

        # Save game history
        game = OddEvenHistory(
            user_id=user.id,
            bet_amount=bet_amount,
            user_choice=user_choice,
            generated_number=generated_number,
            result=result
        )
        db.session.add(game)
        db.session.commit()

        return render_template('odd_even_result.html', user_choice=user_choice, generated_number=generated_number, result=result, balance=user.wallet_balance)

    return render_template('odd_even_play.html', balance=user.wallet_balance)

@app.route('/odd-even/history')
def odd_even_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    games = OddEvenHistory.query.filter_by(user_id=session['user_id']).all()
    return render_template('odd_even_history.html', games=games)

@app.route('/play', methods=['GET', 'POST'])
def play_rock():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        bet_amount = int(request.form['bet_amount'])
        user_choice = request.form['user_choice']
        
        if bet_amount > user.wallet:
            return "Insufficient Balance!"

        computer_choice = get_computer_choice()
        result = determine_winner(user_choice, computer_choice)

        # Update wallet balance
        if result == 'win':
            user.wallet += bet_amount
        elif result == 'lose':
            user.wallet -= bet_amount

        # Save game history
        game = RockPaperScissorsHistory(
            user_id=user.id,
            bet_amount=bet_amount,
            user_choice=user_choice,
            computer_choice=computer_choice,
            result=result
        )
        db.session.add(game)
        db.session.commit()

        return render_template('rockpapar.html', user_choice=user_choice, computer_choice=computer_choice, result=result, balance=user.wallet)

    return render_template('rockpapar.html', balance=user.wallet)

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    games = RockPaperScissorsHistory.query.filter_by(user_id=session['user_id']).all()
    return render_template('history.html', games=games)



# Helper function to roll the dice
def roll_dice():
    return random.randint(1, 6)

@app.route('/dice', methods=['GET', 'POST'])
def dice_game():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        bet_amount = int(request.form['bet_amount'])
        user_choice = int(request.form['user_choice'])

        if bet_amount > user.wallet:
            return "Insufficient Balance!"

        dice_roll = roll_dice()
        result = 'win' if user_choice == dice_roll else 'lose'

        # Update wallet balance
        if result == 'win':
            user.wallet += bet_amount * 5  # Winning payout is 5x the bet
        else:
            user.wallet -= bet_amount

        # Save game history
        game = DiceBettingHistory(
            user_id=user.id,
            bet_amount=bet_amount,
            user_choice=user_choice,
            dice_roll=dice_roll,
            result=result
        )
        db.session.add(game)
        db.session.commit()

        return render_template('dice_result.html', user_choice=user_choice, dice_roll=dice_roll, result=result, balance=user.wallet)

    return render_template('dice_play.html', balance=user.wallet)



@app.route('/dice/history')
def dice_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    games = DiceBettingHistory.query.filter_by(user_id=session['user_id']).all()
    return render_template('dice_history.html', games=games)



@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Validate the input
    if not name or not email or not message:
        return "All fields are required!", 400

    # Save to the database
    try:
        new_message = ContactMessage(name=name, email=email, message=message)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('contact_success'))
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/contact_success')
def contact_success():
    return "Your message has been sent successfully!"

@app.route('/messages')
def view_messages():
    messages = ContactMessage.query.all()
    return {
        "messages": [
            {
                "name": msg.name,
                "email": msg.email,
                "message": msg.message,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            } for msg in messages
        ]
    }

# Wallet route
@app.route('/wallet', methods=['GET', 'POST'])
def wallet():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if request.method == 'POST':
        action = request.form.get('action')
        amount = float(request.form.get('amount', 0))
        if action == 'deposit':
            return redirect(url_for('create_order', amount=amount))
        elif action == 'withdraw' and amount <= user.wallet:
            user.wallet -= amount
            db.session.commit()
            flash('Withdrawal successful!', 'success')
        else:
            flash('Insufficient balance or invalid action!', 'danger')
    return render_template('wallet.html', user=user)

# Create order for Razorpay payment
@app.route('/create_order/<float:amount>', methods=['GET'])
def create_order(amount):
    amount_in_paise = int(amount * 100)  # Convert amount to paise
    order_data = {
        'amount': amount_in_paise,
        'currency': 'INR',
        'payment_capture': '1'
    }
    order = razorpay_client.order.create(data=order_data)
    return render_template('pay.html', order_id=order['id'], amount=amount)

# Payment success route
@app.route('/payment_success', methods=['POST'])
def payment_success():
    payment_id = request.form.get('razorpay_payment_id')
    if not payment_id:
        flash("Payment ID not found!", 'danger')
        return redirect(url_for('wallet'))
    
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    amount = float(request.form.get('amount', 0))
    user.wallet += amount
    db.session.commit()
    flash("Payment Successful!", 'success')
    return redirect(url_for('wallet'))

# Payment failure route
@app.route('/payment_failed', methods=['POST'])
def payment_failed():
    flash("Payment Failed! Please try again.", 'danger')
    return redirect(url_for('wallet'))

# Account route
@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.name = request.form['name']
        db.session.commit()
        flash('Profile updated successfully.', 'success')
    return render_template('account.html', user=user)

# Promotion route
@app.route('/promo', methods=['GET', 'POST'])
def promotions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        promo_code = request.form['promo_code']
        valid_codes = ["WELCOME100", "WEEKLYCASHBACK", "REFER100"]
        if promo_code in valid_codes:
            flash(f'Promo code "{promo_code}" redeemed successfully!', 'success')
        else:
            flash('Invalid promo code. Please try again.', 'danger')
    return render_template('promo.html')

# Route for displaying game history
@app.route('/game-history')
def game_history():
    # Check if the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Fetch each game type's history from the database
    # color_game_history = ColorGameResult.query.filter_by(user_id=user_id).order_by(ColorGameResult.timestamp.desc()).all()
    odd_even_game_history = OddEvenGameResult.query.filter_by(user_id=user_id).order_by(OddEvenGameResult.timestamp.desc()).all()
    generic_game_history = GameResult.query.filter_by(user_id=user_id).order_by(GameResult.timestamp.desc()).all()

    # Structure data to pass to the template
    all_games_history = {
        # 'color_game': color_game_history,
        'odd_even_game': odd_even_game_history,
        'generic_game': generic_game_history
    }

    # Render the game history template
    return render_template('game_history.html', all_games_history=all_games_history)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        user = User.query.filter_by(phone=phone).first()
        if user and check_password_hash(user.pass_hash, password):
            login_user(user)
            session['user_id'] = user.id
            session['name'] = user.name
            return redirect(url_for('account'))
        flash('Invalid login credentials. Please try again.', 'danger')
    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    session.pop('name', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        password = request.form['password']
        existing_user = User.query.filter_by(phone=phone).first()
        if existing_user:
            flash('Phone number already registered. Please login.', 'warning')
            return redirect(url_for('login'))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, phone=phone, pass_hash=hashed_password, wallet_balance=0.0)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully. Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')



import mysql.connector
# from flask import Flask, render_template, request, redirect, url_for, session, flash
import bcrypt
import sqlite3

  # Change this

# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='myadmin'
    )

# Admin Login Route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
        admin = cursor.fetchone()
        conn.close()

        if admin and bcrypt.checkpw(password.encode('utf-8'), admin['password'].encode('utf-8')):
            session['admin_logged_in'] = True
            session['admin_username'] = admin['username']
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid credentials", "danger")

    return render_template('admin_login.html')

# Admin Dashboard Route
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_users FROM user")
    total_users = cursor.fetchone()['total_users']

    cursor.execute("SELECT COUNT(*) AS total_bets FROM bet_history")
    total_bets = cursor.fetchone()['total_bets']

    cursor.execute("SELECT COUNT(*) AS pending_withdrawals FROM transactions WHERE type='withdrawal' AND status='pending'")
    pending_withdrawals = cursor.fetchone()['pending_withdrawals']

    conn.close()

    return render_template('admin_dashboard.html', total_users=total_users, total_bets=total_bets, pending_withdrawals=pending_withdrawals)

# Manage Users
@app.route('/manage_users')
def manage_user():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    conn.close()

    return render_template('manage_users.html', users=users)

# Block User
@app.route('/block_user/<int:user_id>')
def block_user(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_blocked = TRUE WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('manage_users'))

# Approve Withdrawal
@app.route('/approve_withdrawal/<int:transaction_id>')
def approve_withdrawal(transaction_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE transactions SET status = 'approved' WHERE id = %s", (transaction_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))

# Logout
@app.route('/admin_logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))







@app.route('/')
def main():
    return redirect(url_for('home'))

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


@app.route("/manage-users")
def manage_users():
    return render_template("manage_users.html")

@app.route('/color')
def color():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('color.html', User=session)

@app.route('/contact')
def contact_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('contact.html')
    

@app.route('/colorgame')
def colorgame():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('color_game.html', User=session, balance=user.wallet)

@app.route('/color_game/place_bet', methods=['POST'])
def color_game_place_bet():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401

    try:
        data = request.get_json()
        bet_type = data.get('type')
        bet_value = data.get('value')
        bet_amount = float(data.get('betAmount', 0))
        multiplier = float(data.get('multiplier', 0))

        # Validate inputs
        if not all([bet_type, bet_value, bet_amount, multiplier]):
            return jsonify({"success": False, "error": "Invalid bet parameters"}), 400

        # Get user and check balance
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404

        if bet_amount > user.wallet:
            return jsonify({"success": False, "error": "Insufficient balance"}), 400

        # Deduct bet amount from wallet
        user.wallet -= bet_amount
        
        # Save bet to history
        bet_history = BetHistory(
            user_id=user.id,
            bet_type=bet_type,
            bet_value=bet_value,
            bet_amount=bet_amount,
            multiplier=multiplier
        )
        db.session.add(bet_history)
        db.session.commit()

        return jsonify({
            "success": True,
            "new_balance": user.wallet,
            "bet_id": bet_history.id
        })

    except Exception as e:
        db.session.rollback()
        print("Error placing bet:", str(e))
        return jsonify({"success": False, "error": "Failed to place bet"}), 500

@app.route('/color_game/get_result', methods=['GET'])
def color_game_get_result():
    """Get the result for the current game round"""
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401

    try:
        # Generate results
        _, color = generate_color_game_result("Color")
        _, number = generate_color_game_result("Number")
        _, bigSmall = generate_color_game_result("BigSmall")

        # Update any pending bets
        pending_bets = BetHistory.query.filter_by(
            user_id=session['user_id'],
            result=None
        ).all()

        user = User.query.get(session['user_id'])

        for bet in pending_bets:
            # Determine if bet won
            won = False
            if bet.bet_type == "Color" and bet.bet_value == color:
                won = True
            elif bet.bet_type == "Number" and bet.bet_value == number:
                won = True
            elif bet.bet_type == "BigSmall" and bet.bet_value == bigSmall:
                won = True

            # Update bet result
            bet.result = "win" if won else "lose"
            
            # If won, add winnings to wallet
            if won:
                winnings = bet.bet_amount * bet.multiplier
                user.wallet += winnings

        db.session.commit()

        return jsonify({
            "success": True,
            "results": {
                "color": color,
                "number": number,
                "bigSmall": bigSmall
            }
        })

    except Exception as e:
        db.session.rollback()
        print("Error getting result:", str(e))
        return jsonify({"success": False, "error": "Failed to get result"}), 500

@app.route('/dice')
def dice():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dice_play.html', User=session)

@app.route('/keno')
def keno():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('keno_play.html', User=session)

@app.route('/get_balance', methods=['GET'])
def get_balance():
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    if user:
        return jsonify({"balance": user.wallet})
    return jsonify({"error": "User not found"}), 404

@app.route('/update_balance', methods=['POST'])
def update_balance():
    data = request.json
    user_id = data.get("user_id")
    new_balance = data.get("new_balance")

    user = User.query.get(user_id)
    if user:
        user.wallet = new_balance
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "User not found"}), 404


# ///////////////////////////////////////////////////

@app.route('/get_wallet_balance', methods=['GET'])
def get_wallet_balance():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404

    print("Returning Wallet Balance:", user.wallet)  # Debugging
    return jsonify({"wallet_balance": user.wallet})



@app.route('/place_bet', methods=['POST'])
def place_bet():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    data = request.json
    bet_amount = float(data['betAmount'])
    bet_type = data['type']
    bet_value = data['value']
    multiplier = float(data['multiplier'])

    if bet_amount > user.wallet:
        return jsonify({"success": False, "error": "Insufficient balance"})

    # Deduct balance
    user.wallet -= bet_amount
    
    # Determine result (random for now, can be replaced with actual game logic)
    result = "win" if random.random() < 0.5 else "lose"
    
    # Update balance if win
    if result == "win":
        winnings = bet_amount * multiplier
        user.wallet += winnings
    
    # Save bet history with result
    bet = BetHistory(
        user_id=user.id, 
        bet_type=bet_type, 
        bet_value=bet_value, 
        bet_amount=bet_amount, 
        multiplier=multiplier,
        result=result
    )
    db.session.add(bet)
    db.session.commit()

    return jsonify({
        "success": True,
        "new_balance": user.wallet,
        "bet_history": {"type": bet_type, "value": bet_value, "amount": bet_amount},
        "result": result
    })



@app.route('/get_bet_history', methods=['GET'])
def get_bet_history():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404

    bet_history = BetHistory.query.filter_by(user_id=user.id).order_by(BetHistory.id.desc()).limit(10).all()

    bet_data = [
        {
            "type": bet.bet_type,
            "value": bet.bet_value,
            "amount": bet.bet_amount,
            "multiplier": bet.multiplier,
            "result": bet.result or "pending"
        }
        for bet in bet_history
    ]

    return jsonify({"bet_history": bet_data})

@app.route('/color_game/get_state')
def color_game_get_state():
    """Get current game state including timer and results"""
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 401
    
    # Get remaining time and check if round needs to be updated
    remaining_time = get_remaining_time()
    
    # Get current results if time is up
    current_results = game_state['results'] if remaining_time <= 0 else None
    
    return jsonify({
        "success": True,
        "game_id": game_state['current_round_id'],
        "remaining_time": remaining_time,
        "results": current_results,
        "server_time": time.time()  # Send server time for better synchronization
    })

@app.route('/mine-betting', methods=['GET'])
def mine_betting_game():
    """Render the mine betting game page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('mine_betting.html', balance=user.wallet)

@app.route('/mine-betting/start', methods=['POST'])
def mine_betting_start():
    """Start a new mine betting game"""
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401
    
    try:
        data = request.get_json()
        bet_amount = float(data.get('bet_amount', 0))
        grid_size = int(data.get('grid_size', 5))  # Default 5x5 grid
        mines_count = int(data.get('mines_count', 3))  # Default 3 mines
        
        # Validate inputs
        if not bet_amount or bet_amount <= 0:
            return jsonify({"success": False, "error": "Invalid bet amount"}), 400
        
        if grid_size < 3 or grid_size > 8:
            return jsonify({"success": False, "error": "Grid size must be between 3x3 and 8x8"}), 400
        
        if mines_count < 1 or mines_count >= (grid_size * grid_size) / 2:
            return jsonify({"success": False, "error": f"Mines count must be between 1 and {(grid_size * grid_size) // 2 - 1}"}), 400
        
        # Get user and check balance
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        if bet_amount > user.wallet:
            return jsonify({"success": False, "error": "Insufficient balance"}), 400
        
        # Deduct bet amount from wallet
        user.wallet -= bet_amount
        db.session.commit()
        
        # Generate mine positions
        total_cells = grid_size * grid_size
        all_positions = list(range(total_cells))
        random.shuffle(all_positions)
        mine_positions = all_positions[:mines_count]
        
        # Calculate multiplier table based on grid size and mines count
        # The more mines, the higher the potential multiplier
        base_multiplier = 1 + (mines_count / (grid_size * grid_size)) * 10
        multipliers = []
        
        for i in range(1, total_cells - mines_count + 1):
            # Multiplier increases as more cells are revealed
            # Higher risk (more revealed cells) = higher reward
            multiplier = base_multiplier * (1 + (i / (total_cells - mines_count)) * mines_count)
            multipliers.append(round(multiplier, 2))
        
        # Store game state in session
        session['mine_game'] = {
            'bet_amount': bet_amount,
            'grid_size': grid_size,
            'mines_count': mines_count,
            'mine_positions': mine_positions,
            'revealed_positions': [],
            'current_multiplier': 1.0,
            'multiplier_table': multipliers,
            'game_over': False,
            'result': None
        }
        
        return jsonify({
            "success": True,
            "grid_size": grid_size,
            "mines_count": mines_count,
            "multiplier_table": multipliers,
            "new_balance": user.wallet
        })
    
    except Exception as e:
        db.session.rollback()
        print("Error starting mine game:", str(e))
        return jsonify({"success": False, "error": "Failed to start game"}), 500

@app.route('/mine-betting/reveal', methods=['POST'])
def mine_betting_reveal():
    """Reveal a cell in the mine betting game"""
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401
    
    if 'mine_game' not in session:
        return jsonify({"success": False, "error": "No active game found"}), 400
    
    try:
        data = request.get_json()
        position = int(data.get('position', -1))
        
        game = session['mine_game']
        
        # Check if game is already over
        if game['game_over']:
            return jsonify({"success": False, "error": "Game is already over"}), 400
        
        # Check if position is valid
        if position < 0 or position >= game['grid_size'] * game['grid_size']:
            return jsonify({"success": False, "error": "Invalid position"}), 400
        
        # Check if position is already revealed
        if position in game['revealed_positions']:
            return jsonify({"success": False, "error": "Cell already revealed"}), 400
        
        # Check if position has a mine
        hit_mine = position in game['mine_positions']
        
        # Add position to revealed positions
        game['revealed_positions'].append(position)
        
        # Update game state
        if hit_mine:
            game['game_over'] = True
            game['result'] = 'lose'
            winnings = 0
        else:
            # Update multiplier based on number of revealed cells
            revealed_count = len(game['revealed_positions'])
            
            if revealed_count <= len(game['multiplier_table']):
                game['current_multiplier'] = game['multiplier_table'][revealed_count - 1]
            
            # Check if all safe cells are revealed
            if revealed_count == game['grid_size'] * game['grid_size'] - game['mines_count']:
                game['game_over'] = True
                game['result'] = 'win'
                winnings = game['bet_amount'] * game['current_multiplier']
            else:
                winnings = 0  # Game still in progress
        
        # Update session
        session['mine_game'] = game
        
        # If game is over, save to history and update wallet
        if game['game_over']:
            user = User.query.get(session['user_id'])
            
            # If won, add winnings to wallet
            if game['result'] == 'win':
                user.wallet += winnings
            
            # Save game to history
            history = MineBettingHistory(
                user_id=user.id,
                bet_amount=game['bet_amount'],
                grid_size=game['grid_size'],
                mines_count=game['mines_count'],
                cells_revealed=len(game['revealed_positions']),
                mine_positions=game['mine_positions'],
                revealed_positions=game['revealed_positions'],
                multiplier_achieved=game['current_multiplier'],
                result=game['result'],
                winnings=winnings
            )
            db.session.add(history)
            db.session.commit()
            
            return jsonify({
                "success": True,
                "hit_mine": hit_mine,
                "game_over": True,
                "result": game['result'],
                "multiplier": game['current_multiplier'],
                "winnings": winnings,
                "mine_positions": game['mine_positions'],
                "new_balance": user.wallet
            })
        
        return jsonify({
            "success": True,
            "hit_mine": hit_mine,
            "game_over": False,
            "multiplier": game['current_multiplier'],
            "revealed_position": position
        })
    
    except Exception as e:
        db.session.rollback()
        print("Error revealing cell:", str(e))
        return jsonify({"success": False, "error": "Failed to reveal cell"}), 500

@app.route('/mine-betting/cashout', methods=['POST'])
def mine_betting_cashout():
    """Cash out current winnings and end the game"""
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Please login first"}), 401
    
    if 'mine_game' not in session:
        return jsonify({"success": False, "error": "No active game found"}), 400
    
    try:
        game = session['mine_game']
        
        # Check if game is already over
        if game['game_over']:
            return jsonify({"success": False, "error": "Game is already over"}), 400
        
        # Calculate winnings
        winnings = game['bet_amount'] * game['current_multiplier']
        
        # Update game state
        game['game_over'] = True
        game['result'] = 'win'
        
        # Update user wallet
        user = User.query.get(session['user_id'])
        user.wallet += winnings
        
        # Save game to history
        history = MineBettingHistory(
            user_id=user.id,
            bet_amount=game['bet_amount'],
            grid_size=game['grid_size'],
            mines_count=game['mines_count'],
            cells_revealed=len(game['revealed_positions']),
            mine_positions=game['mine_positions'],
            revealed_positions=game['revealed_positions'],
            multiplier_achieved=game['current_multiplier'],
            result='win',
            winnings=winnings
        )
        db.session.add(history)
        db.session.commit()
        
        # Update session
        session['mine_game'] = game
        
        return jsonify({
            "success": True,
            "game_over": True,
            "result": 'win',
            "multiplier": game['current_multiplier'],
            "winnings": winnings,
            "mine_positions": game['mine_positions'],
            "new_balance": user.wallet
        })
    
    except Exception as e:
        db.session.rollback()
        print("Error cashing out:", str(e))
        return jsonify({"success": False, "error": "Failed to cash out"}), 500

@app.route('/mine-betting/history')
def mine_betting_history():
    """Get user's mine betting history"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    history = MineBettingHistory.query.filter_by(
        user_id=session['user_id']
    ).order_by(MineBettingHistory.timestamp.desc()).limit(20).all()
    
    history_data = []
    for game in history:
        history_data.append({
            "id": game.id,
            "bet_amount": game.bet_amount,
            "grid_size": game.grid_size,
            "mines_count": game.mines_count,
            "cells_revealed": game.cells_revealed,
            "multiplier": game.multiplier_achieved,
            "result": game.result,
            "winnings": game.winnings,
            "timestamp": game.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return render_template('mine_betting_history.html', history=history_data)

@app.route('/aviator', methods=['GET'])
def aviator_game():
    if not current_user.is_authenticated:
        flash('Please log in to play Aviator game')
        return redirect(url_for('login'))
    
    return render_template('aviator.html', balance=current_user.wallet)

@app.route('/aviator/history')
def aviator_history():
    if not current_user.is_authenticated:
        flash('Please log in to view your history')
        return redirect(url_for('login'))
    
    # Get user's game history
    history = AviatorHistory.query.filter_by(user_id=current_user.id).order_by(AviatorHistory.timestamp.desc()).limit(20).all()
    
    # Calculate statistics
    total_games = len(history)
    total_wagered = sum(game.bet_amount for game in history)
    total_winnings = sum(game.winnings for game in history)
    total_profit = total_winnings - total_wagered
    highest_multiplier = max([game.multiplier for game in history]) if history else 0
    
    stats = {
        'total_games': total_games,
        'total_wagered': round(total_wagered, 2),
        'total_profit': round(total_profit, 2),
        'highest_multiplier': round(highest_multiplier, 2)
    }
    
    return render_template('aviator_history.html', history=history, stats=stats, balance=current_user.wallet)

@app.route('/aviator/start', methods=['POST'])
def aviator_start():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'error': 'User not logged in'})
    
    data = request.get_json()
    bet_amount = float(data.get('bet_amount', 0))
    auto_cashout = data.get('auto_cashout')
    
    if bet_amount <= 0:
        return jsonify({'success': False, 'error': 'Invalid bet amount'})
    
    if current_user.wallet < bet_amount:
        return jsonify({'success': False, 'error': 'Insufficient balance'})
    
    # Generate a unique game ID
    game_id = str(uuid.uuid4())
    
    # Store game state in session
    session['aviator_game'] = {
        'game_id': game_id,
        'bet_amount': bet_amount,
        'auto_cashout': auto_cashout,
        'start_time': time.time(),
        'active': True,
        'crash_point': calculate_crash_point()
    }
    
    # Deduct bet amount from wallet
    current_user.wallet -= bet_amount
    db.session.commit()
    
    return jsonify({
        'success': True,
        'game_id': game_id,
        'new_balance': current_user.wallet
    })

@app.route('/aviator/cashout', methods=['POST'])
def aviator_cashout():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'error': 'User not logged in'})
    
    if 'aviator_game' not in session:
        return jsonify({'success': False, 'error': 'No active game'})
    
    data = request.get_json()
    multiplier = float(data.get('multiplier', 1.0))
    
    game = session['aviator_game']
    
    # Check if the game is active
    if not game.get('active', False):
        return jsonify({'success': False, 'error': 'Game is not active'})
    
    # Check if multiplier is valid (not crashed yet)
    if multiplier > game['crash_point']:
        return jsonify({'success': False, 'error': 'Invalid multiplier'})
    
    # Calculate winnings
    bet_amount = game['bet_amount']
    winnings = bet_amount * multiplier
    
    # Update wallet
    current_user.wallet += winnings
    db.session.commit()
    
    # Save game to history
    history = AviatorHistory(
        user_id=current_user.id,
        bet_amount=bet_amount,
        multiplier=multiplier,
        auto_cashout=game.get('auto_cashout'),
        winnings=winnings,
        result='win',
        timestamp=datetime.now()
    )
    db.session.add(history)
    db.session.commit()
    
    # Mark game as inactive
    session.pop('aviator_game', None)
    
    return jsonify({
        'success': True,
        'multiplier': multiplier,
        'winnings': winnings,
        'new_balance': current_user.wallet
    })

@app.route('/aviator/crash', methods=['POST'])
def aviator_crash():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'error': 'User not logged in'})
    
    if 'aviator_game' not in session:
        return jsonify({'success': False, 'error': 'No active game'})
    
    data = request.get_json()
    crash_multiplier = float(data.get('crash_multiplier', 1.0))
    
    game = session['aviator_game']
    
    # Check if the game is active
    if not game.get('active', False):
        return jsonify({'success': False, 'error': 'Game is not active'})
    
    # Record loss
    history = AviatorHistory(
        user_id=current_user.id,
        bet_amount=game['bet_amount'],
        multiplier=crash_multiplier,
        auto_cashout=game.get('auto_cashout'),
        winnings=0,
        result='loss',
        timestamp=datetime.now()
    )
    db.session.add(history)
    db.session.commit()
    
    # Clear game from session
    session.pop('aviator_game', None)
    
    return jsonify({
        'success': True,
        'new_balance': current_user.wallet
    })

@app.route('/aviator/get_multiplier', methods=['GET'])
def get_aviator_multiplier():
    if 'aviator_game' not in session:
        return jsonify({'success': False, 'error': 'No active game'})
    
    game = session['aviator_game']
    
    # Check if the game is active
    if not game.get('active', False):
        return jsonify({'success': False, 'error': 'Game is not active'})
    
    elapsed_time = time.time() - game['start_time']
    
    # Calculate current multiplier based on elapsed time
    # Using a simple exponential growth formula
    current_multiplier = 1.0 + (0.1 * elapsed_time)
    
    # Check if game should crash
    should_crash = current_multiplier >= game['crash_point']
    
    # Check if auto cashout is triggered
    auto_cashout = game.get('auto_cashout')
    auto_cashout_triggered = auto_cashout is not None and current_multiplier >= auto_cashout
    
    return jsonify({
        'success': True,
        'multiplier': current_multiplier,
        'should_crash': should_crash,
        'auto_cashout_triggered': auto_cashout_triggered
    })

def calculate_crash_point():
    # Generate a random crash point between 1.1 and 10.0
    # With occasional higher values for excitement
    if random.random() < 0.05:  # 5% chance for a high multiplier
        return random.uniform(10.0, 50.0)
    else:
        return random.uniform(1.1, 10.0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Add this function to migrate the database
def migrate_database():
    try:
        # Check if wallet column exists
        with db.engine.connect() as conn:
            result = conn.execute(db.text("SHOW COLUMNS FROM user LIKE 'wallet'"))
            has_wallet = result.fetchone() is not None
            
            # If wallet doesn't exist but wallet_balance does, we're good
            if not has_wallet:
                print("Using existing wallet_balance column")
            else:
                # If wallet exists, migrate data to wallet_balance
                print("Migrating wallet to wallet_balance")
                conn.execute(db.text("ALTER TABLE user ADD COLUMN wallet_balance FLOAT DEFAULT 0.0"))
                conn.execute(db.text("UPDATE user SET wallet_balance = wallet"))
                conn.execute(db.text("ALTER TABLE user DROP COLUMN wallet"))
    except Exception as e:
        print(f"Migration error: {e}")
        
# Call migration after db.create_all()
with app.app_context():
    db.create_all()
    migrate_database()

# Plinko Game Routes
@app.route('/plinko', methods=['GET'])
def plinko_game():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('plinko.html', wallet_balance=user.wallet_balance)

@app.route('/plinko/history')
def plinko_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    history = PlinkoHistory.query.filter_by(user_id=session['user_id']).order_by(PlinkoHistory.timestamp.desc()).limit(20).all()
    history_list = []
    
    for item in history:
        history_list.append({
            'id': item.id,
            'bet_amount': item.bet_amount,
            'risk_level': item.risk_level,
            'rows': item.rows,
            'multiplier': item.multiplier,
            'winnings': item.winnings,
            'timestamp': item.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(history_list)

@app.route('/plinko/play', methods=['POST'])
def play_plinko():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login to play'}), 401
    
    data = request.get_json()
    bet_amount = float(data.get('bet_amount', 0))
    risk_level = data.get('risk_level', 'medium')
    rows = int(data.get('rows', 8))
    
    if rows < 8 or rows > 16:
        return jsonify({'error': 'Invalid number of rows'}), 400
    
    user = User.query.get(session['user_id'])
    
    if bet_amount <= 0:
        return jsonify({'error': 'Bet amount must be greater than 0'}), 400
    
    if user.wallet_balance < bet_amount:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Generate random path (L = left, R = right)
    path = ''.join(random.choice(['L', 'R']) for _ in range(rows))
    
    # Calculate final position (0 to rows)
    final_position = path.count('R')
    
    # Get multiplier based on risk level and position
    multipliers = get_plinko_multipliers(risk_level, rows)
    multiplier = multipliers[final_position]
    
    # Calculate winnings
    winnings = bet_amount * multiplier
    
    # Update user wallet
    user.wallet_balance -= bet_amount
    if multiplier > 0:
        user.wallet_balance += winnings
    
    # Save game history
    game = PlinkoHistory(
        user_id=user.id,
        bet_amount=bet_amount,
        risk_level=risk_level,
        rows=rows,
        path=path,
        multiplier=multiplier,
        winnings=winnings
    )
    
    db.session.add(game)
    db.session.commit()
    
    return jsonify({
        'path': path,
        'multiplier': multiplier,
        'winnings': winnings,
        'new_balance': user.wallet_balance
    })

def get_plinko_multipliers(risk_level, rows):
    """
    Returns the multipliers for each position based on risk level and number of rows
    """
    if rows == 8:
        if risk_level == 'low':
            return [5.6, 2.1, 1.1, 1.0, 0.5, 1.0, 1.1, 2.1, 5.6]
        elif risk_level == 'medium':
            return [13.0, 3.0, 1.3, 0.7, 0.4, 0.7, 1.3, 3.0, 13.0]
        else:  # high
            return [110.0, 14.0, 2.0, 0.2, 0.1, 0.2, 2.0, 14.0, 110.0]
    elif rows == 12:
        if risk_level == 'low':
            return [8.1, 3.1, 1.9, 1.3, 1.0, 0.7, 0.5, 0.7, 1.0, 1.3, 1.9, 3.1, 8.1]
        elif risk_level == 'medium':
            return [33.0, 11.0, 4.0, 2.0, 1.0, 0.5, 0.3, 0.5, 1.0, 2.0, 4.0, 11.0, 33.0]
        else:  # high
            return [170.0, 47.0, 9.0, 2.0, 0.7, 0.2, 0.1, 0.2, 0.7, 2.0, 9.0, 47.0, 170.0]
    else:  # rows == 16
        if risk_level == 'low':
            return [10.0, 3.8, 2.5, 1.7, 1.4, 1.1, 0.9, 0.7, 0.5, 0.7, 0.9, 1.1, 1.4, 1.7, 2.5, 3.8, 10.0]
        elif risk_level == 'medium':
            return [110.0, 42.0, 16.0, 7.0, 3.0, 1.4, 0.9, 0.6, 0.3, 0.6, 0.9, 1.4, 3.0, 7.0, 16.0, 42.0, 110.0]
        else:  # high
            return [1000.0, 130.0, 26.0, 9.0, 3.0, 1.4, 0.5, 0.2, 0.1, 0.2, 0.5, 1.4, 3.0, 9.0, 26.0, 130.0, 1000.0]

if __name__ == '__main__':
    app.run(debug=True)
