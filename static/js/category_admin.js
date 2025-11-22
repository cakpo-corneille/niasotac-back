/**
 * static/admin/js/category_admin.js
 * Aperçu en temps réel des icônes uploadées
 */

(function() {
    'use strict';

    // Attendre que le DOM soit complètement chargé
    document.addEventListener('DOMContentLoaded', function() {
        initIconPreview();
    });

    /**
     * Initialise l'aperçu en temps réel de l'icône
     */
    function initIconPreview() {
        const fileInput = document.querySelector('input[name="icon_file"]');
        const previewBox = document.getElementById('icon-preview-box');
        const clearCheckbox = document.querySelector('input[name="icon_file-clear"]');

        if (!fileInput || !previewBox) {
            return; // Pas sur la page du formulaire
        }

        // Écouter les changements de fichier
        fileInput.addEventListener('change', function(e) {
            handleFileSelect(e, previewBox);
        });

        // Gérer la case "Effacer" pour les fichiers existants
        if (clearCheckbox) {
            clearCheckbox.addEventListener('change', function(e) {
                if (e.target.checked) {
                    showDefaultIcon(previewBox);
                } else {
                    // Restaurer l'icône actuelle si on décoche
                    const currentIcon = previewBox.querySelector('img');
                    if (currentIcon && currentIcon.dataset.originalSrc) {
                        currentIcon.src = currentIcon.dataset.originalSrc;
                    }
                }
            });
        }

        // Drag & Drop support
        setupDragAndDrop(fileInput, previewBox);
    }

    /**
     * Gère la sélection d'un fichier
     */
    function handleFileSelect(event, previewBox) {
        const file = event.target.files[0];

        if (!file) {
            return;
        }

        // Validation du fichier
        const validationResult = validateFile(file);
        if (!validationResult.valid) {
            showError(previewBox, validationResult.message);
            event.target.value = ''; // Reset l'input
            return;
        }

        // Afficher l'animation de chargement
        showLoading(previewBox);

        // Lire et afficher le fichier
        const reader = new FileReader();

        reader.onload = function(e) {
            showPreview(previewBox, e.target.result, file.name);
        };

        reader.onerror = function() {
            showError(previewBox, 'Erreur lors de la lecture du fichier');
            event.target.value = '';
        };

        reader.readAsDataURL(file);
    }

    /**
     * Valide le fichier uploadé
     */
    function validateFile(file) {
        const maxSize = 5 * 1024 * 1024; // 5MB
        const allowedTypes = [
            'image/x-icon',
            'image/vnd.microsoft.icon',
            'image/png',
            'image/jpeg',
            'image/jpg',
            'image/svg+xml',
            'image/webp'
        ];

        // Vérifier la taille
        if (file.size > maxSize) {
            return {
                valid: false,
                message: `Le fichier est trop volumineux (${formatFileSize(file.size)}). Maximum 5MB.`
            };
        }

        // Vérifier le type
        if (!allowedTypes.includes(file.type)) {
            return {
                valid: false,
                message: `Format non supporté (${file.type}). Utilisez .ico, .png, .jpg ou .svg`
            };
        }

        return { valid: true };
    }

    /**
     * Affiche l'aperçu de l'image
     */
    function showPreview(container, dataUrl, filename) {
        // Créer une nouvelle image
        const img = document.createElement('img');
        img.src = dataUrl;
        img.alt = filename;
        img.className = 'icon-preview-large';
        img.dataset.originalSrc = dataUrl;

        // Gérer les erreurs de chargement de l'image
        img.onerror = function() {
            showError(container, 'Impossible d\'afficher cette image');
        };

        img.onload = function() {
            // Remplacer le contenu de la preview box
            container.innerHTML = '';
            container.classList.remove('loading');
            container.appendChild(img);

            // Afficher un message de succès temporaire
            showSuccessMessage(filename);
        };
    }

    /**
     * Affiche l'icône par défaut
     */
    function showDefaultIcon(container) {
        container.innerHTML = `
            <div class="default-icon-large">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect width="24" height="24" rx="4" fill="#e3e8ef"/>
                    <path d="M12 8v8M8 12h8" stroke="#8899a6" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </div>
        `;
        container.classList.remove('loading');
    }

    /**
     * Affiche l'animation de chargement
     */
    function showLoading(container) {
        container.classList.add('loading');
        container.innerHTML = '';
    }

    /**
     * Affiche une erreur dans la preview box
     */
    function showError(container, message) {
        container.classList.remove('loading');
        container.innerHTML = `
            <div class="icon-error">
                ${escapeHtml(message)}
            </div>
        `;

        // Afficher également un message d'erreur Django-style
        showErrorMessage(message);

        // Retour à l'icône par défaut après 3 secondes
        setTimeout(function() {
            showDefaultIcon(container);
        }, 3000);
    }

    /**
     * Configure le Drag & Drop
     */
    function setupDragAndDrop(fileInput, previewBox) {
        const dropZone = fileInput.closest('.form-row') || fileInput.parentElement;

        if (!dropZone) return;

        // Prévenir le comportement par défaut
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        // Highlight sur drag over
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, function() {
                dropZone.classList.add('drag-over');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, function() {
                dropZone.classList.remove('drag-over');
            }, false);
        });

        // Gérer le drop
        dropZone.addEventListener('drop', function(e) {
            const dt = e.dataTransfer;
            const files = dt.files;

            if (files.length > 0) {
                fileInput.files = files;
                // Déclencher l'événement change manuellement
                const event = new Event('change', { bubbles: true });
                fileInput.dispatchEvent(event);
            }
        }, false);

        // Ajouter du style CSS pour le drag over
        const style = document.createElement('style');
        style.textContent = `
            .drag-over {
                background: #e3f2fd !important;
                border: 2px dashed #417690 !important;
                border-radius: 8px;
                padding: 10px;
                transition: all 0.2s ease;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Affiche un message de succès
     */
    function showSuccessMessage(filename) {
        removeExistingMessages();
        
        const message = document.createElement('div');
        message.className = 'icon-upload-success';
        message.textContent = `✓ Icône "${filename}" chargée avec succès`;
        
        const previewContainer = document.querySelector('.icon-preview-container');
        if (previewContainer) {
            previewContainer.parentNode.insertBefore(message, previewContainer.nextSibling);
            
            // Retirer le message après 5 secondes
            setTimeout(function() {
                message.style.opacity = '0';
                setTimeout(function() {
                    message.remove();
                }, 300);
            }, 5000);
        }
    }

    /**
     * Affiche un message d'erreur
     */
    function showErrorMessage(errorText) {
        removeExistingMessages();
        
        const message = document.createElement('div');
        message.className = 'icon-upload-error';
        message.textContent = `✗ ${errorText}`;
        
        const previewContainer = document.querySelector('.icon-preview-container');
        if (previewContainer) {
            previewContainer.parentNode.insertBefore(message, previewContainer.nextSibling);
            
            // Retirer le message après 8 secondes
            setTimeout(function() {
                message.style.opacity = '0';
                setTimeout(function() {
                    message.remove();
                }, 300);
            }, 8000);
        }
    }

    /**
     * Supprime les messages existants
     */
    function removeExistingMessages() {
        const existingMessages = document.querySelectorAll('.icon-upload-success, .icon-upload-error');
        existingMessages.forEach(msg => msg.remove());
    }

    /**
     * Formate la taille du fichier
     */
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    /**
     * Échappe le HTML pour éviter les XSS
     */
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

})();