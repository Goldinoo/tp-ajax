"""
Connexion à la BD.
"""
import hashlib
import types
import contextlib
import mysql.connector


@contextlib.contextmanager
def creer_connexion():
    """Pour créer une connexion à la BD"""
    conn = mysql.connector.connect(
        user="garneau",
        password="qwerty123",
        host="127.0.0.1",
        database="420_05c_magasin",
        raise_on_warnings=True
    )

    # Pour ajouter la méthode getCurseur() à l'objet connexion
    conn.get_curseur = types.MethodType(get_curseur, conn)

    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()


@contextlib.contextmanager
def get_curseur(self):
    """Permet d'avoir *tous* les enregistrements dans un dictionnaire"""
    curseur = self.cursor(dictionary=True, buffered=True)
    try:
        yield curseur
    finally:
        curseur.close()


def get_produits(conn):
    "Retourne tous les produits"
    with conn.get_curseur() as curseur:
        curseur.execute("""
                    SELECT id_produit, titre, description, prix, quantite, image
                    FROM produit
                    ORDER BY id_produit DESC  # Supposant que l'ID est auto-incrémenté et représente la nouveauté
                    LIMIT 5
                """)
        return curseur.fetchall()


def get_produits_recherche(conn, motCles):
    "Retourne tous les produits"
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT id_produit, titre, description, prix, quantite, image "
                        "FROM produit WHERE titre LIKE %s",
                        ('%' + motCles + '%',))
        return curseur.fetchall()

def get_produits_recherche_paginated(conn, motCles, offset, limit):
    # Assurez-vous d'adapter cette méthode pour supporter la pagination dans votre base de données
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_produit, titre, description, prix, quantite, image
        FROM produit 
        WHERE titre LIKE %s 
        ORDER BY titre 
        LIMIT %s OFFSET %s
        """, ('%' + motCles + '%', limit, offset))
    return cursor.fetchall()


def get_produit(conn, id_produit):
    "Retourne un produit"
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT id_produit, titre, description, prix, quantite, image"
                        " FROM produit"
                        " WHERE id_produit = %(id)s",
                        {"id": id_produit})
        return curseur.fetchone()


def hacher_mdp(mdp_en_clair):
    return hashlib.sha512(mdp_en_clair.encode()).hexdigest()


def update_produit_image(conn, id_produit, image_path):
    with conn.cursor() as cursor:
        cursor.execute("UPDATE produit SET image=%s WHERE id_produit=%s", (image_path, id_produit))
        conn.commit()


def authetifier(conn, courriel, mdp):
    """Pour se connecter"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT id_utilisateur,courriel, mdp, nom, est_administrateur from utilisateur"
            " where courriel=%(courriel)s AND mdp=%(mdp)s",
            {
                "courriel": courriel,
                "mdp": mdp
            }
        )
        return curseur.fetchone()


def ajouter_utilisateur(conn, utilisateur):
    with conn.get_curseur() as curseur:
        curseur.execute(
            "INSERT INTO utilisateur (id_utilisateur, adresse_postale, courriel, nom,  mdp) VALUES (%(id_utilisateur)s, %(courriel)s, %(adresse_postale)s, %(nom)s, %(mdp)s)",
            {
                "courriel": utilisateur["courriel"],
                "id_utilisateur": utilisateur["id_utilisateur"],
                "adresse_postale": utilisateur["adresse_postale"],
                "nom": utilisateur["nom"],
                "mdp": utilisateur["mdp"]
            }

        )
        return curseur.lastrowid


def existe_identifiant(conn, identifiant):
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM utilisateur WHERE id_utilisateur = %s", (identifiant,))
        existe = cursor.fetchone()[0] > 0
    return existe


def mettre_a_jour_produit(conn, id_produit, quantite):
    with conn.get_curseur() as curseur:
        curseur.execute(
            "UPDATE `produit` SET `quantite` = %(quantite)s WHERE id_produit = %(id)s ",
            {
                "quantite": quantite,
                "id": id_produit
            }
        )
        return True


def ajouter_achat(conn, date_achat, quantite, id_user, id_produit):
    with conn.get_curseur() as curseur:
        curseur.execute(
            "INSERT INTO achat (date_achat, quantite, fk_utilisateur, fk_produit) "
            "VALUES (%(date_achat)s, "
            "%(quantite)s, "
            "%(id_user)s, "
            "%(id_produit)s) "
            ,
            {
                "date_achat": date_achat,
                "quantite": quantite,
                "id_produit": id_produit,
                "id_user": id_user
            })

        return True


def get_achats(conn, id_user):
    "Retourne tous les achats"
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT id_achat, date_achat, quantite, fk_utilisateur, fk_produit "
                        "FROM achat where fk_utilisateur= %(id_user)s",
                        {
                            "id_user": id_user
                        })
        return curseur.fetchall()
