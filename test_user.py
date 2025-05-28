import users  # Importa el módulo de usuarios

def test_registeruser():
    # Datos de prueba
    id = 347612486
    contraseña = "20202020"
    programa = "matematicas"
    rol = "estudiante"
    
    # Registra al usuario (esto debería ser exitoso en el primer intento)
    resultado = users.registerUser(id, contraseña, programa, rol)
    assert resultado == "User succesfully registered", f"Se esperaba 'User succesfully registered', pero se obtuvo '{resultado}'"
    
    # Intenta registrar el mismo usuario nuevamente (esto debe devolver un error ya que el usuario ya está registrado)
    resultado = users.registerUser(id, contraseña, programa, rol)
    assert resultado == "User already registered", f"Se esperaba 'User already registered', pero se obtuvo '{resultado}'"


def test_getQR():
    # Datos de prueba
    id = 1234556
    contraseña = "456723"
    programa = "matematicas"
    rol = "estudiante"
    
    # Primero, registra al usuario para que exista en el sistema
    users.registerUser(id, contraseña, programa, rol)
    
    # Llama la función
    resultado = users.getQR(id, contraseña)
    
    # Verifica que el resultado sea de tipo 'bytes'
    assert type(resultado.getvalue()) is bytes, f"Se esperaba 'bytes', pero se obtuvo '{type(resultado)}'"

def test_sendQR():
    # Los datos de prueba
    id = 1234556
    contraseña = "456723"
    programa = "matematicas"
    rol = "estudiante"
    
    # Primero, registra al usuario para que exista en el sistema
    users.registerUser(id, contraseña, programa, rol)
    
    # Genera el QR para el usuario
    qr_bytes = users.getQR(id, contraseña)
    
    # Llama a la función para enviar el código QR
    resultado = users.sendQR(qr_bytes)
    
    # Verifica que el resultado sea el esperado
    assert resultado == "Error, la clave ha expirado o el QR no es válido", f"Se esperaba 'Error, la clave ha expirado o el QR no es válido', pero se obtuvo '{resultado}'"
