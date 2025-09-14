from datetime import datetime
import asyncio
from google.cloud.firestore_v1.base_query import FieldFilter
from services.firebase_service import db
from services.data_cache import DataCache

async def login_tutor(email: str, password: str) -> dict:
    """
    Autentica a un tutor y si es exitoso, carga los datos en caché

    Args:
        email (str): Email del tutor
        password (str): Contraseña del tutor

    Returns:
        dict: Datos del tutor si login es exitoso, None en caso contrario
    """
    try:
        # 1. Verificar credenciales contra Firestore
        query = db.collection("tutors").where(filter=FieldFilter("email", "==", email))
        docs = await asyncio.to_thread(query.get)
        
        if not docs:
            print(f"[AUTH] No existe tutor con email: {email}")
            return None
            
        tutor_data = docs[0].to_dict()
        
        if tutor_data.get("password") != password:
            print(f"[AUTH] Contraseña incorrecta para: {email}")
            return None
        
        print(f"[AUTH] Tutor autenticado: {email}")
        
        # 2. Inicializar y cargar caché
        cache = DataCache()
        await cache.load_all_data()
        
        # 3. Obtener datos del tutor desde el caché
        tutor = cache.get_tutor(docs[0].id)
        if not tutor:
            print(f"[AUTH ERROR] Tutor no encontrado en caché: {email}")
            return None

        # 4. Obtener usuarios de los grupos del tutor
        tutor_groups = tutor.get("groups", [])
        group_users = []
        for group in tutor_groups:
            group_users.extend(cache.get_users_by_group(group))

        # 5. Retornar datos del tutor con información de usuarios
        return {
            "id": tutor["doc_id"],
            "full_name": tutor.get("full_name", "Tutor"),
            "email": tutor.get("email", email),
            "groups": tutor_groups,
            "group_users": [
                {
                    "id": user["doc_id"],
                    "name": user.get("name"),
                    "email": user.get("email"),
                    "group": user.get("group"),
                    "recommendations": cache.get_user_recommendations(user["doc_id"]),
                    "responses": cache.get_user_responses(user["doc_id"])
                }
                for user in group_users
            ],
            "cache_updated_at": cache.last_update.isoformat() if cache.last_update else None
        }
        
    except Exception as e:
        print(f"[AUTH ERROR] Error en login: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def register_tutor(full_name: str, email: str, password: str, groups: list) -> dict:
    """
    Registra un nuevo tutor en el sistema

    Args:
        full_name (str): Nombre completo del tutor
        email (str): Email único del tutor
        password (str): Contraseña (debería estar hasheada en producción)
        groups (list): Lista de grupos asignados

    Returns:
        dict: {success: bool, error: str|None, tutor_id: str|None}
    """
    try:
        # 1. Verificar si el email ya existe
        query = db.collection("tutors").where(filter=FieldFilter("email", "==", email))
        existing_tutors = await asyncio.to_thread(query.get)
        
        if existing_tutors:
            return {
                "success": False,
                "error": "El email ya está registrado",
                "tutor_id": None
            }
        
        # 2. Crear nuevo tutor
        tutor_data = {
            "full_name": full_name,
            "email": email,
            "password": password,  # ¡En producción usar hashing!
            "groups": groups,
            "created_at": datetime.now(),
            "last_login": None
        }
        
        # 3. Guardar en Firestore
        doc_ref = await asyncio.to_thread(
            lambda: db.collection("tutors").add(tutor_data)
        )
        
        print(f"[AUTH] Nuevo tutor registrado: {email}")
        
        # 4. Actualizar caché
        cache = DataCache()
        await cache.load_all_data()
        
        return {
            "success": True,
            "error": None,
            "tutor_id": doc_ref[1].id
        }
        
    except Exception as e:
        print(f"[AUTH ERROR] Error en registro: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "tutor_id": None
        }