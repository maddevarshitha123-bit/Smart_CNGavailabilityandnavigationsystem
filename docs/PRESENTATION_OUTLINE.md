# Presentation Outline (15 slides)

| # | Slide | Content | Say | Likely viva question |
|---|---|---|---|---|
| 1 | Title | Smart CNG Availability Prediction and Navigation System Using AI; your name, guide, college | Introduce topic and team | What is your project about? |
| 2 | Introduction | CNG vehicles are growing; stations have queues | Fuel search wastes time | Why CNG? |
| 3 | Problem Statement | No easy way to know queue/availability or the best station | Drivers guess and queue | What problem do you solve? |
| 4 | Existing System | Maps show location only; calls/word of mouth; no prediction | Static info, no waiting estimate | Why not Google Maps? |
| 5 | Proposed System | Web app: nearby stations, AI prediction, recommendation, navigation | Predicts instead of guessing | What is new? |
| 6 | Objectives | Find, predict, recommend, navigate, admin manage | Read the 5 goals | Which objective is most important? |
| 7 | Architecture | UI → utils → ML/DB → OSM (use Mermaid diagram from report) | Layers each do one job | Explain data flow. |
| 8 | Modules | Account, Location, Search, Prediction, Recommendation, Admin | One line each | Which module is hardest? |
| 9 | Technologies | Python, Streamlit, MySQL, scikit-learn, Folium/OSM, bcrypt | Why each was chosen | Why Streamlit? |
| 10 | AI/ML Methodology | Data → clean → encode → time split → train → compare → save | Two targets, two model families | Why Random Forest? |
| 11 | Database | 4 tables + ER diagram | Status history enables retraining | What is a foreign key? |
| 12 | Implementation | Screenshots: Find Stations, Prediction, Recommendation, Admin | Live demo | How is distance computed? |
| 13 | Results | Metrics table from Admin → Analytics; charts (synthetic data) | State clearly that data is synthetic | Is ~69% good? |
| 14 | Advantages & Limitations | Cheap, explainable, extensible / no live data, synthetic dataset | Be honest about limits | What are the limitations? |
| 15 | Conclusion & Future Scope | Working prototype; IoT/API, real data, mobile app | Ready for real data | How would you get real-time data? |
