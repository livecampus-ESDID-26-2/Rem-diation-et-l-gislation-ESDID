# Remédiation et Législation

**École :** Livecampus  
**Cours :** Remédiation et Législation  
**Professeur :** M. AUMAGY Yannick  
**Livrable :** MINI CAS 4  
**Chapitres couverts :** cours global  
**Modalité :** Travail de **groupe**  
**Groupe :** G1  

**Membres du groupe :**
- BADET Mael
- LEBLOND Tristan
- LOURENCO Quentin
- MASIA Antoine

**Format de dépôt attendu :** `REMEDIATION_ET_LEGISLATION_BADET_LEBLOND_LOURENCO_MASIA_MINI_CAS_4_G1.pdf`

---

## Énoncé du mini-cas

### Contexte

Une entreprise française spécialisée dans les **services numériques aux professionnels** vient de remporter un important contrat pour exploiter une nouvelle plateforme destinée à plusieurs grandes entreprises et organismes publics.

Cette plateforme doit permettre à plusieurs milliers d’utilisateurs d’échanger des **documents confidentiels**, de gérer leurs comptes clients et d’accéder à différents services en ligne.

La mise en production définitive est prévue dans **trois semaines**. Cependant, plusieurs éléments viennent inquiéter la direction :

- un **audit récent** a identifié plusieurs **vulnérabilités importantes** sur des serveurs exposés à Internet ;
- un **prestataire externe** dispose encore de **comptes administrateurs permanents** sur une partie de l’infrastructure ;
- plusieurs tentatives de **phishing ciblé** ont été reçues par des membres de la direction et de l’équipe informatique ;
- les **journaux de sécurité** montrent des **connexions inhabituelles** provenant de l’étranger, sans qu’une intrusion ait pour l’instant été confirmée ;
- le **plan de reprise d’activité** n’a jamais été testé dans les conditions réelles ;
- les **responsabilités** entre l’entreprise, son hébergeur et plusieurs sous-traitants restent **imprécises** en cas d’incident majeur.

La direction hésite entre **maintenir la date de lancement**, **reporter la mise en production** ou **lancer le service avec des mesures compensatoires**.

Elle demande à votre groupe de réaliser une **analyse globale** de la situation et de présenter une **recommandation argumentée**.

Cette situation mobilise notamment les notions de **cadre réglementaire**, **analyse de la menace**, **stratégie**, **gouvernance**, **détection**, **réponse aux incidents**, **résilience** et **retour d’expérience** étudiées pendant l’ensemble du cours.

---

## Vos tâches

### 1. Analyser la situation et qualifier les risques

Identifiez les principaux risques techniques, humains, organisationnels, réglementaires et liés aux prestataires.

Pour chacun des risques principaux :

- estimez sa **probabilité** ;
- estimez son niveau de **gravité** ;
- précisez ses **conséquences potentielles** ;
- déterminez s’il est **acceptable** avant la mise en production.

Présentez votre analyse dans un **tableau de risques hiérarchisé**.

### 2. Déterminer les obligations et responsabilités

Identifiez les principaux acteurs concernés par la situation :

- direction ;
- RSSI et équipes techniques ;
- métiers ;
- service juridique ;
- hébergeur ;
- prestataires et sous-traitants ;
- autorités compétentes.

Expliquez les responsabilités de chacun.

Identifiez également les principales **obligations réglementaires ou de notification** susceptibles de s’appliquer si une compromission de données ou un incident majeur était confirmé.

### 3. Proposer un plan de sécurisation avant lancement

Établissez les mesures qui doivent être réalisées pendant les **trois semaines** précédant la mise en production.

Classez-les en trois catégories :

- actions **impératives** avant lancement ;
- actions pouvant être réalisées **rapidement après** lancement ;
- actions d’amélioration à **moyen terme**.

Votre plan devra prendre en compte notamment :

- les vulnérabilités techniques ;
- les comptes et accès privilégiés ;
- les prestataires ;
- la surveillance et la détection ;
- les sauvegardes et la capacité de restauration ;
- la sensibilisation des utilisateurs.

### 4. Définir les critères de décision de mise en production

La direction doit choisir entre :

- **Option A** : maintenir le lancement à la date prévue ;
- **Option B** : reporter la mise en production ;
- **Option C** : lancer le service avec des mesures compensatoires.

Définissez des **critères objectifs** permettant de prendre cette décision. Vous pouvez notamment prendre en compte :

- le niveau de risque résiduel ;
- la criticité des vulnérabilités restantes ;
- les capacités de détection ;
- les capacités de confinement et de restauration ;
- la dépendance aux prestataires ;
- les conséquences financières et opérationnelles d’un report ;
- les obligations réglementaires ;
- l’impact potentiel sur la confiance des clients.

Choisissez ensuite une option et **justifiez votre recommandation**.

### 5. Préparer l’organisation en cas d’incident après lancement

Supposez finalement que la plateforme soit mise en production.

Définissez le **dispositif minimal** permettant de réagir efficacement si un incident survient dans les premières semaines :

- conditions d’activation de la cellule de crise ;
- informations à collecter ;
- personnes à prévenir ;
- règles de conservation des preuves ;
- critères de confinement ou d’arrêt du service ;
- organisation de la communication ;
- conditions permettant la reprise du service ;
- organisation du retour d’expérience après l’incident.

L’objectif n’est pas de décrire à nouveau tout le processus de gestion de crise étudié précédemment, mais de montrer comment il doit être **préparé avant la mise en production**.

---

## Livrable attendu

Un document PDF d’aspect professionnel comprenant :

- une **page de garde** (nom de l’école, nom du cours, nom du professeur, noms des membres du groupe) ;
- une **page reprenant l’énoncé** du mini-cas ;
- des **pages numérotées** avec une présentation claire et professionnelle ;
- des **graphiques, schémas ou images** pour illustrer les analyses et rendre la lecture plus agréable.

### Contenu du livrable

- Une **page de synthèse** : présentation de la situation, niveau de risque global et décision recommandée concernant la mise en production.
- Le **détail des analyses** : tableau des risques, responsabilités des acteurs, mesures de sécurisation et critères utilisés pour décider du lancement.
- Vos **recommandations priorisées** : liste des actions impératives avant mise en production, actions à court terme et mesures permettant d’assurer la résilience du service après son lancement.
