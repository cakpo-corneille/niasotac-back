# ARCHITECTURE FONCTIONNELLE - NIASOTAC BACKEND

## RÉSUMÉ GLOBAL DU PROJET

**Niasotac Backend** est un système de gestion de catalogue produits intelligent avec des fonctionnalités avancées de marketing et de recommandation.

**Ce que fait le système:**
- Organise des produits dans un catalogue hiérarchique (comme une bibliothèque avec des rayons et des étagères)
- Applique automatiquement des promotions et calcule les meilleurs prix
- Évalue et recommande les produits les plus pertinents aux visiteurs
- Gère une liste d'abonnés newsletter et l'envoi de campagnes
- Expose toutes ces informations via une interface de programmation (API) pour alimenter un site web ou une application mobile

---

# COMMENT FONCTIONNE LE SYSTÈME

## 1. LES ENTITÉS DU SYSTÈME

### 1.1 Les Catégories - L'Organisation du Catalogue

**Rôle:** Structurer le catalogue de manière hiérarchique (parent → enfants → petits-enfants)

**Logique:**
- Chaque catégorie peut avoir une catégorie parente (sauf les catégories racines)
- Une catégorie peut avoir plusieurs sous-catégories
- Le système conserve automatiquement le chemin complet depuis la racine (ex: "Électronique → Téléphones → Smartphones")
- Chaque catégorie a un nom, une description, une icône et un ordre d'affichage

**Cas d'usage:**
- Un visiteur navigue "Vêtements → Hommes → Chemises" pour affiner sa recherche
- L'administrateur réorganise l'arborescence en déplaçant "Accessoires" sous "Mode"

**Interactions:**
- Les produits sont rattachés à une ou plusieurs catégories
- Les promotions peuvent cibler une catégorie entière et ses sous-catégories

---

### 1.2 Les Produits - Le Cœur du Catalogue

**Rôle:** Représenter chaque article à vendre avec toutes ses informations commerciales et marketing

**Logique:**
Les produits contiennent deux types d'informations:

**Informations descriptives:**
- Identité: nom, code produit (SKU), description courte/longue
- Visuels: images principales et galerie
- Classification: rattachement à une ou plusieurs catégories
- Tarification: prix unitaire, coût d'achat

**Informations opérationnelles:**
- Disponibilité: en stock, rupture, précommande, arrêt définitif
- Marketing: tags (nouveauté, promotion, coup de cœur)
- Métriques: nombre de vues, nombre de clics WhatsApp
- Scoring: note de pertinence, flags "à la une" et "recommandé"

**Cas d'usage:**
- Un visiteur consulte la fiche d'un produit → le système enregistre +1 vue
- Le stock est épuisé → l'administrateur change le statut en "rupture"
- Un produit obtient beaucoup de clics WhatsApp → son score augmente automatiquement

**Interactions:**
- Les promotions s'appliquent aux produits pour modifier leurs prix
- Le service de scoring analyse les produits pour les mettre en avant
- Les catégories regroupent les produits

---

### 1.3 Les Promotions - La Gestion Commerciale

**Rôle:** Appliquer des réductions de prix automatiques selon des règles commerciales

**Logique des types de promotion:**

**1. Prix fixe**
- Objectif: Imposer un prix final indépendamment du prix d'origine
- Exemple: "Ce produit à 50€ au lieu de son prix normal"
- Usage: Ventes flash, déstockage

**2. Réduction en valeur absolue**
- Objectif: Retirer un montant fixe du prix
- Exemple: "-15€ sur ce produit"
- Usage: Promotions simples, offres fidélité

**3. Réduction en pourcentage**
- Objectif: Appliquer un taux de réduction
- Exemple: "-20% sur ce produit"
- Usage: Soldes, réductions saisonnières

**4. Offres "Achetez X, recevez Y"**
- Objectif: Valoriser le geste commercial en quantité gratuite équivalente
- Exemple: "Achetez 2 unités, recevez 1 gratuite" → 33% de réduction effective
- Usage: Promotion de volume, écoulement de stock

**Ciblage des promotions:**
- Promotion sur un produit spécifique
- Promotion sur une catégorie entière (tous ses produits)
- Promotion globale (tout le catalogue)

**Période de validité:**
- Date de début et de fin obligatoires
- Activation/désactivation manuelle possible

**Cas d'usage:**
- Le responsable commercial lance "-30% sur tous les téléphones du 1er au 15 décembre"
- Un produit a deux promotions actives → le système choisit automatiquement la plus avantageuse
- Une promotion expire → elle cesse automatiquement de s'appliquer

**Interactions:**
- Le service de promotions calcule le meilleur prix pour chaque produit
- Les produits affichent leurs prix promotionnels sur le site

---

### 1.4 Les Abonnés Newsletter - La Communication Marketing

**Rôle:** Gérer la base d'abonnés pour les campagnes email

**Logique du cycle de vie:**

**Étape 1 - Inscription:**
- Un visiteur entre son email pour s'abonner
- Le système crée un abonné avec statut "en attente de confirmation"
- Un email de confirmation est envoyé avec un lien unique

**Étape 2 - Confirmation:**
- Le visiteur clique sur le lien dans l'email
- Le statut passe à "confirmé"
- L'abonné reçoit désormais les newsletters

**Étape 3 - Désabonnement:**
- L'abonné clique sur "se désabonner" dans une newsletter
- Le statut passe à "désabonné"
- Il ne reçoit plus d'emails

**Règles de protection:**
- Impossible de renvoyer un email de confirmation plus d'une fois toutes les 24h
- Les abonnés non confirmés depuis 30 jours peuvent être purgés
- Un email désabonné ne peut pas se réabonner automatiquement (nécessite validation manuelle)

**Cas d'usage:**
- Un visiteur s'inscrit → il reçoit un email de confirmation
- Le marketing lance une campagne → seuls les abonnés confirmés la reçoivent
- Un abonné oublie de confirmer → son inscription expire après 30 jours

**Interactions:**
- Le service newsletter gère les confirmations et les envois
- Les tâches automatiques nettoient les abonnés non confirmés

---

### 1.5 Les Services Institutionnels

**Rôle:** Présenter les services offerts par l'entreprise (livraison, SAV, garanties...)

**Logique:**
- Chaque service a un titre, une description et une icône
- Les services peuvent être activés/désactivés
- Ils sont affichés sur le site pour rassurer les visiteurs

**Cas d'usage:**
- Afficher "Livraison gratuite dès 50€" sur la page d'accueil
- Présenter "SAV réactif sous 48h" dans le footer

---

### 1.6 Les Paramètres du Site

**Rôle:** Centraliser les informations de configuration du site

**Logique:**
- Stocke les informations de contact (email, téléphone, WhatsApp, adresse)
- Permet de configurer l'apparence (couleurs, logo)
- Gère les liens réseaux sociaux
- Stocke les mentions légales et CGV

**Cas d'usage:**
- Le site affiche le numéro WhatsApp depuis les paramètres
- L'administrateur change le logo → il est mis à jour partout

---

## 2. LES SERVICES ET ALGORITHMES

### 2.1 Service de Gestion des Newsletters

**Rôle:** Orchestrer tout le cycle de vie des abonnés newsletter

**Algorithme de confirmation:**

1. **Réception d'une demande de confirmation**
   - Le système reçoit un email et un token unique
   - Il cherche l'abonné correspondant dans la base

2. **Vérifications de sécurité**
   - Le token est-il valide?
   - L'abonné existe-t-il?
   - Est-il déjà confirmé?
   - Est-il désabonné?

3. **Décision:**
   - Si tout est OK → Statut passe à "confirmé", date de confirmation enregistrée
   - Si déjà confirmé → Message "Vous êtes déjà abonné"
   - Si désabonné → Refus avec message explicatif
   - Si token invalide → Erreur de sécurité

**Algorithme d'envoi de campagne:**

1. **Préparation**
   - Le marketing crée le contenu de la newsletter
   - Il sélectionne les destinataires (tous les confirmés ou un segment)

2. **Filtrage des destinataires**
   - Le système récupère UNIQUEMENT les abonnés avec statut "confirmé"
   - Il exclut automatiquement les "en attente" et "désabonnés"

3. **Envoi en lot**
   - Pour chaque abonné confirmé:
     - Personnalisation du contenu (insertion du prénom si disponible)
     - Ajout du lien de désabonnement unique
     - Envoi de l'email
     - Enregistrement de la date d'envoi

4. **Gestion des erreurs**
   - Si un email échoue → l'abonné est marqué avec l'erreur
   - Si l'email n'existe plus → passage au statut "désabonné"

**Cas d'usage concret:**

*Scénario 1 - Nouvelle inscription:*
1. Marie entre son email sur le site
2. Elle reçoit "Confirmez votre inscription - Cliquez ici"
3. Elle clique → Son statut passe à "confirmé"
4. Elle reçoit la prochaine newsletter

*Scénario 2 - Campagne mensuelle:*
1. Le marketing prépare la newsletter de décembre
2. Le système identifie 5000 abonnés confirmés
3. Chacun reçoit l'email avec son lien de désabonnement unique
4. 50 personnes se désabonnent → elles ne recevront plus les prochaines

---

### 2.2 Service de Calcul des Promotions

**Rôle:** Déterminer le meilleur prix pour chaque produit quand plusieurs promotions s'appliquent

**Algorithme de sélection de la meilleure promotion:**

**Étape 1 - Collecte des promotions actives**
- Le système cherche toutes les promotions en cours (dans leur période de validité)
- Il filtre celles qui sont activées manuellement
- Pour un produit donné, il identifie:
  - Les promotions directes sur ce produit
  - Les promotions sur ses catégories (et catégories parentes)
  - Les promotions globales

**Étape 2 - Calcul de la réduction pour chaque promotion**

Pour chaque promotion active, calcul de la réduction effective:

*Cas 1 - Prix fixe:*
- Réduction = Prix original - Prix fixe imposé
- Exemple: Produit à 100€ avec promotion "prix fixe 70€" → Réduction de 30€

*Cas 2 - Réduction en valeur:*
- Réduction = Valeur indiquée
- Exemple: Promotion "-15€" → Réduction de 15€

*Cas 3 - Réduction en pourcentage:*
- Réduction = Prix original × (Pourcentage / 100)
- Exemple: Produit à 100€ avec "-20%" → Réduction de 20€

*Cas 4 - Offre "Achetez X, recevez Y":*
- Calcul du pourcentage effectif: Y / (X + Y) × 100
- Application de ce pourcentage au prix
- Exemple: "Achetez 3, recevez 1" = 1/(3+1) = 25% → Réduction de 25%

**Étape 3 - Sélection de la meilleure**
- Le système compare toutes les réductions calculées
- Il choisit celle qui donne la réduction maximale
- Il retourne le prix final et les détails de la promotion appliquée

**Étape 4 - Garanties de cohérence**
- Le prix promotionnel ne peut jamais être négatif
- Le prix promotionnel ne peut jamais être supérieur au prix d'origine
- Si aucune promotion ne s'applique, le prix reste inchangé

**Cas d'usage concret:**

*Exemple - Produit "Smartphone XYZ" à 500€*

Promotions actives:
1. Promotion globale site: "-10%" (toute la boutique)
2. Promotion catégorie "Téléphones": "-15%"
3. Promotion produit direct: "Prix fixe 380€"

Calculs:
1. Promotion globale: 500€ - 10% = 450€ (réduction de 50€)
2. Promotion catégorie: 500€ - 15% = 425€ (réduction de 75€)
3. Promotion produit: Prix imposé à 380€ (réduction de 120€)

**Résultat:** Le système choisit la promotion n°3 (prix fixe 380€) car c'est la plus avantageuse.
Le client voit: ~~500€~~ **380€** avec le badge "Meilleure offre"

---

### 2.3 Service de Scoring et Recommandation

**Rôle:** Évaluer automatiquement la pertinence de chaque produit pour décider lesquels mettre en avant sur le site

**Algorithme de calcul du score de pertinence:**

Le système calcule un score sur 100 points en analysant 6 critères pondérés:

**Critère 1 - Popularité (30 points max)**
- Logique: Plus un produit est consulté, plus il intéresse les visiteurs
- Calcul: Nombre de vues × pondération "vues"
- Exemple: 150 vues × 0.2 point par vue = 30 points

**Critère 2 - Engagement WhatsApp (25 points max)**
- Logique: Un clic WhatsApp = intention d'achat forte
- Calcul: Nombre de clics WhatsApp × pondération "clics"
- Exemple: 50 clics × 0.5 point par clic = 25 points

**Critère 3 - Fraîcheur (15 points max)**
- Logique: Les nouveaux produits méritent plus de visibilité
- Calcul: Points qui diminuent avec le temps depuis l'ajout
- Exemple: Produit ajouté il y a 2 jours = 14 points, produit ajouté il y a 60 jours = 3 points

**Critère 4 - Disponibilité Stock (15 points max)**
- Logique: Privilégier les produits en stock
- Règles:
  - En stock = 15 points
  - Précommande = 10 points
  - Rupture = 5 points
  - Arrêté = 0 point

**Critère 5 - Compétitivité Prix (10 points max)**
- Logique: Les prix attractifs (faible marge) méritent plus de visibilité
- Calcul: Points inversement proportionnels à la marge
- Exemple: Marge de 10% = 10 points, marge de 50% = 2 points

**Critère 6 - Rentabilité (5 points max)**
- Logique: Équilibre entre attractivité et rentabilité
- Calcul: Proportionnel à la marge bénéficiaire
- Exemple: Marge de 40% = 5 points, marge de 5% = 0.5 point

**Étape 2 - Attribution des badges:**

**Badge "À la une" (Featured):**
- Condition: Score total ≥ 70 points ET produit en stock
- Affichage: Première page, carrousel principal
- Objectif: Maximiser les conversions sur les produits performants

**Badge "Recommandé":**
- Condition: Score total ≥ 50 points ET produit disponible (stock ou précommande)
- Affichage: Section "Nos recommandations"
- Objectif: Créer une sélection de qualité

**Étape 3 - Déclenchement du recalcul:**

Le score est recalculé automatiquement quand:
- Le produit est modifié (prix, stock, description)
- Une nouvelle vue est enregistrée
- Un clic WhatsApp est enregistré
- Chaque nuit (pour la fraîcheur)

**Cas d'usage concret:**

*Exemple - Produit "Écouteurs Bluetooth Pro"*

Données:
- 200 vues
- 30 clics WhatsApp
- Ajouté il y a 5 jours
- En stock
- Prix: 80€, Coût: 60€ (marge 25%)

Calcul du score:
- Vues: 200 × 0.15 = 30 points
- Clics: 30 × 0.8 = 24 points
- Fraîcheur: 13 points (produit récent)
- Stock: 15 points (disponible)
- Compétitivité: 7 points (marge raisonnable)
- Rentabilité: 3 points (marge 25%)

**Total: 92 points**
**Badges obtenus:** "À la une" + "Recommandé"
**Affichage:** Carrousel principal + Section recommandations

*Contraste - Produit "Câble USB Standard"*

Données:
- 10 vues
- 1 clic WhatsApp
- Ajouté il y a 120 jours
- En stock
- Prix: 5€, Coût: 4.50€ (marge 10%)

Calcul du score:
- Vues: 10 × 0.15 = 1.5 points
- Clics: 1 × 0.8 = 0.8 point
- Fraîcheur: 1 point (ancien)
- Stock: 15 points
- Compétitivité: 10 points (bonne marge)
- Rentabilité: 1 point

**Total: 29 points**
**Badges:** Aucun
**Affichage:** Catalogue standard uniquement

---

## 3. LES FLUX ET INTERACTIONS

### 3.1 Flux de Consultation Produit (Visiteur → API → Base de données)

**Scénario:** Un visiteur veut voir les téléphones en promotion

**Étape 1 - Requête du visiteur**
- Le visiteur clique sur "Téléphones" dans le menu
- Son navigateur envoie une demande à l'API: "Donne-moi tous les produits de la catégorie Téléphones"

**Étape 2 - Filtrage**
L'API applique des filtres automatiques:
- Catégorie = "Téléphones" (et toutes ses sous-catégories)
- Statut = "Actif" (exclure les brouillons)
- Éventuellement: Prix min/max, disponibilité, recherche par mot-clé

**Étape 3 - Enrichissement des données**
Pour chaque produit trouvé, l'API ajoute:
- Le chemin complet de catégorie ("Électronique → Téléphones → Smartphones")
- Les images formatées avec leurs URLs complètes
- Le calcul du prix promotionnel (si applicable)
- Les promotions actives avec leurs détails
- Les badges "À la une" et "Recommandé"

**Étape 4 - Tri et réponse**
- L'API trie les produits selon la demande (prix, popularité, score)
- Elle renvoie la liste complète au navigateur
- Le site affiche les produits avec leurs prix, images et badges

**Étape 5 - Actions visiteur**
- Le visiteur clique sur un produit → +1 vue enregistrée
- Le visiteur clique sur "Contacter sur WhatsApp" → +1 clic enregistré
- Ces actions déclenchent un recalcul du score en arrière-plan

---

### 3.2 Flux de Gestion des Promotions (Administrateur → Calcul → Affichage)

**Scénario:** Le responsable commercial crée une promotion Black Friday

**Étape 1 - Création de la promotion**
L'administrateur entre dans le back-office:
- Nom: "Black Friday 2024"
- Type: "Pourcentage"
- Valeur: 40%
- Cible: Catégorie "Électronique"
- Période: 24/11/2024 au 27/11/2024
- Statut: Activée

**Étape 2 - Validation automatique**
Le système vérifie:
- La date de fin est bien après la date de début
- Le pourcentage est entre 0 et 100%
- La catégorie existe bien
- Aucun doublon sur la même période

**Étape 3 - Activation**
Dès que la date de début arrive:
- Le service de promotions identifie tous les produits de "Électronique" et ses sous-catégories
- Il recalcule leur prix promotionnel
- Il compare avec les autres promotions actives
- Il applique la meilleure

**Étape 4 - Affichage côté client**
Sur le site, chaque produit électronique affiche:
- Prix barré: ~~199€~~
- Nouveau prix: **119€** (économie de 80€)
- Badge: "Black Friday -40%"

**Étape 5 - Expiration**
Le 28/11/2024:
- La promotion expire automatiquement
- Les prix reviennent à la normale
- Le badge disparaît

---

### 3.3 Flux de Newsletter (Inscription → Confirmation → Envoi)

**Scénario complet:**

**Phase 1 - Inscription (J1, 14h00)**
1. Sophie visite le site et entre son email: sophie@example.com
2. L'API crée un abonné avec:
   - Email: sophie@example.com
   - Statut: "En attente de confirmation"
   - Token unique: xyz123abc
   - Date d'inscription: J1 14h00
3. Un email automatique est envoyé:
   - Objet: "Confirmez votre inscription à notre newsletter"
   - Contenu: "Cliquez ici pour confirmer: https://site.com/confirm?token=xyz123abc"

**Phase 2 - Confirmation (J1, 16h30)**
1. Sophie clique sur le lien dans l'email
2. L'API reçoit le token xyz123abc
3. Le service newsletter vérifie et confirme l'abonné:
   - Statut: "Confirmé"
   - Date de confirmation: J1 16h30
4. Sophie reçoit un email de bienvenue

**Phase 3 - Campagne newsletter (J8, 10h00)**
1. Le marketing prépare la newsletter de décembre
2. Il lance l'envoi via le back-office
3. Le service newsletter:
   - Identifie 4823 abonnés confirmés (dont Sophie)
   - Exclut automatiquement les 156 "en attente" et 89 "désabonnés"
4. Chaque abonné confirmé reçoit l'email avec:
   - Le contenu personnalisé
   - Son lien de désabonnement unique: https://site.com/unsubscribe?token=xyz123abc

**Phase 4 - Désabonnement (J15)**
1. Sophie n'est plus intéressée et clique sur "Se désabonner"
2. L'API change son statut à "Désabonné"
3. Sophie ne recevra plus les prochaines newsletters

---

### 3.4 Schéma Narratif Complet des Interactions

```
┌─────────────────────────────────────────────────────────────┐
│                      VISITEUR DU SITE                        │
│  (Consulte, recherche, clique, s'inscrit à la newsletter)  │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                      API REST                                │
│  (Reçoit les demandes, applique les filtres, renvoie JSON)  │
└──┬────────┬────────┬────────┬────────┬─────────────────────┘
   │        │        │        │        │
   │        │        │        │        │
   ▼        ▼        ▼        ▼        ▼
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────────┐
│PROD │ │PROMO│ │CATEG│ │NEWS │ │SETTINGS │
│UITS │ │TIONS│ │ORIES│ │LETTE│ │         │
└──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └────┬────┘
   │       │       │       │         │
   └───────┴───────┴───────┴─────────┘
                   │
                   ▼
        ┌────────────────────┐
        │  BASE DE DONNÉES   │
        │ (Stocke tout)      │
        └──────┬─────────────┘
               │
               │ Modifications détectées
               ▼
        ┌────────────────────┐
        │  SIGNAUX DJANGO    │
        │ (Déclencheurs auto)│
        └──────┬─────────────┘
               │
               ▼
        ┌────────────────────┐
        │  TÂCHES CELERY     │
        │ (Traitement async) │
        └──────┬─────────────┘
               │
               ▼
   ┌────────────────────────────┐
   │  SERVICES MÉTIER           │
   │  - Scoring                 │
   │  - Promotions              │
   │  - Newsletter              │
   └────────────────────────────┘
```

**Exemple de flux complet:**

1. **Visiteur** cherche "écouteurs"
2. **API** reçoit la recherche et interroge la base
3. **Base de données** retourne les produits correspondants
4. **Service Promotions** calcule les prix pour chaque produit
5. **Service Scoring** ajoute les badges recommandation
6. **API** renvoie la liste enrichie au visiteur
7. Visiteur clique sur un produit → **Signal** détecté
8. **Tâche Celery** lancée en arrière-plan pour recalculer le score
9. **Service Scoring** met à jour le score du produit
10. **Base de données** sauvegarde le nouveau score

---

## 4. LES AUTOMATISATIONS

### 4.1 Automatisation par Signaux

**Qu'est-ce qu'un signal?**
Un déclencheur automatique qui réagit à un événement du système (comme un capteur de mouvement qui allume une lumière).

**Signal 1 - Nettoyage des fichiers médias**

**Déclencheur:** Un produit est supprimé ou ses images sont remplacées
**Action automatique:**
- Le système détecte les anciennes images devenues inutiles
- Il les supprime du serveur pour économiser l'espace de stockage
- Cela évite d'accumuler des fichiers orphelins

**Signal 2 - Création du statut produit**

**Déclencheur:** Un nouveau produit est créé
**Action automatique:**
- Le système crée automatiquement un enregistrement de statut
- Statut initial: "En stock"
- Prêt à être modifié par l'administrateur

**Signal 3 - Recalcul du score produit**

**Déclencheur:** Un produit est modifié (prix, description, stock, etc.)
**Action automatique:**
- Le système lance une tâche de recalcul du score en arrière-plan
- Le nouveau score est calculé selon l'algorithme de scoring
- Les badges "À la une" et "Recommandé" sont mis à jour

**Pourquoi en arrière-plan?**
Pour que l'administrateur n'ait pas à attendre que le calcul se termine. Il peut continuer à travailler immédiatement.

---

### 4.2 Tâches Planifiées (Celery)

**Qu'est-ce qu'une tâche planifiée?**
Une action programmée qui s'exécute automatiquement à intervalles réguliers (comme un réveil qui sonne tous les jours).

**Tâche 1 - Recalcul des scores (déclenchée par signaux)**

**Quand:** Chaque fois qu'un produit est modifié
**Action:**
- Recalculer le score de pertinence (0-100)
- Mettre à jour les flags "featured" et "recommended"
- Sauvegarder dans la base de données

**Tâche 2 - Nettoyage des abonnés non confirmés (à planifier)**

**Quand:** Tous les jours à 3h du matin (par exemple)
**Action:**
- Identifier les abonnés "en attente" depuis plus de 30 jours
- Les supprimer automatiquement
- Économiser l'espace de stockage

**Tâche 3 - Mise à jour quotidienne de la fraîcheur (à planifier)**

**Quand:** Tous les jours à minuit
**Action:**
- Recalculer le score de fraîcheur pour tous les produits
- Les nouveaux produits gardent leur boost de visibilité
- Les anciens produits voient progressivement leur score diminuer

---

## 5. POINTS CRITIQUES ET DÉPENDANCES

### 5.1 Dépendances Critiques

**1. Serveur de base de données (PostgreSQL)**
- **Rôle:** Stocke TOUTES les données du système
- **Criticité:** MAXIMALE - Sans base, le site ne peut pas fonctionner
- **Point de vigilance:** Sauvegardes régulières obligatoires

**2. Serveur de cache et files d'attente (Redis)**
- **Rôle:** Gère les tâches asynchrones (Celery)
- **Criticité:** ÉLEVÉE - Sans Redis, les tâches en arrière-plan échouent
- **Impact:** Pas de recalcul de score automatique, pas d'envoi de newsletter

**3. Serveur d'emails (SMTP)**
- **Rôle:** Envoie les emails de confirmation et newsletters
- **Criticité:** MOYENNE - Le site fonctionne mais pas la newsletter
- **Point de vigilance:** Vérifier la réputation de l'IP pour éviter le spam

**4. Stockage des fichiers (local ou S3)**
- **Rôle:** Conserve les images de produits
- **Criticité:** ÉLEVÉE - Sans images, le catalogue est visuellement pauvre
- **Point de vigilance:** En production, utiliser un stockage cloud (S3) pour la persistance

---

### 5.2 Points Critiques de Configuration

**1. Pondérations du Scoring (SCORE_WEIGHTS)**

**Où:** Configuration du service de scoring
**Impact:** Change complètement les produits mis en avant

Valeurs actuelles (à ajuster selon la stratégie commerciale):
- Vues: 0.15 point par vue (peut favoriser les best-sellers)
- Clics WhatsApp: 0.8 point par clic (forte valorisation de l'engagement)
- Fraîcheur: Décroissance sur 90 jours (équilibre nouveautés/classiques)
- Stock: 15 points si disponible (forte priorité à la disponibilité)
- Compétitivité prix: Favorise les marges faibles (peut réduire la rentabilité)
- Rentabilité: Poids faible (risque de privilégier les produits peu rentables)

**Recommandation:** Ajuster ces pondérations tous les trimestres selon:
- Le taux de conversion par badge
- La marge moyenne des produits "À la une"
- Les retours clients

---

**2. Seuils des Badges**

**Badge "À la une":** Score ≥ 70 points
- **Trop bas:** Trop de produits "à la une" → perte de sens
- **Trop haut:** Pas assez de produits → page d'accueil vide

**Badge "Recommandé":** Score ≥ 50 points
- **Recommandation:** Analyser mensuellement la distribution des scores
- **Objectif:** 10-15% des produits "à la une", 25-35% "recommandés"

---

**3. Règles de Promotions**

**Cumul de promotions:** Non autorisé (seulement la meilleure)
- **Avantage:** Simplicité et clarté pour le client
- **Inconvénient:** Impossible de cumuler "promo catégorie + code promo"
- **Alternative possible:** Permettre le cumul avec un ordre de priorité

**Périodes de validité:** Obligatoires
- **Avantage:** Évite les promotions oubliées qui grèvent la marge
- **Point de vigilance:** Prévoir un système d'alerte avant expiration

---

### 5.3 Scénarios de Défaillance et Impacts

**Scénario 1 - Redis tombe en panne**
- **Impact immédiat:** Les tâches Celery échouent
- **Conséquence:** 
  - Pas de recalcul de score automatique → les badges ne se mettent pas à jour
  - Pas d'envoi de newsletter → les campagnes sont bloquées
- **Solution:** Le site continue de fonctionner avec les anciennes données
- **Action:** Redémarrer Redis, relancer les tâches échouées

**Scénario 2 - Le serveur d'emails ne répond plus**
- **Impact:** Les emails de confirmation ne partent pas
- **Conséquence:** Les nouveaux abonnés restent "en attente" indéfiniment
- **Solution:** Configurer un serveur SMTP de secours (failover)

**Scénario 3 - Erreur dans le calcul de promotion**
- **Impact:** Affichage de prix incorrects (trop bas ou trop haut)
- **Conséquence:** Perte financière ou mécontentement client
- **Prévention:** Tests automatiques sur les calculs de promotion
- **Solution:** Désactiver manuellement la promotion problématique

**Scénario 4 - Explosion du nombre de vues sur un produit (attaque ou viralité)**
- **Impact:** Score artificiellement gonflé
- **Conséquence:** Mise en avant d'un produit non pertinent
- **Prévention:** Plafonner le nombre de vues quotidiennes par IP
- **Solution:** Implémenter un algorithme de détection d'anomalies

---

### 5.4 Tableaux de Correspondance Métier

**Types de Promotions ↔ Scénarios Commerciaux**

| Type Promotion | Scénario Commercial | Exemple | Quand l'utiliser |
|----------------|---------------------|---------|------------------|
| Prix fixe | Vente flash | "Ce produit à 49€" | Déstockage, soldes, produits à marge élevée |
| Réduction valeur | Promotion simple | "-15€ sur ce produit" | Animation commerciale, fidélisation |
| Réduction % | Soldes saisonnières | "-30% sur tout l'électronique" | Soldes, Black Friday, fin de saison |
| Achetez X recevez Y | Promotion volume | "Achetez 2, recevez 1 gratuit" | Écoulement de stock, produits à rotation lente |

---

**Statuts Produits ↔ Affichage Site**

| Statut Technique | Signification Métier | Affichage Client | Action Possible |
|------------------|----------------------|------------------|-----------------|
| En stock | Disponible immédiatement | "En stock" + Bouton "Acheter" | Achat normal |
| Précommande | Bientôt disponible | "Précommande" + Date estimée | Réservation |
| Rupture | Temporairement indisponible | "Rupture de stock" + Alerte dispo | Alerte email |
| Arrêté | Définitivement retiré | Masqué ou "Plus disponible" | Aucune |

---

**Statuts Newsletter ↔ Actions Autorisées**

| Statut | Peut recevoir newsletter | Peut renvoyer confirmation | Peut se réabonner |
|--------|--------------------------|----------------------------|-------------------|
| En attente | ❌ Non | ✅ Oui (1 fois/24h) | ✅ Oui (auto) |
| Confirmé | ✅ Oui | ❌ Non (déjà confirmé) | ✅ Oui (déjà le cas) |
| Désabonné | ❌ Non | ❌ Non | ⚠️ Oui (validation manuelle) |

---

## 6. RECOMMANDATIONS OPÉRATIONNELLES

### 6.1 Pour l'Équipe Produit

**1. Gestion des Pondérations de Scoring**
- **Fréquence:** Révision trimestrielle
- **Méthode:** Analyse A/B testing sur échantillons
- **Objectif:** Maximiser le taux de conversion tout en préservant la marge

**2. Stratégie de Promotions**
- **Planification:** Calendrier annuel des opérations commerciales
- **Règle:** Ne jamais avoir plus de 3 promotions actives simultanées sur un même produit
- **Suivi:** Dashboard hebdomadaire des promotions actives et de leur impact

**3. Curation du Catalogue**
- **Fréquence:** Audit mensuel des produits avec score < 20
- **Action:** Améliorer (photos, descriptions) ou retirer du catalogue
- **Objectif:** Maintenir un catalogue de qualité

### 6.2 Pour l'Équipe Marketing

**1. Gestion de la Newsletter**
- **Fréquence d'envoi recommandée:** Hebdomadaire ou bimensuel (éviter le spam)
- **Segmentation:** Créer des listes selon les centres d'intérêt
- **Qualité:** Nettoyer les abonnés inactifs tous les 6 mois

**2. Contenu des Campagnes**
- **Structure:** 60% contenu éditorial, 40% promotions
- **Personnalisation:** Utiliser les données de navigation (produits vus, catégories favorites)
- **Call-to-action:** Clair et unique par email

### 6.3 Pour l'Équipe Technique

**1. Monitoring Critique**
- Alertes si le nombre de produits "À la une" < 5 ou > 30
- Alertes si le taux d'échec d'envoi email > 5%
- Alertes si le temps de calcul des promotions > 2 secondes

**2. Performance**
- Indexer la base de données sur: catégorie, statut, score, dates de promotion
- Mettre en cache les résultats du service de promotions (TTL: 15 minutes)
- Optimiser les images produits (compression, format WebP)

**3. Sécurité et Qualité de Données**
- Valider tous les emails avant insertion (format + existence du domaine)
- Limiter le taux de requêtes API (rate limiting) pour éviter les abus
- Logger toutes les actions administratives (audit trail)

---

## CONCLUSION

Le système **Niasotac Backend** est une plateforme sophistiquée qui automatise intelligemment:
- La recommandation de produits par analyse de comportement et de business rules
- L'optimisation tarifaire via un moteur de promotions multi-critères
- L'engagement client par une gestion avancée de la newsletter
- L'expérience utilisateur par un catalogue organisé et enrichi

**Forces principales:**
- Automatisation poussée (scoring, promotions, notifications)
- Logique métier robuste et extensible
- Architecture modulaire facilitant les évolutions

**Points de vigilance:**
- Ajustement régulier des paramètres de scoring selon les objectifs commerciaux
- Surveillance de la cohérence des promotions multiples
- Qualité des données d'entrée (emails, prix, images)

Le système est conçu pour évoluer et s'adapter aux besoins métier grâce à sa structure modulaire et ses services réutilisables.
