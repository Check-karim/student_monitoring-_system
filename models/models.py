from extensions import db

class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    acronym = db.Column(db.String(50), nullable=False, unique=True)

    @property
    def data(self):
        return {
            'id': self.id,
            'name': self.name,
            'acronym': self.acronym
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_all(cls):
        r = cls.query.all()
        result = [i.data for i in r]
        return result
    
    @classmethod
    def get_by_acronym(cls, acronym):
        return cls.query.filter(cls.acronym == acronym).first()

class Student(db.Model):
    __tablename__ = 'student'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    registration_number = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    course_acronym = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    @property
    def data(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone_number': self.phone_number,
            'registration_number': self.registration_number,
            'course_acronym': self.course_acronym,
            'password': self.password
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_all(cls):
        r = cls.query.all()
        result = [i.data for i in r]
        return result

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter(cls.id == id).first()

    @classmethod
    def get_by_registration_number_password(cls, registration_number, password):
        return cls.query.filter(cls.registration_number == registration_number, cls.password == password).first()

class Admin(db.Model):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False, unique=True, default='admin@example.com')
    password = db.Column(db.String(255), nullable=False, default='123')
    created_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    @property
    def data(self):
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_all(cls):
        r = cls.query.all()
        result = []

        for i in r:
            result.append(i.data)
        return result
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter(cls.id == id).first()

    @classmethod
    def get_by_email_password(cls, email, password):
        return cls.query.filter(cls.email == email, cls.password == password).first()
