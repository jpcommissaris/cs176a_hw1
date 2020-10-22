import socket, select, sys, os, time

# resources:
# https://docs.python.org/3/
# https://docs.python.org/3/library/socket.html
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

def connect(addr):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(addr)
        return sock
    except Exception as e:
        print("Could not connect to server.")
        sys.exit(1)

def getCommand():
    command = input("Enter command: ")
    return command

def handleCommand(sock, command): 
    try:
        print('')
        __sendCommand(sock, command)
        __getResponse(sock)
    except CannotSendCommand:
        print('Failed to send command. Terminating.')
    except NoResponse: 
        print('Did not receive response.')
    finally:
        sock.close()
        sys.exit(0)

def __sendCommand(sock, command):
    try:
        encoded_command = bytes(command, 'utf-8')
        command_length = len(encoded_command)
        if(command_length < 1000000):
            leading_zeros = '000000000000'
            len_as_str = leading_zeros[:12-len(str(command_length))]+str(command_length)
            encoded_len = bytes(len_as_str, 'utf-8')
            sock.sendall(encoded_len)
            sock.sendall(encoded_command)
        else:
            raise CannotSendCommand()
    except Exception:
        raise CannotSendCommand()


def __getResponse(sock):
    try: 
        length = int(sock.recv(12).decode("utf-8"))
        res = ''
        while len(res) < length:
            res += sock.recv(32).decode("utf-8")
        __writeToFile(res)
    except Exception as e:
        raise NoResponse()

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
    sock = connect(addr)
    command = getCommand()
    handleCommand(sock, command)

    

