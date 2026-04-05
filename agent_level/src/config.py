import os

TRANSPORT_URL = os.getenv("TRANSPORT_URL", "http://localhost:8001")
SEGMENT_SIZE = int(os.getenv("SEGMENT_SIZE", "200"))
MOVE_DELAY = float(os.getenv("MOVE_DELAY", "0.5"))
ERROR_PROBABILITY = float(os.getenv("ERROR_PROBABILITY", "0.01"))