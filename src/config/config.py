WEATHER_MULTIPLIERS = {
    "clear": 1.00,
    "clouds": 0.98,
    "rain_light": 0.90,
    "rain": 0.85,
    "storm": 0.75,
    "fog": 0.88,
    "wind": 0.92,
    "heat": 0.90
}

URL = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/"

# --- Constantes de Jugador y Reputación ---
REP_BONUS_EARLY = 5
REP_BONUS_ON_TIME = 3
REP_BONUS_STREAK = 2
REP_PENALTY_SLIGHTLY_LATE = -2
REP_PENALTY_LATE = -5
REP_PENALTY_VERY_LATE = -10
REP_PENALTY_CANCEL_ORDER = 4

# CAMBIO IMPORTANTE: Tiempo base de pedido en segundos (10 minutos = 600 segundos)
# Este es el tiempo que se usa para calcular si una entrega es "temprana" (20% antes del deadline)
ORDER_BASE_TIME_SECONDS = 600

# Constantes de resistencia
STAMINA_RECOVERY_RESTING = 5
STAMINA_RECOVERY_AT_POINT = 10
STAMINA_EXHAUSTED_THRESHOLD = 30