# Viva Questions and Answers

**Python**
1. *Why Python?* Simple syntax, and rich libraries for ML (scikit-learn), data (pandas), web UI (Streamlit).
2. *What is a virtual environment?* An isolated folder of packages so this project's versions don't clash with others.
3. *Why `.env` and python-dotenv?* Keeps passwords/keys out of source code and out of GitHub.

**Streamlit**
4. *What is Streamlit?* A Python framework that turns scripts into web apps without HTML/JS.
5. *How do you keep a user logged in?* `st.session_state["user"]` stores login data during the browser session.
6. *How does multi-page work?* Every file in `pages/` becomes a sidebar page; number prefixes set the order.

**MySQL**
7. *Why four tables?* Users, stations, status history, predictions: each holds one kind of data (normalisation).
8. *What is a foreign key / ON DELETE CASCADE?* `station_id` in child tables references `stations`; deleting a station deletes its rows too.
9. *Why keep every status row?* The newest row is "current"; older rows form history usable for retraining.
10. *What is a parameterized query?* SQL with `%s` placeholders and separate values, so input can't change the SQL (prevents injection).

**Machine Learning**
11. *What do you predict?* Availability (High/Medium/Low, classification) and waiting time in minutes (regression).
12. *Why Random Forest?* Many decision trees vote; handles non-linear patterns and reduces overfitting versus one tree.
13. *What is a Decision Tree?* A flowchart of if/else splits on features that ends in a class.
14. *Why Linear Regression for waiting time?* It scored best (lowest MAE) on our data, where wait is roughly proportional to queue. We choose by metrics, not by fashion.
15. *Which metrics?* Accuracy, precision, recall, F1, confusion matrix; MAE, RMSE, R² for regression.
16. *Why a time-based split?* We predict the future, so we train on earlier dates and test on the latest ones.
17. *What is overfitting?* Memorising training data and failing on new data; limited by tree depth and testing on unseen data.
18. *Are results real-world accuracy?* No. Data is synthetic; the score only shows the pipeline works. Real data is needed.

**Haversine / Maps / APIs**
19. *What is Haversine?* Great-circle distance between two lat/lon points on a sphere.
20. *Why not Pythagoras?* The Earth is curved; error grows with distance.
21. *Limitation of Haversine?* Straight-line, not road distance; we optionally use OSRM for roads.
22. *Which map services?* Folium/Leaflet with OpenStreetMap tiles, Nominatim (geocoding), OSRM (routes); all keyless.
23. *What if the API fails?* try/except falls back to estimated distance and time.

**Recommendation**
24. *How do you recommend?* Weighted score from distance, predicted wait, availability, travel time and traffic; not just nearest.
25. *Why transparent?* The score parts are displayed so users see why a station is ranked first.

**Security / Limitations / Future**
26. *How are passwords stored?* bcrypt hash with salt; never plain text.
27. *How is admin protected?* Role stored in DB; admin page checks it on the server before showing anything.
28. *Main limitations?* Synthetic data, no live feed, public routing servers limited, GPS needs HTTPS/localhost.
29. *Future scope?* IoT sensors or fuel-company APIs for real-time data, retraining on live logs, mobile app, booking/payments, multiple cities.
30. *Is availability real-time?* No. It is labelled "AI Predicted Availability", an estimate.
