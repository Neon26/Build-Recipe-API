from flask import Flask, request, make_response, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth

class Config():
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")

app = Flask(__name__)
app.config.from_object(Config)
db= SQLAlchemy(app)
migrate=Migrate(app,db)
basic_auth = HTTPBasicAuth()

@basic_auth.verify_password
def verify_password(email, password):
    u = User.query.filter_by(email=email).first()
    if u is None:
        return False
    g.current_user = u
    return u.check_hashed_password(password)


class User(db.Model):
    __tablename__ = "user"  
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, index=True)
    password = db.Column(db.String)
    recipes = db.relationship("Recipe", backref='author',lazy="dynamic", cascade ='all, delete-orphan')

    def __repr__(self):
        return f'<{self.user_id} | {self.email}>'
    
    def hash_password(self, original_password):
        return generate_password_hash(original_password)

    def check_hashed_password(self, login_password):
        return check_password_hash(self.password, login_password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def from_dict(self,data):
        self.email = data['email']
        self.password=self.hash_password(data['password'])

    def to_dict(self):
        return {"user_id": self.user_id,
        "email":self.email
        }

@app.post('/user')
def create_user():
    data = request.json
    user = User()
    user.from_dict(data)
    user.save()
    return make_response(user.to_dict(), 200)

@app.get('/user/<int:id>')
def get_user(id):
    return make_response(User.query.get(id).to_dict(), 200)

@app.get('/users')
def get_users():
    return make_response(User.query.all(), 200)    

@app.put('/user/<int:id>')
def edit_user(id):
    user = User.query.get(id)
    data = request.json
    user.from_dict(data)
    user.save()
    return make_response(user.to_dict(), 200)

@app.delete('/user/<int:id>')
def delete_user(id):
    user = User.query.get(id)
    user.delete()
    return make_response({"message": "User deleted"}, 200)   
    

@app.get('/user/<int:id>/recipes')
def get_user_recipes(id):
    return make_response(Recipe.query.filter_by(user_id=id).all(), 200) 



class Recipe(db.Model):
    __tablename__ = "recipes"
    recipe_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    body = db.Column(db.String)
    user_id = db.Column(db.ForeignKey('user.user_id'))

    def __repr__(self):
        return f'<{self.recipe_id} | {self.title}>'

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def from_dict(self, data):
        self.title = data['title']
        self.body = data['body']
        self.user_id = data['user_id']

    def to_dict(self):
        return {
            "recipe_id": self.recipe_id,
            "title":self.title,
            "body":self.body,
            "user_id":self.user_id
            }




@app.post('/recipe')
def create_recipe():
    data = request.json
    recipe = Recipe()
    recipe.from_dict(data)
    recipe.save()
    return make_response(recipe.to_dict(), 200)

@app.get('/recipe/<int:id>')
def get_recipe(id):
    return make_response(Recipe.query.get(id).to_dict(), 200)

@app.get('/recipes')
def get_recipes():
    return make_response(Recipe.query.all(), 200)


@app.put('/recipe/<int:id>')
def edit_recipe(id):
    recipe = Recipe.query.get(id)
    data = request.json
    recipe.from_dict(data)
    recipe.save()
    return make_response(recipe.to_dict(), 200)

@app.delete('/recipe/<int:id>')
def delete_recipe(id):
    recipe = Recipe.query.get(id)
    recipe.delete()
    return make_response({"message": "Recipe deleted"}, 200)




if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
    