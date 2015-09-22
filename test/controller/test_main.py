import main
import mock
import unittest

# Tests for Main module
class MainTest(unittest.TestCase):

    @mock.patch('main.ConfigParser')
    @mock.patch('main.Controller')
    @mock.patch('main.Thread')
    @mock.patch('main.sleep')
    
    def test_main(self,
                  mock_sleep,
                  mock_Thread,
                  mock_Controller,
                  mock_ConfigParser):
        
        # Prepare test
        mock_config = mock_ConfigParser.return_value
        mock_user = mock_config.get.return_value
        mock_passw = mock_config.get.return_value
        mock_address = mock_config.get.return_value
        mock_port = mock_config.get.return_value
        mock_request_period = mock_config.get.return_value
        mock_url = mock_config.get.return_value
        
        mock_controller = mock_Controller.return_value
        
        mock_reply_thread = mock_Thread.return_value
        mock_request_thread = mock_Thread.return_value
        
        mock_sleep.side_effect = KeyboardInterrupt
        
        # Test sequence
        main.main()

        # Check results
        mock_ConfigParser.assert_called_once_with()
        mock_config.read.assert_called_once_with('config.ini')
        mock_Controller.assert_called_once_with(mock_user,
                                                mock_passw,
                                                mock_address,
                                                mock_port,
                                                mock_url)
        mock_Thread.assert_called_once_with(target=mock_controller.start_consuming)
        mock_Thread.assert_called_once_with(target=mock_controller.start_requesting,
                                            args=(request_period))


