# List of agent labels
LABEL_LIST = ['agent_windows', 'agent_linux']

# Maximum times a request is sent after a timeout timer expires
MAX_RETRY_COUNTER_CFG = 3

# Period, in seconds, of the main loop
LOOP_PERIOD_CFG = 1.5

# Value, in seconds, before timeout occurs after a request is sent to an agent
TIMEOUT_VAL_CFG = 1

# RabbitMQ server connection parameters
USER_CFG = 'controller'
PASW_CFG = '1234'
IP_CFG = '192.168.0.103'
PORT_CFG = 5672

# SQL Alchemy url
_DALECT_CFG = 'sqlite:///'
_FILENAME_CFG = 'statistics.db'

DB_URL_CFG = _DALECT_CFG + _FILENAME_CFG
