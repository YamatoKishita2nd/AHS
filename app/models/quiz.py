"""
クイズモデル
"""
from app.models.abstract import AbstractModel


class QuizModel(AbstractModel):
    def __init__(self, config):
        super(QuizModel, self).__init__(config)

    def fetch_quiz_by_id(self, quiz_id):
        """
        指定されたIDの問題を取得
        :param quiz_id: 取得したい問題のID
        :return: 指定された問題のID
        """
        # sql = "SELECT * FROM quizzes INNER JOIN users u on quizzes.user_id = u.id WHERE quizs.id=%s"
        sql = "SELECT * FROM quizzes WHERE id=%s"
        return self.fetch_one(sql, quiz_id)

    def get_result(self, user_id):
        # sql = "SELECT score FROM scores INNER JOIN users on scores.user_id = users.id WHERE scores.user_id=%s"
        sql = "SELECT * FROM scores INNER JOIN users u on scores.user_id = u.id WHERE scores.user_id=%s ORDER BY scores.id DESC"
        return self.fetch_one(sql, user_id)

    def insert_score(self, user_id, score):
        sql = "INSERT INTO scores(user_id, score) VALUE (%s, %s);"
        self.execute(sql, user_id, score)