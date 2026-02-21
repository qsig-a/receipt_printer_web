import sys
from unittest.mock import MagicMock

# Mock external dependencies before importing app
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

import os
os.environ['ACCESS_PASSWORD'] = 'password'
os.environ['WEBHOOK_URL'] = 'http://localhost:9999' # Mock webhook

from app import app, db

# Mock the Firestore client instance
db_mock = MagicMock()
# Mock collection().document().set()
db_mock.collection.return_value.document.return_value.set = MagicMock()
# Mock log_to_firestore to avoid using the real db object if it leaked
import app as app_module
app_module.db = db_mock

# Mock requests to avoid actual network calls
import requests
app_module.requests = MagicMock()
app_module.requests.post.return_value.status_code = 200

if __name__ == '__main__':
    print("Starting mock app on port 5000...")
    app.run(port=5000)
