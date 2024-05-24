"""
Exercice de validation
"""
import os
from datetime import datetime
import re

from flask import Flask, render_template, request, redirect, url_for, abort, make_response, session, flash, Blueprint, \
    jsonify, send_from_directory
from produit import bp_produit
from compte import bp_compte
import bd

app = Flask(__name__)

app.register_blueprint(bp_produit, url_prefix='/produit')
app.register_blueprint(bp_compte, url_prefix='/compte')

regex_courriel = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

caracteres_interdits = re.compile('<|>')

app.secret_key = "cf8431380d807e3944ed5dd5c2d1d119b1f2dbcaa55910fa891aa3f190bb2beb"
app.config['UPLOAD_FOLDER'] = 'chemin/vers/le/dossier/des/images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Utilisez os.path.join pour construire les chemins de manière sécurisée
app.config['MORCEAUX_VERS_AJOUTS'] = ["static", "images", "ajouts"]
app.config['ROUTE_VERS_AJOUTS'] = "/".join(app.config['MORCEAUX_VERS_AJOUTS'])
app.config['CHEMIN_VERS_AJOUTS'] = os.path.join(
    app.instance_path.replace("instance", ""),  # Assurez-vous que ce chemin est correct et que le dossier existe
    *app.config['MORCEAUX_VERS_AJOUTS']
)

@app.route('/')
def index():
    """Affiche les jeux"""
    produits = []

    with bd.creer_connexion() as conn:
        produits = bd.get_produits(conn)

    if "identifiant" not in session:
        # return render_template('index.jinja', message="Vous devez être authentifié")
        return render_template('index.jinja',
                               produits=produits,
                               authentifie=False)
        # nom = session["nom"]

    """Affiche l'accueil"""
    return render_template('index.jinja',
                           produits=produits,
                           authentifie=True)


@app.route('/api/recherche')
def api_recherche():
    motCles = request.args.get('mots-cles', '').strip()
    ajax = request.args.get('ajax', 0)  # Paramètre pour identifier si c'est une requête AJAX

    with bd.creer_connexion() as conn:
        if ajax:
            resultats = bd.get_produits_recherche(conn, motCles)
            return jsonify([{
                'id': prod['id_produit'],
                'titre': prod['titre'],
                'description': prod['description'],
                'prix': prod['prix'],
                'quantite': prod['quantite'],
                'image': prod['image']
            } for prod in resultats])
        else:
            resultats = bd.get_produits_recherche(conn, motCles)
            if "identifiant" not in session:
                return render_template('index.jinja',
                                       produits=resultats,
                                       authentifie=False)
            else:
                return render_template('index.jinja',
                                       produits=resultats,
                                       authentifie=True)

@app.route('/api/produits-recents')
def produits_recents():
    with bd.creer_connexion() as conn:
        produits = bd.get_produits(conn)
    return jsonify([{
        'id': p['id_produit'],
        'titre': p['titre'],
        'description': p['description'],
        'prix': p['prix'],
        'quantite': p['quantite'],
        'image': p['image']
    } for p in produits])





# @app.route('/rechercher', methods=["GET"])
# def rechercher():
#     resultats = []
#
#     motCles = request.args.get("chercher")
#     # motCLes = request.form['chercher']
#
#     with bd.creer_connexion() as conn:
#         resultats = bd.get_produits_recherche(conn, motCles)
#
#         # if "identifiant" not in session:
#         #     # abort(401, "Vous devez être authentifié")
#         #     return render_template('index.jinja', message="Vous devez être authentifié")
#
#         """Affiche l'accueil"""
#         return render_template('index.jinja',
#                                resultats=resultats)


# @app.route('/confrimation', methods=['GET', 'POST'])
# def confirmation(identifiant):
#
#     with bd.creer_connexion() as conn:
#         if request.method == "POST":
#             quantite = int(request.form.get('quantite'))
#             if bd.mettre_a_jour_produit(conn, identifiant, quantite):
#                 return render_template("confirmation.jinja",
#                                        produit=produit,
#                                        quantite=quantite)
#     return render_template("confirmation.jinja")


@app.route('/acheter/<int:id>', methods=['POST'])
def acheter(id):
    with bd.creer_connexion() as conn:
        produit = bd.get_produit(conn, id)

    if produit is None:
        flash("Produit non trouvé", "error")
        return redirect(url_for('index'))

    # quantite_demandee = request.form.get('inputQte')
    quantite_demandee = int(request.form['inputQte'])

    if quantite_demandee > produit['quantite']:
        flash("Quantité demandée non disponible", "error")
        return redirect(url_for('produit', id=id))

    nouvelle_quantite = produit['quantite'] - quantite_demandee

    id_user = session['identifiant']

    with bd.creer_connexion() as conn:
        bd.ajouter_achat(conn, datetime.now(), nouvelle_quantite, id_user, produit["id_produit"])
        bd.mettre_a_jour_produit(conn, id, nouvelle_quantite)
        flash('Achat effectué avec succès!', 'success')

    return redirect(url_for('confirmation'))


@app.route('/confirmation')
def confirmation():
    # identifiant = request.args.get('identifiant')
    # quantite = request.args.get('quantite')
    # return render_template('confirmation.jinja', identifiant=identifiant, quantite=quantite)
    return render_template("confirmation.jinja")


@app.route('/compte/achats/<int:id>')
def achats(id):
    # identifiant = request.args.get('identifiant')
    # quantite = request.args.get('quantite')
    # return render_template('confirmation.jinja', identifiant=identifiant, quantite=quantite)

    with bd.creer_connexion() as conn:
        achats = bd.get_achats(conn, id)

    return render_template("achats.jinja", achats=achats)




@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.jinja'), 404


@app.errorhandler(400)
def page_not_found(error):
    return render_template('400.jinja'), 400


@app.errorhandler(500)
def internal_error(error):
    print(error)

    return render_template('500.jinja'), 500
