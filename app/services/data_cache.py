from datetime import datetime
import asyncio
from typing import Dict, List
from services.firebase_service import db
from google.cloud.firestore_v1.base_query import FieldFilter
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DataCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataCache, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Inicializa el caché vacío"""
        self.tutors: Dict[str, dict] = {}
        self.users: Dict[str, dict] = {}
        self.responses: Dict[str, List[dict]] = {}
        self.last_update: datetime = None
        logger.debug("DataCache inicializado")

    async def load_all_data(self):
        """Carga/actualiza todos los datos desde Firestore"""
        try:
            logger.debug("[CACHE] Cargando datos...")
            await asyncio.gather(
                self._load_tutors(),
                self._load_users_and_recommendations(),
                self._load_responses()
            )
            self.last_update = datetime.now()
            logger.info(f"[CACHE] Datos cargados. Tutores: {len(self.tutors)}, Usuarios: {len(self.users)}, Respuestas: {sum(len(r) for r in self.responses.values())}")
        except Exception as e:
            logger.error(f"[CACHE ERROR] Error al cargar datos: {str(e)}")
            raise

    async def _load_tutors(self):
        """Carga todos los tutores desde Firestore"""
        try:
            tutors_ref = await asyncio.to_thread(
                lambda: db.collection("tutors").get()
            )
            self.tutors = {
                tutor.id: {
                    **tutor.to_dict(),
                    "doc_id": tutor.id,
                    "groups": tutor.to_dict().get("groups", [])
                }
                for tutor in tutors_ref
            }
            logger.debug(f"[CACHE] Cargados {len(self.tutors)} tutores")
        except Exception as e:
            logger.error(f"[CACHE ERROR] Error al cargar tutores: {str(e)}")
            raise

    async def _load_users_and_recommendations(self):
        """Carga todos los usuarios y sus recomendaciones desde Firestore"""
        try:
            users_ref = await asyncio.to_thread(
                lambda: db.collection("users").get()
            )
            self.users = {}
            for user in users_ref:
                user_data = user.to_dict()
                user_data["doc_id"] = user.id
                user_data["group"] = user_data.get("group", "")
                recommendations_ref = await asyncio.to_thread(
                    lambda: db.collection("users").document(user.id).collection("recomendaciones").get()
                )
                user_data["recommendations"] = [
                    {
                        **rec.to_dict(),
                        "doc_id": rec.id,
                        "fecha": rec.to_dict().get("fecha", datetime.now())
                    }
                    for rec in recommendations_ref
                ]
                self.users[user.id] = user_data
            logger.debug(f"[CACHE] Cargados {len(self.users)} usuarios con recomendaciones")
        except Exception as e:
            logger.error(f"[CACHE ERROR] Error al cargar usuarios y recomendaciones: {str(e)}")
            raise

    async def _load_responses(self):
        """Carga todas las respuestas desde Firestore"""
        try:
            responses_ref = await asyncio.to_thread(
                lambda: db.collection("respuestas_cuestionarios").get()
            )
            self.responses = {}
            for response in responses_ref:
                resp_data = response.to_dict()
                user_id = resp_data.get("id_user")
                if not user_id:
                    logger.warning(f"[CACHE] Respuesta sin id_user: {response.id}")
                    continue
                # Convertir date a datetime si es necesario
                if isinstance(resp_data.get("date"), str):
                    try:
                        resp_data["date"] = datetime.fromisoformat(resp_data["date"].replace("Z", "+00:00"))
                    except ValueError:
                        logger.warning(f"[CACHE] Formato de fecha inválido en respuesta {response.id}")
                        continue
                if user_id not in self.responses:
                    self.responses[user_id] = []
                self.responses[user_id].append({
                    **resp_data,
                    "doc_id": response.id
                })
            logger.debug(f"[CACHE] Cargadas respuestas para {len(self.responses)} usuarios")
        except Exception as e:
            logger.error(f"[CACHE ERROR] Error al cargar respuestas: {str(e)}")
            raise

    def get_tutor(self, tutor_id: str) -> dict:
        """Obtiene datos de un tutor desde el caché"""
        tutor = self.tutors.get(tutor_id, {})
        logger.debug(f"[CACHE] Obteniendo tutor {tutor_id}: {'encontrado' if tutor else 'no encontrado'}")
        return tutor

    def get_users_by_group(self, group: str) -> List[dict]:
        """Obtiene usuarios de un grupo específico desde el caché"""
        users = [
            user_data for user_data in self.users.values()
            if user_data.get("group") == group
        ]
        logger.debug(f"[CACHE] Obtenidos {len(users)} usuarios para el grupo {group}")
        return users

    def get_user_recommendations(self, user_id: str) -> Dict[str, str]:
        """Obtiene las recomendaciones más recientes de un usuario en formato {cuestionario: recomendacion}"""
        user = self.users.get(user_id, {})
        recommendations = user.get("recommendations", [])
        result = {"BAI": "N/A", "BDI": "N/A", "PSS": "N/A"}
        # Ordenar por fecha descendente y tomar la más reciente por tipo
        sorted_recs = sorted(
            recommendations,
            key=lambda x: x.get("fecha", datetime.now()),
            reverse=True
        )
        for rec in sorted_recs:
            rec_type = rec.get("cuestionario")
            if rec_type in result and result[rec_type] == "N/A":
                result[rec_type] = rec.get("recomendacion", "N/A")
        logger.debug(f"[CACHE] Obtenidas recomendaciones para usuario {user_id}: {result}")
        return result

    def get_user_responses(self, user_id: str) -> List[dict]:
        """Obtiene respuestas de un usuario desde el caché"""
        responses = self.responses.get(user_id, [])
        logger.debug(f"[CACHE] Obtenidas {len(responses)} respuestas para usuario {user_id}: {[r.get('date') for r in responses]}")
        return responses

    async def get_tutor_groups(self, tutor_id: str) -> List[str]:
        """Obtiene la lista de grupos de un tutor desde el caché"""
        try:
            tutor = self.get_tutor(tutor_id)
            groups = tutor.get("groups", []) if tutor else []
            logger.debug(f"[CACHE] Obtenidos {len(groups)} grupos para tutor {tutor_id}")
            return groups
        except Exception as e:
            logger.error(f"[CACHE ERROR] Error al obtener grupos para tutor {tutor_id}: {str(e)}")
            raise

    async def add_tutor_group(self, tutor_id: str, group_name: str):
        """Agrega un grupo al tutor y actualiza el caché"""
        try:
            tutor_ref = db.collection("tutors").document(tutor_id)
            tutor = await asyncio.to_thread(tutor_ref.get)
            if not tutor.exists:
                raise ValueError(f"Tutor {tutor_id} no encontrado")
            groups = tutor.to_dict().get("groups", []) + [group_name]
            await asyncio.to_thread(tutor_ref.set, {"groups": groups}, merge=True)
            self.tutors[tutor_id] = {
                **tutor.to_dict(),
                "doc_id": tutor_id,
                "groups": groups
            }
            self.users.clear()  # Invalidar caché de usuarios
            self.responses.clear()  # Invalidar respuestas
            logger.info(f"[CACHE] Grupo {group_name} agregado al tutor {tutor_id}")
        except Exception as e:
            logger.error(f"[CACHE ERROR] Error al agregar grupo {group_name} al tutor {tutor_id}: {str(e)}")
            raise

    async def update_tutor_group(self, tutor_id: str, old_group_name: str, new_group_name: str):
        """Actualiza el nombre de un grupo del tutor y refresca el caché"""
        try:
            tutor_ref = db.collection("tutors").document(tutor_id)
            tutor = await asyncio.to_thread(tutor_ref.get)
            if not tutor.exists:
                raise ValueError(f"Tutor {tutor_id} no encontrado")
            groups = tutor.to_dict().get("groups", [])
            if old_group_name not in groups:
                raise ValueError(f"Grupo {old_group_name} no encontrado")
            groups[groups.index(old_group_name)] = new_group_name
            await asyncio.to_thread(tutor_ref.set, {"groups": groups}, merge=True)
            self.tutors[tutor_id] = {
                **tutor.to_dict(),
                "doc_id": tutor_id,
                "groups": groups
            }
            self.users.clear()  # Invalidar caché de usuarios
            self.responses.clear()  # Invalidar respuestas
            logger.info(f"[CACHE] Grupo {old_group_name} actualizado a {new_group_name} para tutor {tutor_id}")
        except Exception as e:
            logger.error(f"[CACHE ERROR] Error al actualizar grupo {old_group_name} a {new_group_name} para tutor {tutor_id}: {str(e)}")
            raise

    async def delete_tutor_group(self, tutor_id: str, group_name: str):
        """Elimina un grupo del tutor y actualiza el caché"""
        try:
            tutor_ref = db.collection("tutors").document(tutor_id)
            tutor = await asyncio.to_thread(tutor_ref.get)
            if not tutor.exists:
                raise ValueError(f"Tutor {tutor_id} no encontrado")
            groups = tutor.to_dict().get("groups", [])
            if group_name not in groups:
                raise ValueError(f"Grupo {group_name} no encontrado")
            groups.remove(group_name)
            await asyncio.to_thread(tutor_ref.set, {"groups": groups}, merge=True)
            self.tutors[tutor_id] = {
                **tutor.to_dict(),
                "doc_id": tutor_id,
                "groups": groups
            }
            self.users.clear()  # Invalidar caché de usuarios
            self.responses.clear()  # Invalidar respuestas
            logger.info(f"[CACHE] Grupo {group_name} eliminado del tutor {tutor_id}")
        except Exception as e:
            logger.error(f"[CACHE ERROR] Error al eliminar grupo {group_name} del tutor {tutor_id}: {str(e)}")
            raise