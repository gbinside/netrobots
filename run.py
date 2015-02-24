# Run a test server.
from app import app
app.run(host='192.168.1.105', port=8080, debug=True)
