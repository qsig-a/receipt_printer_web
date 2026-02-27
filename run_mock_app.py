import sys
from unittest.mock import MagicMock

# Mock dependencies
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

from app import app

if __name__ == '__main__':
    # Disable debug reloader to avoid messing up the mocks in the subprocess
    app.run(host='0.0.0.0', port=5000, debug=False)
