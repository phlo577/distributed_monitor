"""
    Agent module
"""

from pika import PlainCredentials, ConnectionParameters, BlockingConnection
from logging import basicConfig, CRITICAL
from datetime import datetime
from metric import Metric
from socket import gethostname


class Agent(object):
    """Agent class"""
    def __init__(self, user, password, ip, port, metric_labels):
        """Generate metrics list, connect to RabbitMQ server"""
        # Add valid metrics to list
        self.metric_list = []
        for label in metric_labels:
            metric = Metric.create(label)
            if metric is not None:
                self.metric_list.append(metric)

        # Connect to RabbitMQ server
        credentials = PlainCredentials(user,
                                       password)
        basicConfig(format='%(levelname)s:%(message)s',
                    level=CRITICAL)
        connection_parameters = ConnectionParameters(ip,
                                                     port,
                                                     '/',
                                                     credentials)
        self.connection = BlockingConnection(connection_parameters)
        self.channel = self.connection.channel()
        self.host = gethostname()

        # Prepare request queue
        self.processing_request = False
        self.channel.exchange_declare(exchange='request',
                                      type='fanout')
        result = self.channel.queue_declare(exclusive=True)
        request_queue = result.method.queue
        self.channel.queue_bind(exchange='request',
                                queue=request_queue)
        self.channel.basic_consume(self.request_metric,
                                   queue=request_queue,
                                   no_ack=True)

        # Prepare reply queue
        self.channel.queue_declare(queue='reply')

    def request_metric(self, channel, method, properties, body):
        """Request local metrics and send them to the controller"""
        print 'Request received'
        if not self.processing_request:
            self.processing_request = True
            for metric in self.metric_list:
                # Get current time, host and metric
                metric_type = metric.get_type()
                value = metric.get_value()

                timestamp = [datetime.now().year,
                             datetime.now().month,
                             datetime.now().day,
                             datetime.now().hour,
                             datetime.now().minute,
                             datetime.now().second,
                             0]

                # Send reply to controller
                reply = str([timestamp, self.host, metric_type, value])
                self.channel.basic_publish(exchange='',
                                           routing_key='reply',
                                           body=reply)
                print 'Metric ' + metric_type + ' sent'
            self.processing_request = False

    def start_consuming(self):
        """Start consuming request messages"""
        self.channel.start_consuming()

    def stop_consuming(self):
        """Stop consuming request messages"""
        self.channel.stop_consuming()

    def disconnect(self):
        """Disconnect controller from RabbitMQ server"""
        self.connection.close()
