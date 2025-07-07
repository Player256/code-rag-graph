import os
import ast
import git
import shutil
from neo4j import Driver

from .connections import GraphDBConnection
from . import queries


class CodebaseIngestor:
    def __init__(self):
        self.driver: Driver = GraphDBConnection.get_driver()

    def ingest_repository(self, repo_url: str, local_path: str):
        if os.path.exists(local_path):
            shutil.rmtree(local_path)

        git.Repo.clone_from(repo_url, local_path)

        for root, _, files in os.walk(local_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, local_path)
                    self._process_file(relative_path, file_path)

        shutil.rmtree(local_path)

    def _process_file(self, relative_path: str, full_path: str):
        with self.driver.session() as session:
            session.run(queries.CREATE_FILE_NODE, path=relative_path)

            with open(full_path, "r", encoding="utf-8") as f:
                try:
                    content = f.read()
                    tree = ast.parse(content)
                    visitor = ASTVisitor(self.driver, relative_path)
                    visitor.visit(tree)
                except (SyntaxError, UnicodeDecodeError) as e:
                    print(f"Skipping file due to parsing error: {relative_path} - {e}")


class ASTVisitor(ast.NodeVisitor):
    def __init__(self, driver: Driver, file_path: str):
        self.driver = driver
        self.file_path = file_path
        self.current_class = None
        self.current_function = None

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            with self.driver.session() as session:
                session.run(
                    queries.CREATE_IMPORT_RELATIONSHIP,
                    file_path=self.file_path,
                    module_name=node.module,
                )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        with self.driver.session() as session:
            session.run(
                queries.CREATE_CLASS_NODE_AND_RELATIONSHIP,
                file_path=self.file_path,
                class_name=node.name,
            )

            for base in node.bases:
                if isinstance(base, ast.Name):
                    session.run(
                        queries.CREATE_INHERITANCE_RELATIONSHIP,
                        file_path=self.file_path,
                        child_class=node.name,
                        parent_class=base.id,
                    )

        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        with self.driver.session() as session:
            session.run(
                queries.CREATE_FUNCTION_NODE_AND_RELATIONSHIP,
                file_path=self.file_path,
                function_name=node.name,
                parent_name=self.current_class,
            )

        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = None

    def visit_Call(self, node: ast.Call):
        if self.current_function and isinstance(node.func, ast.Name):
            callee_name = node.func.id
            with self.driver.session() as session:
                session.run(
                    queries.CREATE_CALL_RELATIONSHIP,
                    file_path=self.file_path,
                    caller_name=self.current_function,
                    callee_name=callee_name,
                )
        self.generic_visit(node)
