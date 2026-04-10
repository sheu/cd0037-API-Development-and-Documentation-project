import os
import unittest

from sqlalchemy import text

from flaskr import create_app
from models import db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def reset_database(self):
        db.session.execute(text("DROP TABLE IF EXISTS questions CASCADE"))
        db.session.execute(text("DROP TABLE IF EXISTS categories CASCADE"))
        db.session.execute(text("DROP SEQUENCE IF EXISTS questions_id_seq CASCADE"))
        db.session.execute(text("DROP SEQUENCE IF EXISTS categories_id_seq CASCADE"))
        db.session.commit()

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = os.getenv("TRIVIA_TEST_DB_NAME", "trivia_test")
        self.database_user = os.getenv("TRIVIA_DB_USER", os.getenv("POSTGRES_USER", "myuser"))
        self.database_password = os.getenv("TRIVIA_DB_PASSWORD", os.getenv("POSTGRES_PASSWORD", "mypassword"))
        self.database_host = os.getenv("TRIVIA_DB_HOST", "localhost")
        self.database_port = os.getenv("TRIVIA_DB_PORT", "5432")
        self.database_path = (
            f"postgresql://{self.database_user}:{self.database_password}@"
            f"{self.database_host}:{self.database_port}/{self.database_name}"
        )

        # Create app with the test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            self.reset_database()
            db.create_all()
            self.seed_data()

    def seed_data(self):
        categories = [
            Category(type="Science"),
            Category(type="Art"),
            Category(type="Geography"),
        ]
        db.session.add_all(categories)
        db.session.flush()

        questions = [
            Question(
                question="What is the heaviest organ in the human body?",
                answer="The Liver",
                category=str(categories[0].id),
                difficulty=4,
            ),
            Question(
                question="Who discovered penicillin?",
                answer="Alexander Fleming",
                category=str(categories[0].id),
                difficulty=3,
            ),
            Question(
                question="Which Dutch graphic artist initially created MC Escher's impossible shapes?",
                answer="M.C. Escher",
                category=str(categories[1].id),
                difficulty=2,
            ),
            Question(
                question="What is the capital of Peru?",
                answer="Lima",
                category=str(categories[2].id),
                difficulty=2,
            ),
        ]
        db.session.add_all(questions)
        db.session.commit()

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()
            self.reset_database()

    def test_get_categories(self):
        response = self.client.get("/categories")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["categories"]), 3)

    def test_categories_method_not_allowed(self):
        response = self.client.post("/categories")
        data = response.get_json()

        self.assertEqual(response.status_code, 405)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "method not allowed")

    def test_get_paginated_questions(self):
        response = self.client.get("/questions?page=1")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["total_questions"], 4)
        self.assertEqual(len(data["questions"]), 4)
        self.assertIn("categories", data)

    def test_get_paginated_questions_not_found(self):
        response = self.client.get("/questions?page=999")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "resource not found")

    def test_delete_question(self):
        with self.app.app_context():
            question_id = Question.query.first().id

        response = self.client.delete(f"/questions/{question_id}")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["deleted"], question_id)

        with self.app.app_context():
            self.assertIsNone(db.session.get(Question, question_id))

    def test_delete_missing_question(self):
        response = self.client.delete("/questions/9999")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "resource not found")

    def test_update_question(self):
        with self.app.app_context():
            question_id = Question.query.first().id

        response = self.client.put(
            f"/questions/{question_id}",
            json={
                "question": "Updated prompt?",
                "answer": "Updated answer",
                "difficulty": 5,
            },
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["updated"], question_id)
        self.assertEqual(data["question"]["question"], "Updated prompt?")
        self.assertEqual(data["question"]["difficulty"], 5)

        with self.app.app_context():
            updated_question = db.session.get(Question, question_id)
            self.assertEqual(updated_question.question, "Updated prompt?")
            self.assertEqual(updated_question.answer, "Updated answer")
            self.assertEqual(updated_question.difficulty, 5)

    def test_update_missing_question(self):
        response = self.client.put(
            "/questions/9999",
            json={"question": "No record here"},
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "resource not found")

    def test_update_question_bad_request(self):
        with self.app.app_context():
            question_id = Question.query.first().id

        response = self.client.put(
            f"/questions/{question_id}",
            json={},
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "bad request")

    def test_create_question(self):
        payload = {
            "question": "What is 2 + 2?",
            "answer": "4",
            "category": "1",
            "difficulty": 1,
        }
        response = self.client.post("/questions", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIsInstance(data["created"], int)

        with self.app.app_context():
            self.assertIsNotNone(db.session.get(Question, data["created"]))

    def test_create_question_bad_request(self):
        response = self.client.post(
            "/questions",
            json={"question": "Missing fields"},
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "bad request")

    def test_search_questions(self):
        response = self.client.post("/questions", json={"searchTerm": "capital"})
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["total_questions"], 1)
        self.assertEqual(data["questions"][0]["answer"], "Lima")

    def test_search_questions_with_empty_result(self):
        response = self.client.post("/questions", json={"searchTerm": "does-not-exist"})
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["total_questions"], 0)
        self.assertEqual(data["questions"], [])

    def test_get_questions_by_category(self):
        response = self.client.get("/categories/1/questions")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["current_category"], "Science")
        self.assertGreaterEqual(data["total_questions"], 1)

    def test_get_questions_by_missing_category(self):
        response = self.client.get("/categories/9999/questions")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "resource not found")

    def test_play_quiz(self):
        response = self.client.post(
            "/quizzes",
            json={"previous_questions": [], "quiz_category": {"id": 1, "type": "Science"}},
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIsNotNone(data["question"])
        self.assertEqual(data["question"]["category"], "1")

    def test_play_quiz_bad_request(self):
        response = self.client.post(
            "/quizzes",
            data="not-json",
            content_type="text/plain",
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "bad request")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
