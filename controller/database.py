from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Get base mapper class
Base = declarative_base()


# Agent table mapping class
class AgentTable(Base):
    __tablename__ = 'agent'
    label = Column(String(250), primary_key=True)


# CPU table mapping class
class CpuTable(Base):
    __tablename__ = 'cpu'
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    agent_id = Column(String(250), ForeignKey('agent.label'))
    cpu_usage = Column(Integer)
    agent = relationship(AgentTable)


# Memory table mapping class
class MemoryTable(Base):
    __tablename__ = 'memory'
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    agent_id = Column(String(250), ForeignKey('agent.label'))
    total_memory = Column(Integer)
    available_memory = Column(Integer)
    agent = relationship(AgentTable)


# Disk table mapping class
class DiskTable(Base):
    __tablename__ = 'disk'
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    agent_id = Column(String(250), ForeignKey('agent.label'))
    bytes_read_sec = Column(Integer)
    bytes_write_sec = Column(Integer)
    agent = relationship(AgentTable)


# Network table mapping class
class NetworkTable(Base):
    __tablename__ = 'network'
    timestamp = Column(DateTime(timezone=True), primary_key=True)
    agent_id = Column(String(250), ForeignKey('agent.label'))
    bytes_sent_sec = Column(Integer)
    bytes_received_sec = Column(Integer)
    agent = relationship(AgentTable)

# Database class
class Database:

    # Create database and session
    def __init__(self, url):
        self.engine = create_engine(url)
        Base.metadata.create_all(self.engine)
        Base.metadata.bind = self.engine
        DBSession = sessionmaker(bind=self.engine)
        self.session = DBSession()
        self.agent_table = []

    # 
    def insert_agent_entry(self, agent_label):
        if self.session.query(AgentTable).filter(AgentTable.label == agent_label).first() is None:
            # Agent entry not found, add it into database
            agent_entry = AgentTable(label=agent_label)
            self.session.add(agent_entry)
            self.session.commit()
        else:
            # Retrieve existing entry from database
            agent_entry = self.session.query(AgentTable).filter(AgentTable.label == agent_label).first()
        #Add entry to list
        self.agent_table.append(agent_entry) 
    
    # Returns agent entry based on the label filter
    def get_agent_entry(self, agent_label):
        found = False
        for entry in self.agent_table:
            if entry.label == agent_label and not found:
                agent_entry = entry
                found = True
        if not found:
            agent_entry = None
        return agent_entry

    # Returns current database session
    def get_session(self):
        return self.session

