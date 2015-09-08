import sys
import pika
import logging
import time
from config import OS, LABEL, USER_CFG, PASW_CFG, IP_CFG, PORT_CFG

if OS == 'Windows':
    # For Windows, use WMI
    import wmi    
elif OS == 'Linux':
    # For Linux, use psutil
    import psutil
    
    # Variables used to calcualte disk iops
    old_time = time.time()
    old_read_bytes = psutil.disk_io_counters().read_bytes
    old_write_bytes = psutil.disk_io_counters().write_bytes
    
else:
    print("Invalid OS label")
    sys.exit()

        
def get_linux_statistics(label):
    result = []
    global old_time
    global old_read_bytes
    global old_write_bytes
    
    if label == 'cpu_usage':
        # Get CPU usage of each core
        percent_list = psutil.cpu_percent(percpu=True)
        for cpu_percent in percent_list:
            result.append((str)((int)(cpu_percent)))
                        
    elif label == 'memory':
        # Get total and total available virtual memory
        memory = psutil.virtual_memory()
        result = [(str)(memory.total), (str)(memory.available)]

    elif label == 'disk_iops':
        # Calculate iops, because psutil only provides bytes read and written since startup
        disk = psutil.disk_io_counters()
        current_time = time.time()

        read_bytes_sec = (int)((disk.read_bytes - old_read_bytes)/(current_time - old_time))
        write_bytes_sec = (int)((disk.write_bytes - old_write_bytes)/(current_time - old_time))
        old_write_bytes = disk.write_bytes
        old_read_bytes = disk.read_bytes
        old_time = current_time
        
        result = [(str)(read_bytes_sec), (str)(write_bytes_sec)]

    else:
        # Get total network bytes sent/received
        network = psutil.net_io_counters()
        result = [(str)(network.bytes_sent), (str)(network.bytes_recv)]

    return result

def get_windows_statistics(label):
    c = wmi.WMI()
    result = []
    if label == 'cpu_usage':
        # Get CPU usage of each core
        for cpu in c.Win32_Processor():
            result.append((str)(cpu.LoadPercentage))
            
    elif label == 'memory':
        # Calculate total and total available virtual memory
        total_memory = 0
        available_memory = 0
        for os in c.Win32_OperatingSystem():
            total_memory += (int)(os.TotalVirtualMemorySize)
            available_memory += (int)(os.FreeVirtualMemory)
        result = [(str)(total_memory), (str)(available_memory)]
        
    elif label == 'disk_iops':
        # Get total disk byres read/written per second
        disk = c.Win32_PerfFormattedData_PerfDisk_LogicalDisk()
        result = [(str)(disk[0].DiskReadBytesPerSec), (str)(disk[0].DiskWriteBytesPerSec)]
        
    else:
        # Calculate total network bytes sent/received
        bytes_sent = 0
        bytes_received = 0
        for network in c.Win32_PerfRawData_Tcpip_NetworkInterface():
            bytes_sent += (int)(network.BytesSentPerSec)
            bytes_received += (int)(network.BytesReceivedPerSec)
        result = [(str)(bytes_sent), (str)(bytes_received)]

    return result


def on_request(channel, method, props, body):
    
    print '[<] Received request for ' + body
    if OS == 'Windows':
        # Get statistics for Windows using WMI
        response = get_windows_statistics(body)            
    else:
        # Get statistics from Linux using psutil
        response = get_linux_statistics(body)

    # Publish response to server
    channel.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                         body=str(response))

    channel.basic_ack(delivery_tag = method.delivery_tag)
    print '[>] Sent statistics for ' + body


def main():

    # Connect to RabbitMQ server and start consuming
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.CRITICAL)
    credentials = pika.PlainCredentials(USER_CFG, PASW_CFG)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
                        IP_CFG,
                        PORT_CFG,
                        '/',
                        credentials))
    channel = connection.channel()
    channel.queue_declare(LABEL)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(on_request, queue=LABEL)
    try:
        print '[.] Awaiting requests'
        channel.start_consuming()
        
    except KeyboardInterrupt:
        print 'STOP'
        channel.stop_consuming()
        connection.close()

if __name__ == "__main__":
    main()
