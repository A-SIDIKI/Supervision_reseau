from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from ping_service import PingService

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ma-super-cle-secrete-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///supervision.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------- MODÈLES ----------
class Equipement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    adresse_ip = db.Column(db.String(15), nullable=False, unique=True)
    type = db.Column(db.String(50))
    emplacement = db.Column(db.String(100))
    actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Equipement {self.nom} ({self.adresse_ip})>'

class Historique(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipement_id = db.Column(db.Integer, db.ForeignKey('equipement.id'), nullable=False)
    disponible = db.Column(db.Boolean, nullable=False)
    temps_reponse = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    equipement = db.relationship('Equipement', backref='historiques')

def ajouter_equipements_test():
    if Equipement.query.count() == 0:
        equipements = [
            Equipement(nom='Serveur Web', adresse_ip='192.168.1.10', type='serveur', emplacement='Salle serveur A'),
            Equipement(nom='Routeur Principal', adresse_ip='192.168.1.1', type='routeur', emplacement='Local technique'),
            Equipement(nom='Switch Core', adresse_ip='192.168.1.2', type='switch', emplacement='Local technique'),
            Equipement(nom='Imprimante Bureau', adresse_ip='192.168.1.100', type='imprimante', emplacement='Bureau 101'),
        ]
        for e in equipements:
            db.session.add(e)
        db.session.commit()
        print("✅ Équipements de test ajoutés !")

# ---------- ROUTES ----------
@app.route('/')
def index():
    return "🚀 Projet 2 : Supervision Réseau - Service de ping intégré !"

@app.route('/tester_ping')
def tester_ping():
    """Route de test pour vérifier le ping des équipements"""
    equipements = Equipement.query.all()
    resultats = []
    
    for e in equipements:
        disponible, temps = PingService.ping(e.adresse_ip)
        resultats.append({
            'nom': e.nom,
            'ip': e.adresse_ip,
            'disponible': disponible,
            'temps_reponse': temps
        })
    
    return jsonify(resultats)

with app.app_context():
    db.create_all()
    ajouter_equipements_test()
    print("✅ Tables créées avec succès !")

if __name__ == '__main__':
    app.run(debug=True)