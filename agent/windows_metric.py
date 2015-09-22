"""
    Metrics module for Windows
"""
import wmi
from abc import ABCMeta, abstractmethod
from metric import Metric

class WindowsMetric(Metric):
    """Windows metric abstract class"""
    __metaclass__ = ABCMeta

    def __init__(self):
        self.wmi = wmi.WMI()
        super(WindowsMetric, self).__init__()

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
        """Windows metric factory"""
        if metric_label == 'available_memory':
            metric = WinAvailableMemory()
        elif metric_label == 'total_memory':
            metric = WinTotalMemory()
        elif metric_label == 'cpu_percentage':
            metric = WinCpuPercentage()
        elif metric_label == 'network_bytes_sent':
            metric = WinNetworkBytesSent()
        elif metric_label == 'network_bytes_received':
            metric = WinNetworkBytesReceived()
        elif metric_label == 'disk_reads_sec':
            metric = WinDiskReadsPerSec()
        elif metric_label == 'disk_writes_sec':
            metric = WinDiskWritesPerSec()
        else:
            metric = None
        return metric


class WinAvailableMemory(WindowsMetric):
    """Available virtual memory, in kilobytes, for Windows"""
    def __init__(self):
        self.metric_type = 'available_memory'
        super(WinAvailableMemory, self).__init__()

    def get_type(self):
        return self.metric_type

    def get_value(self):
        available_memory = 0
        for operating_system in self.wmi.Win32_OperatingSystem():
            available_memory += (int)(operating_system.FreeVirtualMemory)
        return available_memory


class WinTotalMemory(WindowsMetric):
    """Total virtual memory, in kilobytes, for Windows"""
    def __init__(self):
        self.metric_type = 'total_memory'
        super(WinTotalMemory, self).__init__()

    def get_type(self):
        return self.metric_type

    def get_value(self):
        total_memory = 0
        for operating_system in self.wmi.Win32_OperatingSystem():
            total_memory += (int)(operating_system.TotalVirtualMemorySize)
        return total_memory


class WinCpuPercentage(WindowsMetric):
    """CPU percentage, for Windows"""
    def __init__(self):
        self.metric_type = 'cpu_percentage'
        super(WinCpuPercentage, self).__init__()

    def get_type(self):
        return self.metric_type

    def get_value(self):
        total_percentage = 0
        for cpu in self.wmi.Win32_Processor():
            # Get percentage of each core
            total_percentage += (int)(cpu.LoadPercentage)
        cpu_percentage = (int)(total_percentage / len(self.wmi.Win32_Processor()))
        return cpu_percentage


class WinNetworkBytesSent(WindowsMetric):
    """Total network bytes sent for Windows"""
    def __init__(self):
        self.metric_type = 'network_bytes_sent'
        super(WinNetworkBytesSent, self).__init__()

    def get_type(self):
        return self.metric_type

    def get_value(self):
        bytes_sent = 0
        for network in self.wmi.Win32_PerfRawData_Tcpip_NetworkInterface():
            bytes_sent += (int)(network.BytesSentPerSec)
        return bytes_sent


class WinNetworkBytesReceived(WindowsMetric):
    """Total network bytes received for Windows"""
    def __init__(self):
        self.metric_type = 'network_bytes_received'
        super(WinNetworkBytesReceived, self).__init__()

    def get_type(self):
        return self.metric_type

    def get_value(self):
        bytes_received = 0
        for network in self.wmi.Win32_PerfRawData_Tcpip_NetworkInterface():
            bytes_received += (int)(network.BytesReceivedPerSec)
        return bytes_received


class WinDiskReadsPerSec(WindowsMetric):
    """Total disk byte reads/secfor Windows"""
    def __init__(self):
        self.metric_type = 'disk_reads_sec'
        super(WinDiskReadsPerSec, self).__init__()

    def get_type(self):
        return self.metric_type

    def get_value(self):
        disk = self.wmi.Win32_PerfFormattedData_PerfDisk_LogicalDisk()
        byte_reads_sec = (int)(disk[0].DiskReadBytesPerSec)
        return byte_reads_sec


class WinDiskWritesPerSec(WindowsMetric):
    """Total disk byte writes/secfor Windows"""
    def __init__(self):
        self.metric_type = 'disk_writes_sec'
        super(WinDiskWritesPerSec, self).__init__()

    def get_type(self):
        return self.metric_type

    def get_value(self):
        disk = self.wmi.Win32_PerfFormattedData_PerfDisk_LogicalDisk()
        disk_writes_sec = (int)(disk[0].DiskWriteBytesPerSec)
        return disk_writes_sec

