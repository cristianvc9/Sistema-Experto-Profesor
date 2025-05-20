from flask import request, session

def evaluar_unidad(data):
    total = 0

    # Sumar componentes básicos 
    total += float(data.get("examen", 0)) * 35
    total += float(data.get("problemas_ad", 0)) * 5
    total += float(data.get("participacion", 0)) * 5
    total += float(data.get("curso", 0)) * 5
    total += float(data.get("pextras", 0)) * 5
    total += float(data.get("puntualidad", 0)) * 5

    # Obtener puntajes directamente de los datos pasados
    problemas = float(data.get("problemas_score", 0))
    explicacion = float(data.get("explicacion_score", 0))

    print(f"[DEBUG FINAL] Puntaje Problemas: {problemas}")
    print(f"[DEBUG FINAL] Puntaje Explicación: {explicacion}")

    total += problemas
    total += explicacion

    print(f"[DEBUG FINAL] Total final de unidad: {total}")
    return round(total, 2)


def evaluar_problemas_rule(data):
    raw_score = (
        float(data.get("puntos_1", 0)) +
        float(data.get("puntos_2", 0)) +
        float(data.get("puntos_3", 0)) +
        float(data.get("puntos_4", 0)) +
        float(data.get("puntos_5", 0))
    )

    max_possible = 100
    if max_possible > 0:
        porcentaje = (raw_score / max_possible) * 100
    else:
        porcentaje = 0

    session['problemas_score'] = porcentaje
    session.modified = True

    print(f"[DEBUG] Problemas - Raw: {raw_score}, Porcentaje: {porcentaje}%")

    if porcentaje >= 70:
        return 35  # IF porcentaje >= 70 THEN asigna 35
    else:
        return 0   # ELSE asigna 0


def evaluar_explicacion_rule(data, unidad_num='4'):
    config = PUNTUACIONES['unidad4']['rubricas']['explicacion_problemasP']
    total = sum(float(data.get(key, 0)) for key in data if key.startswith('puntos_'))

    if config['max_puntos'] > 0:
        porcentaje = (total / config['max_puntos']) * 100
    else:
        porcentaje = 0

    # Guarda correctamente en la sesión
    session[f'explicacion_problemasP_score_unidad{unidad_num}'] = porcentaje
    session.modified = True

    print(f"[DEBUG] Explicación - Total: {total}, Porcentaje: {porcentaje}%")

    if porcentaje >= 70:
        return config['peso'] * 100  # Esto da 5.0
    else:
        return 0



def evaluar_documentacion_rule(data):
    config = PUNTUACIONES['unidad4']['rubricas']['documentacion']
    total = sum(float(data.get(f'puntos_{i}', 0)) for i in range(1, 6))

    if config['max_puntos'] > 0:
        porcentaje = (total / config['max_puntos']) * 100
    else:
        porcentaje = 0

    session['documentacion_score_unidad4'] = porcentaje
    session.modified = True

    print(f"[DEBUG] Documentación - Total: {total}, Porcentaje: {porcentaje}%")

    if porcentaje >= 70:
        return config['peso'] * 100
    else:
        return 0


def calcular_puntos_unidad4(data):
    config = PUNTUACIONES['unidad4']

    puntos_base = 0
    for componente, puntos in config['componentes'].items():
        if data.get(componente) == '1':
            puntos_base += puntos  # IF está seleccionado, THEN suma el valor

    puntos_rubricas = 0
    for nombre_rubrica, config_rubrica in config['rubricas'].items():
        porcentaje = float(session.get(f'{nombre_rubrica}_score_unidad4', 0))
        print(f"[DEBUG] Rúbrica {nombre_rubrica} - Porcentaje: {porcentaje}")

        if porcentaje >= 70:
            puntos_rubricas += config_rubrica['peso'] * 100
        else:
            puntos_rubricas += 0
            


    return round(puntos_base + puntos_rubricas, 2)


def evaluar_exposicion_rule(data):
    config = PUNTUACIONES['unidad4']['rubricas']['exposicion']
    total = sum(float(data.get(f'puntos_{i}', 0)) for i in range(1, 12))

    if config['max_puntos'] > 0:
        porcentaje = (total / config['max_puntos']) * 100
    else:
        porcentaje = 0

    session['exposicion_score_unidad4'] = porcentaje
    session.modified = True

    print(f"[DEBUG] Exposición - Total: {total}, Porcentaje: {porcentaje}%")

    if porcentaje >= 70:
        return config['peso'] * 100
    else:
        return 0


# Puntuaciones de componentes y rúbricas
PUNTUACIONES = {
    'unidad4': {
        'componentes': {
            'examen': 20,
            'problemas_ad': 5,
            'participacion': 5,
            'curso': 5,
            'opciones_extra': 5,
            'beneficio_comunidad': 5
        },
        'rubricas': {
            'exposicion': {'max_puntos': 100, 'peso': 0.30},
            'documentacion': {'max_puntos': 100, 'peso': 0.20},
            'explicacion_problemasP': {'max_puntos': 100, 'peso': 0.05}
        }
    }
}
