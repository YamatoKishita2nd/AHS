"""
グラフモデル
"""
from app.models.abstract import AbstractModel


class GraphModel(AbstractModel):
    def __init__(self, config):
        super(GraphModel, self).__init__(config)

    def get_graph(self, user_id):
        sql = "SELECT score FROM scores WHERE scores.user_id=%s"
        return self.fetch_all(sql, user_id)
