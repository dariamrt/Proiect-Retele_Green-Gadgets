import socket
import json
import threading
import time

class DebugClient:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.current_program = None
        self.listening = False
    
    def connect(self):
        # conecteaza la server
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            
            # porneste thread pentru ascultarea mesajelor
            listen_thread = threading.Thread(target=self.listen_for_messages)
            listen_thread.daemon = True
            listen_thread.start()
            
            print(f"conectat la server {self.host}:{self.port}")
            return True
            
        except Exception as e:
            print(f"eroare la conectare: {e}")
            return False
    
    def listen_for_messages(self):
        # asculta mesajele de la server
        self.listening = True
        while self.listening and self.connected:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                try:
                    message = json.loads(data)
                    self.handle_server_message(message)
                except json.JSONDecodeError:
                    print("mesaj invalid de la server")
                    
            except Exception as e:
                if self.connected:
                    print(f"eroare la primirea mesajului: {e}")
                break
    
    def handle_server_message(self, message):
        # gestioneaza mesajele de la server
        if message.get('type') == 'paused':
            print(f"\nprogram oprit la linia {message['line']}")
            print("variabile curente:")
            for var, value in message['variables'].items():
                print(f"  {var} = {value}")
            print("comenzi disponibile: evaluate, set, continue")
            
        elif message.get('type') == 'finished':
            print("\nprogram terminat")
            print("variabile finale:")
            for var, value in message['variables'].items():
                print(f"  {var} = {value}")
    
    def send_command(self, command_data):
        # trimite o comanda la server
        if not self.connected:
            print("nu esti conectat la server!")
            return None
        
        try:
            message = json.dumps(command_data)
            self.socket.send(message.encode('utf-8'))
            
            # asteapta raspuns (doar pentru comenzile care nu sunt notificari)
            if command_data.get('command') not in ['continue']:
                response_data = self.socket.recv(1024).decode('utf-8')
                return json.loads(response_data)
            
        except Exception as e:
            print(f"eroare la trimiterea comenzii: {e}")
            return None
    
    def load_program(self, name, code):
        # incarca un program pe server
        command = {
            'command': 'load_program',
            'name': name,
            'code': code
        }
        response = self.send_command(command)
        if response:
            print(response['message'])
            return response['status'] == 'success'
        return False
    
    def list_programs(self):
        # listeaza programele disponibile
        command = {'command': 'list_programs'}
        response = self.send_command(command)
        if response and response['status'] == 'success':
            print("\nprograme disponibile:")
            for prog in response['programs']:
                status = "ruleaza" if prog['running'] else "oprit"
                monitored = "monitorizat" if prog['monitored'] else "nu e monitorizat"
                print(f"  {prog['name']} - {prog['lines']} linii - {status} - {monitored}")
            return True
        return False
    
    def attach(self, program_name):
        # ataseaza la un program
        command = {
            'command': 'attach',
            'program': program_name
        }
        response = self.send_command(command)
        if response:
            print(response['message'])
            if response['status'] == 'success':
                self.current_program = program_name
                print("\ncod program:")
                for i, line in enumerate(response['lines']):
                    print(f"  {i}: {line}")
            return response['status'] == 'success'
        return False
    
    def detach(self):
        # detaseaza de la program
        command = {'command': 'detach'}
        response = self.send_command(command)
        if response:
            print(response['message'])
            if response['status'] == 'success':
                self.current_program = None
            return response['status'] == 'success'
        return False
    
    def add_breakpoint(self, line):
        # adauga breakpoint
        command = {
            'command': 'add_breakpoint',
            'line': line
        }
        response = self.send_command(command)
        if response:
            print(response['message'])
            return response['status'] == 'success'
        return False
    
    def remove_breakpoint(self, line):
        # elimina breakpoint
        command = {
            'command': 'remove_breakpoint',
            'line': line
        }
        response = self.send_command(command)
        if response:
            print(response['message'])
            return response['status'] == 'success'
        return False
    
    def run_program(self, program_name):
        # ruleaza un program
        command = {
            'command': 'run_program',
            'program': program_name
        }
        response = self.send_command(command)
        if response:
            print(response['message'])
            return response['status'] == 'success'
        return False
    
    def evaluate(self, variable):
        # evalueaza o variabila
        command = {
            'command': 'evaluate',
            'variable': variable
        }
        response = self.send_command(command)
        if response:
            if response['status'] == 'success':
                print(f"{response['variable']} = {response['value']}")
            else:
                print(response['message'])
            return response['status'] == 'success'
        return False
    
    def set_variable(self, variable, value):
        # seteaza o variabila
        command = {
            'command': 'set_variable',
            'variable': variable,
            'value': value
        }
        response = self.send_command(command)
        if response:
            print(response['message'])
            return response['status'] == 'success'
        return False
    
    def continue_execution(self):
        # continua executia
        command = {'command': 'continue'}
        self.send_command(command)
        print("continuare executie...")
    
    def disconnect(self):
        # deconecteaza de la server
        self.listening = False
        self.connected = False
        if self.socket:
            self.socket.close()
        print("deconectat de la server")

def main():
    # interfata principala
    client = DebugClient()
    
    if not client.connect():
        return
    
    print("\nclient debugger")
    print("comenzi disponibile:")
    print("  load <nume> <cod>     - incarca program")
    print("  list                  - listeaza programe")
    print("  attach <nume>         - ataseaza la program") 
    print("  detach                - detaseaza de la program")
    print("  break <linie>         - adauga breakpoint")
    print("  unbreak <linie>       - elimina breakpoint")
    print("  run <nume>            - ruleaza program")
    print("  eval <variabila>      - evalueaza variabila")
    print("  set <var> <valoare>   - seteaza variabila")
    print("  continue              - continua executia")
    print("  quit                  - iesire")
    
    while True:
        try:
            command = input("\n> ").strip().split()
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd == 'quit':
                break
                
            elif cmd == 'load':
                if len(command) < 3:
                    print("folosire: load <nume> <cod>")
                    continue
                name = command[1]
                code = ' '.join(command[2:])
                # pentru teste, folosim cod predefinit
                if code == 'test1':
                    code = "x = 5\ny = x + 3\nz = y * 2\nresult = z - 1"
                elif code == 'test2':
                    code = "a = 10\nb = a / 2\nc = b + 7\nfinal = c * 3"
                client.load_program(name, code)
                
            elif cmd == 'list':
                client.list_programs()
                
            elif cmd == 'attach':
                if len(command) < 2:
                    print("folosire: attach <nume_program>")
                    continue
                client.attach(command[1])
                
            elif cmd == 'detach':
                client.detach()
                
            elif cmd == 'break':
                if len(command) < 2:
                    print("folosire: break <numar_linie>")
                    continue
                try:
                    line = int(command[1])
                    client.add_breakpoint(line)
                except ValueError:
                    print("numar de linie invalid")
                    
            elif cmd == 'unbreak':
                if len(command) < 2:
                    print("folosire: unbreak <numar_linie>")
                    continue
                try:
                    line = int(command[1])
                    client.remove_breakpoint(line)
                except ValueError:
                    print("numar de linie invalid")
                    
            elif cmd == 'run':
                if len(command) < 2:
                    print("folosire: run <nume_program>")
                    continue
                client.run_program(command[1])
                
            elif cmd == 'eval':
                if len(command) < 2:
                    print("folosire: eval <nume_variabila>")
                    continue
                client.evaluate(command[1])
                
            elif cmd == 'set':
                if len(command) < 3:
                    print("folosire: set <variabila> <valoare>")
                    continue
                client.set_variable(command[1], command[2])
                
            elif cmd == 'continue':
                client.continue_execution()
                
            else:
                print("comanda necunoscuta")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"eroare: {e}")
    
    client.disconnect()

if __name__ == "__main__":
    main()