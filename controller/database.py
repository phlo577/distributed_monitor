"""
    Database module
"""
from abc import ABCMeta
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Get base mapper class
Base = declarative_base()


class MetricTable(object):
    """Generic metric table"""
    __metaclass__ = ABCMeta

    @classmethod
    def insert(cls, metric, timestamp, host, value):
        """Table factory"""
        if metric == 'available_memory':
            table = AvailableMemoryTable(timestamp=timestamp,
                                         host=host,
                                         available_memory=value)
        elif metric == 'total_memory':
            table = TotalMemoryTable(timestamp=timestamp,
                                     host=host,
                                     total_memory=value)
        elif metric == 'cpu_percentage':
            table = CpuPercentageTable(timestamp=timestamp,
                                       host=host,
                                       cpu_percentage=value)
        elif metric == 'network_bytes_sent':
            table = NetworkBytesSentTable(timestamp=timestamp,
                                          host=host,
                                          bytes_sent=value)
        elif metric == 'network_bytes_received':
            table = NetworkBytesReceivedTable(timestamp=timestamp,
                                              host=host,
                                              bytes_received=value)
        elif metric == 'disk_reads_sec':
            table = DiskReadsPerSecTable(timestamp=timestamp,
                                         host=host,
                                         reads_sec=value)
        elif metric == 'disk_writes_sec':
            table = DiskWritesPerSecTable(timestamp=timestamp,
                                          host=host,
                                          writes_sec=value)
        else:
            table = None
        return table


# Metric tables
class AvailableMemoryTable(Base):
    """Available virtual memory class"""
    __tablename__ = 'Available virtual memory'
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    host = Column(String(250))
    available_memory = Column(Integer)


class TotalMemoryTable(Base):
    """Total virtual memory table"""
    __tablename__ = 'Total virtual memory'
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    host = Column(String(250))
    total_memory = Column(Integer)


class CpuPercentageTable(Base):
    """CPU percentage table"""
    __tablename__ = 'CPU percentage'
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    host = Column(String(250))
    cpu_percentage = Column(Integer)


class NetworkBytesSentTable(Base):
    """Network bytes sent table"""
    __tablename__ = 'Network bytes sent'
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    host = Column(String(250))
    bytes_sent = Column(Integer)


class NetworkBytesReceivedTable(Base):
    """Network bytes received table"""
    __tablename__ = 'Network bytes received'
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    host = Column(String(250))
    bytes_received = Column(Integer)


class DiskReadsPerSecTable(Base):
    """Disk reads/sec table"""
    __tablename__ = 'Disk reads/sec'
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    host = Column(String(250))
    reads_sec = Column(Integer)


class DiskWritesPerSecTable(Base):
    """Disk writes/sec table"""
    __tablename__ = 'Disk writes/sec'
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    host = Column(String(250))
    writes_sec = Column(Integer)


class Database(object):
    """Main database class"""

    def __init__(self, url):
        """Create new session"""
        engine = create_engine(url)
        Base.metadata.create_all(engine)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def set_metric(self, metric, timestamp, host, value):
        """Set new metric data to the appropriate table"""
        new_entry = MetricTable.insert(metric=metric,
                                       timestamp=timestamp,
                                       host=host,
                                       value=value)
        self.session.add(new_entry)
        self.session.commit()

    def close_session(self):
        """Close database session"""
        self.session.close_all()
