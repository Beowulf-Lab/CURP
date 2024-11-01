from flask import Flask, request, render_template
import re
from datetime import datetime

app = Flask(__name__)

def process_curp(curp):
    tokens = []
    errors = []
    counts = {
        'Apellido Paterno': 0,
        'Apellido Materno': 0,
        'Nombre': 0,
        'Año': 0,
        'Mes': 0,
        'Día': 0,
        'Género': 0,
        'Estado': 0,
        'Consonantes Internas': 0,
        'Homoclave': 0,
        'Dígito Verificador': 0,
        'Total': 0  # Para el conteo total
    }

    if len(curp) != 18:
        errors.append("La CURP debe tener 18 caracteres.")
        return tokens, errors, counts
    curp = curp.upper()
    ap = curp[0:2]   # Apellido Paterno (primeras dos letras)
    am = curp[2]     # Apellido Materno (tercera letra)
    n = curp[3]      # Nombre (cuarta letra)
    date_str = curp[4:10]
    gender = curp[10]
    state_code = curp[11:13]
    internals = curp[13:16]
    homonym = curp[16]
    check_digit = curp[17]

    # Validación de la fecha de nacimiento antes de continuar
    if re.match(r'^\d{6}$', date_str):
        # Validar componentes de la fecha
        year = int(date_str[0:2])
        month = int(date_str[2:4])
        day = int(date_str[4:6])
        # Ajustar año para considerar siglos (asumiendo fechas de 1900 a 2099)
        current_year_short = int(datetime.now().strftime("%y"))
        if year <= current_year_short:
            year += 2000
        else:
            year += 1900
        try:
            datetime(year, month, day)
        except ValueError:
            errors.append("Fecha de nacimiento inválida. Verifica día, mes y año, incluyendo años bisiestos.")
            return tokens, errors, counts  # No continuar si la fecha es inválida
    else:
        errors.append("Fecha de nacimiento inválida.")
        return tokens, errors, counts  # No continuar si la fecha es inválida

    # Si la fecha es válida, continuar con la extracción de tokens
    tokens.append(('Año', str(year)))
    counts['Año'] += 1
    tokens.append(('Mes', f"{month:02d}"))
    counts['Mes'] += 1
    tokens.append(('Día', f"{day:02d}"))
    counts['Día'] += 1

    # Validación y conteo de los demás tokens
    if re.match(r'^[A-ZÑ]{2}$', ap):
        tokens.append(('Apellido Paterno', ap))
        counts['Apellido Paterno'] += 1
    else:
        errors.append("Iniciales del apellido paterno inválidas.")

    if re.match(r'^[A-ZÑ]$', am):
        tokens.append(('Apellido Materno', am))
        counts['Apellido Materno'] += 1
    else:
        errors.append("Inicial del apellido materno inválida.")

    if re.match(r'^[A-ZÑ]$', n):
        tokens.append(('Nombre', n))
        counts['Nombre'] += 1
    else:
        errors.append("Inicial del nombre inválida.")

    # Género
    if gender in ['H', 'M']:
        tokens.append(('Género', gender))
        counts['Género'] += 1
    else:
        errors.append("Género inválido.")

    # Estado
    valid_states = ['AS','BC','BS','CC','CL','CM','CS','CH','DF','DG','GT','GR',
                    'HG','JC','MC','MN','MS','NT','NL','OC','PL','QT','QR','SP',
                    'SL','SR','TC','TS','TL','VZ','YN','ZS','NE']
    if state_code in valid_states:
        tokens.append(('Estado', state_code))
        counts['Estado'] += 1
    else:
        errors.append("Código de estado inválido.")

    # Consonantes Internas
    if re.match(r'^[B-DF-HJ-NP-TV-Z]{3}$', internals):
        tokens.append(('Consonantes Internas', internals))
        counts['Consonantes Internas'] += 1
    else:
        errors.append("Consonantes internas inválidas.")

    # Homoclave
    if re.match(r'^[0-9A-Z]$', homonym):
        tokens.append(('Homoclave', homonym))
        counts['Homoclave'] += 1
    else:
        errors.append("Homoclave inválida.")

    # Dígito Verificador
    if re.match(r'^[0-9A-Z]$', check_digit):
        tokens.append(('Dígito Verificador', check_digit))
        counts['Dígito Verificador'] += 1
    else:
        errors.append("Dígito verificador inválido.")

    # Calcular el total de tokens reconocidos
    counts['Total'] = sum(counts[key] for key in counts if key != 'Total')

    return tokens, errors, counts

@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = None
    success_message = None
    tokens = []
    counts = {}
    text = ''

    if request.method == 'POST':
        text = request.form['text']
        tokens, errors, counts = process_curp(text)

        if errors:
            error_message = '; '.join(errors)
            tokens = []  # No mostrar tokens si hay errores
            counts = {}  # No mostrar conteos si hay errores
        else:
            success_message = "CURP válida."

    return render_template('index.html', text=text, tokens=tokens,
                           error_message=error_message,
                           success_message=success_message, counts=counts)

if __name__ == '__main__':
    app.run(debug=True)