# GuitarShop — React + Django REST conversion

Acest proiect e conversia site-ului GuitarShop din Django template-uri
server-side într-un frontend React (Vite), care consumă un backend Django
REST Framework + JWT.

```
guitarshop-react/
├── backend/guitarshop/    ← proiectul Django original + API nou (app "api")
└── frontend/               ← proiectul React (Vite)
```

## Ce s-a schimbat față de proiectul original

- Am adăugat un app nou `api` în Django cu Django REST Framework +
  `djangorestframework-simplejwt` pentru autentificare pe token (JWT),
  în loc de sesiune. Login-ul folosește tot email + parolă, ca înainte.
- Am adăugat `django-cors-headers`, configurat să accepte cereri de la
  `http://localhost:5173` (dev server-ul Vite).
- Coșul de cumpărături nu mai stă în sesiunea Django, ci în `localStorage`
  pe frontend; backend-ul doar calculează totalurile (`/api/cart/quote/`)
  și validează stocul la finalizarea comenzii (`/api/cart/checkout/`).
- Review-urile live merg prin WebSocket (Django Channels), autentificat cu
  JWT: frontend-ul trimite tokenul ca query param la conectare
  (`?token=<access>`), iar backend-ul validează tokenul înainte de a
  accepta conexiunea. Username-ul recenziei vine mereu din tokenul
  validat pe server, niciodată din ce trimite clientul.
- Template-urile Django (`.html`) rămân în proiect neatinse, dar nu mai
  sunt folosite — tot UI-ul e acum în React.

## Rulare — Backend (Django)

```bash
cd backend/guitarshop
python -m venv venv
.\venv\Scripts\Activate.ps1         # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend-ul pornește pe `http://127.0.0.1:8000` folosind Daphne (server
ASGI, necesar pentru WebSocket) — asigură-te că `daphne` e prima intrare
din `INSTALLED_APPS` în `settings.py`, altfel `runserver` pornește
serverul WSGI clasic și rutele WebSocket nu funcționează.

> Notă: `payments/views.py` importă `stripe`. E deja în `requirements.txt`.
> Pentru ca stocul să se actualizeze corect după o plată, vezi secțiunea
> „Configurare Stripe" mai jos — fără `stripe listen` pornit local,
> plățile trec prin Stripe dar stocul nu se scade niciodată.

## Rulare — Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

Frontend-ul pornește pe `http://localhost:5173`.

Fișierul `.env` din `frontend/` conține adresa backend-ului:

```
VITE_API_URL=http://127.0.0.1:8000
VITE_WS_URL=ws://127.0.0.1:8000
```

Modifică-l dacă rulezi backend-ul pe alt port/host.

## Configurare Stripe (plăți de test)

Checkout-ul creează o sesiune Stripe reală (`api/views.py:CheckoutView`), dar
scăderea stocului se face abia după confirmarea plății, printr-un webhook
(`payments/views.py:stripe_webhook`). Local, Stripe nu poate trimite acest
webhook direct către `localhost` — ai nevoie de Stripe CLI ca intermediar.

**O singură dată** (autentificare + selectare cont):

```bash
stripe login
stripe switch context
```

Din meniul afișat, alege contul de test, ex. **GuitarShop sandbox** — nu
`live`. Selecția rămâne activă pentru sesiunile viitoare de terminal.

**De fiecare dată când testezi o plată**, într-un terminal separat, lăsat
deschis pe tot parcursul testului:

```bash
stripe listen --forward-to localhost:8000/payments/webhook/
```

La pornire afișează un secret de forma `whsec_...` — copiază-l în `.env`
(sau `settings.py`) la `STRIPE_WEBHOOK_SECRET`, apoi **repornește Django**
ca să încarce noua valoare. Acest secret se schimbă la fiecare pornire a
`stripe listen`, dacă nu ai definit un endpoint fix în Dashboard.

Testează cu cardul `4242 4242 4242 4242`, orice dată viitoare, orice CVC.
În terminalul `stripe listen` ar trebui să apară `checkout.session.completed`
urmat de `200`; dacă apare `400`, secretul din `.env` nu se potrivește cu
cel afișat la pornirea curentă a listener-ului.

> Notă: dacă `stripe switch context` revine mereu la `live`, forțează
> sandbox-ul direct fără să depinzi de context activ:
> ```bash
> stripe listen --forward-to localhost:8000/payments/webhook/ --api-key sk_test_...
> ```
> (cheia de test se ia din Dashboard → Developers → API keys, cu toggle-ul
> pe Sandbox).

## Cum funcționează autentificarea

- `/api/auth/register/` — creează cont (username, email, parolă, adresă)
- `/api/auth/login/` — primește `{ email, password }`, întoarce `access` +
  `refresh` token (JWT). Salvate în `localStorage` sub cheile `access` și
  `refresh`.
- Token-ul `access` e atașat automat la fiecare cerere din
  `src/api/client.js`; la un 401, se încearcă automat refresh cu token-ul
  `refresh`.
- **2FA opțional**: userul poate activa autentificare în doi pași (TOTP,
  compatibil Google Authenticator) din `/api/auth/2fa/setup/`. Dacă e
  activ, login-ul cere și un cod suplimentar (`code`).
- Rutele de produse/coș/wishlist din React sunt protejate
  (`ProtectedRoute`) — dacă nu ești logat, ești trimis la `/login`.
- Conexiunile WebSocket (recenzii live) necesită și ele un token JWT
  valid trimis ca query param la conectare — vezi `jwt_auth_middleware.py`
  în app-ul `api`.

## Rate limiting

Toate endpoint-urile sensibile sunt protejate cu throttling
(`DEFAULT_THROTTLE_RATES` în `settings.py`):

| Endpoint | Limită |
|---|---|
| Login | 5/min |
| 2FA confirm | 5/min |
| Register | 3/oră |
| Checkout | 10/min |
| Restul endpoint-urilor autentificate | 60/min |

## Structura paginilor React

| Rută                  | Corespondent Django original          |
|------------------------|----------------------------------------|
| `/`                    | `index.html`                          |
| `/electric` `/acoustic` `/bass` | `electric.html`, `acoustic.html`, `bass.html` |
| `/products/:brand`     | `products.html`                       |
| `/product/:id`         | `Produs.html`                         |
| `/cart`                 | `cart.html`                           |
| `/wishlist`             | `wishlist.html`                       |
| `/login`                | `login.html`                          |
| `/signin`               | `signin.html`                         |

## Ce merită continuat

- Pagina de detaliu produs presupune că brand-ul e cunoscut de frontend
  (`src/config/catalog.js`) — dacă adaugi branduri noi în baza de date,
  actualizează și fișierul acela.
- View-urile Django clasice din `products/views.py`, `cart/views.py`
  (server-rendered, neconectate la React) ar trebui verificate — dacă nu
  mai sunt folosite în `urls.py`, e mai sigur să fie șterse decât lăsate
  active în paralel cu API-ul DRF.