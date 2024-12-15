from flask import Flask, render_template, request, redirect, url_for, flash
import hashlib
from datetime import datetime
import random
from flask import session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

class Block:
    def __init__(self, index, previous_hash, data):
        self.index = index
        self.previous_hash = previous_hash
        self.data = data
        self.timestamp = datetime.now()
        self.current_hash = self.calculate_hash()

    def calculate_hash(self):
        return hashlib.sha256(
            f"{self.index}{self.timestamp}{self.previous_hash}{self.data}".encode()
        ).hexdigest()

class Blockchain:
    def __init__(self):
        self.head = Block(0, "0", "Genesis Block")
        self.tail = self.head

    def add_block(self, data):
        new_block = Block(self.tail.index + 1, self.tail.current_hash, data)
        self.tail.next = new_block
        self.tail = new_block

    def display_chain(self):
        chain = []
        current = self.head
        while current:
            chain.append({
                "index": current.index,
                "data": current.data,
                "timestamp": current.timestamp,
                "previous_hash": current.previous_hash,
                "current_hash": current.current_hash
            })
            current = getattr(current, "next", None)
        return chain

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.balance = 1000.0
        self.transaction_history = []

    def add_transaction(self, transaction):
        self.transaction_history.append(transaction)

class DEXSystem:
    def __init__(self):
        self.users = {}
        self.blockchain = Blockchain()

    def create_account(self, username, password):
        if username in self.users:
            return False
        self.users[username] = User(username, password)
        return True

    def login(self, username, password):
        user = self.users.get(username)
        if user and user.password == password:
            return user
        return None

    def add_funds(self, user, amount):
        user.balance += amount
        self.blockchain.add_block(f"{user.username} added {amount} USD.")
        user.add_transaction(f"Added {amount} USD.")

    def withdraw_funds(self, user, amount):
        if amount > user.balance:
            return False
        user.balance -= amount
        self.blockchain.add_block(f"{user.username} withdrew {amount} USD.")
        user.add_transaction(f"Withdrew {amount} USD.")
        return True

    def transfer_funds(self, sender, receiver, amount):
        if sender.balance >= amount:
            sender.balance -= amount
            receiver.balance += amount
            self.blockchain.add_block(f"{sender.username} transferred {amount} USD to {receiver.username}.")
            sender.add_transaction(f"Transferred {amount} USD to {receiver.username}.")
            receiver.add_transaction(f"Received {amount} USD from {sender.username}.")
            return True
        return False

    def convert_currency(self, user, amount, choice):
        # Define the crypto prices
        crypto_prices = {
            1: {"name": "Bitcoin", "price": 98000},
            2: {"name": "Ethereum", "price": 3900},
            3: {"name": "Solana", "price": 250},
            4: {"name": "Ripple", "price": 2.53},
            5: {"name": "Polkadot", "price": 12},
            6: {"name": "BNB Chain", "price": 602.5},
            7: {"name": "ShibaInu", "price": 0.00039},
            8: {"name": "THENA", "price": 2.53},
            9: {"name": "XION", "price": 0.000987},
            10: {"name": "Chainlink", "price": 12.6},
            11: {"name": "Polygon", "price": 87.99},
            12: {"name": "Stellar", "price": 1.293},
            13: {"name": "VeChain", "price": 0.0023},
            14: {"name": "Avalanche", "price": 5800},
            15: {"name": "TheSandbox", "price": 0.0099},
            16: {"name": "ThetaToken", "price": 7600},
            17: {"name": "Tezos", "price": 88.9}
        }

        # Update prices with random fluctuation
        for key, value in crypto_prices.items():
            change = random.uniform(-0.05, 0.05) * value["price"]
            value["price"] += change
            if value["price"] < 0:
                value["price"] = 0.01

        # Check if the user has sufficient funds
        if amount <= user.balance:
            crypto_rate = crypto_prices[choice]["price"]
            converted_amount = amount / crypto_rate
            selected_currency = crypto_prices[choice]["name"]
            user.balance -= amount
            user.add_transaction(f"Converted {amount} USD to {converted_amount:.5f} {selected_currency}.")
            self.blockchain.add_block(f"{user.username} converted {amount} USD to {converted_amount:.5f} {selected_currency}.")
            return converted_amount, selected_currency
        return None, None

# Initialize DEX System
system = DEXSystem()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if system.create_account(username, password):
            flash("Account created successfully!", "success")
            return redirect(url_for('login'))
        flash("Username already exists.", "danger")
    return render_template('create_account.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = system.login(username, password)
        if user:
            session['username'] = username
            return redirect(url_for('user_menu', username=username))
        flash("Invalid credentials.", "danger")
    return render_template('login.html')

@app.route('/user_menu/<username>')
def user_menu(username):
    user = system.users.get(username)
    if user:
        return render_template('user_menu.html', user=user)
    return redirect(url_for('login'))

@app.route('/add_funds/<username>', methods=['POST'])
def add_funds(username):
    user = system.users.get(username)
    if user:
        amount = float(request.form['amount'])
        system.add_funds(user, amount)
        flash(f"Added {amount} USD to balance.", "success")
    return redirect(url_for('user_menu', username=username))

@app.route('/withdraw_funds/<username>', methods=['POST'])
def withdraw_funds(username):
    user = system.users.get(username)
    if user:
        amount = float(request.form['amount'])
        if system.withdraw_funds(user, amount):
            flash(f"Withdrew {amount} USD from balance.", "success")
        else:
            flash("Insufficient funds.", "danger")
    return redirect(url_for('user_menu', username=username))

@app.route('/transfer/<username>', methods=['GET', 'POST'])
def transfer(username):
    user = system.users.get(username)
    if request.method == 'POST':
        receiver_name = request.form['receiver']
        amount = float(request.form['amount'])
        receiver = system.users.get(receiver_name)
        if receiver and system.transfer_funds(user, receiver, amount):
            flash(f"Transferred {amount} USD to {receiver_name}.", "success")
        else:
            flash("Transfer failed. Check balance or receiver.", "danger")
        return redirect(url_for('user_menu', username=username))
    return render_template('transfer.html', user=user)

@app.route('/validate')
def validate():
    username = session.get('username')
    # Simple blockchain validation for demonstration
    message = "Blockchain is valid!"
    current = system.blockchain.head
    while getattr(current, "next", None):
        if current.current_hash != current.next.previous_hash:
            message = "Blockchain is invalid!"
            break
        current = current.next
    return render_template('validate.html', message=message, username= username)

@app.route('/history/<username>')
def history(username):
    user = system.users.get(username)
    if user:
        return render_template('history.html', transactions=user.transaction_history, user=user)
    return redirect(url_for('login'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    user = None
    balance = None
    username = session.get('username')
    if request.method == 'POST':
        username = request.form['user']
        user = system.users.get(username)
        if user:
            balance = user.balance
        else:
            flash("User not found.", "danger")
    return render_template('search.html', user=user, balance=balance, username=username)

@app.route('/convert/<username>', methods=['GET', 'POST'])
def convert(username):
    user = system.users.get(username)
    crypto_prices = {
        1: {"name": "Bitcoin", "price": 98000},
        2: {"name": "Ethereum", "price": 3900},
        3: {"name": "Solana", "price": 250},
        4: {"name": "Ripple", "price": 2.53},
        5: {"name": "Polkadot", "price": 12},
        6: {"name": "BNB Chain", "price": 602.5},
        7: {"name": "ShibaInu", "price": 0.00039},
        8: {"name": "THENA", "price": 2.53},
        9: {"name": "XION", "price": 0.000987},
        10: {"name": "Chainlink", "price": 12.6},
        11: {"name": "Polygon", "price": 87.99},
        12: {"name": "Stellar", "price": 1.293},
        13: {"name": "VeChain", "price": 0.0023},
        14: {"name": "Avalanche", "price": 5800},
        15: {"name": "TheSandbox", "price": 0.0099},
        16: {"name": "ThetaToken", "price": 7600},
        17: {"name": "Tezos", "price": 88.9}
    }

    if request.method == 'POST':
        amount = float(request.form['amount'])
        choice = int(request.form['crypto_choice'])
        converted, selected_currency = system.convert_currency(user, amount, choice)
        if converted is not None:
            flash(f"Converted {amount} USD to {converted:.5f} {selected_currency}.", "success")
        else:
            flash("Conversion failed. Check balance.", "danger")
        return redirect(url_for('user_menu', username=username))
    
    return render_template('convert.html', user=user, crypto_prices=crypto_prices)

@app.route('/logout')
def logout():
    flash("Logged out successfully!", "success")
    return redirect(url_for('home'))

@app.route('/view_blockchain')
def view_blockchain():
    username = session.get('username')  # Get username from session
    if not username:  # Redirect if username is not in session
        flash("Session expired. Please log in again.", "danger")
        return redirect(url_for('login'))
    chain = system.blockchain.display_chain()
    return render_template('blockchain.html', chain=chain, username=username)

if __name__ == '__main__':
    app.run(debug=True)
