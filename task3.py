class TypedProperty:
    def __init__(self, expected_type):
        self._expected_type = expected_type

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if self.name not in instance.__dict__:
            raise AttributeError(self.name)

        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if not isinstance(value, self._expected_type):
            raise TypeError(self._expected_type, type(value))

        instance.__dict__[self.name] = value


class ValidatedProperty(TypedProperty):
    def __init__(
            self,
            expected_type,
            min_value=None,
            max_value=None,
            min_len=None,
            max_len=None,
    ):
        super().__init__(expected_type)
        self.min_value = min_value
        self.max_value = max_value
        self.min_len = min_len
        self.max_len = max_len

    def __set__(self, instance, value):
        super().__set__(instance, value)

        if isinstance(value, (int, float)):
            if self.min_value is not None and value < self.min_value:
                raise ValueError(f"Value {value} is less than min value {self.min_value}")
            if self.max_value is not None and value > self.max_value:
                raise ValueError(f"Value {value} is greater than max value {self.max_value}")

        if isinstance(value, str):
            length = len(value)
            if self.min_len is not None and length < self.min_len:
                raise ValueError(f"String's length {length} is less than min length {self.min_len}")
            if self.max_len is not None and length > self.max_len:
                raise ValueError(f"String's length {length} is greater than max length {self.max_len}")


class RegistryMeta(type):
    registry = {}

    def __new__(cls, name, bases, attrs):
        new_cls = super().__new__(cls, name, bases, attrs)

        if name in cls.registry:
            raise ValueError(f"Duplicate registry name {name}")

        RegistryMeta.registry[name] = new_cls
        return new_cls


class ModelMeta(RegistryMeta):
    def __new__(cls, name, bases, attrs):
        fields = {key: value for key, value in attrs.items() if isinstance(value, TypedProperty)}
        print(attrs)
        attrs['_fields'] = fields
        print(attrs)

        return super().__new__(cls, name, bases, attrs)


class Model(metaclass=ModelMeta):
    pass


# Тестовый запуск
if __name__ == "__main__":
    class User(Model):
        name = ValidatedProperty(str, min_len=2)
        age = ValidatedProperty(int, min_value=18)


    user = User()
    user.name = "Jo"
    user.age = 20

    print(f"Registered models: {list(RegistryMeta.registry.keys())}")
    print(f"User fields: {list(User._fields.keys())}")
