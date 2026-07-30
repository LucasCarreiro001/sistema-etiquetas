from auth import hash_password, criar_token, verify_password, verificar_token

token = criar_token({'user_id': 1, 'cargo': 'admin'})
print("Token gerado:", token)

payload = verificar_token(token)
print("Payload decodificado:", payload)

payload_invalid = verificar_token("token_invalido")
print("Payload decodificado de token inválido:", payload_invalid)

