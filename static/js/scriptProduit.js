/**
 * Script pour l'affichage de suggestion de recherche
 */

"use strict"

document.addEventListener('DOMContentLoaded', async function () {
    const quantiteDisplay = document.getElementById('quantite-display');
    const container = document.getElementById('product-container');
    const path = window.location.pathname;
    const pathSegments = path.split('/');
    const productId = pathSegments[pathSegments.length - 1];


    // Fonction pour mettre à jour la quantité du produit régulièrement
    function fetchQuantite() {
        fetch(`/produit/api/quantite/${productId}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error("Erreur lors de la récupération de la quantité");
                } else {
                    quantiteDisplay.textContent = `Quantité disponible: ${data.quantite}`;
                }
            })
            .catch(error => console.error("Erreur AJAX: ", error));
    }

    // Appeler fetchQuantite immédiatement et ensuite toutes les 5 secondes
    fetchQuantite();
    setInterval(fetchQuantite, 5000);
});


document.getElementById('btn-show-form').addEventListener('click', function() {
    document.getElementById('form-modifier-image').style.display = 'block';
});

document.getElementById('form-modifier-image').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const path = window.location.pathname;
    const pathSegments = path.split('/');
    const productId = pathSegments[pathSegments.length - 1];

    fetch(`/produit/modifier_image/${productId}`, {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mettre à jour l'image sur la page
            document.getElementById('productImage').src = data.img_path;
            //alert('Image modifiée avec succès !');
            window.location.href = data.redirect_url;
            document.getElementById('form-modifier-image').style.display = 'none';  // Cachez le formulaire après la mise à jour
        } else {
            alert('Erreur lors de la modification de l\'image.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Erreur de chargement du produit');
    });
});
