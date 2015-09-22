import metric
import windows_metric
import mock
import unittest

class WindowsMetricTest(unittest.TestCase):

    @mock.patch('windows_metric.wmi')
    @mock.patch('metric.sys')
    def test_available_memory(self,
                              mock_sys,
                              mock_wmi):

        # Prepare test
        mock_sys.platform = 'win32'
        metric_label = 'available_memory'
        mock_os1 = mock.MagicMock()
        mock_os2 = mock.MagicMock()
        mock_os1.FreeVirtualMemory = 20000000
        mock_os2.FreeVirtualMemory = 30000000
        wmi = mock_wmi.WMI.return_value
        wmi.Win32_OperatingSystem.return_value = [mock_os1, mock_os2]
        available_memory = mock_os1.FreeVirtualMemory + mock_os2.FreeVirtualMemory

        # Test sequence
        metric_object = metric.Metric.create(metric_label)
        metric_type = metric_object.get_type()
        metric_value = metric_object.get_value()

        # Check results
        self.assertEqual(metric_type, metric_label)
        self.assertEqual(metric_value, available_memory)

    @mock.patch('windows_metric.wmi')
    @mock.patch('metric.sys')
    def test_total_memory(self,
                          mock_sys,
                          mock_wmi):

        # Prepare test
        mock_sys.platform = 'win32'
        metric_label = 'total_memory'
        mock_os1 = mock.MagicMock()
        mock_os2 = mock.MagicMock()
        mock_os1.TotalVirtualMemorySize = 20000000
        mock_os2.TotalVirtualMemorySize = 30000000
        wmi = mock_wmi.WMI.return_value
        wmi.Win32_OperatingSystem.return_value = [mock_os1, mock_os2]
        total_memory = mock_os1.TotalVirtualMemorySize + mock_os2.TotalVirtualMemorySize

        # Test sequence
        metric_object = metric.Metric.create(metric_label)
        metric_type = metric_object.get_type()
        metric_value = metric_object.get_value()

        # Check results
        self.assertEqual(metric_type, metric_label)
        self.assertEqual(metric_value, total_memory)

    @mock.patch('windows_metric.wmi')
    @mock.patch('metric.sys')
    def test_cpu_percentage(self,
                            mock_sys,
                            mock_wmi):

        # Prepare test
        mock_sys.platform = 'win32'
        metric_label = 'cpu_percentage'
        mock_cpu1 = mock.MagicMock()
        mock_cpu2 = mock.MagicMock()
        mock_cpu1.LoadPercentage = 10
        mock_cpu2.LoadPercentage = 20
        wmi = mock_wmi.WMI.return_value
        wmi.Win32_Processor.return_value = [mock_cpu1, mock_cpu2]
        cpu_percentage = (mock_cpu1.LoadPercentage + mock_cpu2.LoadPercentage) / 2

        # Test sequence
        metric_object = metric.Metric.create(metric_label)
        metric_type = metric_object.get_type()
        metric_value = metric_object.get_value()

        # Check results
        self.assertEqual(metric_type, metric_label)
        self.assertEqual(metric_value, cpu_percentage)

    @mock.patch('windows_metric.wmi')
    @mock.patch('metric.sys')
    def test_network_bytes_sent(self,
                                mock_sys,
                                mock_wmi):

        # Prepare test
        mock_sys.platform = 'win32'
        metric_label = 'network_bytes_sent'
        mock_net1 = mock.MagicMock()
        mock_net2 = mock.MagicMock()
        mock_net1.BytesSentPerSec = 20000000
        mock_net2.BytesSentPerSec = 30000000
        wmi = mock_wmi.WMI.return_value
        wmi.Win32_PerfRawData_Tcpip_NetworkInterface.return_value = [mock_net1, mock_net2]
        bytes_sent = mock_net1.BytesSentPerSec + mock_net2.BytesSentPerSec

        # Test sequence
        metric_object = metric.Metric.create(metric_label)
        metric_type = metric_object.get_type()
        metric_value = metric_object.get_value()

        # Check results
        self.assertEqual(metric_type, metric_label)
        self.assertEqual(metric_value, bytes_sent)

    @mock.patch('windows_metric.wmi')
    @mock.patch('metric.sys')
    def test_network_bytes_received(self,
                                    mock_sys,
                                    mock_wmi):

        # Prepare test
        mock_sys.platform = 'win32'
        metric_label = 'network_bytes_received'
        mock_net1 = mock.MagicMock()
        mock_net2 = mock.MagicMock()
        mock_net1.BytesReceivedPerSec = 20000000
        mock_net2.BytesReceivedPerSec = 30000000
        wmi = mock_wmi.WMI.return_value
        wmi.Win32_PerfRawData_Tcpip_NetworkInterface.return_value = [mock_net1, mock_net2]
        bytes_received = mock_net1.BytesReceivedPerSec + mock_net2.BytesReceivedPerSec

        # Test sequence
        metric_object = metric.Metric.create(metric_label)
        metric_type = metric_object.get_type()
        metric_value = metric_object.get_value()

        # Check results
        self.assertEqual(metric_type, metric_label)
        self.assertEqual(metric_value, bytes_received)

    @mock.patch('windows_metric.wmi')
    @mock.patch('metric.sys')
    def test_disk_reads_sec(self,
                            mock_sys,
                            mock_wmi):

        # Prepare test
        mock_sys.platform = 'win32'
        metric_label = 'disk_reads_sec'
        mock_disk = mock.MagicMock()
        mock_disk.DiskReadBytesPerSec = 20000000
        wmi = mock_wmi.WMI.return_value
        wmi.Win32_PerfFormattedData_PerfDisk_LogicalDisk.return_value = [mock_disk]
        disk_reads_sec = mock_disk.DiskReadBytesPerSec

        # Test sequence
        metric_object = metric.Metric.create(metric_label)
        metric_type = metric_object.get_type()
        metric_value = metric_object.get_value()

        # Check results
        self.assertEqual(metric_type, metric_label)
        self.assertEqual(metric_value, disk_reads_sec)

    @mock.patch('windows_metric.wmi')
    @mock.patch('metric.sys')
    def test_disk_writes_sec(self,
                             mock_sys,
                             mock_wmi):

        # Prepare test
        mock_sys.platform = 'win32'
        metric_label = 'disk_writes_sec'
        mock_disk = mock.MagicMock()
        mock_disk.DiskWriteBytesPerSec = 20000000
        wmi = mock_wmi.WMI.return_value
        wmi.Win32_PerfFormattedData_PerfDisk_LogicalDisk.return_value = [mock_disk]
        disk_writes_sec = mock_disk.DiskWriteBytesPerSec

        # Test sequence
        metric_object = metric.Metric.create(metric_label)
        metric_type = metric_object.get_type()
        metric_value = metric_object.get_value()

        # Check results
        self.assertEqual(metric_type, metric_label)
        self.assertEqual(metric_value, disk_writes_sec)
