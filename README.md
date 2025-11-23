# Zinsrechner-NEU

# Flet Zinsrechner (Compound Interest Calculator)

[![Flet App](https://img.shields.io/badge/Made%20with-Flet-blue.svg)](https://flet.dev)

Ein **moderner Zinseszinsrechner**, entwickelt mit dem Flet Framework, basierend auf Flutter.

Diese Anwendung bietet eine **responsive Benutzeroberfläche (GUI)** und kann als native App für Desktop und Mobile (Android/iOS) kompiliert werden. Die komplexen Berechnungen (Zinssatz und Dauer) werden mit einem reinen **Python-Algorithmus (Bisektionsmethode)** gelöst, wodurch externe wissenschaftliche Abhängigkeiten vermieden werden.

[Zinsrechner Screenshot.pdf](https://github.com/user-attachments/files/23697461/Zinsrechner.Screenshot.pdf)

---

## ✨ Hauptmerkmale

Die wichtigsten Vorteile und technischen Details auf einen Blick:

* **💻 Technologie:** Moderne, plattformunabhängige GUI dank **Flet**.
* **📱 Kompatibel:** Lauffähig als Desktop-Anwendung und kompilierbar als **Android/iOS-App**.
* **⚖️ Mathematische Robustheit:** Berechnungen für Zinssatz und Dauer nutzen die **Bisektionsmethode** für hohe Präzision.

---

## 🔢 Berechnungen

Die App löst die Zinseszinsformel nach fünf zentralen Variablen auf:

* **Endkapital**
* **Anfangskapital**
* **Zinssatz**
* **Dauer (in Jahren)**
* **Monatliche Einzahlung **

---

## 🛠️ Anforderungen

Um die Anwendung auszuführen, benötigen Sie:

* **Python 3.10+**
* **Flet** (Installieren Sie die neueste Version):
    ```bash
    pip install flet
    ```

---

## ▶️ App starten (Entwicklungsmodus)

Navigieren Sie in das Projektverzeichnis und starten Sie die Anwendung in der Vorschau:

```bash
py -m flet run main.py
