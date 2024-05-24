/**
 * Script pour démontrer data-
 */

"use strict";


/**
 * Appelée lors de l'initialisation de la page.
 */
function initialisation() {
    const p = document.getElementById("information-cachee")
    console.log(p.dataset.message)
    console.log(p.dataset.reponseUniverselle)
    console.log(p.dataset.unNomLong)
}

window.addEventListener("load", initialisation)