import socket, sys, os, _thread

# resources:
# https://pymotw.com/2/socket/tcp.html
# https://janakiev.com/blog/python-shell-commands/
# https://stackoverflow.com/questions/10810249/python-socket-multiple-clients

class CannotRecieveInstructions(Exception):
    pass
class CannotWriteFile(Exception):
    pass

def getPort(): 
    if(len(sys.argv)>1):
        return int(sys.argv[1])
    return 9001

def bind_socket(): 
    try: 
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', port))
    except Exception as e:
        print(e)
        sys.exit(1)
    return sock

def listen(sock): 
    sock.listen(5)
    while True: 
        connection, client_address = sock.accept()
        _thread.start_new_thread(__handleConnection,(connection, client_address))
        

def __handleConnection(connection, client_address):
    try:
        command = __getCommand(connection)
        output = __handleCommand(command)
        __sendResponse(connection, output)
    except CannotRecieveInstructions as e:
        print('Failed to receive instructions from the client.')   
    except CannotWriteFile as e: 
        print('File transmission failed.')
    except Exception as e: 
        print(e)
    finally:
        if(connection):
            connection.close()

            
def __getCommand(connection):
    try: 
        length = int(connection.recv(12).decode("utf-8"))
        data = ''
        while len(data) < length:
            data += connection.recv(32).decode("utf-8")
        return data
    except Exception as e:
        raise CannotRecieveInstructions(e)

def __handleCommand(command):
    try:
        output = os.popen(command).read()
        if '>>' in command or '>' in command:
            output = __getPipeOutput(command)
        return output 
    except Exception as e:
        raise CannotWriteFile(e)

def __getPipeOutput(command):
    filename = command[command.rfind('>')+2:]
    if(filename.find(' ') != -1):
        filename = filename[:filename.find(' ')]
    with open(filename, 'r') as f:
        output = f.read()
        f.close() 
        return output

def __sendResponse(connection, res): 
    try: 
        encoded_res = bytes(res, 'utf-8') 
        res_length = len(encoded_res)
        leading_zeros = '000000000000'
        len_as_str = leading_zeros[:12-len(str(res_length))]+str(res_length)
        encoded_len = bytes(len_as_str, 'utf-8')
        connection.sendall(encoded_len)
        connection.sendall(encoded_res) 
    except Exception as e:
        print(e) 



if __name__ == '__main__':
    port = getPort()
    sock = bind_socket()
    listen(sock)

    

    