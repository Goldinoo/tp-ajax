/**
 * Script pour l'affichage de suggestion de recherche
 */

"use strict"

let controleur = null
let rechercheActive = false;
//////////////////////////////////////////////////////////////////////////////////////////////////////
//****************Recherche*****************//////////////////////
let page = 1;  // Page initiale
const resultatsParPage = 5;  // Nombre de résultats par page
const suggestions = document.getElementById('suggestions');

async function rechercherSuggestions(texte) {
    if (texte.length > 2) {
        if (controleur !== null) {
            controleur.abort();
        }
        controleur = new AbortController();

        try {
            // Ajout des paramètres pour la pagination
            const resultats = await envoyerRequeteAjax(
                "/api/recherche",
                "GET",
                {"mots-cles": texte, "page": page, "resultats-par-page": resultatsParPage, "ajax": "1"},
                controleur
            );

            suggestions.innerHTML = '';  // Vider les suggestions précédentes
            suggestions.innerHTML = '';  // Vider les suggestions précédentes
            if (resultats.length > 0) {
                const pages = Math.ceil(resultats.length / resultatsParPage);  // Calculer le nombre total de pages
                const debut = (page - 1) * resultatsParPage;
                const fin = debut + resultatsParPage;
                const resultatsPage = resultats.slice(debut, fin);

                const ul = document.createElement('ul');
                ul.className = 'suggestions-list';  // Utilisation d'une classe pour le style

                resultatsPage.forEach(prod => {
                    const li = document.createElement('li');
                    li.className = 'suggestion-item';  // Utilisation d'une classe pour le style
                    const a = document.createElement('a');
                    a.href = `/produit/${prod.id}`;
                    a.textContent = prod.titre;
                    a.className = 'suggestion-link';
                    li.appendChild(a);
                    ul.appendChild(li);
                });
                suggestions.appendChild(ul);
// Ajouter les boutons de navigation à l'intérieur de la liste des suggestions
                const boutonPrecedent = document.createElement('button');
                boutonPrecedent.textContent = 'Précédent';
                boutonPrecedent.classList.add("btn", "btn-primary", "mt-3")
                boutonPrecedent.onclick = pagePrecedente;
                ul.appendChild(boutonPrecedent);

                const boutonSuivant = document.createElement('button');
                boutonSuivant.textContent = 'Suivant';
                boutonSuivant.classList.add("btn", "btn-primary", "mt-3")
                boutonSuivant.onclick = pageSuivante
                ul.appendChild(boutonSuivant);

                suggestions.style.display = 'block';
            } else {
                suggestions.style.display = 'none';
            }
        } catch (err) {
            console.error("Erreur lors de la requête AJAX", err);
            suggestions.style.display = 'none';
        }
    } else {
        suggestions.style.display = 'none';
    }
}


// Fonctions pour la navigation entre les pages
function pagePrecedente() {
    if (page > 1) {
        page--;
        rechercherSuggestions(document.getElementById('recherche').value); // Mettre à jour les suggestions avec le nouveau numéro de page
    }
}

function pageSuivante() {
    page++;
    rechercherSuggestions(document.getElementById('recherche').value); // Mettre à jour les suggestions avec le nouveau numéro de page
}


async function envoyerRequeteAjax(
    url,
    methode = "GET",
    parametres = {},
    controleur = null
) {
    let urlCible = url;

    let body = null;
    if ((parametres !== null) && (Object.keys(parametres).length > 0)) {
        const paramStr = new URLSearchParams(parametres);
        if (methode.toUpperCase() === "GET") {
            urlCible = `${urlCible}?${paramStr}`;
        } else {
            body = paramStr;
        }
    }

    const parametresFetch = {
        method: methode,
        headers: {
            "Content-Type": 'application/x-www-form-urlencoded'
        },
        body: body,
        cache: "no-store"
    }

    if (controleur != null) {
        parametresFetch["signal"] = controleur.signal
    }

    const reponse = await fetch(
        urlCible,
        parametresFetch
    );

    if (!reponse.ok) {
        // Pour gérer les codes 4xx et 5xx :
        throw new Error(`${reponse.status} ${reponse.statusText}`)
    }

    return await reponse.json();
}


document.addEventListener('DOMContentLoaded', function () {
    //updateProduits()

    //Pour mettre à jour les produits chaque 5 secondes
    if (window.location.pathname === '/') {
        updateProduits()
        setInterval(updateProduitsConditionnel, 5000);

        const recherche = document.getElementById('recherche');
        const suggestions = document.getElementById('suggestions');


        recherche.addEventListener('input', function () {
            rechercherSuggestions(this.value);
        });

        recherche.addEventListener('keydown', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault();  // Empêcher le formulaire de soumettre
                lancerRecherche(this.value);
                suggestions.style.display = 'none';
            }
        });

        // Gestion du clic sur les suggestions
        suggestions.addEventListener('click', function (event) {
            if (event.target.tagName === 'A') {
                lancerRecherche(event.target.textContent);
                suggestions.style.display = 'none';
                //updateProduitsRecherche(motsCles)
            }
        });
    }


});

function effectuerRecherche() {
    const motsCles = document.getElementById('recherche').value;
    updateProduitsRecherche(motsCles);
    rechercheActive = true;
    return false; // Empêche la soumission normale du formulaire
}

function updateProduitsConditionnel() {
    if (!rechercheActive) {  // Vérifie si aucune recherche n'est active
        updateProduits();
    }
}

function lancerRecherche(query) {
    //window.location.href = `/produit/${query}`;  // Redirection vers la page de recherche/produit
    effectuerRecherche()
    enregistrerRecherche(query);
}

function enregistrerRecherche(query) {
    let recherches = JSON.parse(localStorage.getItem('recherches')) || [];
    if (!recherches.includes(query)) {
        recherches.push(query);
        localStorage.setItem('recherches', JSON.stringify(recherches));
    }
}

function afficherRecherchesRecentes() {
    if (window.location.pathname === '/') {
        let recherches = JSON.parse(localStorage.getItem('recherches')) || [];
        const container = document.getElementById('recherchesRecentes');
        container.innerHTML = '<h3>Recherches récentes</h3>';

        // Création du dropdown
        const select = document.createElement('select');
        select.className = "form-select w-25"; // Classe Bootstrap pour la mise en forme
        select.setAttribute('aria-label', 'Recherches récentes');

        // Option par défaut qui invite à choisir
        const defaultOption = document.createElement('option');
        defaultOption.selected = true;
        defaultOption.disabled = true;
        defaultOption.textContent = "Choisir une recherche récente";
        select.appendChild(defaultOption);

        // Récupérer seulement les 5 dernières recherches
        recherches = recherches.slice(-5);

        recherches.forEach(recherche => {
            const option = document.createElement('option');
            option.textContent = recherche;
            option.value = recherche;
            option.classList.add("p-2")
            select.appendChild(option);
        });

        // Gestionnaire d'événements pour la sélection
        select.onchange = function () {
            document.getElementById('recherche').value = this.value;
            // Supposez que vous avez une fonction pour lancer la recherche
            // lancerRecherche(this.value);
        };

        container.appendChild(select);
    }
}


async function updateProduits() {
    const response = await fetch('/api/produits-recents');
    const produits = await response.json();
    const container = document.getElementById('liste-produits');
    container.innerHTML = '';  // Nettoyer les anciens produits

    if (produits.length > 0) {
        container.style.marginTop = '200px';  // Ajouter un margin-top si des produits sont présents
    } else {
        container.style.marginTop = '0';  // Aucun margin-top si la liste est vide
    }

    produits.forEach(prod => {
        const divCol = document.createElement('div');
        divCol.className = 'col-3 mt-2';
        divCol.style.width = '18rem'; // Assure que toutes les colonnes ont une largeur uniforme

        const card = document.createElement('div');
        card.className = 'card rounded-3';
        card.style.width = '100%';  // Utiliser 100% de la largeur de la colonne parent
        card.style.height = '400px';  // Hauteur fixe pour toutes les cartes

        const img = document.createElement('img');
        img.className = 'w-100 h-75 card-img-top border-2 rounded-2';
        img.style.objectFit = 'cover'; // Assure que l'image couvre bien la zone dédiée sans déformer
        img.alt = `Image pour: ${prod.titre}`;
        img.id = 'productImage';

        if (prod.image === "")
            img.src = `/produit/images/ajouts/product.jpg`;
        else
            img.src = `/produit/images/ajouts/${prod.image}`;

        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';

        const title = document.createElement('h5');
        title.className = 'card-title mb-2';
        title.textContent = prod.titre;

        const detailsDiv = document.createElement('div');
        detailsDiv.className = 'd-flex justify-content-between mt-5';

        const detailLink = document.createElement('a');
        detailLink.href = `/produit/${prod.id}`;
        detailLink.className = 'btn btn-primary';
        detailLink.textContent = 'Plus de détail';
        detailLink.type = 'button';

        const price = document.createElement('h5');
        price.className = 'text-info';
        price.innerHTML = `<strong>${prod.prix}$</strong>`;

        detailsDiv.appendChild(detailLink);
        detailsDiv.appendChild(price);

        cardBody.appendChild(title);
        cardBody.appendChild(detailsDiv);

        card.appendChild(img);
        card.appendChild(cardBody);

        divCol.appendChild(card);

        container.appendChild(divCol);
    });
}

async function updateProduitsRecherche(motsCles) {
    if (motsCles.length > 0) {
        const response = await fetch(`/api/recherche?mots-cles=${encodeURIComponent(motsCles)}&ajax=1`);
        const produits = await response.json();
        const container = document.getElementById('liste-produits');
        container.innerHTML = '';  // Nettoyer les anciens produits

        if (produits.length > 0) {
            container.style.marginTop = '200px';  // Ajouter un margin-top si des produits sont présents
        } else {
            container.style.marginTop = '0';  // Aucun margin-top si la liste est vide
        }

        produits.forEach(prod => {
            const divCol = document.createElement('div');
            divCol.className = 'col-3 mt-2';
            divCol.style.width = '18rem'; // Assure que toutes les colonnes ont une largeur uniforme

            const card = document.createElement('div');
            card.className = 'card rounded-3';
            card.style.width = '100%';  // Utiliser 100% de la largeur de la colonne parent
            card.style.height = '400px';  // Hauteur fixe pour toutes les cartes

            const img = document.createElement('img');
            img.className = 'w-100 h-75 card-img-top border-2 rounded-2';
            img.style.objectFit = 'cover'; // Assure que l'image couvre bien la zone dédiée sans déformer
            img.alt = `Image pour: ${prod.titre}`;
            img.id = 'productImage';

            if (prod.image === "")
                img.src = `/produit/images/ajouts/product.jpg`;
            else
                img.src = `/produit/images/ajouts/${prod.image}`;

            const cardBody = document.createElement('div');
            cardBody.className = 'card-body';

            const title = document.createElement('h5');
            title.className = 'card-title mb-2';
            title.textContent = prod.titre;

            const detailsDiv = document.createElement('div');
            detailsDiv.className = 'd-flex justify-content-between mt-5';

            const detailLink = document.createElement('a');
            detailLink.href = `/produit/${prod.id}`;
            detailLink.className = 'btn btn-primary';
            detailLink.textContent = 'Plus de détail';
            detailLink.type = 'button';

            const price = document.createElement('h5');
            price.className = 'text-info';
            price.innerHTML = `<strong>${prod.prix}$</strong>`;

            detailsDiv.appendChild(detailLink);
            detailsDiv.appendChild(price);

            cardBody.appendChild(title);
            cardBody.appendChild(detailsDiv);

            card.appendChild(img);
            card.appendChild(cardBody);

            divCol.appendChild(card);

            container.appendChild(divCol);
        });
    }

}


window.addEventListener('load', function () {
    afficherRecherchesRecentes();
});