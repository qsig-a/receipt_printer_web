from unittest.mock import MagicMock
import sys
from datetime import datetime

# Mock Firestore before importing app
# We need to mock google.cloud.firestore specifically because app.py imports it
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

# Now we can import app
from app import app, db

if __name__ == '__main__':
    # Configure the mock db
    mock_doc = MagicMock()
    mock_doc.to_dict.return_value = {
        'timestamp': datetime.now(),
        'source': 'Test Source',
        'status': 'SUCCESS',
        'message': 'Test Message'
    }
    # Mock the chain: db.collection().order_by().limit().stream()
    db.collection.return_value.order_by.return_value.limit.return_value.stream.return_value = [mock_doc]

    # Also mock document().set() etc. if needed, but for history view (GET) the above is enough

    print("Starting mock server on port 5001...")
    # Using 5001 to avoid conflict if 5000 is zombie
    app.run(port=5001)
