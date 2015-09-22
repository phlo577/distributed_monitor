"""
<<<<<<< HEAD
    Main program entry
"""
from agent import Agent
from ConfigParser import ConfigParser
from time import sleep


def main():
    """Main program entry"""
    print 'Starting agent...'
    config = ConfigParser()
    config.read('config.ini')
    user = config.get('Connection', 'user')
    passw = config.get('Connection', 'passw')
    address = config.get('Connection', 'ip')
    port = config.get('Connection', 'port')
    metrics = config.get('Metrics', 'metrics').split()
    agent = Agent(user, passw, address, (int)(port), metrics)
    print 'Agent started. Waiting for requests...'
    try:
        agent.start_consuming()
    except KeyboardInterrupt:
        print 'Stopping agent'
        agent.stop_consuming()
        sleep(5)
        agent.disconnect()
        print 'Agent stopped'

if __name__ == "__main__":
    main()
=======
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
>>>>>>> origin/master
