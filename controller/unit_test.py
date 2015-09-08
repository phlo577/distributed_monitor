import mock
import unittest
import pika
import uuid
import ast
import sqlalchemy
from agent import Agent
from loop_timer import LoopTimer
from timeout_timer import TimeoutTimer
from database import AgentTable, Database, Base
from connection import Connection
from config import DB_URL_CFG, TIMEOUT_VAL_CFG, MAX_RETRY_COUNTER_CFG, LABEL_LIST
from main import initialize, transmit_loop, main
from main import agent_list, database, connection, loop_timer

# Tests for Agent class
class AgentTest(unittest.TestCase):

    #1 Test initialization
    @mock.patch('main.database')
    @mock.patch('main.connection')
    def test_init(self,
                  mock_connection,
                  mock_database):
        # Prepare test
        channel = mock_connection.get_channel()
        
        # Test sequence
        agent = Agent('agent', channel, mock_database)
        
        # Check results        
        self.assertTrue(channel.queue_declare.called)
        self.assertEqual(agent.label,'agent')
        self.assertEqual(agent.channel, channel)
        self.assertEqual(agent.session, mock_database.get_session())        
        self.assertEqual(agent.timeout_timer.value, TIMEOUT_VAL_CFG)
        self.assertEqual(agent.timeout_timer.callback, agent.on_timeout)
        self.assertEqual(agent.retry_counter, 0)
        self.assertEqual(agent.timeout, False)
        channel.basic_consume.assert_called_once_with(agent.on_response,			      no_ack=True,
                                                      queue=channel
                                                      .queue_declare(exclusive=True)
                                                      .method.queue)
   
    #2 Test sending a request to an agent 
    @mock.patch('uuid.uuid4')
    @mock.patch('main.database')
    @mock.patch('main.connection')
    @mock.patch('timeout_timer.threading.Timer')
    def test_send_request(self,
                          mock_Timer,
                          mock_connection,
                          mock_database,
                          mock_uuid):
        # Prepare test
        channel = mock_connection.get_channel()
        agent = Agent('agent', channel, mock_database)
        agent.timeout = False
        
        # Test sequence        
        agent.send_request('cpu_request')
        
        # Check results
        self.assertEqual(agent.data_label, 'cpu_request')
        self.assertEqual(agent.response, None)
        self.assertTrue(mock_uuid.called)
        channel.basic_publish.assert_called_once_with(exchange='',
                                                      routing_key='agent',
                                                      properties = agent.props,
                                                      body= agent.data_label)
        self.assertTrue(agent.timeout_timer.timer.start.called)


    #3 Test cpu_usage request and response
    @mock.patch('pika.spec.BasicProperties')
    @mock.patch('main.database')
    @mock.patch('main.connection')
    @mock.patch('ast.literal_eval', return_value = [1])
    def test_cpu_usage(self,
                       mock_literal_eval,
                       mock_connection,
                       mock_database,
                       mock_header_frame):
        # Prepare test
        channel = mock_connection.get_channel()
        agent = Agent('agent', channel, mock_database)
        
        #Test sequence
        agent.send_request('cpu_usage')
        mock_header_frame.correlation_id = agent.correlation_id
        agent.on_response(channel, None, mock_header_frame, '[1]' )
        
        # Check results
        self.assertEqual(agent.retry_counter, 0)
        self.assertEqual(agent.timeout, False)
        self.assertEqual(agent.response[0], 1)
        self.assertEqual(agent.data_label, 'cpu_usage')
        self.assertTrue(agent.session.add.called)
        self.assertTrue(agent.session.commit.called)


    #4 Test memory request and response
    @mock.patch('pika.spec.BasicProperties')
    @mock.patch('main.database')
    @mock.patch('main.connection')
    @mock.patch('ast.literal_eval', return_value = [0, 1])
    def test_memory(self,
                    mock_literal_eval,
                    mock_connection,
                    mock_database,
                    mock_header_frame):
        # Prepare test
        channel = mock_connection.get_channel()
        agent = Agent('agent', channel, mock_database)
                
        #Test sequence
        agent.send_request('memory')
        mock_header_frame.correlation_id = agent.correlation_id
        agent.on_response(channel, None, mock_header_frame, '[0, 1]' )

        # Check results
        self.assertEqual(agent.retry_counter, 0)
        self.assertEqual(agent.timeout, False)
        self.assertEqual(agent.response[0], 0)
        self.assertEqual(agent.response[1], 1)
        self.assertEqual(agent.data_label, 'memory')
        self.assertTrue(agent.session.add.called)
        self.assertTrue(agent.session.commit.called)


    #5 Test disk iops request and response
    @mock.patch('pika.spec.BasicProperties')
    @mock.patch('main.database')
    @mock.patch('main.connection')
    @mock.patch('ast.literal_eval', return_value = [2, 3])
    def test_disk_iops(self,
                       mock_literal_eval,
                       mock_connection,
                       mock_database,
                       mock_header_frame):
        # Prepare test
        channel = mock_connection.get_channel()
        agent = Agent('agent', channel, mock_database)
                
        #Test sequence
        agent.send_request('disk_iops')
        mock_header_frame.correlation_id = agent.correlation_id
        agent.on_response(channel, None, mock_header_frame, '[2, 3]' )
        
        # Check results
        self.assertEqual(agent.retry_counter, 0)
        self.assertEqual(agent.timeout, False)
        self.assertEqual(agent.response[0], 2)
        self.assertEqual(agent.response[1], 3)
        self.assertEqual(agent.data_label, 'disk_iops')
        self.assertTrue(agent.session.add.called)
        self.assertTrue(agent.session.commit.called)


    #6 Test disk iops request and response
    @mock.patch('pika.spec.BasicProperties')
    @mock.patch('main.database')
    @mock.patch('main.connection')
    @mock.patch('ast.literal_eval', return_value = [4, 5])
    def test_network_usage(self,
                           mock_literal_eval,
                           mock_connection,
                           mock_database,
                           mock_header_frame):
        # Prepare test
        channel = mock_connection.get_channel()
        agent = Agent('agent', channel, mock_database)
                
        #Test sequence
        agent.send_request('network_usage')
        mock_header_frame.correlation_id = agent.correlation_id
        agent.on_response(channel, None, mock_header_frame, '[4, 5]' )
        
        # Check results
        self.assertEqual(agent.retry_counter, 0)
        self.assertEqual(agent.timeout, False)
        self.assertEqual(agent.response[0], 4)
        self.assertEqual(agent.response[1], 5)
        self.assertEqual(agent.data_label, 'network_usage')
        self.assertTrue(agent.session.add.called)
        self.assertTrue(agent.session.commit.called)


    #7 Test timeout handling when maximum retry count not reached
    @mock.patch('main.database')
    @mock.patch('main.connection')
    def test_on_timeout(self,
                        mock_connection,
                        mock_database):
        # Prepare test
        channel = mock_connection.get_channel()
        agent = Agent('agent', channel, mock_database)

        #Test sequence
        agent.on_timeout()
        
        # Check results
        self.assertEqual(agent.retry_counter, 1)
        self.assertFalse(agent.timeout)


    #8 Test timeout handling when maximum retry count reached
    @mock.patch('main.database')
    @mock.patch('main.connection')
    def test_on_timeout_max_retry(self,
                                 mock_connection,
                                 mock_database):
        # Prepare test
        channel = mock_connection.get_channel()
        agent = Agent('agent', channel, mock_database)
        agent.retry_counter = MAX_RETRY_COUNTER_CFG - 1
        
        #Test sequence
        agent.on_timeout()
                        
        # Check results
        self.assertEqual(agent.retry_counter, MAX_RETRY_COUNTER_CFG)
        self.assertTrue(agent.timeout)

        
# Tests for Connection class
class ConnectionTest(unittest.TestCase):

    #9 Test that a connection si correctly initialized
    @mock.patch('pika.PlainCredentials')
    def test_init(self,
                  mock_Credentials):
        #Test sequence
        connection = Connection('user','pass','123.456.789.012', 1234)

        # Check Results
        mock_Credentials.assert_called_once_with('user','pass')
        self.assertEqual(connection.ip,'123.456.789.012')
        self.assertEqual(connection.port, 1234)


    #10 Test that connection request is handled correctly
    @mock.patch('pika.BlockingConnection')
    @mock.patch('pika.ConnectionParameters')
    @mock.patch('pika.PlainCredentials')
    def test_connect(self,
                     mock_Credentials,
                     mock_ConnectionParameters,
                     mock_BlockingConnection):
        # Prepare test
        connection = Connection('user','pass','123.456.789.012', 1234)

        #Test sequence
        connection.connect()
        
        # Check results
        mock_ConnectionParameters.assert_called_once_with('123.456.789.012',
                                                          1234,
                                                          '/',
                                                          connection.credentials)
        mock_BlockingConnection.assert_called_once_with(
            mock_ConnectionParameters('123.456.789.012',
                                      1234,
                                      '/',
                                      connection.credentials
                                      ))
        self.assertTrue(connection.connection.channel.called)


    #11 Test that disconnection request is handled correctly
    @mock.patch('pika.BlockingConnection')
    @mock.patch('pika.ConnectionParameters')
    @mock.patch('pika.PlainCredentials')
    def test_disconnect(self,
                        mock_Credentials,
                        mock_ConnectionParameters,
                        mock_BlockingConnection):
        # Prepare test
        connection = Connection('user','pass','123.456.789.012', 1234)
        connection.connect()
        
        #Test sequence
        connection.disconnect()
        
        # Check results
        self.assertTrue(connection.connection.close.called)


    #12 Test that channel is retrieved correctly
    @mock.patch('pika.BlockingConnection')
    @mock.patch('pika.ConnectionParameters')
    @mock.patch('pika.PlainCredentials')
    def test_get_channel(self,
                         mock_Credentials,
                         mock_ConnectionParameters,
                         mock_BlockingConnection):
        # Prepare test
        connection = Connection('user','pass','123.456.789.012', 1234)
        connection.connect()

        #Test sequence
        channel = connection.get_channel()
        
        # Check results
        self.assertEqual(connection.channel, channel)


# Tests for Database class
class DatabaseTest(unittest.TestCase):

    #13 Test database initialization
    @mock.patch('database.create_engine')
    @mock.patch('database.relationship')
    @mock.patch('database.sessionmaker')
    @mock.patch('database.Base.metadata')
    def test_init(self,
                  mock_Base_metadata,
                  mock_sessionmaker,
                  mock_relationship,
                  mock_create_engine):
        # Test sequence
        database = Database(DB_URL_CFG)

        # Check results
        mock_create_engine.assert_called_once_with(DB_URL_CFG)
        mock_Base_metadata.create_all.assert_called_once_with(database.engine)
        self.assertEqual(mock_Base_metadata.bind, database.engine)
        mock_sessionmaker.assert_called_once_with(bind=database.engine)


    #14 Test agent entry insertion into the database if it does not exist
    @mock.patch('database.AgentTable')
    @mock.patch('database.create_engine')
    @mock.patch('database.relationship')
    @mock.patch('database.sessionmaker')
    @mock.patch('database.Base.metadata')
    def test_insert_agent_entry_inexistent(self,
                                              mock_Base_metadata,
                                              mock_sessionmaker,
                                              mock_relationship,
                                              mock_create_engine,
                                              mock_AgentTable):
        mock_database = Database(DB_URL_CFG)
        mock_database.agent_table = []
        mock_query = mock_database.session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = None
        
        mock_database.insert_agent_entry(mock.sentinel.agent_label)
        
        mock_AgentTable.assert_called_once_with(label=mock.sentinel.agent_label)
        mock_database.session.add.assert_called_once_with(mock_AgentTable.return_value)
        mock_database.session.commit.assert_called_once_with()


    #15 Test agent entry insertion into the database if it already exists
    @mock.patch('database.AgentTable')
    @mock.patch('database.create_engine')
    @mock.patch('database.relationship')
    @mock.patch('database.sessionmaker')
    @mock.patch('database.Base.metadata')
    def test_insert_agent_entry_existent(self,
                                         mock_Base_metadata,
                                         mock_sessionmaker,
                                         mock_relationship,
                                         mock_create_engine,
                                         mock_AgentTable):
        # Prepare test
        mock_database = Database(DB_URL_CFG)
        mock_database.agent_table = []
        mock_query = mock_database.session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = mock_AgentTable.return_value

        # Test sequence        
        mock_database.insert_agent_entry(mock.sentinel.agent_label)
        
        # Check results
        mock_AgentTable.assert_not_called()
        mock_database.session.add.assert_not_called()
        mock_database.session.commit.assert_not_called()
        self.assertEqual(mock_database.agent_table[0], mock_AgentTable.return_value)


    #16 Test agent entry retrieval
    @mock.patch('database.create_engine')
    @mock.patch('database.relationship')
    @mock.patch('database.sessionmaker')
    @mock.patch('database.Base.metadata')
    def test_get_agent_entry(self,
                             mock_Base_metadata,
                             mock_sessionmaker,
                             mock_relationship,
                             mock_create_engine):
        # Prepare test
        mock_database = Database(DB_URL_CFG)
        mock_database.agent_table = []
        mock_database.agent_table.append(AgentTable(label=mock.sentinel.agent_label))        

        # Test sequence
        agent_entry = mock_database.get_agent_entry(mock.sentinel.agent_label)

        # Check test
        self.assertEqual(agent_entry.label, mock.sentinel.agent_label)


    #17 Test session retrieval
    @mock.patch('database.create_engine')
    @mock.patch('database.relationship')
    @mock.patch('database.sessionmaker')
    @mock.patch('database.Base.metadata')
    def test_get_session(self,
                         mock_Base_metadata,
                         mock_sessionmaker,
                         mock_relationship,
                         mock_create_engine):
        # Prepare test
        database = Database(DB_URL_CFG)

        # Test sequence
        session = database.get_session()

        # Check results
        self.assertEqual(session, database.session)


# Tests for LoopTimer class
class LoopTimerTest(unittest.TestCase):

    #18 Test timer initialization
    def test_init(self):
        # Test sequence
        loop_timer = LoopTimer(2, callback)
        
        # Check results
        self.assertEqual(loop_timer.period, 2)
        self.assertEqual(loop_timer.callback, callback)
        self.assertEqual(loop_timer.timer, None)


    #19 Test starting timer
    @mock.patch('loop_timer.threading.Timer')    
    def test_start(self,
                   mock_Timer):
        # Prepare test
        loop_timer = LoopTimer(2, callback)

        # Test sequence
        loop_timer.start()
        
        # Check results
        self.assertEqual(loop_timer.stopped, False)
        mock_Timer.assert_called_once_with(2, callback)
        self.assertTrue(loop_timer.timer.start.called)

        
    #20 Test restarting timer before it was stopped   
    @mock.patch('loop_timer.threading.Timer')         
    def test_restart_before_stopped(self,
                                    mock_Timer):  
        # Prepare test   
        loop_timer = LoopTimer(2, callback)
        loop_timer.stopped = True
        
        # Test sequence
        loop_timer.restart()
        
        # Check results
        self.assertFalse(mock_Timer.called)


    #21 Test restarting timer after it was stopped  
    @mock.patch('loop_timer.threading.Timer')         
    def test_restart_after_stopped(self,
                                   mock_Timer):
        # Prepare test
        loop_timer = LoopTimer(2, callback)
        loop_timer.stopped = False
        
        # Test sequence
        loop_timer.restart()
        
        # Check results
        mock_Timer.assert_called_once_with(2, callback)
        self.assertTrue(loop_timer.timer.start.called)


    #22 Test stopping timer before it is started
    @mock.patch('loop_timer.threading.Timer')  
    def test_stop_before_start(self,
                               mock_Timer):
        # Prepare test
        loop_timer = LoopTimer(2, callback)
        
        # Test sequence
        loop_timer.stop()
        
        # Check results
        self.assertRaises(AttributeError)


    #23 Test stopping timer after it is started
    @mock.patch('loop_timer.threading.Timer')  
    def test_stop_after_start(self,
                              mock_Timer):
        # Prepare test
        loop_timer = LoopTimer(2, callback)
        loop_timer.start()
        
        # Test sequence
        loop_timer.stop()
        
        # Check results
        self.assertTrue(loop_timer.timer.cancel.called)


# Callback used to test timeout timer
def callback(self):
    pass


# Tests for TimeoutTimer class    
class TimeoutTimerTest(unittest.TestCase):

    #24 Test timer initialization
    def test_init(self):
        # Test sequence
        timeout_timer = TimeoutTimer(2, callback)
        
        # Check results
        self.assertEqual(timeout_timer.value, 2)
        self.assertEqual(timeout_timer.callback, callback)
        self.assertEqual(timeout_timer.timer, None)


    #25 Test starting timer
    @mock.patch('timeout_timer.threading.Timer')    
    def test_start(self, mock_Timer):
        # Prepare test
        timeout_timer = TimeoutTimer(2, callback)
        
        # Test sequence
        timeout_timer.start()
        
        # Check results
        mock_Timer.assert_called_once_with(2, callback)
        self.assertTrue(timeout_timer.timer.start.called)
 

    #26 Test stopping timer before it is started       
    @mock.patch('timeout_timer.threading.Timer')  
    def test_stop_before_start(self,
                               mock_Timer):
        timeout_timer = TimeoutTimer(2, callback)
        timeout_timer.stop()
        # Check results
        self.assertRaises(AttributeError)


    #27 Test stopping timer after it is started        
    @mock.patch('timeout_timer.threading.Timer')  
    def test_stop_after_start(self,
                              mock_Timer):
        # Prepare test
        timeout_timer = TimeoutTimer(2, callback)
        timeout_timer.start()
        
        # Test sequence
        timeout_timer.stop()
        
        # Check results
        self.assertTrue(timeout_timer.timer.cancel.called)


# Tests for main program
class MainTest(unittest.TestCase):

    #28 Test system initialization
    @mock.patch('main.connection')
    @mock.patch('main.database')
    @mock.patch('main.loop_timer')
    def test_initialize(self,
                        mock_loop_timer,
                        mock_database,
                        mock_connection):
        # Test sequence
        initialize()

        # Check results
        self.assertTrue(mock_connection.connect.called)
        self.assertTrue(mock_connection.get_channel.called)
        self.assertTrue(mock_database.insert_agent_entry.called)
        count=0
        for agent_label in LABEL_LIST:
            self.assertEqual(agent_label, agent_list[count].label)
            count+=1


    #29 Test transmit loop handler in phase 1
    @mock.patch('main.database')
    @mock.patch('main.connection')
    @mock.patch('main.agent_list')
    @mock.patch('main.loop_timer')
    @mock.patch('agent.Agent')
    def test_transmit_loop_1(self,
                             mock_Agent,
                             mock_loop_timer,
                             mock_agent_list,
                             mock_connection,
                             mock_database):
        # Prepare test
        connection.connect()
        mock_channel = mock_connection.get_channel()
        mock_agent = mock_Agent('agent', mock_channel, mock_database)
        mock_agent.timeout = False
        mock_agent_list = []
        mock_agent_list.append(mock_agent)
        mock_loop_timer.count = 0

        # Test sequence
        transmit_loop(mock_agent_list)

        # Check results
        self.assertEqual(mock_loop_timer.count, 1)
        mock_agent.send_request.assert_called_once_with('cpu_usage')
        mock_loop_timer.restart.assert_called_once_with()


    #30 Test transmit loop handler in phase 2
    @mock.patch('main.database')
    @mock.patch('main.connection')
    @mock.patch('main.agent_list')
    @mock.patch('main.loop_timer')
    @mock.patch('agent.Agent')
    def test_transmit_loop_2(self,
                             mock_Agent,
                             mock_loop_timer,
                             mock_agent_list,
                             mock_connection,
                             mock_database):
        # Prepare test
        connection.connect()
        mock_channel = mock_connection.get_channel()
        mock_agent = mock_Agent('agent', mock_channel, mock_database)
        mock_agent.timeout = False
        mock_agent_list = []
        mock_agent_list.append(mock_agent)
        mock_loop_timer.count = 1

        # Test sequence
        transmit_loop(mock_agent_list)

        # Check results
        self.assertEqual(mock_loop_timer.count, 2)
        mock_agent.send_request.assert_called_once_with('memory')
        mock_loop_timer.restart.assert_called_once_with()


    #31 Test transmit loop handler in phase 3
    @mock.patch('main.database')
    @mock.patch('main.connection')
    @mock.patch('main.agent_list')
    @mock.patch('main.loop_timer')
    @mock.patch('agent.Agent')
    def test_transmit_loop_3(self,
                             mock_Agent,
                             mock_loop_timer,
                             mock_agent_list,
                             mock_connection,
                             mock_database):
        # Prepare test
        connection.connect()
        mock_channel = mock_connection.get_channel()
        mock_agent = mock_Agent('agent', mock_channel, mock_database)
        mock_agent.timeout = False
        mock_agent_list = []
        mock_agent_list.append(mock_agent)
        mock_loop_timer.count = 2

        # Test sequence
        transmit_loop(mock_agent_list)

        # Check results
        self.assertEqual(mock_loop_timer.count, 3)
        mock_agent.send_request.assert_called_once_with('network_usage')
        mock_loop_timer.restart.assert_called_once_with()


    #32 Test transmit loop handler in phase 4
    @mock.patch('main.database')
    @mock.patch('main.connection')
    @mock.patch('main.agent_list')
    @mock.patch('main.loop_timer')
    @mock.patch('agent.Agent')
    def test_transmit_loop_4(self,
                             mock_Agent,
                             mock_loop_timer,
                             mock_agent_list,
                             mock_connection,
                             mock_database):
        # Prepare test
        connection.connect()
        mock_channel = mock_connection.get_channel()
        mock_agent = mock_Agent('agent', mock_channel, mock_database)
        mock_agent.timeout = False
        mock_agent_list = []
        mock_agent_list.append(mock_agent)
        mock_loop_timer.count = 3

        # Test sequence
        transmit_loop(mock_agent_list)

        # Check results
        self.assertEqual(mock_loop_timer.count, 0)
        mock_agent.send_request.assert_called_once_with('disk_iops')
        mock_loop_timer.restart.assert_called_once_with()


    #33 Test main routine
    @mock.patch('main.connection')
    @mock.patch('main.loop_timer.start')
    @mock.patch('main.initialize')
    def test_main(self,
                  mock_initialize,
                  mock_timer_start,
                  mock_connection
                  ):
        # Prepare test
        mock_connection.connect()
        mock_channel = mock_connection.get_channel()
        mock_start_consuming = mock_channel.start_consuming
        # Test sequence
        main()

        # Check results
        mock_initialize.assert_called_once_with()
        mock_timer_start.assert_called_once_with()
        mock_start_consuming.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
