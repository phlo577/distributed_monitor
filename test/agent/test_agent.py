import agent
import mock
import unittest
from datetime import datetime

# Tests for Agent module
class AgentTest(unittest.TestCase):

    @mock.patch('agent.PlainCredentials')
    @mock.patch('agent.ConnectionParameters')
    @mock.patch('agent.BlockingConnection')
    @mock.patch('agent.Metric')
    def setUp(self,
              mock_Metric,
              mock_BlockingConnection,
              mock_ConnectionParameters,
              mock_Credentials):
        super(AgentTest, self).setUp()
        mock_metric_labels = ['foo','cpu_percentage']
        mock_Cpu_Metric = mock.MagicMock()
        mock_Metric.create.side_effect = [None, mock_Cpu_Metric]
        self.agent = agent.Agent(mock.sentinel.user,
                                 mock.sentinel.password,
                                 mock.sentinel.ip,
                                 mock.sentinel.port,
                                 mock_metric_labels)

    @mock.patch('agent.PlainCredentials')
    @mock.patch('agent.ConnectionParameters')
    @mock.patch('agent.BlockingConnection')
    @mock.patch('agent.Metric.create')
    @mock.patch('agent.Agent.request_metric')
    def test_init(self,
                  mock_request_metric,
                  mock_metric_create,
                  mock_BlockingConnection,
                  mock_ConnectionParameters,
                  mock_Credentials):

        # Prepare test
        mock_credentials = mock_Credentials.return_value
        mock_connection = mock_BlockingConnection.return_value
        mock_channel = mock_connection.channel.return_value
        mock_parameters = mock_ConnectionParameters.return_value
        mock_metric_labels = ['foo','cpu_percentage']
        mock_Cpu_Metric = mock.MagicMock()
        mock_metric_create.side_effect = [None, mock_Cpu_Metric]
        expected_metric_list = [mock_Cpu_Metric]

        # Test sequence
        new_agent = agent.Agent(mock.sentinel.user,
                                mock.sentinel.password,
                                mock.sentinel.ip,
                                mock.sentinel.port,
                                mock_metric_labels)

        # Check results
        self.assertEqual(new_agent.metric_list, expected_metric_list)
        mock_Credentials.assert_called_once_with(mock.sentinel.user,
                                                 mock.sentinel.password)
        mock_ConnectionParameters.assert_called_once_with(mock.sentinel.ip,
                                                          mock.sentinel.port,
                                                          '/',
                                                          mock_credentials)
        mock_BlockingConnection.assert_called_once_with(mock_parameters)
        mock_channel.exchange_declare.assert_called_once_with(exchange='request',
                                                              type='fanout')
        mock_queue = mock_channel.queue_declare.return_value.method.queue
        mock_channel.queue_bind.assert_called_once_with(exchange='request',
                                                        queue=mock_queue)
        mock_channel.basic_consume.assert_called_once_with(mock_request_metric,
                                                           queue=mock_queue,
                                                           no_ack=True)
        mock_channel.queue_declare.assert_called_with(queue='reply')

    def test_request_metric(self):

        # Prepare test
        self.agent.processing_request = False
        timestamp = [datetime.now().year,
                     datetime.now().month,
                     datetime.now().day,
                     datetime.now().hour,
                     datetime.now().minute,
                     datetime.now().second,
                     0]
        mock_reply = str([timestamp,
                          self.agent.host,
                          self.agent.metric_list[0].get_type.return_value,
                          self.agent.metric_list[0].get_value.return_value])

        # Test sequence
        self.agent.request_metric(mock.sentinel.channel,
                                  mock.sentinel.method,
                                  mock.sentinel.properties,
                                  mock.sentinel.body)


        # Check results
        self.agent.channel.basic_publish.assert_called_once_with(exchange='',
                                                                 routing_key='reply',
                                                                 body=mock_reply)


    def test_start_consuming(self):
        # Prepare test
        mock_start_consuming = self.agent.channel.start_consuming

        # Test sequence
        self.agent.start_consuming()

        # Check results
        mock_start_consuming.assert_called_once_with()

    def test_stop_consuming(self):
        # Prepare test
        mock_stop_consuming = self.agent.channel.stop_consuming

        # Test sequence
        self.agent.stop_consuming()

        # Check results
        mock_stop_consuming.assert_called_once_with()

    def test_disconnect(self):
        # Prepare test
        mock_connection = self.agent.connection

        # Test sequence
        self.agent.disconnect()

        # Check results
        mock_connection.close.assert_called_once_with()
