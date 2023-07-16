from fastapi import FastAPI, Request, Form, Cookie
# from fastapi import FastAPI, Request, Form, Cookie, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
from fastapi.staticfiles import StaticFiles
from app.configs import Config
from app.utilities.session import Session
# from app.utilities.save_image import save_image
from app.models.auth import AuthModel
from app.models.articles import ArticleModel
from app.utilities.check_login import check_login

from app.models.quiz import QuizModel
from app.models.graph import GraphModel
from app.models.post import PostModel

import time

# import numpy as np
# import matplotlib.pyplot as plt

app = FastAPI()
app.mount("/app/statics", StaticFiles(directory="app/statics"), name="static")
templates = Jinja2Templates(directory="/app/templates")
config = Config()
session = Session(config)


@app.get("/")
def index(request: Request):
    """
    トップページを返す
    :param request: Request object
    :return:
    """
    return templates.TemplateResponse("index.html", {"request": request})


# @app.post("/login")
# def login(request: Request, username: str = Form(...), password: str = Form(...)):
#     """
#     ログイン処理
#     :param request:
#     :param username:
#     :param password:
#     :return:
#     """
#     auth_model = AuthModel(config)
#     [result, user] = auth_model.login(username, password)
#     if not result:
#         # ユーザが存在しなければトップページへ戻す
#         return templates.TemplateResponse("index.html", {"request": request, "error": "ユーザ名またはパスワードが間違っています"})
#     response = RedirectResponse("/articles", status_code=HTTP_302_FOUND)
#     session_id = session.set("user", user)
#     response.set_cookie("session_id", session_id)
#     return response


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """
    ログイン処理
    :param request:
    :param username:
    :param password:
    :return:
    """
    auth_model = AuthModel(config)
    [result, user] = auth_model.login(username, password)
    if not result:
        # ユーザが存在しなければトップページへ戻す
        return templates.TemplateResponse("index.html", {"request": request, "error": "ユーザ名またはパスワードが間違っています"})
    response = RedirectResponse("/dashboard", status_code=HTTP_302_FOUND)
    session_id = session.set("user", user)
    response.set_cookie("session_id", session_id)
    return response

@app.get("/register")
def register(request: Request):
    """
    新規登録ページ
    :param request:
    :return:
    """
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def create_user(username: str = Form(...), password: str = Form(...)):
    """
    ユーザ登録をおこなう
    フォームから入力を受け取る時は，`username=Form(...)`のように書くことで受け取れる
    :param username: 登録するユーザ名
    :param password: 登録するパスワード
    :return: 登録が完了したら/blogへリダイレクト
    """
    auth_model = AuthModel(config)
    auth_model.create_user(username, password)
    user = auth_model.find_user_by_name_and_password(username, password)
    response = RedirectResponse(url="/articles", status_code=HTTP_302_FOUND)
    session_id = session.set("user", user)
    response.set_cookie("session_id", session_id)
    return response


@app.get("/dashboard")
@check_login
def dashboard_index(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    # article_model = ArticleModel(config)
    # articles = article_model.fetch_recent_articles()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        # "articles": articles,
        "user": user
    })


@app.get("/articles")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def articles_index(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    article_model = ArticleModel(config)
    articles = article_model.fetch_recent_articles()
    return templates.TemplateResponse("article-index.html", {
        "request": request,
        "articles": articles,
        "user": user
    })


# @app.post("/article/create")
# @check_login
# def post_article(title: str = Form(...), body: str = Form(...), image: UploadFile = Form(...), session_id=Cookie(default=None)):
#     # この辺は画像null　おkかどうかで処理を変えてください
#     if image:
#         upload_dir_path: str = save_image(image)
#     # print(upload_dir_path)
#     article_model = ArticleModel(config)
#     user_id = session.get(session_id).get("user").get("id")
#     article_model.create_article(user_id, title, body, upload_dir_path)
#     return RedirectResponse("/articles", status_code=HTTP_302_FOUND)


@app.get("/quiz")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def quiz_index(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    return templates.TemplateResponse("quiz-index.html", {
        "request": request,
        "user": user
    })


@app.get("/article/create")
@check_login
def create_article_page(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    return templates.TemplateResponse("create-article.html", {"request": request, "user": user})


@app.post("/article/create")
@check_login
def post_article(title: str = Form(...), body: str = Form(...), session_id=Cookie(default=None)):
    article_model = ArticleModel(config)
    user_id = session.get(session_id).get("user").get("id")
    article_model.create_article(user_id, title, body)
    return RedirectResponse("/articles", status_code=HTTP_302_FOUND)


@app.get("/article/{article_id}")
@check_login
def article_detail_page(request: Request, article_id: int, session_id=Cookie(default=None)):
    article_model = ArticleModel(config)
    article = article_model.fetch_article_by_id(article_id)
    user = session.get(session_id).get("user")
    return templates.TemplateResponse("article-detail.html", {
        "request": request,
        "article": article,
        "user": user
    })


@app.get("/logout")
@check_login
def logout(session_id=Cookie(default=None)):
    session.destroy(session_id)
    response = RedirectResponse(url="/")
    response.delete_cookie("session_id")
    return response


@app.get("/quiz/{quiz_id}")
@check_login
def quiz_detail_page(request: Request, quiz_id: int, session_id=Cookie(default=None)):
    quiz_model = QuizModel(config)
    quiz = quiz_model.fetch_quiz_by_id(quiz_id)
    user = session.get(session_id).get("user")
    return templates.TemplateResponse("quiz.html", {
        "request": request,
        "quiz": quiz,
        "user": user
    })


@app.post("/quiz-result")
@check_login
def quiz_save_result(correct_num: int = Form(...), session_id=Cookie(default=None)):
    quiz_model = QuizModel(config)
    user_id = session.get(session_id).get("user").get("id")
    quiz_model.insert_score(user_id, correct_num)
    return RedirectResponse("/quiz-result", status_code=HTTP_302_FOUND)


@app.get("/quiz-result")
@check_login
def quiz_result_page(request: Request, session_id=Cookie(default=None)):
    quiz_model = QuizModel(config)
    user = session.get(session_id).get("user")
    score = quiz_model.get_result(user.get("id"))
    return templates.TemplateResponse("quiz-result.html", {
        "request": request,
        "score": score,
        "user": user
    })


@app.get("/graph")
@check_login
def graph_index(request: Request, session_id=Cookie(default=None)):
    graph_model = GraphModel(config)
    user = session.get(session_id).get("user")
    scores = graph_model.get_graph(user.get("id"))

    sum = 0
    for score in scores:
        sum += score['score']
    avg = round(sum / len(scores), 2)

    return templates.TemplateResponse("graph.html", {
        "request": request,
        "scores": scores,
        "user": user,
        "avg": avg
    })


@app.get("/post")
@check_login
def post_index(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    post_model = PostModel(config)
    posts = post_model.fetch_recent_posts()
    return templates.TemplateResponse("post-index.html", {
        "request": request,
        "posts": posts,
        "user": user
    })


@app.get("/post/{post_id}")
@check_login
def post_detail_page(request: Request, post_id: int, session_id=Cookie(default=None)):
    post_model = PostModel(config)
    post = post_model.fetch_post_by_id(post_id)
    comments = post_model.fetch_comments(post_id)
    user = session.get(session_id).get("user")
    return templates.TemplateResponse("post-detail.html", {
        "request": request,
        "post": post,
        "comments": comments,
        "user": user
    })


@app.post("/post/{post_id}")
@check_login
def comment_create(post_id: int, comment: str = Form(...), session_id=Cookie(default=None)):
    post_model = PostModel(config)
    user_id = session.get(session_id).get("user").get("id")
    post_model.create_comment(user_id, post_id, comment)
    return RedirectResponse("/post/" + str(post_id), status_code=HTTP_302_FOUND)


@app.get("/bulletin-board/create")
@check_login
def post_create_page(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    return templates.TemplateResponse("post-create.html", {
        "request": request,
        "user": user
    })


@app.post("/bulletin-board/create")
@check_login
def post_create(title: str = Form(...), body: str = Form(...), session_id=Cookie(default=None)):
    post_model = PostModel(config)
    user_id = session.get(session_id).get("user").get("id")
    post_model.create_post(user_id, title, body)
    time.sleep(10)
    return RedirectResponse("/post", status_code=HTTP_302_FOUND)

