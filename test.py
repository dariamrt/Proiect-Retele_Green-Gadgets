# test simplu pentru aplicatia de depanare
import time
import threading
import socket
from server import DebugServer, Program

def test_program_logic():
    # verifica daca clasa program functioneaza
    print("test 1: logica program")
    
    code = """x = 5
y = x + 3
z = y * 2
result = z - 1"""
    
    prog = Program("test", code)
    print(f"program creat cu {len(prog.lines)} linii")
    
    # executa manual fiecare linie
    prog.execute_line("x = 5")
    prog.execute_line("y = x + 3") 
    prog.execute_line("z = y * 2")
    prog.execute_line("result = z - 1")
    
    # verifica rezultatele
    expected = {"x": 5, "y": 8, "z": 16, "result": 15}
    all_correct = True
    
    for var, expected_val in expected.items():
        if var in prog.variables and prog.variables[var] == expected_val:
            print(f"{var} = {prog.variables[var]} (corect)")
        else:
            print(f"{var} gresit! asteptat: {expected_val}, gasit: {prog.variables.get(var, 'lipsa')}")
            all_correct = False
    
    return all_correct

def test_server_start():
    # verifica daca serverul porneste
    print("\ntest 2: pornire server")
    
    server = DebugServer(port=9999)  # port unic pentru test
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(1)  # asteapta server-ul sa porneasca
    
    # incearca conectare simpla
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = test_socket.connect_ex(('localhost', 9999))
        test_socket.close()
        
        if result == 0:
            print("server-ul accepta conexiuni pe portul 9999")
            server.stop()
            return True
        else:
            print("server-ul nu accepta conexiuni")
            return False
            
    except Exception as e:
        print(f"eroare la testarea conexiunii: {e}")
        return False

def test_multiple_clients():
    # verifica daca serverul accepta mai multi clienti
    print("\ntest 3: mai multi clienti")
    
    server = DebugServer(port=9998)
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(1)
    
    # incearca conectarea a 3 clienti simultan
    clients = []
    success_count = 0
    
    for i in range(3):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = client_socket.connect_ex(('localhost', 9998))
            if result == 0:
                clients.append(client_socket)
                success_count += 1
                print(f"client {i+1} conectat cu succes")
            else:
                print(f"client {i+1} nu s-a putut conecta")
        except Exception as e:
            print(f"eroare la conectarea clientului {i+1}: {e}")
    
    # inchide toate conexiunile
    for client_socket in clients:
        client_socket.close()
    
    server.stop()
    
    if success_count >= 2:
        print(f"serverul accepta {success_count} clienti simultan")
        return True
    else:
        print(f"serverul accepta doar {success_count} clienti")
        return False

def test_expression_parsing():
    # verifica parsarea expresiilor
    print("\ntest 4: parsare expresii")
    
    prog = Program("test_expr", "")
    
    # adauga cateva variabile manual
    prog.variables = {"a": 10, "b": 5}
    
    test_cases = [
        ("15", 15),
        ("a + b", 15),  # 10 + 5
        ("a * 2", 20),  # 10 * 2
        ("b - 3", 2),   # 5 - 3
    ]
    
    all_passed = True
    for expr, expected in test_cases:
        try:
            result = prog.parse_expression(expr)
            if abs(result - expected) < 0.01:  # floating point comparison
                print(f"{expr} = {result} (corect)")
            else:
                print(f"{expr} = {result}, asteptat {expected}")
                all_passed = False
        except Exception as e:
            print(f"eroare la {expr}: {e}")
            all_passed = False
    
    return all_passed

def test_breakpoints():
    # verifica functionalitatea breakpoint-urilor
    print("\ntest 5: breakpoints")
    
    prog = Program("test_bp", "x = 1\ny = 2\nz = 3")
    
    # adauga breakpoints
    prog.breakpoints.add(0)
    prog.breakpoints.add(2)
    
    print(f"breakpoints adaugate: {prog.breakpoints}")
    
    # verifica daca breakpoint-urile sunt setate corect
    if 0 in prog.breakpoints and 2 in prog.breakpoints:
        print("breakpoints setate corect")
        return True
    else:
        print("probleme cu breakpoints")
        return False

def test_client_program_restriction():
    # verifica ca doar un client poate monitoriza un program
    print("\ntest 6: restrictie un client per program")
    
    server = DebugServer(port=9997)
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(1)
    
    # adauga un program de test
    server.programs["test_prog"] = Program("test_prog", "x = 1\ny = 2")
    
    # simuleaza doua socket-uri
    socket1 = "client1_socket"
    socket2 = "client2_socket"
    
    # primul client se ataseaza
    result1 = server.attach_to_program(socket1, "test_prog")
    
    # al doilea client incearca sa se ataseze la acelasi program
    result2 = server.attach_to_program(socket2, "test_prog")
    
    server.stop()
    
    if (result1["status"] == "success" and 
        result2["status"] == "error" and 
        "deja monitorizat" in result2["message"]):
        print("restrictia functioneaza: doar un client per program")
        return True
    else:
        print("problema cu restrictia clienti")
        return False

def run_all_tests():
    print("teste simple pentru aplicatia de depanare")
    print("-" * 45)
    
    tests_passed = 0
    total_tests = 6
    
    try:
        if test_program_logic():
            tests_passed += 1
            
        if test_server_start():
            tests_passed += 1
            
        if test_multiple_clients():
            tests_passed += 1
            
        if test_expression_parsing():
            tests_passed += 1
            
        if test_breakpoints():
            tests_passed += 1
            
        if test_client_program_restriction():
            tests_passed += 1
            
    except Exception as e:
        print(f"\neroare in teste: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\nrezultate finale")
    print(f"teste trecute: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("toate testele au trecut!")
        print("\naplicatia functioneaza corect. poti rula:")
        print("1. python server.py (in primul terminal)")
        print("2. python client.py (in al doilea terminal)")
        print("3. python client.py (in al treilea terminal pentru al 2-lea client)")
    else:
        print("unele teste au esuat")
        print("verifica codul pentru probleme")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    run_all_tests()