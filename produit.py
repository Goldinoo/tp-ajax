import io
import os
from datetime import datetime
import re

from flask import Flask, render_template, request, redirect, url_for, abort, make_response, session, flash, Blueprint, \
    jsonify, json, Response, send_file, send_from_directory
from werkzeug.utils import secure_filename

import bd
from flask import current_app

bp_produit = Blueprint('produit', __name__)


# @bp_produit.route('/<int:identifiant>', methods=['GET', 'POST'])
# def produit(identifiant):
#     """Affiche les détails d'un produit ou renvoie des données JSON selon l'Accept header."""
#
#     with bd.creer_connexion() as conn:
#         produit = bd.get_produit(conn, identifiant)
#         if produit is None:
#             abort(404, "Produit non trouvé")
#
#     # Vérifier si la requête demande du JSON
#     if request.headers.get('Accept') == 'application/json':
#         return jsonify(produit)
#
#     # Sinon, retourner la page HTML
#     est_authentifie = 'identifiant' in session
#     peut_modifier = session.get("role") == "admin"
#
#
#     return render_template('produit.jinja',
#                            identifiant=identifiant,
#                            produit=produit,
#                            authentifie=est_authentifie,
#                            peut_modifier=peut_modifier)



@bp_produit.route('/<int:identifiant>', methods=['GET', 'POST'])
def produit(identifiant):
    """Affiche le mur d'un utilisateur"""

    # identifiant = request.args.get("identifiant")
    # if not identifiant:
    #     abort(400)
    messages = []
    authentifie = False
    # if "identifiant" not in session:
    # abort(401, "Vous devez être authentifié")
    # return render_template('index.jinja', message="Vous devez être authentifié")

    confirmation = (request.args.get("confirmation") == "ok")

    with bd.creer_connexion() as conn:
        produit = bd.get_produit(conn, identifiant)
        if produit is None:
            abort(404, "Utilisateur n'existe pas")

    if "identifiant" not in session:
        return render_template('produit.jinja',
                               identifiant=identifiant,
                               produit=produit,
                               authentifie=False)

    peut_modifier = False

    if session["role"] == "admin":
        peut_modifier = True

    # if request.method == "POST":
    #     quantite = int(request.form.get('quantite'))
    #     if bd.mettre_a_jour_produit(conn, identifiant, quantite):
    #         return render_template("confirmation.jinja",
    #                                produit=produit,
    #                                quantite=quantite)

    # Code pour déduire la quantité et enregistrer la transaction

    return render_template('produit.jinja',
                           identifiant=identifiant,
                           produit=produit,
                           authentifie=True,
                           peut_modifier=peut_modifier)

# @bp_produit.route('/image/<int:id_produit>')
# def image(id_produit):
#     with bd.creer_connexion() as conn:
#         produit = bd.get_produit(conn, id_produit)
#         if produit and produit['image']:
#             return Response(io.BytesIO(produit['image']), mimetype='image/png')  # Assurez-vous du format de l'image
#         else:
#             return send_file('../static/images/produits/product.jpg', mimetype='image/jpeg')


@bp_produit.route('/modifier_image/<int:id_produit>', methods=['POST'])
def modifier_image(id_produit):
    if 'nouvelle_image' in request.files:
        image_file = request.files['nouvelle_image']
        if image_file :  # Vérifiez l'extension du fichier
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.config['CHEMIN_VERS_AJOUTS'], filename)
            image_file.save(image_path)

            with bd.creer_connexion() as conn:
                bd.update_produit_image(conn, id_produit, filename)

            flash('Image mise à jour avec succès.', 'success')
            #return redirect(url_for('produit.produit', identifiant=id_produit))
            json = jsonify({'success': True, 'redirect_url': url_for('produit.produit', identifiant=id_produit)})
            return json

    flash('Échec de la mise à jour de l''image.', 'error')
    return redirect(url_for('produit.produit', identifiant=id_produit))

# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp_produit.route('/images/ajouts/<filename>')
def serve_image(filename):

    #name = filename.replace("b'", "").replace("'", "")
    name = filename

    if name == "":
        return send_from_directory(current_app.config['CHEMIN_VERS_AJOUTS'], "product.jpg")
    else:
        return send_from_directory(current_app.config['CHEMIN_VERS_AJOUTS'], name)

@bp_produit.route('/api/quantite/<int:id_produit>')
def quantite_produit(id_produit):
    with bd.creer_connexion() as conn:
        produit = bd.get_produit(conn, id_produit)
        if produit is None:
            return jsonify({"error": "Produit non trouvé"}), 404
        return jsonify({"quantite": produit['quantite']})


