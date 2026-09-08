import os
import json

class FileHelper:
    
    @staticmethod
    def save_json(data, filename, directory="data/logs"):
        os.makedirs(directory, exist_ok=True)
        file_path = f"{directory}/{filename}.json"
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return file_path
    
    @staticmethod
    def delete_file(file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False