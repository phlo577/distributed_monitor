import mock
import unittest
import sys
import pika
import logging
import time
from config import OS, LABEL, USER_CFG, PASW_CFG, IP_CFG, PORT_CFG
from main import main, on_request, get_windows_statistics, get_linux_statistics

if OS == 'Windows':

    import wmi
    
    # Test functionality for Windows
    class WindowsTest(unittest.TestCase):

        
        # Test handling of a new request from the controller
        @mock.patch('main.get_windows_statistics')
        @mock.patch('pika.BlockingConnection')
        @mock.patch('pika.BasicProperties')
        @mock.patch('pika.spec.BasicProperties')
        @mock.patch('pika.frame.Method')
        def test_on_request(self,
                            mock_method_frame,
                            mock_header_frame,
                            mock_proprieties,
                            mock_BlockingConnection,
                            mock_get_windows_statistics):
            # Prepare test
            mock_connection = mock_BlockingConnection.return_value
            mock_channel = mock_connection.channel.return_value
            mock_proprieties.correlation_id = mock_header_frame.correlation_id
            mock_response = mock_get_windows_statistics.return_value
            data_label = 'cpu_usage'

            # Test sequence
            on_request(mock_channel, mock_method_frame, mock_header_frame, data_label)

            # Check result
            mock_get_windows_statistics.assert_called_once_with(data_label)
            mock_channel.basic_publish.assert_called_once_with(exchange='',
                                                               routing_key=mock_header_frame.reply_to,
                                                               properties = mock_proprieties.return_value,
                                                               body=str(mock_response))
            

        # Test that cpu usage is correctly gathered from WMI
        @mock.patch('wmi.WMI')
        def test_get_windows_cpu(self,
                                 mock_WMI):
            # Prepare test
            c = mock_WMI.return_value
            mock_cpu1 = mock.MagicMock()
            mock_cpu2 = mock.MagicMock()
            mock_cpu1.LoadPercentage = 1
            mock_cpu2.LoadPercentage = 2
            c.Win32_Processor.return_value = [mock_cpu1, mock_cpu2]
            
            # Test sequence
            cpu_usage = get_windows_statistics('cpu_usage')
            
            # Check result
            self.assertEqual(cpu_usage,[str(mock_cpu1.LoadPercentage),str(mock_cpu2.LoadPercentage)])


        # Test that memory information is correctly gathered from WMI
        @mock.patch('wmi.WMI')
        def test_get_windows_memory(self,
                                    mock_WMI):
            # Prepare test
            c = mock_WMI.return_value
            mock_os1 = mock.MagicMock()
            mock_os2 = mock.MagicMock()
            mock_os1.TotalVirtualMemorySize = 20000000
            mock_os1.FreeVirtualMemory = 10000000
            mock_os2.TotalVirtualMemorySize = 30000000
            mock_os2.FreeVirtualMemory = 20000000
            c.Win32_OperatingSystem.return_value = [mock_os1, mock_os2]
            total_memory = mock_os1.TotalVirtualMemorySize + mock_os2.TotalVirtualMemorySize
            free_memory = mock_os1.FreeVirtualMemory + mock_os2.FreeVirtualMemory
            
            # Test sequence
            memory = get_windows_statistics('memory')
            
            # Check result
            self.assertEqual(memory,[(str)(total_memory), (str)(free_memory)])


        # Test that disk iops is correctly gathered from WMI
        @mock.patch('wmi.WMI')
        def test_get_windows_disk_iops(self,
                                       mock_WMI):
            # Prepare test
            c = mock_WMI.return_value
            mock_disk = mock.MagicMock()
            mock_disk.DiskReadBytesPerSec = 1000
            mock_disk.DiskWriteBytesPerSec = 2000
            c.Win32_PerfFormattedData_PerfDisk_LogicalDisk.return_value = [mock_disk, mock_disk]
            
            # Test sequence
            disk_iops = get_windows_statistics('disk_iops')
            
            # Check result
            self.assertEqual(disk_iops,[(str)(mock_disk.DiskReadBytesPerSec), (str)(mock_disk.DiskWriteBytesPerSec)])


        # Test that network usage is correctly gathered from WMI
        @mock.patch('wmi.WMI')
        def test_get_windows_network(self,
                                     mock_WMI):
            # Prepare test
            c = mock_WMI.return_value
            mock_network1 = mock.MagicMock()
            mock_network1.BytesSentPerSec = 1000
            mock_network1.BytesReceivedPerSec = 2000
            mock_network2 = mock.MagicMock()        
            mock_network2.BytesSentPerSec = 3000
            mock_network2.BytesReceivedPerSec = 2000
            bytes_sent = (int)(mock_network1.BytesSentPerSec) + (int)(mock_network2.BytesSentPerSec)
            bytes_received =  (int)(mock_network1.BytesReceivedPerSec) + (int)(mock_network2.BytesReceivedPerSec)
            c.Win32_PerfRawData_Tcpip_NetworkInterface.return_value = [mock_network1, mock_network2]
            
            # Test sequence
            network_usage = get_windows_statistics('network_usage')
            
            # Check result
            self.assertEqual(network_usage,[(str)(bytes_sent), (str)(bytes_received)])

else:

    import psutil    
    from main import old_time, old_read_bytes, old_write_bytes
    
    # Test functionality for Linux
    class LinuxTest(unittest.TestCase):

        
        # Test handling of a new request from the controller
        @mock.patch('main.get_linux_statistics')
        @mock.patch('pika.BlockingConnection')
        @mock.patch('pika.BasicProperties')
        @mock.patch('pika.spec.BasicProperties')
        @mock.patch('pika.frame.Method')
        def test_on_request(self,
                            mock_method_frame,
                            mock_header_frame,
                            mock_proprieties,
                            mock_BlockingConnection,
                            mock_get_linux_statistics):
            # Prepare test
            mock_connection = mock_BlockingConnection.return_value
            mock_channel = mock_connection.channel.return_value
            mock_proprieties.correlation_id = mock_header_frame.correlation_id
            mock_response = mock_get_linux_statistics.return_value
            data_label = 'cpu_usage'

            # Test sequence
            on_request(mock_channel, mock_method_frame, mock_header_frame, data_label)

            # Check result
            mock_get_linux_statistics.assert_called_once_with(data_label)
            mock_channel.basic_publish.assert_called_once_with(exchange='',
                                                               routing_key=mock_header_frame.reply_to,
                                                               properties = mock_proprieties.return_value,
                                                               body=str(mock_response))
            

        # Test that cpu usage is correctly gathered from psutil
        @mock.patch('psutil.cpu_percent')
        def test_get_linux_cpu(self,
                               mock_cpu_percent):
            # Prepare test
            cpu1_percent = 1
            cpu2_percent = 2
            mock_cpu_percent.return_value = [cpu1_percent,cpu2_percent]
            
            # Test sequence
            cpu_usage = get_linux_statistics('cpu_usage')
            
            # Check result
            self.assertEqual(cpu_usage, [str(cpu1_percent), str(cpu2_percent)])


        # Test that memory information is correctly gathered from psutil
        @mock.patch('psutil.virtual_memory')
        def test_get_linux_memory(self,
                                  mock_memory):
            # Prepare test
            mock_memory.return_value.total = 2000000
            mock_memory.return_value.available = 1000000
            
            # Test sequence
            memory = get_linux_statistics('memory')
            
            # Check result
            self.assertEqual(memory, [str(mock_memory.return_value.total), str(mock_memory.return_value.available)])


        # Test that disk iops is correctly gathered from psutil
        @mock.patch('psutil.disk_io_counters')
        @mock.patch('time.time')
        def test_get_linux_disk_iops(self,
                                     mock_time,
                                     mock_disk_iops):
            # Prepare test
            global old_time
            global old_read_bytes
            global old_write_bytes            
            mock_time.return_value = 2.00 + old_time
            mock_disk_iops.return_value.read_bytes = 1000 + old_read_bytes
            mock_disk_iops.return_value.write_bytes = 1000 + old_write_bytes

            read_bytes_sec = (int)((mock_disk_iops.return_value.read_bytes - old_read_bytes)/(mock_time.return_value - old_time))
            write_bytes_sec = (int)((mock_disk_iops.return_value.write_bytes - old_write_bytes)/(mock_time.return_value - old_time))
            
            # Test sequence
            disk = get_linux_statistics('disk_iops')
            
            # Check result
            self.assertEqual(disk, [(str)(read_bytes_sec), (str)(write_bytes_sec)])


        # Test that network usage is correctly gathered from psutil
        @mock.patch('psutil.net_io_counters')
        def test_get_linux_network(self,
                                   mock_network):
            # Prepare test
            mock_network.return_value.bytes_sent = 2000000
            mock_network.return_value.bytes_recv = 1000000
            
            # Test sequence
            network = get_linux_statistics('network_usage')
            
            # Check result
            self.assertEqual(network, [str(mock_network.return_value.bytes_sent), str(mock_network.return_value.bytes_recv)])


# Tests for main program
class MainTest(unittest.TestCase):

    # Test main routine
    @mock.patch('pika.BlockingConnection')
    @mock.patch('pika.ConnectionParameters')
    @mock.patch('pika.PlainCredentials')
    def test_main(self,
                  mock_Credentials,
                  mock_ConnectionParameters,
                  mock_BlockingConnection):
        # Prepare test
        mock_credentials = mock_Credentials.return_value
        mock_connection = mock_BlockingConnection.return_value
        mock_channel = mock_connection.channel.return_value
        
        # Test sequence
        main()

        # Check results
        mock_ConnectionParameters.assert_called_once_with(IP_CFG,
                                                          PORT_CFG,
                                                          '/',
                                                          mock_credentials)
        mock_BlockingConnection.assert_called_once_with(
            mock_ConnectionParameters(IP_CFG,
                                      PORT_CFG,
                                      '/',
                                      mock_credentials
                                      ))
        mock_channel.queue_declare.assert_called_once_with(LABEL)
        mock_channel.basic_qos.assert_called_once_with(prefetch_count=1)
        mock_channel.basic_consume.assert_called_once_with(on_request, queue=LABEL)



if __name__ == '__main__':
    unittest.main()
