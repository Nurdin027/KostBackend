from pydoc import locate

from flask_restful import reqparse


def responseapi(status_code=200, status="success", message="Success", data=None):
    return {
        "status": status,
        "message": message,
        "count": len(data) if data is not None else None,
        "data": data,
    }, status_code


def global_parser(fields):
    parser = reqparse.RequestParser()
    for f in fields:
        parser.add_argument(
            f['name'],
            type=locate(f['type']),
            required=f.get('req', False),  # required jika key 'req' ditambahkan
            help=f"{f['name']} fields is required"
        )
    return parser.parse_args()
