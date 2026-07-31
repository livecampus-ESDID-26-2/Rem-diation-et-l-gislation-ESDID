# Remédiation et Législation

## Chapitre 6 – Réponse aux incidents de sécurité

### A – Processus de remédiation immédiate

- **Isolation immédiate des systèmes compromis** : déconnecter les postes ou serveurs touchés du réseau.
- **Blocage des accès compromis** : désactiver ou suspendre les comptes utilisateurs soupçonnés d'être détournés.
- **Application de correctifs urgents** : colmater les brèches exploitées (patchs logiciels, mises à jour de sécurité).
- **Conservation des preuves** : capturer des images mémoire, copier les journaux d'événements.
- **Information des responsables clés** : avertir la direction générale, le responsable sécurité (RSSI).

### B – Containment (confinement) et éradication

- **Confinement à court terme** : segmentation du réseau, mise hors ligne de serveurs stratégiques, restriction temporaire des privilèges d'accès. L'objectif est d'empêcher toute propagation latérale de l'attaque.
- **Confinement à long terme** : mise en place de contrôles supplémentaires (authentification renforcée, surveillance accrue, règles de pare-feu temporaires) pour sécuriser durablement l'environnement le temps d'éradiquer la menace.
- **Éradication de la menace** : suppression des logiciels malveillants, désactivation des scripts suspects, suppression des comptes créés par l'attaquant, correction des failles exploitées. Cette phase peut impliquer la réinstallation complète de certains systèmes ou la reconstruction d'environnements critiques.
- **Vérification post-éradication** : s'assurer qu'aucune porte dérobée (backdoor) ni persistence de l'attaquant ne subsiste, en effectuant des analyses forensiques complémentaires.

### C – Stratégies de récupération et de restauration

- **Restauration des services critiques** : redémarrage progressif des serveurs et applications, en priorisant les systèmes essentiels (ex. : messagerie, ERP, services de production).
- **Récupération des données** : restauration depuis des sauvegardes fiables, avec validation de leur intégrité et absence d'infection.
- **Contrôles de sécurité post-restauration**.
- **Mise à jour des politiques et outils** : renforcer la configuration des systèmes, ajuster les règles de détection (IDS/IPS, SIEM), réévaluer les procédures d'accès et de gestion des comptes.
- **Communication interne et externe** : informer les collaborateurs sur l'évolution de la situation.
- **Retour progressif à la normale** : assurer un suivi rapproché durant les jours/semaines suivant la restauration.
