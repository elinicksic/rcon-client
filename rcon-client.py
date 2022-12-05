#!/usr/bin/env python3

import socket
import random
import argparse 
import readline

parser = argparse.ArgumentParser(description="A simple RCON client for Minecraft servers. RCON must be enabled in server.properties to work.")

parser.add_argument("-s", "--server", required=True, help="The server address and port. The port will default to 25575. Ex: localhost:25575")
parser.add_argument("-p", "--password", required=True, help="The password to the rcon server. Should be set in server.properties.")
parser.add_argument('-c', "--command", required=False, help="Runs a command then disconnects. Prints the command output. If not specified, the script will start in interactive mode.")

args = vars(parser.parse_args())

server_arg = args['server'].split(':', 1)
server_address = (server_arg[0], int(server_arg[1]) if len(server_arg) > 1 else 25575)

password = args['password']
command = args['command']

def send_packet(sock, id, payload):
  request_id = random.randint(-2147483648, 2147483647)

  message = request_id.to_bytes(4, 'little', signed=True) + id.to_bytes(4, 'little') + bytes(payload, 'ascii') + b'\x00\x00'
  message = len(message).to_bytes(4, 'little') + message

  sock.send(message)

  return request_id

def receive_packet(sock):
  data = b''
  while not (len(data) > 3 and len(data) - 4 == int.from_bytes(data[:4], 'little')):
    data += sock.recv(1024)
  
  return (int.from_bytes(data[4:8], 'little', signed=True), int.from_bytes(data[8:12], 'little', signed=True), data[12:-2].decode('utf-8'))

def auth(sock, password):
  send_packet(sock, 3, password)
  return receive_packet(sock)[0] != -1

def execute_command(sock, command):
  send_packet(sock, 2, command)
  return receive_packet(sock)[2]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
  sock.connect(server_address)
except ConnectionRefusedError:
  print("Connection Refused! Is RCON enabled on that port?")
  exit(1)

if not auth(sock, password):
  print("Failed to authenticate!")
  exit(-1)

if command:
  print(execute_command(sock, command))
else:
  print("Successfully authenticated!")
  while True:
    command = input("> ")
    print(execute_command(sock, command))
