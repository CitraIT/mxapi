import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dns import resolver
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)


class MXEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.Text, unique=True)
    mx = db.Column(db.Text, unique=True)



@app.route("/mx/<domain>")
def root(domain):
    print(f'receive mx query for {domain}')
    try:
        entry_found = MXEntry.query.filter_by(domain=domain).first()
        if entry_found:
            print(f'serving mx query from database')
            return entry_found.mx
        else:
            answers = resolver.resolve(domain, "MX")
            if answers:
                mx = MXEntry(domain=domain, mx=str(answers[0].exchange))
                db.session.add(mx)
                db.session.commit()
                print(f'serving mx query fresh')
                return str(answers[0].exchange)
            else:
                return ""
    except Exception as e:
        return ""
       


def main():
    # setup database
    if not os.path.exists("db.sqlite"):
        with app.app_context():
            db.create_all()
    app.run(debug=True)




if __name__ == '__main__':
    main()
