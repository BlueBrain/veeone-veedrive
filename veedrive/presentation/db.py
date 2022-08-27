from abc import abstractmethod

LIST_PRESENTATIONS_EXPOSE_ATTRIBUTES = [
    "id",
    "name",
    "createdAt",
    "updatedAt",
    "savedAt",
]


def prepare_presentation_data(item):
    return {key: item.get(key) for key in LIST_PRESENTATIONS_EXPOSE_ATTRIBUTES}


class DBInterface:
    @abstractmethod
    def get_presentation(self, presentation_id):
        raise NotImplementedError

    @abstractmethod
    def get_presentation_versions(self, presentation_id):
        raise NotImplementedError

    @abstractmethod
    def list_presentations(self):
        raise NotImplementedError

    @abstractmethod
    def save_presentation_to_storage(self, presentation_data: dict):
        raise NotImplementedError

    @abstractmethod
    def delete_presentation(self, presentation_id: str):
        raise NotImplementedError

    @abstractmethod
    def purge_presentations(self):
        raise NotImplementedError

    @abstractmethod
    def create_folder(self, folder_name: str):
        raise NotImplementedError

    @abstractmethod
    def list_folders(self):
        raise NotImplementedError

    @abstractmethod
    def remove_folder(self, folder_name: str):
        raise NotImplementedError

    @abstractmethod
    def _archive_presentation(self, presentation):
        raise NotImplementedError
