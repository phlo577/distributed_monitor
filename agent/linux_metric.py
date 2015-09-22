"""
    Metrics module for Linux
"""
import psutil
from abc import ABCMeta, abstractmethod
from time import time
from metric import Metric


class LinuxMetric(Metric):
    """Linux metric abstract class"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_type(self):
        """Get metric type"""
        pass

    @abstractmethod
    def get_value(self):
        """Get value type"""
        pass

    @classmethod
    def create(cls, metric_label):
        """Linux metric factory"""
        if metric_label == 'available_memory':
            metric = LinAvailableMemory()
        elif metric_label == 'total_memory':
            metric = LinTotalMemory()
        elif metric_label == 'cpu_percentage':
            metric = LinCpuPercentage()
        elif metric_label == 'network_bytes_sent':
            metric = LinNetworkBytesSent()
        elif metric_label == 'network_bytes_received':
            metric = LinNetworkBytesReceived()
        elif metric_label == 'disk_reads_sec':
            metric = LinDiskReadsPerSec()
        elif metric_label == 'disk_writes_sec':
            metric = LinDiskWritesPerSec()
        else:
            metric = None
        return metric


class LinAvailableMemory(LinuxMetric):
    """Available virtual memory, in kilobytes, for Linux"""
    def __init__(self):
        self.metric_type = 'available_memory'
        super(LinAvailableMemory, self).__init__()

    def get_type(self):
        return self.metric_type

    def get_value(self):
        memory = psutil.virtual_memory()
        return (int)(memory.available/1024)


class LinTotalMemory(LinuxMetric):
    """Total virtual memory, in kilobytes, for Linux"""
    def __init__(self):
        self.metric_type = 'total_memory'
        super(LinTotalMemory, self).__init__()

    def get_type(self):
        return self.metric_type

    def get_value(self):
        memory = psutil.virtual_memory()
        return (int)(memory.total/1024)


class LinCpuPercentage(Metric):
    """CPU percentage for Linux"""
    def __init__(self):
        self.metric_type = 'cpu_percentage'
        super(LinCpuPercentage, self).__init__()

    def get_type(self):
        return self.metric_type

    def get_value(self):
        cpu_percentage = (int)(psutil.cpu_percent(percpu=False))
        return cpu_percentage


class LinNetworkBytesSent(Metric):
    """Total network bytes sent for Linux"""
    def __init__(self):
        self.metric_type = 'network_bytes_sent'
        super(LinNetworkBytesSent, self).__init__()

    def get_type(self):
        return self.metric_type

    def get_value(self):
        network = psutil.net_io_counters()
        return network.bytes_sent


class LinNetworkBytesReceived(Metric):
    """Total network bytes received for Linux"""
    def __init__(self):
        self.metric_type = 'network_bytes_received'
        super(LinNetworkBytesReceived, self).__init__()

    def get_type(self):
        return self.metric_type

    def get_value(self):
        network = psutil.net_io_counters()
        return network.bytes_recv


class LinDiskReadsPerSec(Metric):
    """Total disk byte reads/sec for Linux"""
    def __init__(self):
        self.metric_type = 'disk_reads_sec'
        self.old_time = time()
        self.old_read_bytes = psutil.disk_io_counters().read_bytes
        super(LinDiskReadsPerSec, self).__init__()

    def get_type(self):
        return self.metric_type

    def get_value(self):
        current_time = time()
        read_bytes = psutil.disk_io_counters().read_bytes
        read_bytes_sec = (int)((read_bytes - self.old_read_bytes) /
                               (current_time - self.old_time))
        self.old_time = current_time
        self.old_read_bytes = read_bytes
        return read_bytes_sec


class LinDiskWritesPerSec(Metric):
    """Total disk byte writes/sec for Linux"""
    def __init__(self):
        self.metric_type = 'disk_writes_sec'
        self.old_time = time()
        self.old_write_bytes = psutil.disk_io_counters().write_bytes
        super(LinDiskWritesPerSec, self).__init__()

    def get_type(self):
        return self.metric_type

    def get_value(self):
        current_time = time()
        write_bytes = psutil.disk_io_counters().write_bytes
        write_bytes_sec = (int)((write_bytes - self.old_write_bytes) /
                                (current_time - self.old_time))
        self.old_time = current_time
        self.old_write_bytes = write_bytes
        return write_bytes_sec
