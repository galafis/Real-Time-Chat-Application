#!/usr/bin/env python3
"""
Real-Time Chat Application
Modern real-time chat application with WebSocket support, user authentication, and message history.
"""

from flask import Flask, render_template_string, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
import sqlite3
import hashlib
import uuid
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

class ChatApplication:
    """Real-time chat application with user management and message history."""
    
    def __init__(self, db_path="chat.db"):
        self.db_path = db_path
        self.init_database()
        self.active_users = {}
        self.rooms = {'general': {'name': 'General', 'users': []}}
    
    def init_database(self):
        """Initialize the chat database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                avatar_color TEXT DEFAULT '#667eea',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Chat rooms table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_name TEXT UNIQUE NOT NULL,
                room_description TEXT,
                created_by INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_private BOOLEAN DEFAULT 0,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_name TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create default room
        cursor.execute("""
            INSERT OR IGNORE INTO chat_rooms (room_name, room_description, created_by)
            VALUES ('general', 'General discussion room', 1)
        """)
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password for secure storage."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, email, password):
        """Create a new user account."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            avatar_colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#43e97b']
            avatar_color = avatar_colors[hash(username) % len(avatar_colors)]
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, avatar_color)
                VALUES (?, ?, ?, ?)
            """, (username, email, password_hash, avatar_color))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
            
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    def authenticate_user(self, username, password):
        """Authenticate user login."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute("""
            SELECT id, username, email, avatar_color
            FROM users
            WHERE username = ? AND password_hash = ?
        """, (username, password_hash))
        
        user = cursor.fetchone()
        
        if user:
            # Update last seen
            cursor.execute("""
                UPDATE users SET last_seen = CURRENT_TIMESTAMP WHERE id = ?
            """, (user[0],))
            conn.commit()
        
        conn.close()
        return user
    
    def get_user_by_id(self, user_id):
        """Get user information by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, avatar_color
            FROM users
            WHERE id = ?
        """, (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        return user
    
    def save_message(self, room_name, user_id, username, message, message_type='text'):
        """Save message to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO messages (room_name, user_id, username, message, message_type)
            VALUES (?, ?, ?, ?, ?)
        """, (room_name, user_id, username, message, message_type))
        
        conn.commit()
        message_id = cursor.lastrowid
        conn.close()
        return message_id
    
    def get_room_messages(self, room_name, limit=50):
        """Get recent messages for a room."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT m.username, m.message, m.message_type, m.timestamp, u.avatar_color
            FROM messages m
            JOIN users u ON m.user_id = u.id
            WHERE m.room_name = ?
            ORDER BY m.timestamp DESC
            LIMIT ?
        """, (room_name, limit))
        
        messages = cursor.fetchall()
        conn.close()
        
        # Reverse to show oldest first
        return list(reversed(messages))
    
    def get_available_rooms(self):
        """Get list of available chat rooms."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT room_name, room_description, created_at
            FROM chat_rooms
            WHERE is_private = 0
            ORDER BY created_at
        """)
        
        rooms = cursor.fetchall()
        conn.close()
        return rooms

chat_app = ChatApplication()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Real-Time Chat</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .chat-container {
            width: 90%;
            max-width: 1200px;
            height: 80vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            display: flex;
            overflow: hidden;
        }
        
        .sidebar {
            width: 300px;
            background: #f8f9fa;
            border-right: 1px solid #e0e0e0;
            display: flex;
            flex-direction: column;
        }
        
        .sidebar-header {
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .user-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            margin-right: 10px;
        }
        
        .rooms-list {
            flex: 1;
            padding: 20px;
        }
        
        .room-item {
            padding: 12px;
            border-radius: 8px;
            cursor: pointer;
            margin-bottom: 5px;
            transition: background 0.3s ease;
        }
        
        .room-item:hover {
            background: #e9ecef;
        }
        
        .room-item.active {
            background: #667eea;
            color: white;
        }
        
        .online-users {
            padding: 20px;
            border-top: 1px solid #e0e0e0;
        }
        
        .online-user {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .online-indicator {
            width: 8px;
            height: 8px;
            background: #27ae60;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .chat-main {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .chat-header {
            padding: 20px;
            background: white;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
        }
        
        .message-avatar {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            margin-right: 10px;
            font-size: 14px;
        }
        
        .message-content {
            flex: 1;
        }
        
        .message-header {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        
        .message-username {
            font-weight: 600;
            margin-right: 10px;
        }
        
        .message-time {
            font-size: 12px;
            color: #666;
        }
        
        .message-text {
            background: white;
            padding: 10px 15px;
            border-radius: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .message.own .message-content {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
        }
        
        .message.own .message-text {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .chat-input {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        
        .input-container {
            display: flex;
            gap: 10px;
        }
        
        .message-input {
            flex: 1;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            outline: none;
            font-size: 14px;
        }
        
        .message-input:focus {
            border-color: #667eea;
        }
        
        .send-button {
            padding: 12px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
        }
        
        .send-button:hover {
            opacity: 0.9;
        }
        
        .typing-indicator {
            padding: 10px 20px;
            font-style: italic;
            color: #666;
            font-size: 14px;
        }
        
        .system-message {
            text-align: center;
            color: #666;
            font-style: italic;
            margin: 10px 0;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="sidebar">
            <div class="sidebar-header">
                <div class="user-info">
                    <div class="user-avatar" style="background-color: {{ user_avatar_color }}">
                        {{ user_username[0].upper() }}
                    </div>
                    <div>
                        <div style="font-weight: 600;">{{ user_username }}</div>
                        <div style="font-size: 12px; opacity: 0.8;">Online</div>
                    </div>
                </div>
                <div style="font-size: 14px; opacity: 0.9;">Real-Time Chat</div>
            </div>
            
            <div class="rooms-list">
                <h4 style="margin-bottom: 15px; color: #333;">Rooms</h4>
                <div class="room-item active" data-room="general">
                    <div style="font-weight: 600;"># General</div>
                    <div style="font-size: 12px; color: #666;">General discussion</div>
                </div>
            </div>
            
            <div class="online-users">
                <h4 style="margin-bottom: 15px; color: #333;">Online Users</h4>
                <div id="onlineUsersList">
                    <!-- Online users will be populated here -->
                </div>
            </div>
        </div>
        
        <div class="chat-main">
            <div class="chat-header">
                <div>
                    <h3 id="currentRoomName"># General</h3>
                    <div style="font-size: 14px; color: #666;" id="roomDescription">General discussion room</div>
                </div>
                <div style="font-size: 14px; color: #666;">
                    <span id="onlineCount">1</span> online
                </div>
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <!-- Messages will be populated here -->
            </div>
            
            <div class="typing-indicator" id="typingIndicator" style="display: none;">
                <!-- Typing indicator will appear here -->
            </div>
            
            <div class="chat-input">
                <div class="input-container">
                    <input type="text" class="message-input" id="messageInput" placeholder="Type a message..." maxlength="500">
                    <button class="send-button" onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        const currentUser = {
            username: '{{ user_username }}',
            avatar_color: '{{ user_avatar_color }}'
        };
        let currentRoom = 'general';
        let typingTimer;
        let isTyping = false;
        
        // Join default room
        socket.emit('join_room', {room: currentRoom});
        
        // Socket event listeners
        socket.on('connect', function() {
            console.log('Connected to server');
        });
        
        socket.on('message', function(data) {
            displayMessage(data);
        });
        
        socket.on('user_joined', function(data) {
            displaySystemMessage(data.username + ' joined the room');
            updateOnlineUsers(data.users);
        });
        
        socket.on('user_left', function(data) {
            displaySystemMessage(data.username + ' left the room');
            updateOnlineUsers(data.users);
        });
        
        socket.on('typing', function(data) {
            showTypingIndicator(data.username);
        });
        
        socket.on('stop_typing', function(data) {
            hideTypingIndicator();
        });
        
        socket.on('room_users', function(data) {
            updateOnlineUsers(data.users);
        });
        
        // Message input handling
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            } else {
                handleTyping();
            }
        });
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (message) {
                socket.emit('send_message', {
                    room: currentRoom,
                    message: message
                });
                
                input.value = '';
                stopTyping();
            }
        }
        
        function displayMessage(data) {
            const messagesContainer = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message' + (data.username === currentUser.username ? ' own' : '');
            
            const timestamp = new Date(data.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            
            messageDiv.innerHTML = `
                <div class="message-avatar" style="background-color: ${data.avatar_color}">
                    ${data.username[0].toUpperCase()}
                </div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="message-username">${data.username}</span>
                        <span class="message-time">${timestamp}</span>
                    </div>
                    <div class="message-text">${escapeHtml(data.message)}</div>
                </div>
            `;
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function displaySystemMessage(message) {
            const messagesContainer = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'system-message';
            messageDiv.textContent = message;
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function updateOnlineUsers(users) {
            const onlineUsersList = document.getElementById('onlineUsersList');
            const onlineCount = document.getElementById('onlineCount');
            
            onlineUsersList.innerHTML = '';
            onlineCount.textContent = users.length;
            
            users.forEach(user => {
                const userDiv = document.createElement('div');
                userDiv.className = 'online-user';
                userDiv.innerHTML = `
                    <div class="online-indicator"></div>
                    <span>${user.username}</span>
                `;
                onlineUsersList.appendChild(userDiv);
            });
        }
        
        function handleTyping() {
            if (!isTyping) {
                isTyping = true;
                socket.emit('typing', {room: currentRoom});
            }
            
            clearTimeout(typingTimer);
            typingTimer = setTimeout(() => {
                stopTyping();
            }, 1000);
        }
        
        function stopTyping() {
            if (isTyping) {
                isTyping = false;
                socket.emit('stop_typing', {room: currentRoom});
            }
        }
        
        function showTypingIndicator(username) {
            const indicator = document.getElementById('typingIndicator');
            indicator.textContent = username + ' is typing...';
            indicator.style.display = 'block';
        }
        
        function hideTypingIndicator() {
            const indicator = document.getElementById('typingIndicator');
            indicator.style.display = 'none';
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Load message history
        fetch(`/api/messages/${currentRoom}`)
            .then(response => response.json())
            .then(messages => {
                messages.forEach(msg => {
                    displayMessage({
                        username: msg[0],
                        message: msg[1],
                        timestamp: msg[3],
                        avatar_color: msg[4]
                    });
                });
            });
    </script>
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .login-header h1 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .login-header p {
            color: #666;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s ease;
        }
        
        .form-group input:focus {
            border-color: #667eea;
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 15px;
        }
        
        .btn:hover {
            opacity: 0.9;
        }
        
        .toggle-form {
            text-align: center;
            color: #666;
        }
        
        .toggle-form a {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .success {
            background: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>💬 Real-Time Chat</h1>
            <p>Connect and chat with others in real-time</p>
        </div>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        {% if success %}
        <div class="success">{{ success }}</div>
        {% endif %}
        
        <form method="POST" action="{{ url_for('login') }}">
            <input type="hidden" name="action" value="login">
            
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="btn">Sign In</button>
        </form>
        
        <div class="toggle-form">
            Don't have an account? <a href="#" onclick="showRegister()">Sign up</a>
        </div>
        
        <form method="POST" action="{{ url_for('login') }}" id="registerForm" style="display: none;">
            <input type="hidden" name="action" value="register">
            
            <div class="form-group">
                <label for="reg_username">Username</label>
                <input type="text" id="reg_username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="reg_email">Email</label>
                <input type="email" id="reg_email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="reg_password">Password</label>
                <input type="password" id="reg_password" name="password" required>
            </div>
            
            <button type="submit" class="btn">Sign Up</button>
            
            <div class="toggle-form">
                Already have an account? <a href="#" onclick="showLogin()">Sign in</a>
            </div>
        </form>
    </div>
    
    <script>
        function showRegister() {
            document.querySelector('form:first-of-type').style.display = 'none';
            document.querySelector('.toggle-form:first-of-type').style.display = 'none';
            document.getElementById('registerForm').style.display = 'block';
        }
        
        function showLogin() {
            document.querySelector('form:first-of-type').style.display = 'block';
            document.querySelector('.toggle-form:first-of-type').style.display = 'block';
            document.getElementById('registerForm').style.display = 'none';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main chat page."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = chat_app.get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    return render_template_string(HTML_TEMPLATE, 
                                user_username=user[1], 
                                user_avatar_color=user[3])

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login and registration page."""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'login':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = chat_app.authenticate_user(username, password)
            if user:
                session['user_id'] = user[0]
                session['username'] = user[1]
                return redirect(url_for('index'))
            else:
                return render_template_string(LOGIN_TEMPLATE, error="Invalid username or password")
        
        elif action == 'register':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            user_id = chat_app.create_user(username, email, password)
            if user_id:
                return render_template_string(LOGIN_TEMPLATE, success="Account created successfully! Please sign in.")
            else:
                return render_template_string(LOGIN_TEMPLATE, error="Username or email already exists")
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    """Logout user."""
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/messages/<room_name>')
def get_messages(room_name):
    """Get message history for a room."""
    if 'user_id' not in session:
        return {'error': 'Not authenticated'}, 401
    
    messages = chat_app.get_room_messages(room_name)
    return messages

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    """Handle user connection."""
    if 'user_id' not in session:
        return False
    
    user = chat_app.get_user_by_id(session['user_id'])
    if user:
        chat_app.active_users[request.sid] = {
            'user_id': user[0],
            'username': user[1],
            'avatar_color': user[3]
        }

@socketio.on('disconnect')
def handle_disconnect():
    """Handle user disconnection."""
    if request.sid in chat_app.active_users:
        user_data = chat_app.active_users[request.sid]
        
        # Leave all rooms
        for room in rooms():
            if room != request.sid:
                leave_room(room)
                
                # Get remaining users in room
                room_users = [chat_app.active_users[sid] for sid in chat_app.active_users 
                             if sid in socketio.server.manager.rooms.get('/', {}).get(room, set())]
                
                emit('user_left', {
                    'username': user_data['username'],
                    'users': room_users
                }, room=room)
        
        del chat_app.active_users[request.sid]

@socketio.on('join_room')
def handle_join_room(data):
    """Handle user joining a room."""
    if request.sid not in chat_app.active_users:
        return
    
    room = data['room']
    user_data = chat_app.active_users[request.sid]
    
    join_room(room)
    
    # Get all users in room
    room_users = [chat_app.active_users[sid] for sid in chat_app.active_users 
                 if sid in socketio.server.manager.rooms.get('/', {}).get(room, set())]
    
    # Notify others
    emit('user_joined', {
        'username': user_data['username'],
        'users': room_users
    }, room=room, include_self=False)
    
    # Send room users to the joining user
    emit('room_users', {'users': room_users})

@socketio.on('send_message')
def handle_send_message(data):
    """Handle sending a message."""
    if request.sid not in chat_app.active_users:
        return
    
    user_data = chat_app.active_users[request.sid]
    room = data['room']
    message = data['message']
    
    # Save message to database
    chat_app.save_message(room, user_data['user_id'], user_data['username'], message)
    
    # Broadcast message to room
    emit('message', {
        'username': user_data['username'],
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'avatar_color': user_data['avatar_color']
    }, room=room)

@socketio.on('typing')
def handle_typing(data):
    """Handle typing indicator."""
    if request.sid not in chat_app.active_users:
        return
    
    user_data = chat_app.active_users[request.sid]
    room = data['room']
    
    emit('typing', {
        'username': user_data['username']
    }, room=room, include_self=False)

@socketio.on('stop_typing')
def handle_stop_typing(data):
    """Handle stop typing indicator."""
    if request.sid not in chat_app.active_users:
        return
    
    room = data['room']
    emit('stop_typing', {}, room=room, include_self=False)

def main():
    """Main execution function."""
    print("Real-Time Chat Application")
    print("=" * 30)
    
    print("Initializing chat system...")
    print("Setting up database...")
    print("Starting web server...")
    print("Open http://localhost:5000 in your browser")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()

