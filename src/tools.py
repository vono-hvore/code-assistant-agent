import os
from src.codebase_scanner import Scanner

approval_handler = None
log_handler = None


async def external_approval_tool(amount: float, reason: str) -> str:
    """
    Ask for user approval for a specified amount and reason.

    Args:
        amount (float): The amount that needs approval
        reason (str): The reason for requesting the approval

    Returns:
        str: 'approved' if the user confirms, 'rejected' if they decline
    """
    log_handler(f"Wating for approval yes/no for: {reason}")
    response = await approval_handler()
    if response.strip().lower() == "yes":
        return "approved"
    else:
        return "rejected"


async def read_folder(path: str = ".") -> dict:
    """
    Read folder structure at the current path.

    Args:
        path (str): entry point to folder structure.

    Returns:
        list: A dictionary containing folder structure.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes 'files' is a list of file paths of the current folder.
              If 'error', includes an 'error_message' key.
    """
    log_handler(f"Reading a folder at path {path}")
    scanner = Scanner()
    codebase = await scanner.scan_path(root_path=path)
    pretty_codebase = scanner.prettier(codebase)
    log_handler(pretty_codebase)
    return {"status": "success", "files": codebase}


def read_file(path: str) -> dict:
    """
    Read and return the content of a file at the given path.

    Args:
        path (str): Path to the file.

    Returns:
        dict: A dictionary containing status and either the content or an error message.
    """
    log_handler(f"Reading a file at path ${path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"status": "success", "content": content}
    except FileNotFoundError:
        return {"status": "error", "message": f"File not found: {path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def edit_file(path: str, content: str) -> dict:
    """
    Edit a file at the given path. If the file doesn't exist, it will be created.

    Args:
        path (str): The full path to the file.
        content (str): Text content to write to the file.

    Returns:
        dict: Status and message.
    """
    log_handler(f"✏️Edit a file at path ${path} with content:\n{content}")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return {"status": "success", "message": f"File edited at: {path}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


async def delete_file(path: str) -> dict:
    """
    Delete a file at the given path.

    Args:
        path (str): The full path to the file.

    Returns:
        dict: Result with 'status' and 'message'.
    """
    log_handler(f"Deleting file at path ${path}")

    try:
        if not os.path.exists(path):
            return {"status": "error", "message": f"File not found: {path}"}
        if not os.path.isfile(path):
            return {"status": "error", "message": f"Path is not a file: {path}"}

        os.remove(path)
        return {"status": "success", "message": f"File deleted: {path}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def search_files(root: str, name: str = "", content: str = "") -> dict:
    """
    Search files by name or content starting from a root directory.

    Args:
        root (str): The root folder to start searching from.
        name (str): Substring to match in filenames (optional).
        content (str): Substring to match in file contents (optional).

    Returns:
        dict: Contains 'status', 'matches' (list), or 'message' on error.
    """
    try:
        codebase_scanner = Scanner()
        matches = codebase_scanner.search_files(root, name, content)
        return {"status": "success", "matches": matches}
    except Exception as e:
        return {"status": "error", "message": str(e)}
