# GuitarShop

Magazin online de chitare. Era făcut inițial cu Django + template-uri
server-side, acum e în curs de conversie la React (Vite) în față, cu
Django ca API (DRF + JWT) în spate.

```
guitarshop-react/
├── backend/guitarshop/    ← Django (proiectul vechi + app-ul nou "api")
└── frontend/               ← React (Vite)
```

## Ce am schimbat față de site-ul original

- Am băgat un app nou, `api`, cu Django REST Framework + JWT pentru login,
  în loc de sesiune. Tot cu email + parolă te loghezi, doar mecanismul din
  spate e diferit.
- `django-cors-headers` ca să nu se plângă browserul când React (pe
  `localhost:5173`) vorbește cu Django (pe `127.0.0.1:8000`).
- Coșul stă acum în `localStorage`, nu în sesiunea Django. Backend-ul doar
  calculează prețul (`/api/cart/quote/`) și verifică stocul la checkout.
- Recenziile live merg pe WebSocket (Django Channels). Tokenul JWT se
  trimite ca query param la conectare, iar numele userului la recenzie
  vine din token, nu din ce trimite clientul — ca să nu poată cineva să
  posteze cu alt nume.
- Template-urile `.html` vechi au rămas în proiect dar nu se mai folosesc,
  tot UI-ul e în React acum.
- Am înlocuit `<select>`-ul de țară din checkout cu o componentă proprie
  (`CountrySelect.jsx`), pentru că highlight-ul albastru de pe opțiunea
  selectată dintr-un `<select>` nativ e desenat de browser, nu poți să-l
  schimbi din CSS oricât ai încerca.

## Cum pornești backend-ul

```bash
cd backend/guitarshop
python -m venv venv
.\venv\Scripts\Activate.ps1         # pe Windows; pe altceva: venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Pornește pe `127.0.0.1:8000`, cu Daphne (server ASGI — trebuie neapărat,
altfel nu merge WebSocket-ul). Verifică să fie `daphne` prima linie din
`INSTALLED_APPS`, altfel `runserver` pornește WSGI clasic și recenziile
live nu mai merg.

> `payments/views.py` are nevoie de `stripe`, e deja în requirements.
> Dacă stocul nu se scade după plată, vezi mai jos la Stripe.

## Cum pornești frontend-ul

```bash
cd frontend
npm install
npm run dev
```

Merge pe `localhost:5173`. În `.env` din `frontend/` ai adresa backend-ului:

```
VITE_API_URL=http://127.0.0.1:8000
VITE_WS_URL=ws://127.0.0.1:8000
```

Schimbă-l dacă rulezi pe alt port.

## Stripe (testare plăți)

Checkout-ul creează o sesiune Stripe reală, dar stocul se scade abia
după ce Stripe confirmă plata, printr-un webhook. Local, Stripe nu
poate trimite webhook-ul direct la localhost, așa că ai nevoie de
Stripe CLI pe post de intermediar.

O singură dată:

```bash
stripe login
stripe switch context
```

Alege contul de test (sandbox), nu `live`.

De fiecare dată când testezi o plată, într-un terminal separat, lăsat
pornit cât timp testezi:

```bash
stripe listen --forward-to localhost:8000/payments/webhook/
```

Îți dă un `whsec_...` — pui valoarea aia în `.env` la
`STRIPE_WEBHOOK_SECRET` și **repornești Django**. Secretul se schimbă
de fiecare dată când repornești `stripe listen`, deci dacă la un
moment dat webhook-ul începe să dea 400, probabil ai un secret vechi.

Cardul de test: `4242 4242 4242 4242`, orice dată viitoare, orice CVC.

> Dacă `stripe switch context` tot revine la `live`, forțează sandbox-ul
> direct: `stripe listen --forward-to localhost:8000/payments/webhook/ --api-key sk_test_...`

### Cum arată o comandă salvată (`Order.items`)

Când se confirmă plata, salvăm în `Order.items` un dicționar de forma
`{"nume produs": cantitate}`, nu id-uri. Ideea e că dacă schimbi numele
unui produs mai târziu, comanda veche păstrează numele de atunci, nu
cel curent. Stocul tot pe id se scade (din coșul original salvat în
metadata Stripe), doar ce afișăm în comandă e pe nume.

Comenzile mai vechi de dinainte de schimbarea asta au rămas cu id-uri,
nu se convertesc singure retroactiv.

În admin, la lista de comenzi, coloana Items nu mai arată JSON brut —
am pus un `items_display` custom care scoate fiecare produs pe rândul
lui.

## Autentificare, pe scurt

- `/api/auth/register/` — cont nou
- `/api/auth/login/` — dă `access` + `refresh` (JWT), salvate în
  `localStorage`
- Tokenul se atașează automat la fiecare request din `src/api/client.js`;
  la 401 se încearcă refresh automat
- 2FA opțional (TOTP, merge cu Google Authenticator), din
  `/api/auth/2fa/setup/`
- Rutele protejate din React (`ProtectedRoute`) te trimit la `/login`
  dacă nu ești logat
- WebSocket-ul de recenzii cere și el token JWT valid ca query param

## Rate limiting

| Endpoint | Limită |
|---|---|
| Login | 5/min |
| Confirmare 2FA | 5/min |
| Register | 3/oră |
| Checkout | 10/min |
| Restul (autentificat) | 60/min |

## Rute React vs paginile vechi

| Rută | Era |
|---|---|
| `/` | `index.html` |
| `/electric` `/acoustic` `/bass` | paginile pe categorie |
| `/products/:brand` | `products.html` |
| `/product/:id` | `Produs.html` |
| `/cart` | `cart.html` |
| `/wishlist` | `wishlist.html` |
| `/login`, `/signin` | login/signin vechi |

## Ce am găsit testând coșul (sept 2026)

Am pierdut o seară testând manual coșul/checkout-ul, ca să văd ce se
poate strica dacă trimit direct request-uri, nu doar din UI. Am găsit
două chestii, ambele reparate.

**1. Cantitate negativă dădea total negativ.** `CartQuoteView` și
`CheckoutView` făceau `int(qty)` fără să verifice dacă e pozitiv. Am
trimis `{"1": -5}` și mi-a dat înapoi `total: -26061.28`. Am adăugat
validare: dacă `qty` nu e număr, sau e `<= 0`, sau depășește stocul,
răspunde 400 direct, înainte să calculeze orice.

La `CheckoutView` chestia asta era parțial "reparată" din întâmplare
— Stripe refuză cantități `<= 0` când creezi sesiunea — dar nu voiam
să depind de faptul că altcineva verifică pentru mine.

**2. Una serioasă: exista un al doilea checkout, fără login.**
`cart/views.py` (fișierul vechi, care ar fi trebuit să nu mai fie
folosit) avea propriile lui `quote()` și `checkout()`, montate la
`/cart/checkout/` — diferit de `/api/cart/checkout/` — cu
`AllowAny`. Adică oricine, fără cont, fără token, putea trimite un
request și primea înapoi un link Stripe funcțional, plătibil, fără
adresă de livrare, fără nimic. Am testat și chiar a mers — mi-a dat
`checkout_url` valid, fără header de autentificare.

L-am șters de tot (funcțiile și rutele din `cart/urls.py`), am lăsat
în `cart/` doar view-urile vechi cu sesiune care oricum nu ating
Stripe.

Lecția: dacă ai două view-uri care fac cam același lucru, unul vechi
și unul nou, nu presupune că cel vechi "nu mai e folosit" doar pentru
că frontend-ul nu-l mai apelează — verifică dacă ruta chiar mai e
montată, pentru că altfel oricine poate să-l lovească direct.

## Ce mai e de făcut

- Pagina de produs presupune că brandul e deja cunoscut în
  `src/config/catalog.js` — dacă adaugi branduri noi în DB, trebuie
  actualizat și acolo manual.
- View-urile vechi din `products/views.py` (server-rendered) ar trebui
  verificate dacă mai sunt folosite undeva — dacă nu, mai bine șterse
  decât lăsate să zacă acolo.
- Comenzile foarte vechi rămân cu id-uri în loc de nume în `items` —
  dacă la un moment dat contează (rapoarte, istoric), ar trebui o
  migrare care să le convertească.