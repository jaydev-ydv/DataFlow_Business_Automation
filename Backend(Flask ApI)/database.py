from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User_Detail(db.Model):
    __tablename__ = "user_detail"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    uploaded_files = db.relationship("UploadedFile", backref="user", cascade="all, delete-orphan")


class UploadedFile(db.Model):
    __tablename__ = "uploaded_file"
    __table_args__ = (
        db.Index("ix_uploaded_file_user_upload_time", "user_id", "upload_time"),
        db.Index("ix_uploaded_file_user_filename", "user_id", "filename"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_detail.id", ondelete="CASCADE"), nullable=False)
    filename = db.Column(db.String(255), nullable=False, index=True)
    file_data = db.Column(db.LargeBinary, nullable=True)
    storage_path = db.Column(db.String(500), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    content_type = db.Column(db.String(120), nullable=True)
    upload_time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)


def init_db(app):
    """Database schema is managed by Flask-Migrate."""
    raise RuntimeError('Use migrations instead: run "flask --app app db upgrade" from the backend directory.')
