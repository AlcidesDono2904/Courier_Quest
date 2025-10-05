"""
Courier Quest - Primer Proyecto Programado
EIF-207 Estructuras de Datos
II Ciclo 2025
main.py
"""

import pygame
import json
from pathlib import Path
from src.logic.game import Game
from src.logic.main_menu import MainMenu


def main():
    """Punto de entrada del juego."""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Courier Quest")
    clock = pygame.time.Clock()

    # Bucle principal que controla el estado (menú o juego)
    while True:
        # Iniciar y correr el menú principal
        menu = MainMenu(screen, 1200, 800)
        action = run_menu_loop(menu, clock)

        # Si el usuario elige "NUEVA PARTIDA"
        if action == "start_game":
            print_game_intro()
            try:
                game = Game()
                game.run()
            except Exception as e:
                print(f"\nError al ejecutar el juego: {e}")
                raise
            break

        # Si el usuario elige "CARGAR PARTIDA"
        elif action == "load_game":
            if load_and_start_game(screen, clock):
                break
            # Si no hay guardado o se cancela, vuelve al menú
            continue

        # Si el usuario elige "RECORDS"
        elif action == "high_scores":
            show_high_scores(screen, clock)
            # Después de ver los records, vuelve al menú
            continue

        # Si el usuario elige "SALIR" o cierra la ventana del menú
        elif action == "exit":
            break

        else:
            print(f"Acción '{action}' no implementada. Saliendo.")
            break

    pygame.quit()


def load_and_start_game(screen, clock):
    """Intenta cargar una partida guardada y comenzar el juego."""
    save_path = Path("saves/slot1.sav")
    
    if not save_path.exists():
        show_message_screen(screen, clock, "No hay partida guardada", 
                           "No se encontró ninguna partida guardada.\nPresiona cualquier tecla para volver.")
        return False
    
    try:
        print_game_intro()
        game = Game()
        
        if game.load_game(1):
            print("Partida cargada exitosamente!")
            game.run()
            return True
        else:
            show_message_screen(screen, clock, "Error al cargar", 
                               "No se pudo cargar la partida.\nPresiona cualquier tecla para volver.")
            return False
            
    except Exception as e:
        print(f"Error al cargar partida: {e}")
        show_message_screen(screen, clock, "Error", 
                           f"Error al cargar: {str(e)}\nPresiona cualquier tecla para volver.")
        return False


def show_high_scores(screen, clock):
    """Muestra la pantalla de puntajes altos."""
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
        
        # Fondo degradado
        screen.fill((20, 20, 40))
        
        # Título
        title_surf = font_title.render("TABLA DE RECORDS", True, (0, 255, 136))
        title_rect = title_surf.get_rect(center=(600, 80))
        screen.blit(title_surf, title_rect)
        
        # Headers
        y = 160
        header_y = y
        headers = ["#", "Nombre", "Puntaje", "Ingresos", "Reputación", "Fecha"]
        x_positions = [100, 200, 400, 550, 720, 900]
        
        for i, header in enumerate(headers):
            text = font_header.render(header, True, (100, 181, 246))
            screen.blit(text, (x_positions[i], header_y))
        
        # Línea separadora
        pygame.draw.line(screen, (100, 181, 246), (80, y + 40), (1120, y + 40), 2)
        
        y += 60
        
        # Mostrar puntajes (top 10)
        if not scores:
            no_scores = font_score.render("No hay puntajes registrados aún", True, (150, 150, 150))
            no_scores_rect = no_scores.get_rect(center=(600, 350))
            screen.blit(no_scores, no_scores_rect)
        else:
            for i, score_data in enumerate(scores[:10]):
                # Alternar colores de fondo
                if i % 2 == 0:
                    pygame.draw.rect(screen, (30, 30, 50), (80, y - 5, 1040, 45))
                
                # Color especial para top 3
                if i == 0:
                    text_color = (255, 215, 0)  # Oro
                elif i == 1:
                    text_color = (192, 192, 192)  # Plata
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
    font_title = pygame.font.Font(None, 48)
    font_message = pygame.font.Font(None, 32)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                running = False
        
        screen.fill((20, 20, 40))
        
        # Título
        title_surf = font_title.render(title, True, (255, 100, 100))
        title_rect = title_surf.get_rect(center=(600, 250))
        screen.blit(title_surf, title_rect)
        
        # Mensaje (puede tener múltiples líneas)
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


def print_game_intro():
    """Imprime los controles e información del juego en la consola."""
    print("=" * 50)
    print("COURIER QUEST")
    print("=" * 50)
    print("\nControles:")
    print("  Flechas: Moverse")
    print("  A: Aceptar pedido (en punto de recogida)")
    print("  N/P: Siguiente/Anterior pedido")
    print("  S: Ordenar por prioridad")
    print("  D: Ordenar por deadline")
    print("  Enter: Completar entrega")
    print("  C: Cancelar pedido actual")
    print("  U: Deshacer")
    print("  F5: Guardar | F9: Cargar")
    print("\n¡Alcanza tu meta de ingresos antes del tiempo!")
    print("=" * 50)


if __name__ == "__main__":
    main()