from config import DB_URL_CFG, USER_CFG, PASW_CFG, IP_CFG, PORT_CFG, LABEL_LIST, LOOP_PERIOD_CFG
from agent import Agent
from connection import Connection
from database import AgentTable, Database
from loop_timer import LoopTimer


# Periodic loop timer container. Sends requests to agents.
def transmit_loop(agent_list):
        for agent in agent_list:
            if agent.timeout:
                # Connection with agent timeout
                print agent.label + ' timeout'
            
        if loop_timer.count == 0:
            # Phase 1 - request CPU usage
            for agent in agent_list:
                agent.send_request('cpu_usage')
            loop_timer.count += 1
            
        elif loop_timer.count == 1:
            # Phase 2 - request memory statistics
            for agent in agent_list:
                agent.send_request('memory')
            loop_timer.count += 1
            
        elif loop_timer.count == 2:
            # Phase 3 - request network usage
            for agent in agent_list:
                agent.send_request('network_usage')
            loop_timer.count += 1
            
        else:
            for agent in agent_list:
            # Phase 4 - request disk iops
                agent.send_request('disk_iops')
            loop_timer.count = 0

        # Restart loop timer
        loop_timer.restart()


# Initialization function
def initialize():
    print 'Connecting to RabbitMQ server...'
    connection.connect()
    channel = connection.get_channel()
    print 'Initializing database... '
    for agent_label in LABEL_LIST:
        # Initialize and store agent entries into database
        database.insert_agent_entry(agent_label)
        # Initialize Agent objects list
        agent_list.append(Agent(agent_label, channel, database))



# List of Agent objects
agent_list = []

# Create database and get session
database = Database(DB_URL_CFG)

# Connection parameters
connection = Connection(USER_CFG, PASW_CFG, IP_CFG, PORT_CFG)


# Create loop timer object
loop_timer = LoopTimer(LOOP_PERIOD_CFG, transmit_loop, [agent_list])


def main():
    initialize()
    loop_timer.start()
    
    try:
        # Start consuming replies
        connection.get_channel().start_consuming()
        
    except KeyboardInterrupt:
        # Stop application
        print 'STOP'
        loop_timer.stop()
        connection.get_channel().stop_consuming()
        for agent in agent_list:
            connection.get_channel().queue_delete(queue=agent.callback_queue)
        connection.disconnect()
        database.get_session().close_all()
        
if __name__ == "__main__":
    main()
