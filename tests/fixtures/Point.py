from sqlalchemy import func
from sqlalchemy.sql.type_api import UserDefinedType


class Point(UserDefinedType):
    def get_col_spec(self):
        return "GEOMETRY"

    def bind_expression(self, bindvalue):
        return func.ST_GeomFromText(bindvalue, type_=self)

    def column_expression(self, col):
        return func.ST_AsText(col, type_=self)

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            assert isinstance(value, tuple)
            lng, lat = value
            return "POINT(%s %s)" % (lng, lat)

        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return None
            # m = re.match(r'^POINT\((\S+) (\S+)\)$', value)
            # lng, lat = m.groups()
            lng, lat = value[
                6:-1
            ].split()  # 'POINT(135.00 35.00)' => ('135.00', '35.00')
            return (float(lng), float(lat))

        return process
