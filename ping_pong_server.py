"""
    Name: ping_pong_server.py
    Creation date: 28/01/2021
    Author: 38
"""

import logging
import select
import socket


class PingPongServer:
    """
    Customize server for get a ping message and return a pong message.
    """
    HOST = 'localhost'
    PING_SIZE = 4
    PONG_MESSAGE = 'pong'
    PING_MESSAGE = 'ping'
    EMPTY_DATA = ''

    def __init__(self, port: int = 1337, timeout: int = 5):
        """
        Create a server socket and init all server configurations.
        :param port: The port which the server will listen on.
        :param timeout: The time the server waits from the connection to the time data sent.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
        self.timeout = timeout
        self.server_socket.bind((PingPongServer.HOST, self.port))
        logging.basicConfig(filename='ping_pong.log', level=logging.INFO)
        logging.log(logging.INFO, f'Server socket created. on port {port} with timeout set to {timeout}')

    def start_server(self):
        """
        Main loop function that activate it.
        :return: None.
        """
        inputs = [self.server_socket]
        writers = []
        while True:
            self.server_socket.listen()
            ready_read, ready_write, ready_exception = select.select(inputs, writers, [])
            for socket_object in ready_read:
                if socket_object is self.server_socket:
                    (client_socket, client_address) = self.accept_connections()
                    inputs.append(client_socket)
                else:
                    is_received_data, received_data = self.get_client_data(socket_object)
                    if self.validate_data(is_received_data, received_data, socket_object):
                        writers.append(socket_object)
                    else:
                        inputs.remove(socket_object)

            for socket_writer in ready_write:
                self.send_response(socket_writer)
                writers.remove(socket_writer)

    def accept_connections(self) -> (socket.socket, tuple):
        """
        Start accepting connections from other sockets.
        :return: The connection socket and the client address.
        """
        logging.log(logging.INFO, 'Server socket ready to read.')
        (client_socket, client_address) = self.server_socket.accept()
        logging.log(logging.INFO, f'Accepted client: {client_address}')
        return client_socket, client_address

    def get_client_data(self, client_socket: socket.socket) -> (bool, str):
        """
        Get the client sent data to our server.
        :param client_socket: The client connection socket.
        :return: Tuple of True or False the client sent data in the timeout range,
                 and the data received.
        """
        received_data = client_socket.recv(PingPongServer.PING_SIZE).decode()
        logging.log(logging.INFO, f'Got {received_data} from {client_socket.getpeername()}')
        return True, received_data

    @staticmethod
    def validate_data(is_received: bool, data: str, client_socket: socket.socket) -> bool:
        """
        Data received validation function, ensure the server got the PING_MESSAGE.
        :param is_received: If we got data from the client.
        :param data: The data we got from the client.
        :param client_socket: The client connection socket.
        :return: True if data equal to PING_MESSAGE else False.
        """
        if is_received and data == PingPongServer.PING_MESSAGE:
            logging.log(logging.INFO, f'Validated {PingPongServer.PING_MESSAGE} received.')
            return True
        else:
            if is_received:
                logging.log(logging.INFO,
                            f'Validation failed. Expected {PingPongServer.PING_MESSAGE}, received {data}.')
                logging.log(logging.INFO, f'Closed connection with {client_socket.getpeername()}')
                client_socket.close()
            return False

    @staticmethod
    def send_response(client_socket: socket.socket):
        """
        Send a response, PONG_MESSAGE to the client.
        :param client_socket: The client connection socket.
        :return: None.
        """
        client_socket.send(PingPongServer.PONG_MESSAGE.encode())
        logging.log(logging.INFO, f'Server  sent {client_socket.getpeername()} => {PingPongServer.PONG_MESSAGE}.')


server = PingPongServer()
server.start_server()
