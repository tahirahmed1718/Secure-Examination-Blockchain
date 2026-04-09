import os
import json
import requests
import io
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from web3 import Web3
from cryptography.fernet import Fernet
from dotenv import load_dotenv  # New Import

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION FROM ENV ---
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///exam_dapp.db')
app.config['UPLOAD_FOLDER'] = 'uploads'

# --- SECURITY CONFIGURATION ---
# Use the key from .env; ensure it is converted to bytes
fernet_key = os.getenv('FERNET_KEY').encode()
cipher_suite = Fernet(fernet_key)

# --- BLOCKCHAIN CONFIG ---
GANACHE_URL = os.getenv('GANACHE_URL', 'http://127.0.0.1:7545')
web3 = Web3(Web3.HTTPProvider(GANACHE_URL))

# Get Contract Address from .env
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')

# Load ABI
try:
    with open('contract_abi.json', 'r') as f:
        CONTRACT_ABI = json.load(f)
    contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
except Exception as e:
    print(f"CRITICAL ERROR: Could not load Contract. {e}")

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- DATABASE MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(200))
    name = db.Column(db.String(100))
    role = db.Column(db.String(20)) 
    wallet_address = db.Column(db.String(42))
    private_key = db.Column(db.String(100)) 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def upload_to_ipfs(file_data):
    try:
        files = {'file': file_data}
        # Use IPFS URL from env
        ipfs_url = os.getenv('IPFS_API_URL', 'http://127.0.0.1:5001')
        response = requests.post(f'{ipfs_url}/api/v0/add', files=files)
        return response.json()['Hash']
    except Exception as e:
        print(f"IPFS Error: {e}")
        return None

def get_from_ipfs(cid):
    try:
        params = {'arg': cid}
        ipfs_url = os.getenv('IPFS_API_URL', 'http://127.0.0.1:5001')
        response = requests.post(f'{ipfs_url}/api/v0/cat', params=params)
        return response.content
    except Exception as e:
        return None

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if User.query.filter_by(email=request.form['email']).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        # Note: In newer Werkzeug, method='sha256' is deprecated; it defaults to a secure hash.
        hashed_pw = generate_password_hash(request.form['password']) 
        new_user = User(
            email=request.form['email'], name=request.form['name'],
            password_hash=hashed_pw, role=request.form['role'],
            wallet_address=request.form['wallet_address'],
            private_key=request.form['private_key']
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            dashboards = {
                'coe': 'dashboard_coe',
                'teacher': 'dashboard_teacher',
                'superintendent': 'dashboard_super'
            }
            return redirect(url_for(dashboards.get(user.role, 'index')))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/teacher/upload', methods=['GET', 'POST'])
@login_required
def dashboard_teacher():
    if current_user.role != 'teacher': return "Unauthorized", 403
    
    if request.method == 'POST':
        file = request.files['paper']
        subject = request.form['subject']
        
        file_data = file.read()
        encrypted_data = cipher_suite.encrypt(file_data)
        ipfs_hash = upload_to_ipfs(encrypted_data)
        
        if ipfs_hash:
            try:
                chain_id = web3.eth.chain_id 
                nonce = web3.eth.get_transaction_count(current_user.wallet_address)
                
                tx = contract.functions.uploadPaper(subject, ipfs_hash).build_transaction({
                    'chainId': chain_id,
                    'gas': 2000000, 
                    'gasPrice': web3.to_wei('20', 'gwei'), 
                    'nonce': nonce
                })
                
                signed_tx = web3.eth.account.sign_transaction(tx, current_user.private_key)
                # Ensure the raw transaction is handled correctly across different Web3 versions
                raw_tx = signed_tx.rawTransaction if hasattr(signed_tx, 'rawTransaction') else signed_tx[0]
                
                tx_hash = web3.eth.send_raw_transaction(raw_tx)
                flash(f'Success! Transaction Hash: {web3.to_hex(tx_hash)}')
            except Exception as e:
                flash(f"Blockchain Error: {str(e)}")
        else:
            flash('IPFS Upload Failed')
    return render_template('teacher_dashboard.html')

@app.route('/coe/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard_coe():
    if current_user.role != 'coe': return "Unauthorized", 403

    try:
        total_papers = contract.functions.paperCount().call()
        papers = []
        for i in range(1, total_papers + 1):
            p = contract.functions.getPaper(i).call()
            papers.append({
                'id': p[0], 'subject': p[1], 'hash': p[2], 
                'teacher': p[3], 'super': p[4], 'finalized': p[5]
            })
    except Exception as e:
        papers = []
        print(f"Contract Call Error: {e}")

    if request.method == 'POST':
        paper_id = int(request.form['paper_id'])
        super_addr = request.form['superintendent_address']
        
        try:
            chain_id = web3.eth.chain_id
            nonce = web3.eth.get_transaction_count(current_user.wallet_address)
            
            tx = contract.functions.finalizePaper(paper_id, super_addr).build_transaction({
                'chainId': chain_id,
                'gas': 2000000, 
                'gasPrice': web3.to_wei('20', 'gwei'), 
                'nonce': nonce
            })
            
            signed_tx = web3.eth.account.sign_transaction(tx, current_user.private_key)
            raw_tx = signed_tx.rawTransaction if hasattr(signed_tx, 'rawTransaction') else signed_tx[0]

            web3.eth.send_raw_transaction(raw_tx)
            flash('Paper Finalized and Assigned!')
            return redirect(url_for('dashboard_coe'))
        except Exception as e:
            flash(f"Error finalizing: {str(e)}")

    return render_template('coe_dashboard.html', papers=papers)

@app.route('/super/dashboard')
@login_required
def dashboard_super():
    if current_user.role != 'superintendent': return "Unauthorized", 403

    total_papers = contract.functions.paperCount().call()
    my_papers = []
    for i in range(1, total_papers + 1):
        p = contract.functions.getPaper(i).call()
        if p[5] and p[4].lower() == current_user.wallet_address.lower():
            my_papers.append({'id': p[0], 'subject': p[1], 'hash': p[2]})
    return render_template('superintendent_dashboard.html', papers=my_papers)

@app.route('/download/<ipfs_hash>')
@login_required
def download_paper(ipfs_hash):
    if current_user.role not in ['superintendent', 'coe']: 
        return "Unauthorized", 403
        
    encrypted_data = get_from_ipfs(ipfs_hash)
    if encrypted_data:
        try:
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            return send_file(
                io.BytesIO(decrypted_data), 
                mimetype='application/pdf', 
                as_attachment=False,
                download_name=f'exam_paper_{ipfs_hash[:6]}.pdf'
            )
        except Exception as e:
            return f"Decryption Failed: {str(e)}", 403
    return "File not found on IPFS", 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)