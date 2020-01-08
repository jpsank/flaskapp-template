from wtforms.validators import ValidationError, Length

from app.util.helpers import is_valid_name


class Unique:
    def __init__(self, query_func, message=u'This element already exists.'):
        self.query_func = query_func
        self.message = message

    def __call__(self, form, field):
        if self.query_func(field.data) is not None:
            raise ValidationError(self.message)


class ValidName:
    def __init__(self, message=u'Name must contain only ASCII printable characters'):
        self.message = message

    def __call__(self, form, field):
        if not is_valid_name(field.data):
            raise ValidationError(self.message)


class ValidLength(Length):
    def __init__(self, column, message=None):
        super().__init__(min=0, max=column.type.length, message=message)
