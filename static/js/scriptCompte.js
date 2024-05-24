/**
 * Script pour l'affichage de suggestion de recherche
 */

"use strict"


document.addEventListener('DOMContentLoaded', function() {
    const identifiantInput = document.getElementById('identifiant');
    const msgDiv = document.getElementById('identifiant-msg');
    const submitButton = document.querySelector('input[type="submit"]');

    identifiantInput.addEventListener('blur', function() {
        const identifiant = encodeURIComponent(this.value);
        fetch(`/compte/creer/verifier_identifiant?identifiant=${identifiant}`)
            .then(response => response.json())
            .then(data => {
                if (data.existe) {
                    msgDiv.textContent = 'Identifiant déjà utilisé.';
                    submitButton.disabled = true;
                } else {
                    msgDiv.textContent = '';
                    submitButton.disabled = false;
                }
            })
            .catch(error => {
                console.error('Erreur lors de la vérification de l\'identifiant:', error);
                msgDiv.textContent = 'Erreur lors de la vérification.';
            });
    });
});



