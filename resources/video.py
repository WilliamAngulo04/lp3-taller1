"""
Recursos y rutas para la API de videos
"""
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from models.video import VideoModel
from models import db

# Campos para serializar respuestas
resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'views': fields.Integer,
    'likes': fields.Integer
}

# Parser para los argumentos en solicitudes PUT (crear video)
video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name", type=str, help="Nombre del video es requerido", required=True)
video_put_args.add_argument("views", type=int, help="Número de vistas del video", required=True)
video_put_args.add_argument("likes", type=int, help="Número de likes del video", required=True)

# Parser para los argumentos en solicitudes PATCH (actualizar video)
video_update_args = reqparse.RequestParser()
video_update_args.add_argument("name", type=str, help="Nombre del video")
video_update_args.add_argument("views", type=int, help="Número de vistas del video")
video_update_args.add_argument("likes", type=int, help="Número de likes del video")

def abort_if_video_doesnt_exist(video_id):
    """
    Verifica si un video existe, y si no, aborta la solicitud
    
    Args:
        video_id (int): ID del video a verificar
    """
    video = VideoModel.query.filter_by(id=video_id).first()
    # print(video_id, video)
    if not video:
        abort(404, message=f"No se encontro un video con el ID {video_id}")
    return video

class Video(Resource):
    """
    Recurso para gestionar videos individuales
    
    Métodos:
        get: Obtener un video por ID
        put: Crear un nuevo video
        patch: Actualizar un video existente
        delete: Eliminar un video
    """
    
    @marshal_with(resource_fields)
    def get(self, video_id):
        """
        Obtiene un video por su ID
        
        ---
        tags:
            - videos
        parameters:
          - in: path
            name: video_id
            type: integer
            required: true
            description: ID del video a obtener
        responses:
          200:
            description: Video encontrado
            schema:
                id: Video
                properties:
                    id:
                        type: integer
                    name:
                        type: string
                    views:
                        type: integer
                    likes:
                        type: integer
          404:
            description: Video no encontrado
        """
        print("GET video called")
        video = abort_if_video_doesnt_exist(video_id)
        print( video_id, video)
        return video
    
    @marshal_with(resource_fields)
    def put(self, video_id):
        """
        Crea un nuevo video con un ID específico
        
        ---
        tags:
            - videos
        parameters:
          - in: path
            name: video_id
            type: integer
            required: true
            description: ID del video a crear
          - in: body
            name: body
            required: true
            schema:
                required: ["name", "views", "likes"]
                properties:
                    name: {type: string}
                    views: {type: integer}
                    likes: {type: integer}
        responses:
          201:
            description: Video creado exitosamente
          409:
            description: El video ya existe
        """
        args = video_put_args.parse_args()
        # Verificar si ya existe
        existing = VideoModel.query.filter_by(id=video_id).first()
        if existing:
            abort(409, message=f"Ya existe un video con el ID {video_id}")
        video = VideoModel(id=video_id, **args)
        try:
            db.session.add(video)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(500, message="Error al crear el video")
        return video, 201

    @marshal_with(resource_fields)
    def patch(self, video_id):
        """
        Actualiza un video existente
        
        ---
        tags:
            - videos
        parameters:
          - name: video_id
            in: path
            type: integer
            required: true
            description: ID del video a actualizar
          - in: body
            name: body
            schema:
                properties:
                    name: {type: string}
                    views: {type: integer}
                    likes: {type: integer}
        responses:
          200:
            description: Video actualizado exitosamente
          404:
            description: Video no encontrado
        """
        video = abort_if_video_doesnt_exist(video_id)
        for key, value in video_update_args.parse_args().items():
            if value is None:
                continue
            setattr(video, key, value)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            abort(500, message="Error al actualizar el video")
        return video

    def delete(self, video_id):
        """
        Elimina un video existente
        
        ---
        tags:
            - videos
        parameters:
          - in: path
            name: video_id
            type: integer
            required: true
            description: ID del video a eliminar
        responses:
          204:
            description: Video eliminado exitosamente
          404:
            description: Video no encontrado
        """
        video = abort_if_video_doesnt_exist(video_id)
        db.session.delete(video)
        db.session.commit()
        return '', 204

class VideosList(Resource):
    @marshal_with(resource_fields)
    def get(self):
        videos = VideoModel.query.all()
        return videos

    @marshal_with(resource_fields)
    def post(self):
        """
        Crea video sin ID (ID Automático)
        ---
        tags:
            - videos
        parameters:
          - in: body
            name: body
            required: true
            schema:
                required: ["name", "views", "likes"]
                properties:
                    name: {type: string}
                    views: {type: integer}
                    likes: {type: integer}
        responses:
          201:
            description: Video creado exitosamente
        """
        args = video_put_args.parse_args()
        video = VideoModel(**args)
        try:
            db.session.add(video)
            db.session.commit()
        except Exception:
            db.session.rollback()
            abort(500, message="Error al crear el video")
        return video, 201