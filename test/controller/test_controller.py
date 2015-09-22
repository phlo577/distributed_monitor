import controller
import mock
import unittest

# Tests for Controller module
class ControllerTest(unittest.TestCase):

    @mock.patch('controller.PlainCredentials')
    @mock.patch('controller.ConnectionParameters')
    @mock.patch('controller.BlockingConnection')
    @mock.patch('controller.Database')
    @mock.patch('controller.Controller.receive_metric')
    def setUp(self,
              mock_receive_metric,
              mock_Database,
              mock_BlockingConnection,
              mock_ConnectionParameters,
              mock_Credentials):
        super(ControllerTest, self).setUp()
        self.controller = controller.Controller(mock.sentinel.user,
                                                mock.sentinel.password,
                                                mock.sentinel.ip,
                                                mock.sentinel.port,
                                                mock.sentinel.url)

    @mock.patch('controller.PlainCredentials')
    @mock.patch('controller.ConnectionParameters')
    @mock.patch('controller.BlockingConnection')
    @mock.patch('controller.Database')
    @mock.patch('controller.Controller.receive_metric')
    def test_init(self,
                  mock_receive_metric,
                  mock_Database,
                  mock_BlockingConnection,
                  mock_ConnectionParameters,
                  mock_Credentials):

        # Prepare test
        mock_credentials = mock_Credentials.return_value
        mock_connection = mock_BlockingConnection.return_value
        mock_channel = mock_connection.channel.return_value
        mock_parameters = mock_ConnectionParameters.return_value
        mock_database = mock_Database.return_value
        # Test sequence
        control = controller.Controller(mock.sentinel.user,
                                        mock.sentinel.password,
                                        mock.sentinel.ip,
                                        mock.sentinel.port,
                                        mock.sentinel.url)

        # Check results
        mock_Credentials.assert_called_once_with(mock.sentinel.user,
                                                 mock.sentinel.password)
        mock_ConnectionParameters.assert_called_once_with(mock.sentinel.ip,
                                                          mock.sentinel.port,
                                                          '/',
                                                          mock_credentials)
        mock_BlockingConnection.assert_called_once_with(mock_parameters)
        mock_channel.queue_declare.assert_called_once_with(queue='reply')
        mock_channel.basic_consume.assert_called_once_with(mock_receive_metric,
                                                           queue='reply',
                                                           no_ack=True)
        mock_Database.assert_called_once_with(mock.sentinel.url)
        self.assertEqual(control.connection, mock_connection)
        self.assertEqual(control.requesting, False)
        self.assertEqual(control.database, mock_database)

    @mock.patch('controller.literal_eval')
    @mock.patch('controller.datetime')
    def test_receive_metric(self,
                            mock_datetime,
                            mock_literal_eval):
        # Prepare test
        mock_set_metric = self.controller.database.set_metric
        mock_timestamp = mock_datetime.return_value
        mock_metric = mock_literal_eval.return_value

        # Test sequence
        self.controller.receive_metric(mock.sentinel.channel,
                                       mock.sentinel.method,
                                       mock.sentinel.properties,
                                       mock.sentinel.body)

        # Check results
        mock_literal_eval.assert_called_once_with(mock.sentinel.body)
        mock_datetime.assert_called_once_with(year=mock_metric[0][0],
                                              month=mock_metric[0][1],
                                              day=mock_metric[0][2],
                                              hour=mock_metric[0][3],
                                              minute=mock_metric[0][4],
                                              second=mock_metric[0][5],
                                              microsecond=mock_metric[0][6])
        mock_set_metric.assert_called_once_with(metric=mock_metric[2],
                                                host=mock_metric[1],
                                                timestamp=mock_timestamp,
                                                value=mock_metric[3])

    @mock.patch('controller.sleep')
    def test_start_requesting(self,
                              mock_sleep):
        # Prepare test
        def stop_request(arg):
            self.controller.requesting = False
        mock_sleep.side_effect = stop_request
        mock_basic_publish = self.controller.channel.basic_publish
        self.controller.requesting = False

        # Test sequence
        self.controller.start_requesting(5)

        # Check results
        mock_basic_publish.assert_called_once_with(exchange='request',
                                                   routing_key='',
                                                   body='request_metrics')
        mock_sleep.assert_called_once_with(5)

    def test_stop_requesting(self):
        # Prepare test
        self.controller.requesting = True

        # Test sequence
        self.controller.stop_requesting()

        # Check results
        self.assertEqual(self.controller.requesting, False)

    def test_start_consuming(self):
        # Prepare test
        mock_start_consuming = self.controller.channel.start_consuming

        # Test sequence
        self.controller.start_consuming()

        # Check results
        mock_start_consuming.assert_called_once_with()

    def test_stop_consuming(self):
        # Prepare test
        mock_stop_consuming = self.controller.channel.stop_consuming

        # Test sequence
        self.controller.stop_consuming()

        # Check results
        mock_stop_consuming.assert_called_once_with()

    def test_disconnect(self):
        # Prepare test
        mock_connection = self.controller.connection
        mock_database = self.controller.database

        # Test sequence
        self.controller.disconnect()

        # Check results
        mock_connection.close.assert_called_once_with()
        mock_database.close_session.assert_called_once_with()
