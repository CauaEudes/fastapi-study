from pydantic import BaseModel
import re

class UserCreate(BaseModel):
    name: str
    cpf: str
    email: str
    password: str

class User(BaseModel):
    id: int
    name: str
    cpf: str
    email: str
    created_at: str
    updated_at: str

def validateEmail(email: str) -> bool:
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

import re

def cleanCpf(cpf: str) -> str:
    return re.sub(r'[^0-9]', '', cpf)

def formatCpf(cpf: str) -> str:
    cpf_limpo = cleanCpf(cpf)
    return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"

def validateCpf(cpf: str) -> bool:
    cpf_limpo = cleanCpf(cpf)

    if len(cpf_limpo) != 11:
        return False

    if cpf_limpo == cpf_limpo[0] * 11:
        return False

    soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
    digito1 = 11 - (soma % 11)
    digito1 = 0 if digito1 >= 10 else digito1

    soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
    digito2 = 11 - (soma % 11)
    digito2 = 0 if digito2 >= 10 else digito2

    return cpf_limpo[-2:] == f"{digito1}{digito2}"