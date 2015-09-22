import main
import mock
import unittest

# Tests for Main module
class MainTest(unittest.TestCase):

    @mock.patch('main.ConfigParser')
    @mock.patch('main.Agent')
    @mock.patch('main.sleep')
    
    def test_main(self,
                  mock_sleep,
                  mock_Agent,
                  mock_ConfigParser):
        
        # Prepare test
        mock_config = mock_ConfigParser.return_value
        mock_user = mock_config.get.return_value
        mock_passw = mock_config.get.return_value
        mock_address = mock_config.get.return_value
        mock_port = mock_config.get.return_value
        mock_metrics = mock_config.get.return_value.split.return_value
        mock_agent = mock_Agent.return_value
        mock_agent.start_consuming.side_effect = KeyboardInterrupt
        
        # Test sequence
        main.main()

        # Check results
        mock_ConfigParser.assert_called_once_with()
        mock_config.read.assert_called_once_with('config.ini')
        mock_Agent.assert_called_once_with(mock_user,
                                           mock_passw,
                                           mock_address,
                                           (int)(mock_port),
                                           mock_metrics)
        mock_agent.start_consuming.assert_called_once_with()
        mock_agent.stop_consuming.assert_called_once_with()
        mock_agent.disconnect.assert_called_once_with()
        
