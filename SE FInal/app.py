from flask import Flask, abort, flash, render_template, request, redirect, url_for, session
from rules_engine import calcular_puntos_unidad4, evaluar_unidad, evaluar_problemas_rule, evaluar_explicacion_rule

app = Flask(__name__)
app.secret_key = "clave_secreta"  # Para sesiones

@app.route('/')
def index():
    calificaciones = {}
    for i in range(1, 5):
        cal = session.get(f'unidad{i}')
        calificaciones[i] = cal if cal is not None else 'Sin evaluar'
    return render_template('index.html', calificaciones=calificaciones)

@app.route('/unidad/<int:num>', methods=['GET', 'POST'])
def unidad(num):
    unidad_key = f'unidad{num}'
    
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        
        # Obtener puntajes de problemas y explicación
        problemas_score = session.get(f'problemas_score_{unidad_key}', 0)
        explicacion_score = session.get(f'explicacion_score_{unidad_key}', 0)
        
        # Añadir los puntajes a los datos para evaluar_unidad
        data['problemas_score'] = problemas_score
        data['explicacion_score'] = explicacion_score
        
        # Guardar y calcular
        session[f'valores_{unidad_key}'] = data
        calificacion = evaluar_unidad(data)
        session[f'unidad{num}'] = calificacion
        
        return redirect(url_for('unidad', num=num))

    valores = session.get(f'valores_{unidad_key}', {})
    calificacion = session.get(f'unidad{num}')
    
    if num == 4:
        return render_template('unidad4.html', unidad=num, valores=valores, calificacion=calificacion)
    else:
        return render_template('unidad1_3.html', unidad=num, valores=valores, calificacion=calificacion)

    
    

@app.route('/evaluar_problemas/<unidad>', methods=['GET', 'POST'])
def evaluar_problemas(unidad):
    unidad_key = f'unidad{unidad[-1]}'  # Extrae el número (ej: 'unidad1' -> '1')
    
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # Calcular puntaje
        problemas_score = evaluar_problemas_rule(data)
        
        # Guardar en sesión con clave específica
        session[f'problemas_form_{unidad_key}'] = data
        session[f'problemas_score_{unidad_key}'] = problemas_score
        session.modified = True
        
        print(f"[DEBUG] Problemas guardados - Score: {problemas_score}, Data: {data}")
        
        return redirect(url_for('unidad', num=int(unidad[-1])))

    valores_guardados = session.get(f'problemas_form_{unidad_key}', {})
    return render_template('evaluar_problemas.html', valores=valores_guardados, unidad=unidad)



@app.route('/evaluar_explicacion_problemasP/<unidad>', methods=['GET', 'POST'])
def evaluar_explicacion_problemasP(unidad):
    unidad_num = unidad[-1]  # Extraer número de unidad, ej: 'unidad1' -> '1'
    
    if request.method == 'POST':
        data = request.form.to_dict()
        
        formatted_data = {}
        for key, value in data.items():
            if key.startswith('puntos_'):
                new_key = key.split('_')[-1]  
                formatted_data[key] = value
         
        explicacion_score = evaluar_explicacion_rule(formatted_data, unidad_num=unidad_num)
        
        session[f'valores_explicacion_unidad{unidad_num}'] = data
        session[f'explicacion_problemasP_score_unidad{unidad_num}'] = explicacion_score
        session.modified = True
        
        print(f"[DEBUG] Explicación guardada unidad {unidad_num} - Score: {explicacion_score}")
        
        return redirect(url_for('unidad', num=int(unidad_num)))

    valores = session.get(f'valores_explicacion_unidad{unidad_num}', {})
    return render_template('evaluar_explicacion_problemasP.html', unidad_num=unidad, valores=valores)



@app.route('/resultado_final')
def resultado_final():
    unidades = [session.get(f'unidad{i}', 0) for i in range(1, 5)]
    promedio = sum(unidades) / 4 if unidades else 0

    # Condición: promedio >= 70 Y todas las unidades >= 70
    aprobado = promedio >= 70 and all(u >= 70 for u in unidades)

    return render_template('resultado.html', promedio=promedio, aprobado=aprobado, unidades=unidades)




@app.route('/evaluar_exposicion/<unidad>', methods=['GET', 'POST'])
def evaluar_exposicion(unidad):
    unidad_key = f'unidad{unidad[-1]}'  # Extrae el número (ej: 'unidad4' -> '4')
    
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # Calcular puntaje total sumando todos los puntos
        total = sum(
            float(data.get(f'puntos_{i}', 0))
            for i in range(1, 12)  # Criterios del 1 al 11
        )
        
        # Guardar en sesión con clave específica
        session[f'exposicion_form_{unidad_key}'] = data
        session[f'exposicion_score_{unidad_key}'] = total
        session.modified = True
        
        print(f"[DEBUG] Exposición guardada - Puntaje: {total}, Data: {data}")
        
        return redirect(url_for('unidad', num=int(unidad[-1])))

    valores_guardados = session.get(f'exposicion_form_{unidad_key}', {})
    return render_template('evaluar_exposicion_proyecto.html', 
                         valores=valores_guardados, 
                         unidad=unidad)
    
    
    
    
@app.route('/evaluar_documentacion/<unidad>', methods=['GET', 'POST'])
def evaluar_documentacion(unidad):
    # Asegurar que solo sea para unidad 4
    if unidad != 'unidad4':
        abort(404, description="Esta evaluación solo está disponible para la Unidad 4")
    
    unidad_key = f'unidad{unidad[-1]}'  # Extrae '4' de 'unidad4'
    
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # Calcular puntaje total sumando todos los puntos_X
        total = sum(
            float(data.get(f'puntos_{i}', 0))
            for i in range(1, 6)  # Criterios del 1 al 5
        )
        
        # Guardar en sesión con claves específicas
        session[f'documentacion_form_{unidad_key}'] = data
        session[f'documentacion_score_{unidad_key}'] = total
        session[f'documentacion_total_{unidad_key}'] = total  # Puntaje crudo (0-100)
        session.modified = True  # Esto es CRUCIAL
        
        print(f"[DEBUG] Documentación guardada - Puntaje: {total}, Data: {data}")
        return redirect(url_for('unidad', num=4))

    # Cargar valores existentes si los hay
    valores = session.get(f'documentacion_form_{unidad_key}', {})
    
    # Debug: Verificar qué valores se están cargando
    print(f"[DEBUG] Valores cargados para documentación: {valores}")
    
    return render_template('evaluar_documentacion.html', 
                         unidad=unidad,
                         valores=valores)
    
    
@app.route('/unidad/4', methods=['GET', 'POST'])
def unidad_4():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        calificacion = calcular_puntos_unidad4(data)
        
        session['valores_unidad4'] = data
        session['unidad4'] = calificacion
        return redirect(url_for('unidad_4'))
    
    return render_template('unidad4.html', 
                         unidad=4,
                         valores=session.get('valores_unidad4', {}),
                         calificacion=session.get('unidad4'))

# --- Ruta opcional: limpiar sesión ---
@app.route('/reiniciar')
def reiniciar():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
