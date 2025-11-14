"""
Courier Quest - Primer Proyecto Programado
EIF-207 Estructuras de Datos
II Ciclo 2025
main.py
"""

import pygame
import json
from datetime import datetime
from pathlib import Path

from src.logic.game import Game
from src.logic.main_menu import MainMenu
from src.logic.input_box import InputBox
from src.logic.game_state import GameState
from src.logic.button import Button 


def _format_elapsed(seconds: float) -> str:
    seconds = int(seconds or 0)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def choose_load_slot_with_preview(screen, clock, game_state: GameState):
    """Menú para elegir uno de 3 slots con vista previa. ESC para cancelar."""
    font_title = pygame.font.Font(None, 64)
    font_row = pygame.font.Font(None, 30)
    font_small = pygame.font.Font(None, 22)

    meta = game_state.list_slots_metadata()  
    selected = 0  
    slots = [1, 2, 3]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % 3
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % 3
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    return int(event.key - pygame.K_0)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return slots[selected]

        screen.fill((20, 20, 40))
        title_surf = font_title.render("Cargar Partida", True, (0, 255, 136))
        screen.blit(title_surf, title_surf.get_rect(center=(600, 100)))

        y = 220
        for i, slot in enumerate(slots):
            m = meta[slot]
            exists = m['exists']
            header = m['header'] or {}

            # Caja del slot
            rect = pygame.Rect(250, y - 16, 700, 84)
            if i == selected:
                pygame.draw.rect(screen, (35, 60, 90), rect, border_radius=12)
            else:
                pygame.draw.rect(screen, (30, 45, 70), rect, width=1, border_radius=12)

            # Título del slot
            label = f"Slot {slot} — {m['display_mtime'] if exists else 'vacío'}"
            color = (255, 255, 255) if exists else (140, 140, 140)
            screen.blit(font_row.render(label, True, color), (270, y - 8))

            # Preview si existe
            if exists:
                name = header.get('name', 'Player')
                income = header.get('income', 0)
                rep = header.get('reputation', 0)
                elapsed = _format_elapsed(header.get('elapsed', 0.0))
                prev = f"Jugador: {name}    Ingresos: ${income}    Reputación: {rep}    Tiempo: {elapsed}"
                screen.blit(font_small.render(prev, True, (220, 220, 220)), (270, y + 28))
            else:
                screen.blit(font_small.render("— vacío —", True, (160, 160, 160)), (270, y + 28))

            y += 100

        hint = "↑/↓ para seleccionar, Enter para confirmar, 1-3 acceso rápido, ESC para volver"
        hint_surf = font_small.render(hint, True, (200, 200, 200))
        screen.blit(hint_surf, hint_surf.get_rect(center=(600, 720)))

        pygame.display.flip()
        clock.tick(60)

# --- FUNCIÓN CORREGIDA: ELEGIR DIFICULTAD ---
def choose_difficulty_screen(screen, clock):
    """Menú para elegir la dificultad del rival IA."""
    font_title = pygame.font.Font(None, 64)
    font_small = pygame.font.Font(None, 24)

    # 1. Limpiar cola de eventos (defensivo)
    pygame.event.get()
    
    # 2. Variable de control para ignorar el mouse residual
    frame_counter = 0

    # Definición de botones
    button_width = 300
    button_height = 60
    spacing = 30
    
    center_x = (1200 - button_width) // 2
    start_y = 250

    buttons = {
        "easy": Button(
            "FÁCIL (Paseo relajado)",
            center_x, start_y,
            button_width, button_height,
            (40, 60, 40), (80, 150, 80), (255, 255, 255), (0, 255, 136), 2, 24
        ),
        "medium": Button(
            "MEDIO (Greedy Search)",
            center_x, start_y + button_height + spacing,
            button_width, button_height,
            (60, 60, 40), (150, 150, 80), (255, 255, 255), (255, 215, 0), 2, 24
        ),
        "hard": Button(
            "DIFÍCIL (A* Pathfinding)",
            center_x, start_y + 2 * (button_height + spacing),
            button_width, button_height,
            (60, 40, 40), (150, 80, 80), (255, 255, 255), (255, 100, 100), 2, 24
        )
    }

    running = True
    while running:
        # Controlar la velocidad y contar frames
        clock.tick(60) 
        frame_counter += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "menu"
            
            # --- CORRECCIÓN ROBUSTA: Ignorar eventos de mouse en los primeros frames ---
            if frame_counter < 5 and (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP):
                continue
            # -------------------------------------------------------------------------
            
            for key, button in buttons.items():
                if button.handle_event(event):
                    return key

        screen.fill((20, 20, 40))
        
        # Título
        title_surf = font_title.render("Seleccionar Dificultad del Rival", True, (0, 255, 136))
        screen.blit(title_surf, title_surf.get_rect(center=(600, 150)))
        
        # Dibujar botones
        for button in buttons.values():
            button.draw(screen)

        # Instrucción
        hint = "ESC para volver al Menú Principal"
        hint_surf = font_small.render(hint, True, (200, 200, 200))
        screen.blit(hint_surf, hint_surf.get_rect(center=(600, 720)))
        
        pygame.display.flip()
# --- FIN FUNCIÓN CORREGIDA ---


def main():
    """Punto de entrada del juego."""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Courier Quest")
    clock = pygame.time.Clock()

    # Bucle principal que controla el estado (menú o juego)
    while True:
        menu = MainMenu(screen, 1200, 800)
        action = run_menu_loop(menu, clock)

        # NUEVA PARTIDA
        if action == "start_game":
            
            # Limpiar cola de eventos, la corrección más fuerte está en choose_difficulty_screen
            pygame.event.get() 
            
            # 1. Elegir dificultad
            difficulty = choose_difficulty_screen(screen, clock)
            if difficulty in ["exit", "menu"]:
                if difficulty == "exit":
                    break
                continue
            
            # 2. Ingresar nombre
            player_name = ask_player_name(screen, clock)
            
            # 3. Mostrar instrucciones
            show_instructions_screen(screen, clock)
            
            try:
                # 4. Iniciar juego (Se pasa la dificultad)
                game = Game(player_name, difficulty) 
                result = game.run()        
                if result == "exit":
                    break                 
                continue                   
            except Exception as e:
                print(f"\nError al ejecutar el juego: {e}")
                continue                  

        elif action == "load_game":
            # MODIFICADO
            result = load_and_start_game(screen, clock)
            if result == "exit":
                break
            continue

        elif action == "high_scores":
            show_high_scores(screen, clock)
            continue

        elif action == "exit":
            break

        else:
            print(f"Acción '{action}' no implementada. Saliendo.")
            break

    pygame.quit()


def ask_player_name(screen, clock):
    """Muestra una pantalla para que el jugador ingrese su nombre."""
    # ... (Resto de la función ask_player_name)
    input_box = InputBox(400, 300, 400, 50)
    done = False
    player_name = "Player"

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            result = input_box.handle_event(event)
            if result is not None:
                player_name = result
                done = True

        input_box.update()
        screen.fill((20, 20, 40))

       
        title_font = pygame.font.Font(None, 64)
        title_surf = title_font.render("COURIER QUEST", True, (0, 255, 136))
        title_rect = title_surf.get_rect(center=(600, 150))
        screen.blit(title_surf, title_rect)

        prompt_font = pygame.font.Font(None, 36)
        prompt_surf = prompt_font.render("Ingresa tu nombre para comenzar:", True, (255, 255, 255))
        prompt_rect = prompt_surf.get_rect(center=(600, 250))
        screen.blit(prompt_surf, prompt_rect)

        input_box.draw(screen)

        # Instrucción para continuar
        instruction_font = pygame.font.Font(None, 24)
        instruction_surf = instruction_font.render("Presiona Enter para continuar...", True, (200, 200, 200))
        instruction_rect = instruction_surf.get_rect(center=(600, 400))
        screen.blit(instruction_surf, instruction_rect)

        pygame.display.flip()
        clock.tick(30)

    if not player_name.strip():
        player_name = "Player"
    return player_name


def show_instructions_screen(screen, clock):
    """Muestra la pantalla de instrucciones antes de empezar a jugar."""
    # ... (Resto de la función show_instructions_screen)
    font_title = pygame.font.Font(None, 64)
    font_header = pygame.font.Font(None, 36)
    font_text = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 20)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                running = False

        screen.fill((20, 20, 40))

        # Título
        title_surf = font_title.render("COURIER QUEST", True, (0, 255, 136))
        title_rect = title_surf.get_rect(center=(600, 80))
        screen.blit(title_surf, title_rect)

        # Subtítulo
        subtitle_surf = font_header.render("Instrucciones y Controles", True, (100, 181, 246))
        subtitle_rect = subtitle_surf.get_rect(center=(600, 150))
        screen.blit(subtitle_surf, subtitle_rect)

        # Controles
        controls_text = [
            "Objetivo: Alcanza tu meta de ingresos antes de que acabe el tiempo.",
            "",
            "Controles:",
            "  Flechas: Moverse",
            "  A: Aceptar pedido (en punto de recogida)",
            "  N/P: Siguiente/Anterior pedido",
            "  S: Ordenar inventario por prioridad",
            "  D: Ordenar inventario por fecha límite",
            "  Enter: Completar entrega (en punto de entrega)",
            "  C: Cancelar pedido actual",
            "  U: Deshacer último movimiento",
            "  F5: Guardar partida (auto-slot) | Cargar: Menú principal",
        ]

        y_offset = 220
        for line in controls_text:
            text_surf = font_text.render(line, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(600, y_offset))
            screen.blit(text_surf, text_rect)
            y_offset += 35

        # Instrucción para continuar
        instruction_surf = font_small.render("Presiona cualquier tecla o haz clic para continuar...", True, (200, 200, 200))
        instruction_rect = instruction_surf.get_rect(center=(600, 750))
        screen.blit(instruction_surf, instruction_rect)

        pygame.display.flip()
        clock.tick(60)


def load_and_start_game(screen, clock):
    """
    Selector visual de slots (1..3). Carga el elegido y arranca el juego.
    Devuelve "exit" si se debe SALIR de la app, "menu" si se vuelve al MENÚ.
    """
    try:
        gs = GameState()
        
        # Limpiar cola de eventos antes de la nueva pantalla
        pygame.event.get() 
        
        slot = choose_load_slot_with_preview(screen, clock, gs)
        if slot is None:
            return "menu"

        data = gs.load_game(slot)
        if data:
            player_name = data.get('player_name', 'Player')
            # MODIFICACIÓN: Se pasa una dificultad por defecto al cargar.
            game = Game(player_name, "hard")
            game.load_game(data)
            game.loaded_slot = slot
            print(f"Partida cargada exitosamente desde Slot {slot}!")
            return game.run()   
        else:
            show_message_screen(
                screen, clock, "Error al cargar",
                f"No se pudo cargar la partida del Slot {slot}.\nPresiona cualquier tecla para volver."
            )
            return "menu"

    except Exception as e:
        print(f"Error al cargar partida: {e}")
        show_message_screen(
            screen, clock, "Error",
            f"Error al cargar: {str(e)}\nPresiona cualquier tecla para volver."
        )
        return "menu"


def show_high_scores(screen, clock):
    """Muestra la pantalla de puntajes altos."""
    # ... (Resto de la función show_high_scores)
    # Cargar puntajes
    try:
        with open("data/puntajes.json", 'r') as f:
            scores = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        scores = []

    font_title = pygame.font.Font(None, 64)
    font_header = pygame.font.Font(None, 32)
    font_score = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 20)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                running = False

        # Fondo
        screen.fill((20, 20, 40))

        # Título
        title_surf = font_title.render("TABLA DE RECORDS", True, (0, 255, 136))
        title_rect = title_surf.get_rect(center=(600, 80))
        screen.blit(title_surf, title_rect)

        # Headers
        y = 160
        headers = ["#", "Nombre", "Puntaje", "Ingresos", "Reputación", "Fecha"]
        x_positions = [100, 200, 400, 550, 720, 900]
        for i, header in enumerate(headers):
            text = font_header.render(header, True, (100, 181, 246))
            screen.blit(text, (x_positions[i], y))

        pygame.draw.line(screen, (100, 181, 246), (80, y + 40), (1120, y + 40), 2)
        y += 60

        # Puntajes (top 10)
        if not scores:
            no_scores = font_score.render("No hay puntajes registrados aún", True, (150, 150, 150))
            no_scores_rect = no_scores.get_rect(center=(600, 350))
            screen.blit(no_scores, no_scores_rect)
        else:
            for i, score_data in enumerate(scores[:10]):
                if i % 2 == 0:
                    pygame.draw.rect(screen, (30, 30, 50), (80, y - 5, 1040, 45))

                if i == 0:
                    text_color = (255, 215, 0)   # Oro
                elif i == 1:
                    text_color = (192, 192, 192) # Plata
                elif i == 2:
                    text_color = (205, 127, 50)  # Bronce
                else:
                    text_color = (255, 255, 255)

                # Ranking
                rank = font_score.render(f"{i + 1}", True, text_color)
                screen.blit(rank, (x_positions[0], y))

                # Nombre
                name = font_score.render(score_data.get('name', 'Player'), True, text_color)
                screen.blit(name, (x_positions[1], y))

                # Puntaje
                score = font_score.render(str(score_data.get('score', 0)), True, text_color)
                screen.blit(score, (x_positions[2], y))

                # Ingresos
                income = font_score.render(f"${score_data.get('income', 0)}", True, text_color)
                screen.blit(income, (x_positions[3], y))

                # Reputación
                rep = score_data.get('reputation', 0)
                rep_color = (50, 255, 100) if rep >= 70 else (255, 200, 50) if rep >= 40 else (255, 50, 50)
                reputation = font_score.render(str(rep), True, rep_color)
                screen.blit(reputation, (x_positions[4], y))

                # Fecha
                date_str = score_data.get('date', '')
                if 'T' in date_str:
                    date_str = date_str.split('T')[0]
                date = font_small.render(date_str, True, (150, 150, 150))
                screen.blit(date, (x_positions[5], y + 5))

                y += 50

        # Instrucciones
        instruction = font_small.render("Presiona cualquier tecla para volver al menú", True, (200, 200, 200))
        instruction_rect = instruction.get_rect(center=(600, 750))
        screen.blit(instruction, instruction_rect)

        pygame.display.flip()
        clock.tick(60)


def show_message_screen(screen, clock, title, message):
    """Muestra una pantalla de mensaje temporal."""
    # ... (Resto de la función show_message_screen)
    font_title = pygame.font.Font(None, 48)
    font_message = pygame.font.Font(None, 32)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        # cerrar con cualquier tecla
        keys = pygame.key.get_pressed()
        if any(keys):
            running = False

        screen.fill((20, 20, 40))

        # Título
        title_surf = font_title.render(title, True, (255, 100, 100))
        title_rect = title_surf.get_rect(center=(600, 250))
        screen.blit(title_surf, title_rect)

        # Mensaje (múltiples líneas)
        y = 320
        for line in message.split('\n'):
            msg_surf = font_message.render(line, True, (255, 255, 255))
            msg_rect = msg_surf.get_rect(center=(600, y))
            screen.blit(msg_surf, msg_rect)
            y += 40

        pygame.display.flip()
        clock.tick(60)


def run_menu_loop(menu, clock):
    """Maneja el bucle de eventos y dibujado del menú principal."""
    while True:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"

            action = menu.handle_event(event)
            if action:
                return action

        menu.update(dt)
        menu.draw()


if __name__ == "__main__":
    main()