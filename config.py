# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 20

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "p4ssw0rd"

# Secret key for signing cookies
SECRET_KEY = "p4ssw0rd"

SITENAME = "Netrobots API"

# The address of the ZMQ socket to use for sending commands to robots.
SERVER_SOCKET = "tcp://0.0.0.0:5555"
