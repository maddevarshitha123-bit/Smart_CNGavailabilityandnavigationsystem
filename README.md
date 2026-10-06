# Smart CNG Availability Prediction and Navigation System Using AI

B.Tech CSE project. Streamlit + Python + MySQL + scikit-learn + OpenStreetMap.

> **Honesty note:** No real-time sensor/API is connected. All availability values are labelled
> **"AI Predicted Availability"** (an ML estimate from historical data). The included dataset and
> stations are **synthetic sample data** (Hyderabad-area, approximate coordinates). Model scores are on
> synthetic data and are **not** real-world accuracy.

## Changes from the original folder plan
- Login/Register/Profile are combined in `pages/1_Account.py`; Station Details and Navigation are inside *Find Stations*; About is `6_About.py`.
- Added `config.py`, `utils/auth.py`, `utils/service.py` (glue), `utils/ui.py`, `utils/charts.py`, `scripts/init_db.py`, `tests/`, `docs/`, `.env.example`.
- Page files are number-prefixed so Streamlit orders the sidebar correctly.

## Folder structure
```
smart_cng/
├── app.py  config.py  generate_dataset.py  requirements.txt  .env.example  .gitignore
├── database/  schema.sql  sample_data.sql
├── data/      cng_history.csv
├── ml/        train_model.py  predict.py  model.pkl  metrics.json
├── pages/     1_Account  2_Find_Stations  3_AI_Prediction  4_Recommendations  5_Admin_Dashboard  6_About
├── utils/     database  auth  distance  location  recommendation  service  charts  ui
├── scripts/   init_db.py
├── tests/     test_core.py
├── assets/    style.css
└── docs/      PROJECT_REPORT.md  VIVA_QA.md  PRESENTATION_OUTLINE.md
```

## Setup on Windows + VS Code
1. Install: Python 3.10+ (tick *Add to PATH*), MySQL Server 8 + Workbench, VS Code, Git.
2. Unzip the project, open the folder in VS Code, open a terminal (Ctrl+`):
```bash
cd smart_cng
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```
If PowerShell blocks activation: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

3. Edit `.env` (already copied from `.env.example`): set `DB_PASSWORD` to your MySQL root password, and set a strong `ADMIN_PASSWORD`.
4. Create database, sample stations and the admin account:
```bash
python scripts/init_db.py
```
Expected: `Sample stations loaded.`, `Admin created: admin@example.com`, `Database ready.`

5. Dataset and model (a ready dataset and model are included, but you can regenerate):
```bash
python generate_dataset.py
python -m ml.train_model
```
Expected: `Saved 2880 rows ...`, then accuracy/MAE for each model and `Saved model -> ...`.

6. Run the app:
```bash
streamlit run app.py
```
A browser tab opens at `http://localhost:8501`. The Home page should show *Database: connected* and *ML model: loaded*.

Log in as the admin (email/password from `.env`) to use the Admin Dashboard. Other users register on the Account page.

## Map, routing and API keys
- Map: Folium/Leaflet with OpenStreetMap tiles. Geocoding: Nominatim. Route time: OSRM demo server (fair use only). Navigate button: OpenStreetMap directions link. **None needs a key.**
- If a route/network call fails, the app falls back to straight-line (Haversine x 1.3) estimates.
- `MAP_API_KEY` is optional. If you switch to OpenRouteService, get a free key at https://openrouteservice.org/dev/#/signup, put it in `.env` only, read it via `config.py`, and never commit `.env`.

## Haversine in simple words
The Earth is round, so flat-map Pythagoras is wrong over distance. Haversine converts the latitude/longitude
differences into an angle at the Earth's centre and multiplies by the Earth's radius (6371 km):
`distance = 2R x asin(sqrt(sin²(dLat/2) + cos(lat1) x cos(lat2) x sin²(dLon/2)))`. It gives straight-line distance, not road distance.

## Recommendation score
Weighted average (x100) of: distance 25%, predicted waiting 30%, predicted availability 25%, travel time 10%, traffic 10%
(adjustable on the page). Distance/wait/travel are scaled so smaller = better. Closed or maintenance stations are excluded.

## Tests
```bash
pytest -v
```
DB tests are skipped automatically if MySQL isn't configured. Verified in development: distance, invalid coordinates,
empty location, recommendation, navigation link, ML prediction, waiting-time behaviour, invalid ML input. Not yet run
end-to-end by me: pages/UI, login/registration, admin CRUD against a live MySQL (fill "Actual Result" yourself when you demo).

| ID | Description | Input | Expected | Actual | Status |
|---|---|---|---|---|---|
| T01 | Registration valid | Name, valid email, `Abcdef1!` | Success message, row in `users` | | |
| T02 | Registration weak password | `abc` | Error listing missing rules | | |
| T03 | Duplicate email | Existing email | "already registered" | | |
| T04 | Login valid | Correct credentials | Welcome, session set | | |
| T05 | Invalid login | Wrong password | "Invalid email or password." | | |
| T06 | Station search | Text "Uppal" | Only matching stations | | |
| T07 | Distance calculation | Two known points | ~6.2 km Hyderabad-Secunderabad | 6.23 km | Pass |
| T08 | Empty location | "" | No crash; default location used | `geocode("")` returns None | Pass |
| T09 | Invalid coordinates | lat 200 | Error, no crash | ValueError raised | Pass |
| T10 | ML availability | Peak hour, High traffic | Valid class + confidence | Valid output | Pass |
| T11 | Waiting time | Queue 2 vs 25 | Larger queue, longer wait | 5 min vs 64 min | Pass |
| T12 | Recommendation | Near-but-bad vs far-but-good | Far-but-good ranked first | Far ranked first | Pass |
| T13 | Navigation | Station coords | Valid OSM link | Link generated | Pass |
| T14 | DB connection | Correct `.env` | Home shows "connected" | | |
| T15 | Admin operations | Add/update/delete station | Table changes; non-admin blocked | | |

## Error handling
DB down, missing model, invalid input, empty station list, invalid coordinates, denied/unavailable GPS and network failure all show
friendly messages (see `utils/database.py`, `ml/predict.py`, `utils/ui.py`). A missing API key never blocks the app (none is required).

## Security practices
Passwords hashed with bcrypt (salted, never stored plain) · all SQL uses `%s` parameters (blocks SQL injection) · secrets only in `.env`
(git-ignored) · email/password/coordinate validation · admin pages check `role == 'admin'` on the server side · same error for wrong
email or password (no user enumeration).

## GitHub
1. Create an empty repository on github.com (no README), e.g. `smart-cng`.
```bash
git init
git add .
git status            # confirm .env is NOT listed
git commit -m "Initial commit: Smart CNG Finder"
git branch -M main
git remote add origin https://github.com/<your-username>/smart-cng.git
git push -u origin main
```
If `.env` was ever pushed: change your DB password and remove it with `git rm --cached .env`, commit and push.

## Known limitations
Synthetic data; predictions are estimates; no live sensors; public OSRM/Nominatim are for light demo use; browser GPS needs HTTPS or localhost.
