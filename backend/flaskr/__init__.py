from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, questions):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    formatted_questions = [question.format() for question in questions]
    return formatted_questions[start:end]

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    CORS(app, resources={r"/*": {"origins": "*"}})

    with app.app_context():
        db.create_all()

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        return jsonify({
            'success': True,
            'categories': {category.id: category.type for category in categories}
        })


    @app.route('/questions', methods=['GET'])
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)

        if len(current_questions) == 0:
            abort(404)

        categories = Category.query.order_by(Category.id).all()

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(questions),
            'current_category': None,
            'categories': {category.id: category.type for category in categories}
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = db.session.get(Question, question_id)

        if question is None:
            abort(404)

        deleted_question_id = question.id

        try:
            question.delete()
        except Exception:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

        return jsonify({
            'success': True,
            'deleted': deleted_question_id
        })

    @app.route('/questions/<int:question_id>', methods=['PUT'])
    def update_question(question_id):
        body = request.get_json(silent=True)

        if body is None:
            abort(400)

        question = db.session.get(Question, question_id)
        if question is None:
            abort(404)

        updatable_fields = ('question', 'answer', 'category', 'difficulty')
        if not any(field in body for field in updatable_fields):
            abort(400)

        try:
            if 'question' in body:
                if not body['question']:
                    abort(400)
                question.question = body['question']

            if 'answer' in body:
                if not body['answer']:
                    abort(400)
                question.answer = body['answer']

            if 'category' in body:
                if not body['category']:
                    abort(400)
                question.category = str(body['category'])

            if 'difficulty' in body:
                if body['difficulty'] in (None, ''):
                    abort(400)
                question.difficulty = int(body['difficulty'])

            question.update()
            updated_question = question.format()
        except ValueError:
            db.session.rollback()
            abort(400)
        except Exception:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

        return jsonify({
            'success': True,
            'updated': question_id,
            'question': updated_question
        })

    @app.route('/questions', methods=['POST'])
    def create_or_search_questions():
        body = request.get_json(silent=True)

        if body is None:
            abort(400)

        search_term = body.get('searchTerm')
        if search_term is not None:
            questions = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')
            ).order_by(Question.id).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions),
                'current_category': None
            })

        question_text = body.get('question')
        answer = body.get('answer')
        category = body.get('category')
        difficulty = body.get('difficulty')

        if not all([question_text, answer, category, difficulty]):
            abort(400)

        try:
            question = Question(
                question=question_text,
                answer=answer,
                category=str(category),
                difficulty=int(difficulty)
            )
            question.insert()
            created_question_id = question.id
        except Exception:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

        return jsonify({
            'success': True,
            'created': created_question_id
        })

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        category = db.session.get(Category, category_id)

        if category is None:
            abort(404)

        questions = Question.query.filter(
            Question.category == str(category_id)
        ).order_by(Question.id).all()

        return jsonify({
            'success': True,
            'questions': [question.format() for question in questions],
            'total_questions': len(questions),
            'current_category': category.type
        })

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json(silent=True)

        if body is None:
            abort(400)

        previous_questions = body.get('previous_questions', [])
        quiz_category = body.get('quiz_category', {})
        category_id = quiz_category.get('id') if quiz_category else None

        query = Question.query
        if category_id and int(category_id) != 0:
            query = query.filter(Question.category == str(category_id))

        available_questions = query.filter(
            Question.id.notin_(previous_questions)
        ).all()

        next_question = random.choice(available_questions).format() if available_questions else None

        return jsonify({
            'success': True,
            'question': next_question
        })

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'internal server error'
        }), 500

    return app

