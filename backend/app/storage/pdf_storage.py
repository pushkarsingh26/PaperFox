import os
from typing import Optional

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage_data", "pdf")


class PDFStorageService:
    def __init__(self, base_dir: str = STORAGE_DIR):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save_pdf(self, user_id: str, artifact_type: str, pdf_bytes: bytes) -> str:
        user_dir = os.path.join(self.base_dir, user_id)
        os.makedirs(user_dir, exist_ok=True)

        filename = f"{artifact_type}_resume.pdf"
        file_path = os.path.join(user_dir, filename)

        with open(file_path, "wb") as f:
            f.write(pdf_bytes)

        # Return decoupled storage reference string
        relative_path = os.path.relpath(file_path, self.base_dir).replace("\\", "/")
        return f"storage://{relative_path}"

    def get_pdf(self, storage_reference: str) -> Optional[bytes]:
        if not storage_reference or not storage_reference.startswith("storage://"):
            return None

        relative_path = storage_reference.replace("storage://", "")
        file_path = os.path.abspath(os.path.join(self.base_dir, relative_path))

        # Security check against directory traversal
        if not file_path.startswith(os.path.abspath(self.base_dir)):
            return None

        if not os.path.exists(file_path):
            return None

        with open(file_path, "rb") as f:
            return f.read()

    def delete_pdf(self, storage_reference: str) -> bool:
        if not storage_reference or not storage_reference.startswith("storage://"):
            return False

        relative_path = storage_reference.replace("storage://", "")
        file_path = os.path.abspath(os.path.join(self.base_dir, relative_path))

        if file_path.startswith(os.path.abspath(self.base_dir)) and os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
