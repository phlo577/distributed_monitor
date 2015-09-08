import pika
import logging

class Connection:

    def __init__(self, user, password, ip, port):
        self.credentials = pika.PlainCredentials(user, password)
        self.ip = ip
        self.port = port
    
    def connect(self):
        # Connect to AMQP server
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.CRITICAL)
        connection_parameters = pika.ConnectionParameters(self.ip,
                                                          self.port,
                                                          '/',
                                                          self.credentials)
        self.connection = pika.BlockingConnection(connection_parameters)
        self.channel = self.connection.channel()

    def disconnect(self):
        self.connection.close()

    def get_channel(self):
        return self.channel
