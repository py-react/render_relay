import os
import socket
import struct
import json
from render_relay.utils import load_settings
from render_relay.utils.constant import DEFAULT_SOCK_PATH
import logging

logger = logging.getLogger(__name__)

class BridgeOperation:
    def __init__(self,debug: bool = False):
        self.settings = load_settings()
        self.bridge_path: str = self.settings.get("CUSTOM_BRDIGE_PATH",DEFAULT_SOCK_PATH)
        self.debug = debug
        self.test_connection()

    def get_client(self):
        logger.info("Getting Client")
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            return client
        except Exception as e:
            logger.error(f"Connetion Failed: {str(e)} ",)
            raise Exception(str(e))

    def test_connection(self):
        try:
            client = self.get_client()
            logger.info("Calling connect")
            client.connect(self.bridge_path)
            try:
                data = self.send_and_receive(json.dumps({"type":"health_check","data":""}))
                if data == "200":
                    logger.info(f"Connected, Status: {data}")        
                    return client
                logger.error(f"Connection failed: {data}")        
            except Exception as e:
                logger.error(f"Health check failed: {str(e)}")
                raise Exception(f"Health check failed: {str(e)}")
        except Exception as e:
            logger.error(f"Connetion Failed: {str(e)} ",)
            raise Exception(f"Connetion Failed: {str(e)} ")

    def send_all(self, data, client:socket.socket):
        """Ensure all data is sent."""
        try:
            client.connect(self.bridge_path)
            logger.info(f"Client Connected")
            length = len(data)
            try:
                length_prefix = struct.pack('!I', length)  # Pack length as 4-byte unsigned int
                message = length_prefix + data
                client.sendall(message)
                logger.info(f"Message sent")
            except (BrokenPipeError, ConnectionResetError, OSError) as e:
                raise Exception(f"Failed to send data over socket: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error during sending data: {e}")

    def send_and_receive(self, message)->str:
        try:
            received_data = b''
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                self.send_all(message.encode("utf-8"),client)
                # Receive the length of the message first (4 bytes, big-endian)
                length_data = client.recv(4)
                if len(length_data) < 4:
                    logger.error(f"Did not receive the complete length header => {len(length_data)} expected 4")
                    raise ValueError("Did not receive the complete length header")
                logger.info(f"Getting Message length")
                message_length = 1024
                try:
                    message_length = struct.unpack('>I', length_data)[0]
                    logger.info(f"Message length : {message_length}")
                except Exception as e:
                    logger.info(f"Exception: {str(e)}" )
                    raise Exception(str(e))
                # Receive the message data
                while len(received_data) < message_length:
                    data = client.recv(min(1024,message_length))
                    if not data:
                        break
                    received_data += data
                    logger.info(f"Chunk : {data}")
                decoded_recived_data = received_data.decode("utf-8")
                logger.info(f"Recived Data: {decoded_recived_data}")
            return received_data.decode('utf-8')
        except FileNotFoundError:
            raise Exception(f"Socket file not found: {self.bridge_path}")
        except ConnectionRefusedError:
            raise Exception(f"Connection refused: is the Node.js server running?")
        except Exception as e:
            raise Exception(f"Unexpected error during socket communication: {e}")


