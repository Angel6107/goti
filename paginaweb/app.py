import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
import random
import datetime

# --- Configuración de la Aplicación Flask ---
app = Flask(__name__)

# Configuración de JWT
# ¡IMPORTANTE! Cambia esto por una clave secreta fuerte y mantenla segura.
# Puedes usar os.urandom(24) para generar una. No la compartas.
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY', 'tu-clave-secreta-muy-fuerte-cambiar')
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=1) # Duración del token
jwt = JWTManager(app)

# Configuración de CORS para permitir peticiones desde cualquier origen a la API
# En producción, deberías restringir esto a los orígenes de tu frontend.
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- Simulación de Base de Datos (en memoria) ---
# En una aplicación real, usarías una base de datos (SQLite, PostgreSQL, MongoDB, etc.)
users = {
    # Ejemplo de usuario (la contraseña se hashea al registrar)
    # "testuser": {
    #     "email": "test@example.com",
    #     "password_hash": generate_password_hash("password123"),
    #     "virtual_balance": 1000,
    #     "is_subscribed": False,
    #     "subscription_tier": None
    # }
}

# Lista de juegos (incluyendo el de dados lite)
games = [
    # --- Juegos de Mesa ---
    {
        "id": "dados-lite",
        "name": "Dados del Jaguar (Lite)",
        "description": "Lanza los dados y prueba tu suerte en esta versión rápida y divertida. ¡Ideal para empezar!",
        "imageUrl": "https://via.placeholder.com/600x360/E4AF00/1E1E1E?text=Dados+Lite",
        "category": "table",
        "type": "lite_frontend", # Se juega en el navegador (modal Lite)
        "liteGameType": "dados" # Identificador para la lógica JS del modal Lite
    },
    {
        "id": "ruleta-azteca",
        "name": "Ruleta del Sol",
        "description": "Apuesta a tus números sagrados y observa girar la rueda del destino.",
        "imageUrl": "https://via.placeholder.com/600x360/C62828/FFFFFF?text=Ruleta+Azteca",
        "category": "table",
        "type": "simulated_frontend" # Simulación visual en el frontend
    },
     {
        "id": "blackjack-obsidiana",
        "name": "Blackjack Obsidiana",
        "description": "¿Podrás vencer al tallador y acercarte a 21 sin pasarte? Requiere suscripción.",
        "imageUrl": "https://via.placeholder.com/600x360/1E1E1E/9CDCFE?text=Blackjack",
        "category": "table",
        "type": "simulated_backend" # Requiere llamada al backend para jugar
    },
    # --- Casino en Vivo (Simulado) ---
    {
        "id": "live-roulette",
        "name": "Ruleta en Vivo: Templo Dorado",
        "description": "Siente la emoción con crupieres reales en nuestra sala más exclusiva (simulado).",
        "imageUrl": "https://via.placeholder.com/600x360/FFD700/000000?text=Live+Roulette",
        "category": "live",
        "type": "simulated_frontend"
    },
    {
        "id": "live-blackjack",
        "name": "Blackjack en Vivo: Sala Quetzal",
        "description": "Mesas interactivas con apuestas en tiempo real (simulado).",
        "imageUrl": "https://via.placeholder.com/600x360/2E7D32/FFFFFF?text=Live+Blackjack",
        "category": "live",
        "type": "simulated_frontend"
    },
    # --- Bingo y Keno ---
    {
        "id": "bingo-pluma",
        "name": "Bingo Pluma Sagrada",
        "description": "Completa tu cartón y canta ¡Bingo! para ganar grandes tributos.",
        "imageUrl": "https://via.placeholder.com/600x360/4DD0E1/1E1E1E?text=Bingo+Pluma",
        "category": "bingo",
        "type": "simulated_frontend"
    },
    {
        "id": "keno-estelar",
        "name": "Keno Estelar",
        "description": "Elige tus números de la suerte y espera el sorteo celestial. Requiere suscripción.",
        "imageUrl": "https://via.placeholder.com/600x360/569CD6/FFFFFF?text=Keno+Estelar",
        "category": "bingo", # Keno a menudo se agrupa con Bingo
        "type": "simulated_backend"
    },
    # --- Promociones ---
    {
        "id": "promo-bienvenida",
        "name": "Ofrenda de Bienvenida",
        "description": "Únete al clan Quetzal o Jaguar y recibe un generoso bono inicial de Tributo.",
        "imageUrl": "https://via.placeholder.com/600x360/6A9955/FFFFFF?text=Bono+Bienvenida",
        "category": "promotions",
        "type": "info" # Solo informativo
    },
    {
        "id": "promo-recarga",
        "name": "Recarga del Guerrero",
        "description": "Obtén un bono extra en tu primer depósito de Tributo de la semana (simulado).",
        "imageUrl": "https://via.placeholder.com/600x360/C586C0/1E1E1E?text=Bono+Recarga",
        "category": "promotions",
        "type": "info"
    }
]

# --- Rutas de API ---

# === Autenticación ===
@app.route('/api/auth/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"message": "Faltan datos (usuario, email, contraseña)"}), 400

    if username in users:
        return jsonify({"message": "El nombre de usuario ya existe."}), 409 # Conflict

    # Validaciones básicas (se pueden mejorar)
    if '@' not in email or '.' not in email.split('@')[-1]:
         return jsonify({"message": "Formato de correo inválido."}), 400
    if len(password) < 6:
         return jsonify({"message": "La contraseña debe tener al menos 6 caracteres."}), 400


    hashed_password = generate_password_hash(password)
    users[username] = {
        "email": email,
        "password_hash": hashed_password,
        "virtual_balance": 100, # Saldo inicial por defecto al registrarse
        "is_subscribed": False,
        "subscription_tier": None
    }
    print(f"Usuario registrado: {username}") # Log en consola
    return jsonify({"message": "Usuario registrado exitosamente."}), 201

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Faltan datos (usuario, contraseña)"}), 400

    user_data = users.get(username)

    if user_data and check_password_hash(user_data['password_hash'], password):
        # Contraseña correcta, crear token JWT
        access_token = create_access_token(identity=username)
        print(f"Usuario logueado: {username}") # Log en consola
        # Devolver token y datos básicos del usuario (sin el hash!)
        user_profile = {
            "username": username,
            "email": user_data["email"],
            "virtual_balance": user_data["virtual_balance"],
            "is_subscribed": user_data["is_subscribed"],
            "subscription_tier": user_data["subscription_tier"]
        }
        return jsonify(token=access_token, user=user_profile), 200
    else:
        return jsonify({"message": "Credenciales inválidas."}), 401 # Unauthorized

# === Perfil de Usuario ===
@app.route('/api/user/profile', methods=['GET'])
@jwt_required() # Requiere un token JWT válido en el header Authorization: Bearer <token>
def get_user_profile():
    current_user_identity = get_jwt_identity() # Obtiene el 'identity' (username en este caso) del token
    user_data = users.get(current_user_identity)

    if user_data:
        # Devolver datos del perfil (excluyendo el hash de la contraseña)
        user_profile = {
            "username": current_user_identity,
            "email": user_data["email"],
            "virtual_balance": user_data["virtual_balance"],
            "is_subscribed": user_data["is_subscribed"],
            "subscription_tier": user_data["subscription_tier"]
        }
        return jsonify(user_profile), 200
    else:
        # Esto no debería pasar si el token es válido y el usuario no ha sido borrado
        return jsonify({"message": "Usuario no encontrado."}), 404

# === Juegos ===
@app.route('/api/games', methods=['GET'])
def get_games():
    category = request.args.get('category') # Obtener ?category= de la URL
    if category and category != 'all':
        filtered_games = [game for game in games if game.get('category') == category]
        return jsonify(filtered_games), 200
    else:
        # Devolver todos los juegos si no hay filtro o es 'all'
        return jsonify(games), 200

# === Jugar (Simulado Backend) ===
@app.route('/api/play/<game_id>', methods=['POST'])
@jwt_required()
def play_game_backend(game_id):
    current_user_identity = get_jwt_identity()
    user_data = users.get(current_user_identity)

    if not user_data:
        return jsonify({"success": False, "message": "Usuario no encontrado."}), 404

    # --- Verificación de Suscripción ---
    if not user_data.get("is_subscribed", False):
         return jsonify({
             "success": False,
             "message": "Se requiere una suscripción activa para jugar este juego."
             }), 403 # Forbidden

    # Encontrar el juego
    game_info = next((game for game in games if game["id"] == game_id), None)
    if not game_info:
        return jsonify({"success": False, "message": "Juego no encontrado."}), 404

    if game_info.get("type") != "simulated_backend":
         return jsonify({"success": False, "message": "Este juego no se ejecuta en el servidor."}), 400

    # --- Simulación de la lógica del juego ---
    # Aquí iría la lógica específica para cada game_id de backend
    # Por ahora, una simulación genérica que gasta y a veces gana
    cost_to_play = 10 # Costo fijo por jugar (simulado)
    win_chance = 0.3 # 30% de probabilidad de ganar
    win_multiplier = 5 # Multiplicador de ganancia

    if user_data["virtual_balance"] < cost_to_play:
        return jsonify({
            "success": False,
            "message": f"Saldo insuficiente para jugar a {game_info['name']} (Necesitas {cost_to_play} Tributo)."
            }), 400 # Bad Request (o 402 Payment Required)

    # Cobrar por jugar
    user_data["virtual_balance"] -= cost_to_play
    result_message = f"Jugaste a {game_info['name']}. Costo: {cost_to_play} Tributo. "

    # Simular resultado
    if random.random() < win_chance:
        winnings = cost_to_play * win_multiplier
        user_data["virtual_balance"] += winnings
        result_message += f"¡Ganaste {winnings} Tributo!"
    else:
        result_message += "No hubo suerte esta vez."

    # Actualizar usuario en nuestra "DB"
    users[current_user_identity] = user_data

    print(f"Usuario {current_user_identity} jugó a {game_id}. Saldo: {user_data['virtual_balance']}") # Log

    # Devolver resultado y perfil actualizado
    user_profile = {
        "username": current_user_identity,
        "email": user_data["email"],
        "virtual_balance": user_data["virtual_balance"],
        "is_subscribed": user_data["is_subscribed"],
        "subscription_tier": user_data["subscription_tier"]
    }
    return jsonify({"success": True, "message": result_message, "user": user_profile}), 200


# === Suscripción (Simulada) ===
@app.route('/api/subscribe', methods=['POST'])
@jwt_required()
def subscribe_user():
    current_user_identity = get_jwt_identity()
    user_data = users.get(current_user_identity)

    if not user_data:
        return jsonify({"success": False, "message": "Usuario no encontrado."}), 404

    data = request.get_json()
    tier = data.get('tier')

    if not tier or tier not in ["Obsidiana", "Quetzal", "Jaguar"]:
        return jsonify({"success": False, "message": "Nivel de suscripción inválido."}), 400

    # Simular actualización de suscripción y bono
    user_data["is_subscribed"] = True
    user_data["subscription_tier"] = tier

    bonus_amount = 0
    if tier == "Obsidiana":
        bonus_amount = 100
    elif tier == "Quetzal":
         bonus_amount = 500
    elif tier == "Jaguar":
         bonus_amount = 1500

    user_data["virtual_balance"] += bonus_amount

    # Actualizar usuario en "DB"
    users[current_user_identity] = user_data

    print(f"Usuario {current_user_identity} suscrito al plan {tier}. Saldo: {user_data['virtual_balance']}") # Log

    # Devolver mensaje y perfil actualizado
    user_profile = {
        "username": current_user_identity,
        "email": user_data["email"],
        "virtual_balance": user_data["virtual_balance"],
        "is_subscribed": user_data["is_subscribed"],
        "subscription_tier": user_data["subscription_tier"]
    }
    return jsonify({
        "success": True,
        "message": f"¡Felicidades! Te has suscrito al Plan {tier} y has recibido {bonus_amount} Tributo.",
        "user": user_profile
    }), 200


# --- Ejecución del Servidor ---
if __name__ == '__main__':
    # Escucha en todas las interfaces (0.0.0.0) en el puerto 5000
    # El modo debug recarga automáticamente el servidor al guardar cambios.
    # ¡NO USAR debug=True EN PRODUCCIÓN!
    app.run(host='0.0.0.0', port=5000, debug=True)