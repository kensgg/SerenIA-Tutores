import asyncio
from datetime import datetime
from firebase_service import db

async def consultar_todos_usuarios_y_respuestas():
    try:
        print("\n=== CONSULTANDO TODOS LOS USUARIOS Y RESPUESTAS ===")
        
        # 1. Consultar todos los usuarios
        users_ref = await asyncio.to_thread(
            lambda: db.collection("users").get()
        )
        
        if not users_ref:
            print("❌ No se encontraron usuarios")
            return
            
        # Procesar cada usuario
        for user_doc in users_ref:
            user_id = user_doc.id
            user_data = user_doc.to_dict()
            
            print(f"\n=== USUARIO: {user_data.get('name', 'Sin nombre')} ===")
            print(f"ID: {user_id}")
            print(f"Email: {user_data.get('email', 'No especificado')}")
            print(f"Grupo: {user_data.get('group', 'No especificado')}")
            print(f"Edad: {user_data.get('age', 'No especificado')}")
            
            # 2. Consultar respuestas para este usuario
            respuestas_ref = await asyncio.to_thread(
                lambda: db.collection("respuestas_cuestionarios")
                .where("id_user", "==", user_id)
                .order_by("date")
                .get()
            )
            
            if not respuestas_ref:
                print("  No tiene respuestas registradas")
                continue
                
            print("  📊 Respuestas:")
            for respuesta in respuestas_ref:
                resp_data = respuesta.to_dict()
                fecha = resp_data.get('date')
                fecha_str = fecha.strftime('%Y-%m-%d %H:%M:%S') if isinstance(fecha, datetime) else str(fecha)
                
                print(f"  - {resp_data.get('questionnaire')} | "
                      f"Fecha: {fecha_str} | "
                      f"Nivel: {resp_data.get('level')} | "
                      f"Puntaje: {resp_data.get('score')}")
        
        print("\n✅ Consulta completada para todos los usuarios")
        
    except Exception as e:
        print(f"\n❌ Error durante la consulta: {str(e)}")

# Ejemplo de uso
if __name__ == "__main__":
    asyncio.run(consultar_todos_usuarios_y_respuestas())