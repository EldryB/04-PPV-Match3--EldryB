# Match3

## Interacción (Drag & Drop) 
Captura: En PlayState.py, al presionar el clic, se guarda la baldosa seleccionada (self.dragged_tile) y su posición original.
Arrastre: update() actualiza constantemente las coordenadas de la baldosa para que siga el cursor.
Liberación: Al soltar el clic, si el movimiento fue de 1 celda (adyacente), se intenta el intercambio. Si fue en la misma celda (distancia 0), se intenta detonar un Power-Up.

## Restricción de Movimientos 
Validación: Se realiza un intercambio *temporal* en la matriz (self.board.tiles) y se evalúa con calculate_matches_for().
Reversión: Si resulta en un match, se confirma y procesa. Si devuelve None, el intercambio se deshace y la baldosa regresa a su origen animada con Timer.tween.

## Reordenamiento Automático
Detección: En Board.py, has_possible_moves() simula intercambios para buscar jugadas, mientras que check_powerup() verifica si hay algún power-up activable.
Reinicio: Al final del turno en PlayState.py, si no existen movimientos ni power-ups, un ciclo while ejecuta _initialize_tiles() iterativamente hasta asegurar un tablero jugable.

## Implementación de Power-Ups
Generación: En _calculate_matches (PlayState.py), si un match es de 4+ (Línea) o 5+ (Bomba), se identifica la baldosa exacta que movió el jugador (epicenter). Se le asigna el tipo de power-up y se salva de ser destruida, conservando su color.
Activación: Detonan de dos formas: al formar parte de otro match o mediante un clic directo.
Efectos: Gestionados por get_powerup_effect(tile) en Board.py. "line" añade a la lista de destrucción toda su fila y columna; "bomb" añade todas las baldosas del tablero que compartan su color.


# NOTA
En el video, para probar la bomba desactive la verificacion de movimientos validos