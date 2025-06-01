import socket
import threading
import json
import re
import time
from typing import Dict, List, Set, Any, Optional

class Program:
    def __init__(self, name: str, code: str):
        self.name = name
        self.code = code
        self.lines = code.strip().split('\n')
        self.variables = {}
        self.current_line = 0
        self.breakpoints = set()
        self.is_running = False
        self.is_paused = False
        self.debugger_client = None
        self.execution_finished = False
    
    def parse_expression(self, expr: str) -> float:
        # evalueaza o expresie aritmetica cu variabile
        # inlocuieste variabilele cu valorile lor
        for var_name, var_value in self.variables.items():
            expr = expr.replace(var_name, str(var_value))
        
        # evalueaza expresia (sigur pentru expresii simple)
        try:
            return eval(expr)
        except:
            return 0
    
    def execute_line(self, line: str):
        # executa o linie de cod
        line = line.strip()
        if not line or line.startswith('#'):
            return
        
        # gaseste atribuirea (variabila = expresie)
        match = re.match(r'(\w+)\s*=\s*(.+)', line)
        if match:
            var_name = match.group(1)
            expr = match.group(2)
            value = self.parse_expression(expr)
            self.variables[var_name] = value
            print(f"program {self.name}: {var_name} = {value}")

class DebugServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.programs = {}  # name -> Program
        self.clients = {}   # client_socket -> client_info
        self.running = True
        self.server_socket = None
    
    def start(self):
        # porneste server-ul
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        print(f"server pornit pe {self.host}:{self.port}")
        
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"client conectat: {address}")
                
                # creeaza thread pentru client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"eroare la acceptarea clientului: {e}")
    
    def handle_client(self, client_socket, address):
        # gestioneaza comunicarea cu un client
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                try:
                    message = json.loads(data)
                    response = self.process_message(client_socket, message)
                    
                    if response:
                        client_socket.send(json.dumps(response).encode('utf-8'))
                        
                except json.JSONDecodeError:
                    error_response = {"status": "error", "message": "mesaj invalid"}
                    client_socket.send(json.dumps(error_response).encode('utf-8'))
                    
        except Exception as e:
            print(f"eroare cu clientul {address}: {e}")
        finally:
            self.disconnect_client(client_socket)
            client_socket.close()
    
    def process_message(self, client_socket, message):
        # proceseaza mesajele de la client
        command = message.get('command')
        
        if command == 'load_program':
            return self.load_program(message.get('name'), message.get('code'))
            
        elif command == 'attach':
            return self.attach_to_program(client_socket, message.get('program'))
            
        elif command == 'detach':
            return self.detach_from_program(client_socket)
            
        elif command == 'add_breakpoint':
            return self.add_breakpoint(client_socket, message.get('line'))
            
        elif command == 'remove_breakpoint':
            return self.remove_breakpoint(client_socket, message.get('line'))
            
        elif command == 'run_program':
            return self.run_program(client_socket, message.get('program'))
            
        elif command == 'evaluate':
            return self.evaluate_variable(client_socket, message.get('variable'))
            
        elif command == 'set_variable':
            return self.set_variable(client_socket, message.get('variable'), message.get('value'))
            
        elif command == 'continue':
            return self.continue_execution(client_socket)
            
        elif command == 'list_programs':
            return self.list_programs()
            
        else:
            return {"status": "error", "message": "comanda necunoscuta"}
    
    def load_program(self, name, code):
        # incarca un program nou
        if not name or not code:
            return {"status": "error", "message": "nume si cod necesare"}
        
        self.programs[name] = Program(name, code)
        return {"status": "success", "message": f"program {name} incarcat"}
    
    def attach_to_program(self, client_socket, program_name):
        # ataseaza un client la un program
        if program_name not in self.programs:
            return {"status": "error", "message": "program inexistent"}
        
        program = self.programs[program_name]
        
        # verifica daca programul e deja monitorizat
        if program.debugger_client and program.debugger_client != client_socket:
            return {"status": "error", "message": "program deja monitorizat de alt client"}
        
        program.debugger_client = client_socket
        self.clients[client_socket] = {"program": program_name}
        
        return {
            "status": "success", 
            "message": f"atasat la programul {program_name}",
            "lines": program.lines
        }
    
    def detach_from_program(self, client_socket):
        # detaseaza un client de la program
        if client_socket not in self.clients:
            return {"status": "error", "message": "nu esti atasat la niciun program"}
        
        program_name = self.clients[client_socket]["program"]
        program = self.programs[program_name]
        program.debugger_client = None
        
        del self.clients[client_socket]
        
        return {"status": "success", "message": f"detasat de la programul {program_name}"}
    
    def add_breakpoint(self, client_socket, line):
        # adauga punct de oprire
        if client_socket not in self.clients:
            return {"status": "error", "message": "nu esti atasat la niciun program"}
        
        program_name = self.clients[client_socket]["program"]
        program = self.programs[program_name]
        
        if program.is_running:
            return {"status": "error", "message": "nu poti modifica breakpoint-uri in timpul executiei"}
        
        if line < 0 or line >= len(program.lines):
            return {"status": "error", "message": "numar de linie invalid"}
        
        program.breakpoints.add(line)
        return {"status": "success", "message": f"breakpoint adaugat la linia {line}"}
    
    def remove_breakpoint(self, client_socket, line):
        # elimina punct de oprire
        if client_socket not in self.clients:
            return {"status": "error", "message": "nu esti atasat la niciun program"}
        
        program_name = self.clients[client_socket]["program"]
        program = self.programs[program_name]
        
        if program.is_running:
            return {"status": "error", "message": "nu poti modifica breakpoint-uri in timpul executiei"}
        
        program.breakpoints.discard(line)
        return {"status": "success", "message": f"breakpoint eliminat de la linia {line}"}
    
    def run_program(self, client_socket, program_name):
        # ruleaza un program
        if program_name not in self.programs:
            return {"status": "error", "message": "program inexistent"}
        
        program = self.programs[program_name]
        
        if program.is_running:
            return {"status": "error", "message": "programul ruleaza deja"}
        
        # creeaza thread pentru executie
        execution_thread = threading.Thread(
            target=self.execute_program,
            args=(program,)
        )
        execution_thread.daemon = True
        execution_thread.start()
        
        return {"status": "success", "message": f"program {program_name} pornit"}
    
    def execute_program(self, program):
        # executa un program cu debugging
        program.is_running = True
        program.is_paused = False
        program.current_line = 0
        program.execution_finished = False
        
        print(f"executie program: {program.name}")
        
        while program.current_line < len(program.lines) and program.is_running:
            # verifica breakpoint
            if program.current_line in program.breakpoints and program.debugger_client:
                program.is_paused = True
                self.notify_client_paused(program)
                
                # asteapta continuarea
                while program.is_paused and program.is_running:
                    time.sleep(0.1)
            
            if not program.is_running:
                break
            
            # executa linia curenta
            if program.current_line < len(program.lines):
                program.execute_line(program.lines[program.current_line])
                program.current_line += 1
                time.sleep(0.5)  # simuleaza timpul de executie
        
        program.is_running = False
        program.execution_finished = True
        
        # notifica clientul ca s-a terminat
        if program.debugger_client:
            self.notify_client_finished(program)
        
        print(f"program {program.name} terminat")
    
    def notify_client_paused(self, program):
        # notifica clientul ca programul e in pauza
        if program.debugger_client:
            try:
                message = {
                    "type": "paused",
                    "line": program.current_line,
                    "variables": program.variables
                }
                program.debugger_client.send(json.dumps(message).encode('utf-8'))
            except:
                pass
    
    def notify_client_finished(self, program):
        # notifica clientul ca programul s-a terminat
        if program.debugger_client:
            try:
                message = {
                    "type": "finished",
                    "variables": program.variables
                }
                program.debugger_client.send(json.dumps(message).encode('utf-8'))
            except:
                pass
    
    def evaluate_variable(self, client_socket, variable_name):
        # evalueaza o variabila
        if client_socket not in self.clients:
            return {"status": "error", "message": "nu esti atasat la niciun program"}
        
        program_name = self.clients[client_socket]["program"]
        program = self.programs[program_name]
        
        if variable_name in program.variables:
            return {
                "status": "success", 
                "variable": variable_name,
                "value": program.variables[variable_name]
            }
        else:
            return {"status": "error", "message": f"variabila {variable_name} nu exista"}
    
    def set_variable(self, client_socket, variable_name, value):
        # seteaza valoarea unei variabile
        if client_socket not in self.clients:
            return {"status": "error", "message": "nu esti atasat la niciun program"}
        
        program_name = self.clients[client_socket]["program"]
        program = self.programs[program_name]
        
        try:
            program.variables[variable_name] = float(value)
            return {
                "status": "success", 
                "message": f"variabila {variable_name} setata la {value}"
            }
        except ValueError:
            return {"status": "error", "message": "valoare invalida"}
    
    def continue_execution(self, client_socket):
        # continua executia programului
        if client_socket not in self.clients:
            return {"status": "error", "message": "nu esti atasat la niciun program"}
        
        program_name = self.clients[client_socket]["program"]
        program = self.programs[program_name]
        
        if not program.is_paused:
            return {"status": "error", "message": "programul nu e in pauza"}
        
        program.is_paused = False
        return {"status": "success", "message": "executie continuata"}
    
    def list_programs(self):
        # listeaza programele disponibile
        programs_info = []
        for name, program in self.programs.items():
            programs_info.append({
                "name": name,
                "lines": len(program.lines),
                "running": program.is_running,
                "monitored": program.debugger_client is not None
            })
        
        return {"status": "success", "programs": programs_info}
    
    def disconnect_client(self, client_socket):
        # deconecteaza un client
        if client_socket in self.clients:
            program_name = self.clients[client_socket]["program"]
            program = self.programs[program_name]
            program.debugger_client = None
            del self.clients[client_socket]
    
    def stop(self):
        # opreste server-ul
        self.running = False
        if self.server_socket:
            self.server_socket.close()

# exemplu de utilizare
if __name__ == "__main__":
    server = DebugServer()
    
    # incarca niste programe de test
    program1_code = """x = 5
y = x + 3
z = y * 2
result = z - 1"""
    
    program2_code = """a = 10
b = a / 2
c = b + 7
final = c * 3"""
    
    server.programs["program1"] = Program("program1", program1_code)
    server.programs["program2"] = Program("program2", program2_code)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\noprire server...")
        server.stop()