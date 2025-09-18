import pygame
from src.logic.player import Player
from src.logic.proxy import Proxy
from src.logic.weather import Weather
from src.logic.main_menu import MainMenu

class Game:
    def __init__(self, width=1024, height=768): # Aumentamos el tamaño para que el menú se vea mejor
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Courier Quest")
        
        self.running = True
        self.state = "MENU" # Estado inicial
        self.clock = pygame.time.Clock()
        
        # Instancias de clases del juego
        self.proxy = Proxy()
        self.player = None # Se inicializará al iniciar el juego
        self.weather = None # Se inicializará al iniciar el juego
        self.main_menu = MainMenu(self.screen, self.width, self.height)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if self.state == "MENU":
                    action = self.main_menu.handle_event(event)
                    if action == "start_game":
                        print("Iniciando nuevo juego...")
                        self.state = "GAMEPLAY"
                        # Aquí inicializarías el mapa, jugador, etc.
                        # self.player = Player(...)
                        # self.weather = Weather(...)
                    elif action == "load_game":
                        print("Cargando partida...")
                        # Lógica para cargar partida
                    elif action == "high_scores":
                        print("Mostrando récords...")
                        # Lógica para mostrar récords
                    elif action == "exit":
                        self.running = False
            
            if self.state == "MENU":
                self.main_menu.draw()
            elif self.state == "GAMEPLAY":
                self.screen.fill((0, 50, 0)) # Fondo verde oscuro para el juego
                # Aquí irá la lógica de actualización y dibujo del juego
                pygame.display.flip()
                
            self.clock.tick(60) # Limita el juego a 60 FPS
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()