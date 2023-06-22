from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Post(db.Model):
    __tablename__ = "post"  # 기본적으로 테이블 이름은 자동으로 정의되지만 이 처럼 명시적으로 정할 수 있다.

    id = db.Column(db.Integer, primary_key=True)
    post_key = db.Column(db.String(30), unique=True)
    post_write_date = db.Column(db.DateTime(), default=datetime.now)

    def __repr__(self):
        return f"Post('{self.post_key}')"
