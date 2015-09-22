"""
    Main program entry
"""
from agent import Agent
from ConfigParser import ConfigParser
from time import sleep


def main():
    """Main program entry"""
    print 'Starting agent...'
    config = ConfigParser()
    config.read('config.ini')
    user = config.get('Connection', 'user')
    passw = config.get('Connection', 'passw')
    address = config.get('Connection', 'ip')
    port = config.get('Connection', 'port')
    metrics = config.get('Metrics', 'metrics').split()
    agent = Agent(user, passw, address, (int)(port), metrics)
    print 'Agent started. Waiting for requests...'
    try:
        agent.start_consuming()
    except KeyboardInterrupt:
        print 'Stopping agent'
        agent.stop_consuming()
        sleep(5)
        agent.disconnect()
        print 'Agent stopped'

if __name__ == "__main__":
    main()
