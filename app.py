from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from ping_service import PingService
import threading
import schedule
import time

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

class Historique(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipement_id = db.Column(db.Integer, db.ForeignKey('equipement.id'), nullable=False)
    disponible = db.Column(db.Boolean, nullable=False)
    temps_reponse = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    equipement = db.relationship('Equipement', backref='historiques')

class Alerte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipement_id = db.Column(db.Integer, db.ForeignKey('equipement.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50))  # 'down', 'up'
    lue = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    equipement = db.relationship('Equipement', backref='alertes')

# ---------- FONCTIONS UTILITAIRES ----------
def ajouter_equipements_test():
    if Equipement.query.count() == 0:
        equipements = [
            Equipement(nom='Serveur Web', adresse_ip='192.168.1.10', type='serveur', emplacement='Salle serveur A'),
            Equipement(nom='Routeur Principal', adresse_ip='192.168.1.1', type='routeur', emplacement='Local technique'),
            Equipement(nom='Switch Core', adresse_ip='192.168.1.2', type='switch', emplacement='Local technique'),
            Equipement(nom='Imprimante Bureau', adresse_ip='192.168.1.100', type='imprimante', emplacement='Bureau 101'),
            Equipement(nom='Google DNS', adresse_ip='8.8.8.8', type='serveur', emplacement='Externe'),
        ]
        for e in equipements:
            db.session.add(e)
        db.session.commit()
        print("✅ Équipements de test ajoutés !")

# ---------- SERVICE DE PING AUTOMATIQUE ----------
def ping_automatique():
    """Vérifie tous les équipements et crée des alertes si changement"""
    with app.app_context():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Vérification automatique...")
        equipements = Equipement.query.all()
        nb_alertes = 0
        
        for e in equipements:
            disponible, temps = PingService.ping(e.adresse_ip)
            
            # Détecter un changement de statut
            if disponible != e.actif:
                if disponible:
                    # Équipement revenu en ligne
                    message = f"🟢 {e.nom} ({e.adresse_ip}) est de nouveau EN LIGNE"
                    type_alerte = 'up'
                else:
                    # Équipement tombé
                    message = f"🔴 {e.nom} ({e.adresse_ip}) est HORS LIGNE"
                    type_alerte = 'down'
                
                alerte = Alerte(
                    equipement_id=e.id,
                    message=message,
                    type=type_alerte
                )
                db.session.add(alerte)
                nb_alertes += 1
                print(f"  ⚠️  {message}")
                
                e.actif = disponible
            
            # Enregistrer l'historique
            historique = Historique(
                equipement_id=e.id,
                disponible=disponible,
                temps_reponse=temps
            )
            db.session.add(historique)
        
        db.session.commit()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Vérification terminée ({nb_alertes} alerte(s))")

def run_scheduler():
    time.sleep(10)
    schedule.every(5).minutes.do(ping_automatique)
    ping_automatique()
    while True:
        schedule.run_pending()
        time.sleep(1)

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()
print("✅ Scheduler de ping automatique démarré (toutes les 5 minutes)")

# ---------- ROUTES ----------
@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    equipements = Equipement.query.all()
    total = len(equipements)
    actifs = sum(1 for e in equipements if e.actif)
    
    stats = {
        'total': total,
        'actifs': actifs,
        'inactifs': total - actifs,
        'taux_disponibilite': (actifs / total * 100) if total > 0 else 0
    }
    
    # Récupérer les alertes non lues
    alertes = Alerte.query.filter_by(lue=False).order_by(Alerte.timestamp.desc()).limit(10).all()
    nb_alertes_non_lues = Alerte.query.filter_by(lue=False).count()
    
    return render_template('dashboard.html',
                         equipements=equipements,
                         stats=stats,
                         alertes=alertes,
                         nb_alertes_non_lues=nb_alertes_non_lues)

@app.route('/api/ping_all', methods=['POST'])
def api_ping_all():
    equipements = Equipement.query.all()
    resultats = []
    
    for e in equipements:
        disponible, temps = PingService.ping(e.adresse_ip)
        
        # Créer une alerte si changement
        if disponible != e.actif:
            if disponible:
                message = f"🟢 {e.nom} ({e.adresse_ip}) est de nouveau EN LIGNE"
                type_alerte = 'up'
            else:
                message = f"🔴 {e.nom} ({e.adresse_ip}) est HORS LIGNE"
                type_alerte = 'down'
            
            alerte = Alerte(
                equipement_id=e.id,
                message=message,
                type=type_alerte
            )
            db.session.add(alerte)
            e.actif = disponible
        
        historique = Historique(
            equipement_id=e.id,
            disponible=disponible,
            temps_reponse=temps
        )
        db.session.add(historique)
        
        resultats.append({
            'nom': e.nom,
            'ip': e.adresse_ip,
            'disponible': disponible,
            'temps_reponse': temps
        })
    
    db.session.commit()
    return jsonify({'success': True, 'resultats': resultats})

@app.route('/historique')
def historique():
    equipement_id = request.args.get('equipement_id', type=int)
    jours = request.args.get('jours', 7, type=int)
    
    query = Historique.query
    
    if equipement_id:
        query = query.filter_by(equipement_id=equipement_id)
    
    date_limit = datetime.utcnow() - timedelta(days=jours)
    query = query.filter(Historique.timestamp >= date_limit)
    
    historiques = query.order_by(Historique.timestamp.desc()).limit(500).all()
    equipements = Equipement.query.all()
    
    return render_template('historique.html',
                         historiques=historiques,
                         equipements=equipements,
                         equipement_id=equipement_id,
                         jours=jours)

@app.route('/alertes')
def alertes():
    """Page dédiée aux alertes"""
    toutes_alertes = Alerte.query.order_by(Alerte.timestamp.desc()).limit(100).all()
    return render_template('alertes.html', alertes=toutes_alertes)

@app.route('/api/alerte_lue/<int:alerte_id>', methods=['POST'])
def alerte_lue(alerte_id):
    """Marquer une alerte comme lue"""
    alerte = Alerte.query.get_or_404(alerte_id)
    alerte.lue = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/alertes_lues_toutes', methods=['POST'])
def alertes_lues_toutes():
    """Marquer toutes les alertes comme lues"""
    Alerte.query.filter_by(lue=False).update({'lue': True})
    db.session.commit()
    return jsonify({'success': True})

@app.route('/ajouter_equipement')
def ajouter_equipement():
    return "➕ Page ajout d'équipement - En construction..."

# ---------- CRÉER LES TABLES ----------
with app.app_context():
    db.create_all()
    ajouter_equipements_test()
    print("✅ Tables créées avec succès !")

if __name__ == '__main__':
    app.run(debug=True)