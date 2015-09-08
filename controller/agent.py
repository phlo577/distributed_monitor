import ast
import datetime
import pika
import uuid

from config import MAX_RETRY_COUNTER_CFG, TIMEOUT_VAL_CFG
from database import CpuTable, MemoryTable, DiskTable, NetworkTable
from timeout_timer import TimeoutTimer

# Class that handles communication with the agents
class Agent:

    # Initialize object
    def __init__(self, label, channel, database):
        self.label = label
        self.channel = channel
        self.database = database
        self.session = database.get_session()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.correlation_id = 0
        self.timeout_timer = TimeoutTimer(TIMEOUT_VAL_CFG, self.on_timeout)
        self.retry_counter = 0
        self.timeout = False
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)
			
    # Publishes a new AMQP request to the agent if timeout is not set.
    def send_request(self, data_label):
        if not self.timeout:
            self.data_label = data_label
            self.response = None
            self.correlation_id = str(uuid.uuid4())
            self.props = pika.BasicProperties(reply_to = self.callback_queue,
                                              correlation_id = self.correlation_id
                                              )
            self.channel.basic_publish(exchange='',
	                               routing_key=self.label,
                                       properties = self.props,
	                               body=data_label)
            self.timeout_timer.start()
            print '[>] Request sent for ' + data_label + ' to ' + self.label +'.'
								   
    # Response callback of a AMQP request
    def on_response(self, channel, method_frame, header_frame, body):
        # Reser timeout parameters
        self.retry_counter = 0
        self.timeout = False
        self.timeout_timer.stop()

        # Check if response id is correlated with request id
        if self.correlation_id == header_frame.correlation_id:

            # Evaluate received string and store information in a list
            self.response = ast.literal_eval(body)
            
            if self.data_label == 'cpu_usage':
                # Response contains CPU usage information. Store it in database.
                cpu_usage = self.response[0]
                timestamp = datetime.datetime.now()
                new_cpu = CpuTable(timestamp = timestamp,
                                   agent=self.database.get_agent_entry(self.label),
                                   cpu_usage=cpu_usage)
                self.session.add(new_cpu)
                self.session.commit()
                print '[<] Received CPU usage from ' + self.label + '.'
                
            elif self.data_label == 'memory':
                # Response contains memory information. Store it in database.
                total_memory = self.response[0]
                available_memory = self.response[1]
                new_memory = MemoryTable(timestamp = datetime.datetime.now(),
                                         agent=self.database.get_agent_entry(self.label),
                                         total_memory=total_memory,
                                         available_memory=available_memory)
                self.session.add(new_memory)
                self.session.commit()
                print '[<] Received memory information from ' + self.label + '.'
                
            elif self.data_label == 'disk_iops':
                # Response contains disk iops information. Store it in database.
                bytes_read_sec = self.response[0]
                bytes_write_sec = self.response[1]
                new_disk = DiskTable(timestamp = datetime.datetime.now(),
                                     agent=self.database.get_agent_entry(self.label),
                                     bytes_read_sec = bytes_read_sec,
                                     bytes_write_sec = bytes_write_sec)
                self.session.add(new_disk)
                self.session.commit()
                print '[<] Received disk information from ' + self.label + '.'

            elif self.data_label == 'network_usage':
                # Response contains network usage information. Store it in database.
                bytes_sent_sec = self.response[0]
                bytes_received_sec = self.response[1]
                new_network = NetworkTable(timestamp = datetime.datetime.now(),
                                     agent=self.database.get_agent_entry(self.label),
                                     bytes_sent_sec = bytes_sent_sec,
                                     bytes_received_sec = bytes_received_sec)
                self.session.add(new_network)
                self.session.commit()
                print '[<] Received network usage from ' + self.label + '.'
                
            else:
                # Response label is wrong, do nothing
                pass


    # Timeout handler. Called when the timeout timer expires.
    # Allows requests to be retried a certain number of times before setting timeout.
    def on_timeout(self):
        self.retry_counter += 1
        if self.retry_counter >= MAX_RETRY_COUNTER_CFG:
            self.timeout = True
