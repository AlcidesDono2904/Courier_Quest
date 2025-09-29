import pygame
from .logic.GameLoop import GameLoop
from src.logic.player import Player
from src.logic.proxy import Proxy
from src.logic.weather import Weather
from src.logic.main_menu import MainMenu

class Game:
    def __init__(self, width=1200, height=800):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Courier Quest - Urban Delivery Challenge")
        
        self.running = True
        self.state = "MENU"
        self.clock = pygame.time.Clock()
        
        self.last_time = pygame.time.get_ticks()
        
        self.proxy = Proxy()
        self.player = None
        self.weather = None
        self.main_menu = MainMenu(self.screen, self.width, self.height)

    def run(self):
        while self.running:
           
            current_time = pygame.time.get_ticks()
            dt = (current_time - self.last_time) / 1000.0  # Convertir a segundos
            self.last_time = current_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if self.state == "MENU":
                    action = self.main_menu.handle_event(event)
                    if action == "start_game":
                        print("Iniciando nuevo juego...")
                        self.state = "GAMEPLAY"
                    elif action == "load_game":
                        print("Cargando partida...")
                    elif action == "high_scores":
                        print("Mostrando récords...")
                    elif action == "exit":
                        self.running = False
            
            
            if self.state == "MENU":
               
                self.main_menu.update(dt)
            
                self.main_menu.draw()
            elif self.state == "GAMEPLAY":
                try:
                    game_loop = GameLoop()
                    game_loop.run()
                except Exception as e:
                    print(f"Error en el demo: {e}")
                    import traceback
                    traceback.print_exc()
                finally:
                    pygame.quit()              
                
            self.clock.tick(60)
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()