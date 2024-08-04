class Config:
    # SESSION_COOKIE_SECURE=True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@127.0.0.1:3306/studentMonitoring'
    SQLALCHEMY_TRACK_MODIFICATIONS = False