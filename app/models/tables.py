from app import db, login_manager

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, nullable=False)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __init__(self, name, lastname, description, email, password):
        self.name = name
        self.lastname = lastname
        self.description = description
        self.email = email
        self.password = password
    
    def __repr__(self):
        return '<User %r>' % self.name

class Map(db.Model):
    __tablename__ = "maps"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    send_date = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String, nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer)

    def __init__(self, title, send_date, category, status, user_id):
        self.title = title
        self.send_date = send_date
        self.category = category
        self.status = status
        self.user_id = user_id

    def __repr__(self):
        return '<Map %r>' % self.title