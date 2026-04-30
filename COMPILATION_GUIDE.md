# 🚀 ZAHEL - Compilation Android

## 📋 Options de compilation (sans WSL)

### 1. 🐙 GitHub Actions (RECOMMANDÉ - 0 stockage local)

**Avantages** :
- ✅ 0 stockage sur votre PC
- ✅ Builds automatisés
- ✅ Gratuit (2000 min/mois)
- ✅ Intégré à Git

**Comment utiliser** :
1. Poussez votre code sur GitHub
2. Allez dans "Actions" → "Build Android APK"
3. Cliquez "Run workflow"
4. Téléchargez l'APK depuis "Artifacts"

---

### 2. 🐳 Docker (Stockage minimal)

**Avantages** :
- ✅ ~5-8 GB pour Docker + image
- ✅ Environnement isolé
- ✅ Builds reproductibles

**Installation** :
```bash
# Windows : Téléchargez Docker Desktop
# Puis exécutez :
chmod +x build-docker.sh
./build-docker.sh
```

---

### 3. ☁️ Services Cloud

#### **GitPod** (codespaces.io)
- **Stockage** : 0 sur votre PC
- **Coût** : 50h gratuites/mois
- **Utilisation** : Importez votre repo GitHub

#### **Replit**
- **Stockage** : 0 sur votre PC
- **Coût** : Gratuit pour petits projets
- **Limite** : Builds Android limités

#### **AWS EC2 Free Tier**
- **Stockage** : 0 sur votre PC
- **Coût** : 750h gratuites/mois
- **Type** : t2.micro Ubuntu

---

### 4. 🖥️ Machines Virtuelles Cloud

#### **Google Cloud Platform**
- **Free Tier** : 2 vCPUs, 8GB RAM
- **Stockage** : 30GB gratuit
- **Coût** : ~$5/mois après free tier

#### **AWS Lightsail**
- **Prix** : $3.50/mois (512MB RAM)
- **Stockage** : 20GB
- **Usage** : Builds occasionnels

---

## 🎯 RECOMMANDATION

**Pour votre cas** : Utilisez **GitHub Actions**

1. Créez un repo GitHub
2. Poussez votre code
3. Le workflow se déclenche automatiquement
4. Téléchargez l'APK

**Avantages** :
- Pas d'installation locale
- Builds fiables sur Linux
- Historique des builds
- Partage facile avec l'équipe

---

## 📱 Test de l'APK

Après compilation :
```bash
# Transférez l'APK sur votre téléphone
# Installez-le (autorisez "sources inconnues")
# Testez l'application
```

---

## 🔧 Dépannage

**Si le build échoue** :
1. Vérifiez les logs dans GitHub Actions
2. Modifiez `buildozer.spec` si nécessaire
3. Ouvrez une issue sur le repo

**Pour les stores** :
- Utilisez `buildozer android release`
- Configurez un keystore pour la signature