"""
    Main program entry
"""
from threading import Thread
from controller import Controller
from time import sleep
from ConfigParser import ConfigParser


def main():
    """Main program entry"""
    print 'Starting controller...'
    config = ConfigParser()
    config.read('config.ini')
    user = config.get('Connection', 'user')
    passw = config.get('Connection', 'passw')
    address = config.get('Connection', 'ip')
    port = config.get('Connection', 'port')
    request_period = config.get('Connection', 'request_period')
    url = config.get('Database', 'dialect')+config.get('Database', 'filename')
    controller = Controller(user, passw, address, (int)(port), url)

    print 'Controller started'
    # Start consuming agent messages
    reply_thread = Thread(target=controller.start_consuming)
    reply_thread.start()

    # Start request sequence
    request_thread = Thread(target=controller.start_requesting,
                            args=(request_period))
    request_thread.start()
    try:
        while True:
            # Keep main program here
            sleep(1)
    except KeyboardInterrupt:
        print 'Stopping controller...'
        # Stop requesting
        controller.stop_requesting()

        # Wait another request period before disconnectig
        sleep((float)(request_period))
        controller.stop_consuming()
        controller.disconnect()
        request_thread.join()
        reply_thread.join()
        print 'Controller stopped'

if __name__ == "__main__":
    main()
