import socket, sys, os, _thread, time

# resources:
# https://docs.python.org/3/
# https://docs.python.org/3/library/socket.html
# https://janakiev.com/blog/python-shell-commands/
# https://wiki.python.org/moin/UdpCommunication
# https://stackoverflow.com/questions/10607688/how-to-create-a-file-name-with-the-current-date-time-in-python

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
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('localhost', port))
    except Exception as e:
        print(e)
        sys.exit(1)
    return sock

def handleIncomingData(sock): 
    while True: 
        sock.settimeout(None)
        length, addr = sock.recvfrom(12)
        __handleData(sock, addr, length)

def __handleData(sock,addr,length):
    try:
        command = __getCommand(sock, addr, length)
        __sendACK(sock,addr)
        command_output = __handleCommand(command)
        __sendResponseByChunks(sock, addr, command_output)
        
    except CannotRecieveInstructions as e:
        print('Failed to receive instructions from the client.')    
    except CannotWriteFile as e: 
        print('File transmission failed.')
        print(e)
    except Exception as e: 
        print('unknown error: ', e) 
                  
def __getCommand(sock, addr, length):
    try: 
        length = int(length.decode("utf-8"))
        sock.settimeout(0.5)
        data, recv_addr = sock.recvfrom(length)
        if(recv_addr == addr and length == len(data)):
            data = data.decode("utf-8")
            return data  
        raise Exception()
    except Exception as e:
        raise CannotRecieveInstructions()

def __sendACK(sock, addr):
    try:
        encoded_ack = bytes('ACK', 'utf-8')
        sock.sendto(encoded_ack, addr)
    except Exception:
        raise CannotRecieveInstructions()

def __handleCommand(command):
    try:
        output = os.popen(command).read()
        if '>>' in command or '>' in command:
            output = __getPipeOutput(command)
        else:
            __writeToFile(output)
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

def __writeToFile(data):
    filename = 'fs_' + time.strftime("%Y%m%d-%H%M%S") + '.txt'
    if os.path.exists(filename):
        f = open(filename, "a")
    else:
        f = open(filename, "w")
    f.write(data)
    f.close() 
    

def encodedResAndLen(res): 
    encoded_res = bytes(res, 'utf-8') 
    res_length = len(encoded_res)
    leading_zeros = '000000000000'
    len_as_str = leading_zeros[:12-len(str(res_length))]+str(res_length)
    encoded_len = bytes(len_as_str, 'utf-8')
    return encoded_res, encoded_len

def __sendResponseByChunks(sock, addr, res): 
    chunk_size=1500
    try: 
        encoded_res, encoded_len = encodedResAndLen(res)
        sock.sendto(encoded_len, addr)
        remaining_bytes_to_send = len(encoded_res)
        while remaining_bytes_to_send > chunk_size:
            __sendChunk(sock, addr, encoded_res[:chunk_size])
            encoded_res = encoded_res[chunk_size:]
            remaining_bytes_to_send -= chunk_size
        __sendChunk(sock, addr, encoded_res)
    except Exception as e:
        raise CannotWriteFile() 

def __sendChunk(sock, addr, chunk):
    for attempt in range(3):
        sock.sendto(chunk, addr)
        if(__checkIfACK(sock)):
            return;
    raise Exception() 

def __checkIfACK(sock):
    try:
        sock.settimeout(1)
        data, addr = sock.recvfrom(3)
        data = data.decode("utf-8")
        return (True if data == 'ACK' else False)
    except socket.timeout:
        return False 


if __name__ == '__main__':
    port = getPort()
    sock = bind_socket()
    handleIncomingData(sock)

    



