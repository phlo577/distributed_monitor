"""
    Metrics module
"""
import sys
from abc import ABCMeta, abstractmethod


class Metric(object):
    """Metric abstract class"""
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
    def create(cls, metric):
        """Metric factory"""
        if sys.platform == 'win32':
            import windows_metric
            return windows_metric.WindowsMetric.create(metric)
        elif sys.platform == 'linux2':
            import linux_metric
            return linux_metric.LinuxMetric.create(metric)
        else:
            raise Exception(sys.platform)
