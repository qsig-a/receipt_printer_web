from flask import Flask, render_template_string, request, redirect, url_for, Response
import requests
import os
import io
import csv
import time
import threading
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
from google.cloud import firestore
from signalwire.rest import Client as signalwire_client

app = Flask(__name__)

# --- Configuration via Environment Variables ---
# Usage: os.environ.get('VARIABLE_NAME', 'DEFAULT_VALUE')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://hooks.nabucasa.com/default_placeholder')
ACCESS_PASSWORD = os.environ.get('ACCESS_PASSWORD', 'password')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'adminpassword')

# SignalWire Configuration
SIGNALWIRE_PROJECT_ID = os.environ.get('SIGNALWIRE_PROJECT_ID')
SIGNALWIRE_TOKEN = os.environ.get('SIGNALWIRE_TOKEN')
SIGNALWIRE_SPACE_URL = os.environ.get('SIGNALWIRE_SPACE_URL')
SIGNALWIRE_FROM_NUMBER = os.environ.get('SIGNALWIRE_FROM_NUMBER')

# Slack Configuration
SLACK_MESSAGE_LIMIT = int(os.environ.get('SLACK_MESSAGE_LIMIT', 5))
SLACK_LIMIT_PERIOD = int(os.environ.get('SLACK_LIMIT_PERIOD', 1)) # minutes

# Log History Limit
LOG_HISTORY_LIMIT = int(os.environ.get('LOG_HISTORY_LIMIT', 50))

# SMS Whitelist
SMS_WHITELIST_COLLECTION = "sms_whitelist"

def get_env_int(key, default):
    try:
        val = os.environ.get(key)
        if val is None:
            return default
        return int(val)
    except ValueError:
        return default

# SMS Whitelist Cache
WHITELIST_CACHE = OrderedDict()
WHITELIST_CACHE_LOCK = threading.Lock()
WHITELIST_TTL = get_env_int('SMS_WHITELIST_TTL', 300)  # Default 5 minutes
WHITELIST_CACHE_LIMIT = get_env_int('SMS_WHITELIST_LIMIT', 1000)

# Convert the string env variable to an integer if it exists
char_limit_raw = os.environ.get('CHARACTER_LIMIT')
CHARACTER_LIMIT = int(char_limit_raw) if char_limit_raw and char_limit_raw.isdigit() else None

# Initialize Firestore Client
# Note: On Cloud Run, it automatically uses the project ID from the environment
db = firestore.Client(database="receipt-printer")
COLLECTION_NAME = "print_history"
SMS_PENDING_COLLECTION = "sms_pending"
SLACK_RATELIMITS_COLLECTION = "slack_ratelimits"

# Thread Pool Executor for background tasks
executor = ThreadPoolExecutor(max_workers=10)

# Global SignalWire Client (Lazy Initialization)
_signalwire_client = None

def get_signalwire_client():
    global _signalwire_client
    if _signalwire_client:
        return _signalwire_client

    if not all([SIGNALWIRE_PROJECT_ID, SIGNALWIRE_TOKEN, SIGNALWIRE_SPACE_URL, SIGNALWIRE_FROM_NUMBER]):
        print("SignalWire configuration missing, skipping SMS.")
        return None

    try:
        _signalwire_client = signalwire_client(SIGNALWIRE_PROJECT_ID, SIGNALWIRE_TOKEN, signalwire_space_url=SIGNALWIRE_SPACE_URL)
        return _signalwire_client
    except Exception as e:
        print(f"Failed to initialize SignalWire client: {e}")
        return None

# --- UI Templates (Unchanged) ---
SHARED_CSS = """
:root {
    --primary: #6366f1; --primary-hover: #4f46e5; --danger: #ef4444;
    --danger-hover: #dc2626; --bg: #f8fafc; --card-bg: rgba(255, 255, 255, 0.9);
}
body {
    font-family: 'Inter', -apple-system, sans-serif;
    background: linear-gradient(135deg, #e0e7ff 0%, #f8fafc 100%);
    display: flex; align-items: center; justify-content: center;
    min-height: 100vh; margin: 0; color: #1e293b;
}
.container {
    background: var(--card-bg); backdrop-filter: blur(10px);
    padding: 2.5rem; border-radius: 20px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    width: 100%; max-width: 600px; text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.5);
}
input, textarea {
    width: 100%; padding: 0.75rem 1rem; border: 2px solid #e2e8f0;
    border-radius: 12px; font-size: 1rem; margin-top: 0.5rem;
    box-sizing: border-box; background: white; font-family: inherit;
}
textarea { resize: vertical; min-height: 120px; font-family: monospace; width: 48ch; max-width: 100%; box-sizing: content-box; margin-left: auto; margin-right: auto; display: block; }
.btn {
    width: 100%; padding: 0.75rem; color: white; border: none; 
    border-radius: 12px; font-weight: 600; cursor: pointer; 
    transition: all 0.2s; margin-top: 1rem; text-decoration: none; display: block;
    box-sizing: border-box;
}
.btn-primary { background-color: var(--primary); }
.btn-primary:hover { background-color: var(--primary-hover); }
.btn-danger { background-color: var(--danger); margin-top: 2rem; }
.btn-secondary { background-color: #64748b; }
.status-box {
    margin-top: 1.5rem; padding: 1rem; background: #fff;
    border-left: 4px solid #10b981; border-radius: 4px;
    font-family: 'Courier New', monospace; font-size: 0.85rem; text-align: left;
}
.status-error { border-left-color: #ef4444; }
.history-table {
    width: 100%; border-collapse: collapse; margin-top: 1.5rem;
    background: white; border-radius: 12px; overflow: hidden; font-size: 0.85rem;
}
.history-table th { background: #f1f5f9; padding: 12px; text-align: left; color: #475569; }
.history-table td { padding: 12px; border-bottom: 1px solid #f1f5f9; text-align: left; vertical-align: top; }
.badge { padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; }
.badge-ok { background: #dcfce7; color: #166534; }
.badge-err { background: #fee2e2; color: #991b1b; }
.admin-actions { display: flex; gap: 10px; margin-top: 2rem; }
.admin-actions form { flex: 1; }
"""

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head><style>""" + SHARED_CSS + """</style></head>
<body>
    <div class="container">
        <h2>Remote Print 📠</h2>
        <p>Send a message directly to my desk.</p>
        <form method="POST">
            <input type="password" name="password" placeholder="Keycode" required>
            <textarea name="message" placeholder="Type your message here..." required></textarea>
            <button type="submit" class="btn btn-primary">Print Now</button>
        </form>
        {% if status %}<div class="status-box {% if '❌' in status %}status-error{% endif %}">{{ status }}</div>{% endif %}
    </div>
</body>
</html>
"""

HISTORY_HTML = """
<!DOCTYPE html>
<html>
<head><style>""" + SHARED_CSS + """</style></head>
<body>
    <div class="container" style="max-width: 900px;">
        <h2>Print History 📜</h2>
        {% if not authorized %}
        <form method="POST">
            <input type="password" name="admin_password" placeholder="Admin Password" required>
            <button type="submit" class="btn btn-primary">View Logs</button>
        </form>
        {% else %}
        <div style="max-height: 500px; overflow-y: auto;">
            <table class="history-table">
                <thead>
                    <tr><th>Time</th><th>Source</th><th>Status</th><th>Message</th></tr>
                </thead>
                <tbody>
                    {% for log in logs %}
                    <tr>
                        <td style="white-space: nowrap; color: #64748b;">{{ log.time }}</td>
                        <td style="font-family: monospace;">{{ log.source }}</td>
                        <td><span class="badge {% if log.status == 'SUCCESS' %}badge-ok{% else %}badge-err{% endif %}">{{ log.status }}</span></td>
                        <td style="word-break: break-all;">{{ log.msg }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <div class="admin-actions">
            <form method="POST" action="/download-csv">
                <input type="hidden" name="admin_password" value="{{ admin_pw }}">
                <button type="submit" class="btn btn-primary">Download CSV</button>
            </form>
            <form method="POST" action="/clear-history" onsubmit="return confirm('Permanently delete all logs?');">
                <input type="hidden" name="admin_password" value="{{ admin_pw }}">
                <button type="submit" class="btn btn-danger" style="margin-top:0;">Clear History</button>
            </form>
        </div>
        <a href="/" class="btn btn-secondary">Back to Portal</a>
        {% endif %}
    </div>
</body>
</html>
"""

# --- Helper Functions ---

def send_sms(to_number, body):
    """Sends an SMS using SignalWire."""
    client = get_signalwire_client()
    if not client:
        return

    try:
        message = client.messages.create(
            from_=SIGNALWIRE_FROM_NUMBER,
            to=to_number,
            body=body
        )
        print(f"SMS sent to {to_number}: {message.sid}")
    except Exception as e:
        print(f"Failed to send SMS: {e}")

def log_to_firestore(source, status, message):
    """Saves a log entry to Google Firestore."""
    doc_ref = db.collection(COLLECTION_NAME).document()
    doc_ref.set({
        'timestamp': firestore.SERVER_TIMESTAMP,
        'source': source,
        'status': status,
        'message': message
    })

def get_logs_from_firestore():
    """Fetches and formats logs from Firestore, newest first."""
    logs = []
    docs = db.collection(COLLECTION_NAME).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(LOG_HISTORY_LIMIT).stream()
    for doc in docs:
        data = doc.to_dict()
        # Handle cases where SERVER_TIMESTAMP hasn't resolved yet
        ts = data.get('timestamp')
        time_str = ts.strftime('%Y-%m-%d %H:%M:%S') if ts else "Just now"
        # Backwards compatibility: check 'source', then 'ip'
        source = data.get('source') or data.get('ip', 'Unknown')
        logs.append({
            'time': time_str,
            'source': source,
            'status': data.get('status', 'ERROR'),
            'msg': data.get('message', '')
        })
    return logs

def check_slack_rate_limit(user_id):
    """Checks if a Slack user is rate limited."""
    doc_ref = db.collection(SLACK_RATELIMITS_COLLECTION).document(user_id)
    doc = doc_ref.get()

    # Use timezone aware now
    now = datetime.now(timezone.utc)

    if not doc.exists:
        doc_ref.set({
            'timestamps': [now],
            'blocked_until': None
        })
        return True, None

    data = doc.to_dict()
    blocked_until = data.get('blocked_until')

    if blocked_until:
        # Ensure blocked_until is timezone aware
        if blocked_until.tzinfo is None:
             blocked_until = blocked_until.replace(tzinfo=timezone.utc)

        if blocked_until > now:
            remaining = (blocked_until - now).total_seconds() / 60
            return False, f"You are temporarily blocked for {int(remaining)+1} more minutes."
        else:
            blocked_until = None

    timestamps = data.get('timestamps', [])
    # Filter timestamps
    cutoff = now - timedelta(minutes=SLACK_LIMIT_PERIOD)

    recent_timestamps = []
    for t in timestamps:
        # Ensure timestamp is timezone aware
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        if t > cutoff:
            recent_timestamps.append(t)

    if len(recent_timestamps) >= SLACK_MESSAGE_LIMIT:
        block_duration = timedelta(minutes=SLACK_LIMIT_PERIOD)
        new_blocked_until = now + block_duration
        doc_ref.set({
            'timestamps': recent_timestamps,
            'blocked_until': new_blocked_until
        })
        return False, f"Rate limit exceeded. You are blocked for {SLACK_LIMIT_PERIOD} minutes."

    recent_timestamps.append(now)
    doc_ref.set({
        'timestamps': recent_timestamps,
        'blocked_until': None
    })
    return True, None

def process_slack_async(response_url, webhook_url, text, source):
    """Async handler for Slack commands to prevent timeouts."""
    try:
        r = requests.post(webhook_url, json={"message": text}, timeout=10)
        if r.status_code == 200:
            log_to_firestore(source, "SUCCESS", text)
            msg = "✅ Message sent to printer!"
        else:
            log_to_firestore(source, f"HA_ERR_{r.status_code}", text)
            msg = f"❌ Error: {r.status_code}"
    except Exception as e:
        log_to_firestore(source, "CONN_FAIL", str(e))
        msg = "❌ Connection failed"

    if response_url:
        try:
            requests.post(response_url, json={"text": msg, "response_type": "ephemeral"})
        except Exception as e:
            print(f"Failed to send delayed Slack response: {e}")

def process_sms_async(from_number, webhook_url, body):
    """Async handler for SMS to prevent timeouts."""
    try:
        r = requests.post(webhook_url, json={"message": body}, timeout=10)
        if r.status_code == 200:
            log_to_firestore(from_number, "SUCCESS", body)
            send_sms(from_number, "✅ Message printed successfully!")
        else:
            log_to_firestore(from_number, f"HA_ERR_{r.status_code}", body)
            send_sms(from_number, f"❌ Error printing message. HA replied: {r.status_code}")
    except Exception as e:
        log_to_firestore(from_number, "CONN_FAIL", f"{body} (Error: {str(e)})")
        send_sms(from_number, "❌ Connection error while printing.")

def is_number_whitelisted(number):
    """
    Checks if a number is whitelisted using a thread-safe in-memory cache
    to reduce Firestore reads. Cache expires after 5 minutes.
    """
    current_time = time.time()

    # Check cache first
    with WHITELIST_CACHE_LOCK:
        if number in WHITELIST_CACHE:
            timestamp, is_whitelisted = WHITELIST_CACHE[number]

            # Refresh LRU position
            WHITELIST_CACHE.move_to_end(number)

            if current_time - timestamp < WHITELIST_TTL:
                return is_whitelisted
            else:
                # Expired
                del WHITELIST_CACHE[number]

    # Not in cache or expired, check Firestore
    is_whitelisted = False
    try:
        docs = db.collection(SMS_WHITELIST_COLLECTION).where('number', '==', number).limit(1).stream()
        for _ in docs:
            is_whitelisted = True
            break
    except Exception as e:
        print(f"Error checking whitelist: {e}")
        # On error, default to False but don't cache potentially transient errors?
        # Or cache False to prevent hammering DB?
        # Let's not cache errors for now, or maybe cache for a short time.
        # But for simplicity, we'll just return False and not update cache if exception occurs.
        return False

    # Update cache
    with WHITELIST_CACHE_LOCK:
        # If cache is full, remove oldest item (LRU)
        if len(WHITELIST_CACHE) >= WHITELIST_CACHE_LIMIT and len(WHITELIST_CACHE) > 0:
            # last=False removes the first (oldest) item
            WHITELIST_CACHE.popitem(last=False)

        WHITELIST_CACHE[number] = (current_time, is_whitelisted)
        # Ensure it's at the end (newest)
        WHITELIST_CACHE.move_to_end(number)

    return is_whitelisted

# --- Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    status = None
    if request.method == 'POST':
        user_pw = request.form.get('password')
        msg = request.form.get('message')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)

        if user_pw != ACCESS_PASSWORD:
            status = "❌ ACCESS_DENIED: Invalid Keycode"
            log_to_firestore(ip, "DENIED", msg)
        elif CHARACTER_LIMIT and msg and len(msg) > CHARACTER_LIMIT:
            status = f"❌ LIMIT_EXCEEDED: Message too long ({len(msg)}/{CHARACTER_LIMIT})"
            log_to_firestore(ip, "LIMIT_EXCEEDED", msg)
        else:
            try:
                r = requests.post(WEBHOOK_URL, json={"message": msg}, timeout=10)
                if r.status_code == 200:
                    status = "✅ PRINT_SUCCESS: Message queued"
                    log_to_firestore(ip, "SUCCESS", msg)
                else:
                    status = f"❌ HA_ERR: {r.status_code}"
                    log_to_firestore(ip, f"HA_ERR_{r.status_code}", msg)
            except Exception as e:
                status = f"❌ CONN_FAIL: {str(e)}"
                log_to_firestore(ip, "CONN_FAIL", str(e))
    return render_template_string(INDEX_HTML, status=status)

@app.route('/history', methods=['GET', 'POST'])
def history():
    authorized = False
    logs = []
    admin_pw = request.form.get('admin_password', '')
    if request.method == 'POST' and admin_pw == ADMIN_PASSWORD:
        authorized = True
        logs = get_logs_from_firestore()
    elif request.method == 'POST':
        return "Unauthorized", 401
    return render_template_string(HISTORY_HTML, authorized=authorized, logs=logs, admin_pw=admin_pw)

@app.route('/download-csv', methods=['POST'])
def download_csv():
    if request.form.get('admin_password') == ADMIN_PASSWORD:
        logs = get_logs_from_firestore()
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(['Time', 'Source', 'Status', 'Message'])
        for log in logs:
            cw.writerow([log['time'], log['source'], log['status'], log['msg']])
        return Response(si.getvalue(), mimetype="text/csv", 
                        headers={"Content-disposition": "attachment; filename=history.csv"})
    return "Unauthorized", 401

@app.route('/clear-history', methods=['POST'])
def clear_history():
    if request.form.get('admin_password') == ADMIN_PASSWORD:
        # Delete documents in batches (standard Firestore pattern)
        docs = db.collection(COLLECTION_NAME).limit(500).select([]).stream()
        batch = db.batch()
        for doc in docs:
            batch.delete(doc.reference)
        batch.commit()
        return redirect(url_for('index'))
    return "Unauthorized", 401

@app.route('/sms', methods=['POST'])
def sms_webhook():
    """Handles incoming SMS from SignalWire."""
    # SignalWire sends form data with From, Body, etc.
    from_number = request.form.get('From')
    body = request.form.get('Body', '').strip()

    if not from_number:
        return "Missing From number", 400

    # Check whitelist
    is_whitelisted = is_number_whitelisted(from_number)

    if is_whitelisted:
        if CHARACTER_LIMIT and len(body) > CHARACTER_LIMIT:
            send_sms(from_number, f"❌ Message too long. Limit is {CHARACTER_LIMIT} characters.")
            return "OK"

        executor.submit(process_sms_async, from_number, WEBHOOK_URL, body)
        return "OK"

    # Check if there is a pending message for this number
    pending_ref = db.collection(SMS_PENDING_COLLECTION).document(from_number)
    pending_doc = pending_ref.get()

    if not pending_doc.exists:
        if CHARACTER_LIMIT and len(body) > CHARACTER_LIMIT:
            send_sms(from_number, f"❌ Message too long. Limit is {CHARACTER_LIMIT} characters.")
            return "OK"

        # New message -> Store it and ask for password
        pending_ref.set({
            'message': body,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        send_sms(from_number, "Please reply with the access password to print your message.")
        return "OK" # SignalWire expects 200 OK
    else:
        # Pending message exists -> This is the password attempt
        pending_data = pending_doc.to_dict()
        original_message = pending_data.get('message')

        if body == ACCESS_PASSWORD:
            # Password correct
            # Use ThreadPoolExecutor to prevent unbounded thread creation and improve stability under load
            future = executor.submit(process_sms_async, from_number, WEBHOOK_URL, original_message)

            # Clear pending status
            pending_ref.delete()
        else:
            # Password incorrect
            log_to_firestore(from_number, "DENIED", original_message)
            send_sms(from_number, "❌ Invalid password. Access denied.")
            # Delete pending state to enforce "Send Message -> Send Password" flow.
            # If they fail password, they start over. This prevents stuck states.
            pending_ref.delete()

    return "OK"

@app.route('/slack', methods=['POST'])
def slack_webhook():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    # URL Verification for Slack Event Subscription
    if data.get('type') == 'url_verification':
        return {"challenge": data.get('challenge')}

    user_id = None
    user_name = None
    text = None

    # Check for Event API structure
    if 'event' in data:
        event = data['event']
        if event.get('type') == 'message' and not event.get('bot_id'):
            user_id = event.get('user')
            text = event.get('text')
            user_name = user_id
    # Check for Slash Command structure
    else:
        user_id = data.get('user_id')
        user_name = data.get('user_name')
        text = data.get('text')

    if not user_id or not text:
        return "Ignored", 200

    allowed, message = check_slack_rate_limit(user_id)
    if not allowed:
        return {"response_type": "ephemeral", "text": f"❌ {message}"}

    source = f"Slack: {user_name or user_id}"

    response_url = data.get('response_url')
    executor.submit(process_slack_async, response_url, WEBHOOK_URL, text, source)
    return {"response_type": "ephemeral", "text": "⏳ Sending to printer..."}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
