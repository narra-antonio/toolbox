from flask import jsonify, render_template, request, Response
from ..db.database import Database
from ..db.project_repository import ProjectRepository
from ..db.credential_repository import Credential, CredentialRepository
from ..db.settings_repository import SettingsRepository


class SettingsController:
    def __init__(self, db: Database):
        self.db = db

    def index(self) -> str:
        return render_template("settings.html")

    # Projects

    def update_project(self, project_id: int) -> Response:
        with self.db as db:
            repo = ProjectRepository(db)
            project = repo.find_by_id(project_id)
            if not project:
                return jsonify({"error": "Project not found"}), 404

            data = request.get_json()
            project.alias = data.get("alias", project.alias)
            project.default_branch = data.get("default_branch", project.default_branch)
            project.credential_id = data.get("credential_id", project.credential_id)

            repo.save(project)
            return jsonify({"status": "ok"})

    def delete_project(self, project_id: int) -> Response:
        with self.db as db:
            repo = ProjectRepository(db)
            if not repo.find_by_id(project_id):
                return jsonify({"error": "Project not found"}), 404
            repo.delete(project_id)
            return jsonify({"status": "ok"})

    # Credentials

    def get_credentials(self) -> Response:
        with self.db as db:
            credentials = CredentialRepository(db).find_all()
            return jsonify(
                [
                    {
                        "id": c.id,
                        "alias": c.alias,
                        "host": c.host,
                        "auth_type": c.auth_type,
                        "ssh_key_path": c.ssh_key_path,
                        "username": c.username,
                    }
                    for c in credentials
                ]
            )

    def create_credential(self) -> Response:
        with self.db as db:
            data = request.get_json()
            credential = Credential(
                id=None,
                alias=data["alias"],
                host=data["host"],
                auth_type=data["auth_type"],
                ssh_key_path=data.get("ssh_key_path"),
                username=data.get("username"),
            )
            CredentialRepository(db).save(credential)
            return jsonify({"status": "ok", "id": credential.id}), 201

    def update_credential(self, credential_id: int) -> Response:
        with self.db as db:
            repo = CredentialRepository(db)
            credential = repo.find_by_id(credential_id)
            if not credential:
                return jsonify({"error": "Credential not found"}), 404

            data = request.get_json()
            credential.alias = data.get("alias", credential.alias)
            credential.host = data.get("host", credential.host)
            credential.auth_type = data.get("auth_type", credential.auth_type)
            credential.ssh_key_path = data.get("ssh_key_path", credential.ssh_key_path)
            credential.username = data.get("username", credential.username)

            repo.save(credential)
            return jsonify({"status": "ok"})

    def delete_credential(self, credential_id: int) -> Response:
        with self.db as db:
            repo = CredentialRepository(db)
            if not repo.find_by_id(credential_id):
                return jsonify({"error": "Credential not found"}), 404
            repo.delete(credential_id)
            return jsonify({"status": "ok"})

    # Settings

    def get_settings(self) -> Response:
        with self.db as db:
            settings = SettingsRepository(db).find_all()
            return jsonify(settings)

    def update_settings(self) -> Response:
        with self.db as db:
            repo = SettingsRepository(db)
            data = request.get_json()
            for key, value in data.items():
                repo.set(key, str(value))
            return jsonify({"status": "ok"})
