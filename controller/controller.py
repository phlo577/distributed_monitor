"""
    Controller module
"""

from pika import PlainCredentials, ConnectionParameters, BlockingConnection
from logging import basicConfig, CRITICAL
from time import sleep
from ast import literal_eval
from database import Database
from datetime import datetime


class Controller(object):
    """Controller handler class"""

    def __init__(self, user, password, ip, port, database_url):
        """Connect to RabbitMQ server and to the database"""

        credentials = PlainCredentials(user, password)
        basicConfig(format='%(levelname)s:%(message)s',
                    level=CRITICAL)
        connection_parameters = ConnectionParameters(ip,
                                                     port,
                                                     '/',
                                                     credentials)
        self.connection = BlockingConnection(connection_parameters)
        self.channel = self.connection.channel()

        # Prepare request exchange
        self.channel.exchange_declare(exchange='request',
                                      type='fanout')

        self.requesting = False

        # Prepare reply queue
        self.channel.queue_declare(queue='reply')
        self.channel.basic_consume(self.receive_metric,
                                   queue='reply',
                                   no_ack=True)

        # Connect to database
        self.database = Database(database_url)

    def receive_metric(self, channel, method, properties, body):
        """Retrieve metric from queue and stores it into the database"""
        metric = literal_eval(body)
        timestamp = datetime(year=metric[0][0],
                             month=metric[0][1],
                             day=metric[0][2],
                             hour=metric[0][3],
                             minute=metric[0][4],
                             second=metric[0][5],
                             microsecond=metric[0][6])
        host = metric[1]
        metric_type = metric[2]
        value = metric[3]
        self.database.set_metric(metric=metric_type,
                                 host=host,
                                 timestamp=timestamp,
                                 value=value)
        print 'Retrieved ' + metric_type + ' from ' + host

    def start_requesting(self, period):
        """Start request loop"""
        message = 'request_metrics'
        self.requesting = True
        while self.requesting:
            self.channel.basic_publish(exchange='request',
                                       routing_key='',
                                       body=message)
            print 'Request sent'
            sleep((float)(period))

    def stop_requesting(self):
        """Stop request loop"""
        self.requesting = False

    def start_consuming(self):
        """Start consuming reply messages"""
        self.channel.start_consuming()

    def stop_consuming(self):
        """Stop consuming reply messages"""
        self.channel.stop_consuming()

    def disconnect(self):
        """Disconnect controller from RabbitMQ server and database"""
        self.connection.close()
        self.database.close_session()
