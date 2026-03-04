from typing import Any, TypeAlias


JSON: TypeAlias = dict[str, Any]

class Model:
    def __init__(self, payload: JSON):
        self.payload = payload


class Field:
    """ Описывает поле модели """

    def __init__(self, path: str):
        """ path: Путь к полю в json-объекте """

        # Разбиваем путь на ключи и сохраняем их в списке
        self.keys = path.split(".")


    def __get__(self, obj, objtype=None):
        """
            Возвращает значение поля

            Args:
                obj - экземпляр модели
                objtype - тип модели

            Returns:
                Значение поля, если оно существует, иначе None
            """

        # Проверяем, как вызывается метод
        # Если через класс, то возвращаем объект поля
        # Если через экземпляр, то продолжаем работу
        if obj is None:
            return self

        # Получаем ссылку на json-объект
        data = obj.payload

        # Пробегаем по ключам и получаем значение последнего поля
        try:
            for key in self.keys:
                data = data[key]
            return data

        # Если поле не существует или обращаемся не к словарю, возвращаем None
        except (KeyError, TypeError):
            return None

    def __set__(self, obj: Model, value: Any):
        """ Устанавливает значение поля """

        data = obj.payload

        # Пробегаем по ключам и получаем последний словарь
        for key in self.keys[:-1]:
            data = data[key]

        # Устанавливаем значение последнего ключа
        data[self.keys[-1]] = value

