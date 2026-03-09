from flask import jsonify, render_template, Response
from ..db.database import Database
from ..db.project_repository import ProjectRepository
from ..git.git_manager import GitManager


class DashboardController:
    def __init__(self, db: Database):
        self.db = db

    def index(self) -> str:
        return render_template("dashboard.html")

    def get_projects(self) -> Response:
        with self.db as db:
            projects = ProjectRepository(db).find_all()
            return jsonify(
                [
                    {
                        "id": p.id,
                        "alias": p.alias,
                        "path": str(p.path),
                        "default_branch": p.default_branch,
                        "credential_id": p.credential_id,
                    }
                    for p in projects
                ]
            )

    def get_commits(self, project_id: int) -> Response:
        with self.db as db:
            matches = GitManager(db).load_by_ids([project_id])
            if not matches:
                return jsonify({"error": "Project not found"}), 404

            project, repo = matches[0]

            try:
                repo.fetch()
            except Exception as e:
                return jsonify({"error": str(e)}), 500

            commits_by_branch = {}
            for branch in repo.local_branches():
                commits = repo.incoming_commits(branch)
                if commits:
                    commits_by_branch[branch] = commits

            deleted = repo.deleted_remote_branches()

            return jsonify(
                {
                    "project": project.alias,
                    "incoming_commits": commits_by_branch,
                    "deleted_remote_branches": deleted,
                }
            )

    def pull_project(self, project_id: int) -> Response:
        with self.db as db:
            result = GitManager(db).pull_project(project_id)
            if result["status"] == "error":
                return jsonify(result), 500
            return jsonify(result)
