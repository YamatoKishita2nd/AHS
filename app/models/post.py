"""
グラフモデル
"""
from app.models.abstract import AbstractModel


class PostModel(AbstractModel):
    def __init__(self, config):
        super(PostModel, self).__init__(config)

    def fetch_recent_posts(self, limit=5):
        """
        最新の記事を取得する．デフォルトでは最新5件まで
        :param limit: 取得する記事の数
        :return:
        """
        sql = "SELECT * FROM posts ORDER BY created_at DESC LIMIT %s"
        return self.fetch_all(sql, limit)

    def fetch_post_by_id(self, post_id):
        """
        指定されたIDの記事を取得
        :param post_id: 取得したい記事のID
        :return: 指定された記事のID
        """
        sql = "SELECT * FROM posts INNER JOIN users u on posts.user_id = u.id WHERE posts.id=%s"
        return self.fetch_one(sql, post_id)

    def fetch_comments(self, post_id):
        sql = "SELECT * FROM comments INNER JOIN posts on comments.post_id = posts.id WHERE posts.id=%s"
        return self.fetch_all(sql, post_id)

    def create_comment(self, user_id, post_id, comment):
        sql = "INSERT INTO comments(user_id, post_id, comment) VALUE (%s, %s, %s);"
        self.execute(sql, user_id, post_id, comment)

    def create_post(self, user_id, title, body):
        """
        新しく記事を作成する
        :param user_id: 投稿したユーザのOD
        :param title: 記事のタイトル
        :param body: 記事の本文
        :return: None
        """
        sql = "INSERT INTO posts(user_id, title, body) VALUE (%s, %s, %s);"
        self.execute(sql, user_id, title, body)