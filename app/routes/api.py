from flask import Blueprint, jsonify, request
from app.services.library_service import library_service

api_blueprint = Blueprint('api', __name__)


# ──────────────────────────── HEALTH ─────────────────────────────────────────

@api_blueprint.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'UP',
        'service': 'Enterprise Smart Library Management Platform',
        'version': '1.0.0',
    }), 200


# ──────────────────────────── DASHBOARD ──────────────────────────────────────

@api_blueprint.route('/dashboard', methods=['GET'])
def dashboard_stats():
    stats = library_service.get_dashboard_stats()
    return jsonify(stats), 200


# ──────────────────────────── USERS ──────────────────────────────────────────

@api_blueprint.route('/users', methods=['POST'])
def create_user():
    data = request.get_json(silent=True) or {}
    result = library_service.add_user(data)
    code = result.pop('code')
    return jsonify(result), code


@api_blueprint.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    result = library_service.get_user(user_id)
    code = result.pop('code')
    return jsonify(result), code


@api_blueprint.route('/users', methods=['GET'])
def get_all_users():
    result = library_service.get_all_users()
    code = result.pop('code')
    return jsonify(result), code


@api_blueprint.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    result = library_service.delete_user(user_id)
    code = result.pop('code')
    return jsonify(result), code


# ──────────────────────────── BOOKS ──────────────────────────────────────────

@api_blueprint.route('/books', methods=['GET'])
def get_books():
    query = request.args.get('q', '')
    result = library_service.search_books(query)
    code = result.pop('code')
    return jsonify(result), code


@api_blueprint.route('/books', methods=['POST'])
def create_book():
    data = request.get_json(silent=True) or {}
    result = library_service.add_book(data)
    code = result.pop('code')
    return jsonify(result), code


@api_blueprint.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    result = library_service.get_book(book_id)
    code = result.pop('code')
    return jsonify(result), code


# ──────────────────────────── LOANS ──────────────────────────────────────────

@api_blueprint.route('/loans', methods=['GET'])
def get_loans():
    result = library_service.get_all_loans()
    code = result.pop('code')
    return jsonify(result), code


# ──────────────────────────── BORROW / RETURN ────────────────────────────────

@api_blueprint.route('/borrow', methods=['POST'])
def borrow_book():
    data = request.get_json(silent=True) or {}
    user_id = (data.get('user_id') or '').strip()
    book_id = (data.get('book_id') or '').strip()

    if not user_id or not book_id:
        return jsonify({'error': 'user_id and book_id are required'}), 400

    result = library_service.borrow_book(user_id, book_id)
    code = result.pop('code')
    if not result.get('success'):
        return jsonify({'error': result.get('error')}), code
    return jsonify(result), code


@api_blueprint.route('/return', methods=['POST'])
def return_book():
    data = request.get_json(silent=True) or {}
    user_id = (data.get('user_id') or '').strip()
    book_id = (data.get('book_id') or '').strip()

    if not user_id or not book_id:
        return jsonify({'error': 'user_id and book_id are required'}), 400

    result = library_service.return_book(user_id, book_id)
    code = result.pop('code')
    if not result.get('success'):
        return jsonify({'error': result.get('error')}), code
    return jsonify(result), code


# ──────────────────────────── ERROR HANDLERS ─────────────────────────────────

@api_blueprint.app_errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404


@api_blueprint.app_errorhandler(405)
def method_not_allowed(e):
    return jsonify({'error': 'Method not allowed'}), 405


@api_blueprint.app_errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500
