# Description du Dataset - Alkhabir Agro

### 1. Nature des données
Le projet "Alkhabir Agro" n'utilise pas un dataset statique classique, mais un **flux de données dynamiques en temps réel (Dynamic Data Chain)**. Pour les besoins du hackathon, nous avons extrait un échantillon représentatif (`sample_dataset.csv`) qui illustre comment notre moteur de calcul transforme les variables brutes en décisions de pompage.

### 2. Sources des données
- **Satellite (Remote Sensing):** Flux via Open-Meteo (Modèle ECMWF/ERA5-Land) pour l'humidité du sol et l'évapotranspiration de référence (ET0).
- **Météorologie au sol:** API OpenWeather pour les variables de température, vent et précipitations en temps réel.
- **Référentiel Agronomique:** Coefficients Kc et constantes de sol basés sur les standards **FAO-56** et les études régionales de l'**ORMVAM** (Maroc).

### 3. Nettoyage et Préparation (Data Work)
- **Normalisation:** Conversion des flux JSON hétérogènes en unités standards (mm, °C, m/s).
- **Validation Scientifique (Sanity Guard):** Implémentation d'un filtre pour éliminer les valeurs aberrantes (ex: heures de pompage > 12h/ha).
- **Interpolation Temporelle:** Alignement des données satellites (souvent retardées de 5 jours) avec les prévisions météo locales pour créer un modèle prédictif sur 7 jours.

### 4. Valeur Ajoutée AI
L'IA (Gemini 1.5 Flash) intervient en fin de chaîne comme **moteur de raisonnement (Reasoning Engine)** pour interpréter ces données techniques et les traduire en conseils actionnables pour le petit agriculteur, rendant la donnée "froide" (satellites) "chaude" et utile.
