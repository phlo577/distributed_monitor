import metric
import linux_metric
import mock
import unittest

class LinuxMetricTest(unittest.TestCase):

    @mock.patch('linux_metric.psutil')
    @mock.patch('metric.sys')
    def test_available_memory(self,
                              mock_sys,
                              mock_psutil):

        # Prepare test
        mock_sys.platform = 'linux2'
        metric_label = 'available_memory'
        mock_psutil.virtual_memory.return_value.available = 1024000 #in bytes
        available_memory = 1000 #in kilobytes

        # Test sequence
        metric_object = metric.Metric.create(metric_label)
        metric_type = metric_object.get_type()
        metric_value = metric_object.get_value()

        # Check results
        self.assertEqual(metric_type, metric_label)
        self.assertEqual(metric_value, available_memory)

    @mock.patch('linux_metric.psutil')
    @mock.patch('metric.sys')
    def test_total_memory(self,
                          mock_sys,
                          mock_psutil):

        # Prepare test
        mock_sys.platform = 'linux2'
        metric_label = 'total_memory'
        mock_psutil.virtual_memory.return_value.total = 1024000 #in bytes
        total_memory = 1000 #in kilobytes

        # Test sequence
        metric_object = metric.Metric.create(metric_label)
        metric_type = metric_object.get_type()
        metric_value = metric_object.get_value()

        # Check results
        self.assertEqual(metric_type, metric_label)
        self.assertEqual(metric_value, total_memory)

    @mock.patch('linux_metric.psutil')
    @mock.patch('metric.sys')
    def test_cpu_percentage(self,
                            mock_sys,
                            mock_psutil):

        # Prepare test
        mock_sys.platform = 'linux2'
        metric_label = 'cpu_percentage'
        mock_psutil.cpu_percent.return_value = 23
        cpu_percentage = 23

        # Test sequence
        metric_object = metric.Metric.create(metric_label)
        metric_type = metric_object.get_type()
        metric_value = metric_object.get_value()

        # Check results
        self.assertEqual(metric_type, metric_label)
        self.assertEqual(metric_value, cpu_percentage)

    @mock.patch('linux_metric.psutil')
    @mock.patch('metric.sys')
    def test_network_bytes_sent(self,
                                mock_sys,
                                mock_psutil):

        # Prepare test
        mock_sys.platform = 'linux2'
        metric_label = 'network_bytes_sent'
        mock_psutil.net_io_counters.return_value.bytes_sent = 1000000
        bytes_sent = mock_psutil.net_io_counters.return_value.bytes_sent

        # Test sequence
        metric_object = metric.Metric.create(metric_label)
        metric_type = metric_object.get_type()
        metric_value = metric_object.get_value()

        # Check results
        self.assertEqual(metric_type, metric_label)
        self.assertEqual(metric_value, bytes_sent)

    @mock.patch('linux_metric.psutil')
    @mock.patch('metric.sys')
    def test_network_bytes_received(self,
                                    mock_sys,
                                    mock_psutil):

        # Prepare test
        mock_sys.platform = 'linux2'
        metric_label = 'network_bytes_received'
        mock_psutil.net_io_counters.return_value.bytes_recv = 1000000
        bytes_received = mock_psutil.net_io_counters.return_value.bytes_recv
        
        # Test sequence
        metric_object = metric.Metric.create(metric_label)
        metric_type = metric_object.get_type()
        metric_value = metric_object.get_value()

        # Check results
        self.assertEqual(metric_type, metric_label)
        self.assertEqual(metric_value, bytes_received)

    @mock.patch('linux_metric.psutil')
    @mock.patch('metric.sys')
    @mock.patch('linux_metric.time')
    def test_disk_reads_sec(self,
                            mock_time,
                            mock_sys,
                            mock_psutil):

        # Prepare test
        mock_sys.platform = 'linux2'
        metric_label = 'disk_reads_sec'
        time1 = 1
        time2 = 5
        read_bytes1 = 1000000
        read_bytes2 = 2000000
        read_bytes_sec = (int)((read_bytes2 - read_bytes1) /
                               (time2 - time1))
        
        mock_time.return_value = time2        
        mock_psutil.disk_io_counters.return_value.read_bytes = read_bytes2

        # Test sequence
        metric_object = metric.Metric.create(metric_label)
        metric_object.old_time = time1
        metric_object.old_read_bytes = read_bytes1
        
        metric_type = metric_object.get_type()
        metric_value = metric_object.get_value()

        # Check results
        self.assertEqual(metric_type, metric_label)
        self.assertEqual(metric_value, read_bytes_sec)

    @mock.patch('linux_metric.psutil')
    @mock.patch('metric.sys')
    @mock.patch('linux_metric.time')
    def test_disk_writes_sec(self,
                             mock_time,
                             mock_sys,
                             mock_psutil):

        # Prepare test
        mock_sys.platform = 'linux2'
        metric_label = 'disk_writes_sec'
        time1 = 1
        time2 = 5
        write_bytes1 = 1000000
        write_bytes2 = 2000000
        write_bytes_sec = (int)((write_bytes2 - write_bytes1) /
                                (time2 - time1))
        
        mock_time.return_value = time2        
        mock_psutil.disk_io_counters.return_value.write_bytes = write_bytes2

        # Test sequence
        metric_object = metric.Metric.create(metric_label)
        metric_object.old_time = time1
        metric_object.old_write_bytes = write_bytes1
        
        metric_type = metric_object.get_type()
        metric_value = metric_object.get_value()

        # Check results
        self.assertEqual(metric_type, metric_label)
        self.assertEqual(metric_value, write_bytes_sec)
