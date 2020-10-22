import socket, select, sys, os, time

# resources:
# https://pymotw.com/2/socket/tcp.html
# https://wiki.python.org/moin/TcpCommunication
# https://stackoverflow.com/questions/1708835/python-socket-receive-incoming-packets-always-have-a-different-size#:~:text=The%20answer%20is%3A%20you%20don,network%20byte%20order%20using%20socket.
# https://stackoverflow.com/questions/10607688/how-to-create-a-file-name-with-the-current-date-time-in-python

class CannotSendCommand(Exception):
    pass
class NoResponse(Exception):
    pass

def getPortAndIP():
    ip = __getIP()
    print(ip)
    port = __getPort()
    print(port)
    return (ip,port)

def __getIP():
    ip = input("Enter server name or IP address: ") 
    if ip == '':
        return '127.0.0.1'
    else:
        return ip
def __getPort(): 
    port = input("Enter port: ")
    if port == '':
        return 9001
    try:
        port = int(port)
        if port < 0 or port > 65535:
            raise Exception()
    except Exception:
        print('Invalid port number.')
        sys.exit(1)
    return port 


def getCommand():
    command = input("Enter command: ")
    return command

def handleCommand(sock, addr, command): 
    try:
        __sendCommand(sock, addr, command)
        __getResponse(sock)
    except CannotSendCommand as e:
        print('Failed to send command. Terminating.')
    except NoResponse: 
        print('Did not receive response.')
    except Exception as e: 
        print(e)
    finally:
        print('')
        sock.close()
        sys.exit(0)

def __sendCommand(sock, addr, command):
    try:
        encoded_command, encoded_len = __getEncodedLengthAndCommand(command)
        for attempt in range(3):
            try: 
                sock.sendto(encoded_len, addr)
            except Exception as e:
                print("Could not connect to server.") 
                sys.exit(1)
            sock.sendto(encoded_command, addr)
            if(__checkIfACK(sock)):
                return;
        raise CannotSendCommand()

    except Exception as e:
        raise CannotSendCommand(e)

def __getEncodedLengthAndCommand(command):
    encoded_command = bytes(command, 'utf-8')
    command_length = len(encoded_command)
    if(command_length < 1000000):
        leading_zeros = '000000000000'
        len_as_str = leading_zeros[:12-len(str(command_length))]+str(command_length)
        encoded_len = bytes(len_as_str, 'utf-8')
    else:
        raise CannotSendCommand()
    return encoded_command, encoded_len

def __checkIfACK(sock):
    try:
        sock.settimeout(1)
        data, addr = sock.recvfrom(3)
        data = data.decode("utf-8")
        return (True if data == 'ACK' else False)
    except socket.timeout:
        return False 

def __getResponse(sock):
    chunk_size = 1500
    try: 
        length = int(sock.recv(12).decode("utf-8"))
        res = ''
        while length > chunk_size:
            res += __getChunck(sock, chunk_size)
            length -= chunk_size
        res += __getChunck(sock, length)
        __writeToFile(res)
    except Exception:
        raise NoResponse()

def __getChunck(sock, length):
    for attempt in range(3):
        try:
            sock.settimeout(0.5)
            res, addr = sock.recvfrom(length)
            if(len(res) == length):
                res = res.decode("utf-8")
                __sendACK(sock, addr)
                return res
        except socket.timeout: 
            pass
    raise NoResponse() 


def __sendACK(sock, addr):
    try:
        encoded_ack = bytes('ACK', 'utf-8')
        sock.sendto(encoded_ack, addr)
    except Exception:
        raise CannotRecieveInstructions()

def __writeToFile(data):
    filename = 'fc_' + time.strftime("%Y%m%d-%H%M%S") + '.txt'
    if os.path.exists(filename):
        f = open(filename, "a")
    else:
        f = open(filename, "w")
    f.write(data)
    print('File '+ filename + ' saved.')
    f.close() 

        

if __name__ == '__main__':
    addr = getPortAndIP()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    command = getCommand()
    handleCommand(sock, addr, command)

    

