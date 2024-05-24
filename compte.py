"""
Exercice de validation
"""
from datetime import datetime
import re

from flask import Flask, render_template, request, redirect, url_for, abort, make_response, session, flash, Blueprint, \
    jsonify
from produit import bp_produit
import bd

app = Flask(__name__)

regex_courriel = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

caracteres_interdits = re.compile('<|>')

app.secret_key = "cf8431380d807e3944ed5dd5c2d1d119b1f2dbcaa55910fa891aa3f190bb2beb"

bp_compte = Blueprint('compte', __name__)


@bp_compte.route('/authentifier', methods=["POST", "GET"])
def authentifier():
    with bd.creer_connexion() as conn:
        produits = bd.get_produits(conn)
        if request.method == "POST":
            # À faire une seule fois, lorsqu'on crée la session :
            session.permanent = True
            confirmation = None

            # confirmation = (request.args.get("confirmation") == "ok")

            courriel = request.form['courriel']
            # mdp_hache = bd.hacher_mdp(request.form['mdp'])

            mdpHache = bd.hacher_mdp(request.form['mdp'])
            mdp = request.form['mdp']

            with bd.creer_connexion() as conn:
                user = bd.authetifier(conn, courriel, mdpHache)
                if user is not None:
                    session['identifiant'] = user["id_utilisateur"]
                    session['courriel'] = user["courriel"]
                    session['mdp'] = user["mdp"]
                    nom = user["nom"]
                    session['authentifie'] = True
                    session['role'] = "user"

                    if user["est_administrateur"] == 1:
                        session['role'] = "admin"
                    return redirect(url_for('index', produits=produits, est_authentifie=True))
                else:
                    confirmation = False
                    # abort(400,f"Courriel ou mot de passe incorrecte ")
                    return render_template("authentifier.jinja",
                                           produits=produits,
                                           courriel=courriel,
                                           mdp=mdp,
                                           confirmation=confirmation)



    return render_template("authentifier.jinja",
                           produits=produits,
                           confirmation=None)


@bp_compte.route('/creer', methods=["POST", "GET"])
def creer():
    message = None  # Initialiser le message à None
    if request.method == "POST":
        courriel = request.form["courriel"]
        nom = request.form["nom"]
        identifiant = request.form["identifiant"]
        adresse = request.form["adresse"]

        if request.form["mdp"] == request.form["mdp1"]:
            mdpHache = bd.hacher_mdp(request.form['mdp'])

            user = {
                "id_utilisateur": identifiant,
                "courriel": courriel,
                "adresse_postale": adresse,
                "nom": nom,
                "mdp": mdpHache
            }

            with bd.creer_connexion() as conn:
                utilisateur_cree = bd.ajouter_utilisateur(conn, user)
                if utilisateur_cree:
                    message = "Compte créé avec succès!"
                    return render_template("authentifier.jinja", confirmation= True)
                else:
                    message = "Erreur lors de la création du compte."

    return render_template("creer.jinja", message=message)


@bp_compte.route('/creer/verifier_identifiant', methods=["GET"])
def verifier_identifiant():
    identifiant = request.args.get('identifiant')
    with bd.creer_connexion() as conn:
        existe = bd.existe_identifiant(conn, identifiant)
    # S'assurer que la réponse est toujours un JSON
    return jsonify(existe=existe)


@bp_compte.route('/deconnecter')
def deconnecter():
    """Détruit la session"""

    # # Effacer seulement une information :
    # session.pop("prenom", default=None)

    # Tout effacer :
    session.clear()

    # return render_template('deconnecter.jinja')
    with bd.creer_connexion() as conn:
        return redirect(url_for('index', produits=bd.get_produits(conn), est_authentifie=False))


@bp_compte.route('/administration')
def administration():
    if "identifiant" not in session:
        abort(401, "Vous devez être authentifié")

    if session["role"] != "admin":
        abort(403, "Vous n'avez pas l'accès")

    return render_template('administration.jinja')
