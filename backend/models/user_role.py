from .user import db

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('roles', lazy='dynamic'))
    role = db.relationship('Role', backref=db.backref('users', lazy='dynamic'))
    
    def __repr__(self):
        return f'<UserRole user_id={self.user_id} role_id={self.role_id}>' 