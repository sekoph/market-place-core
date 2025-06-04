# 🛒 Market Core Place

A microservices-based Django project for a marketplace platform, consisting of the following services:

- 🔐 **Auth Service** — User management and authentication (via Keycloak)
- 👤 **Customer Service** — Customer profile and data management
- 📦 **Product Service** — Product categories, listings, and pricing
- 📑 **Order Service** — Order creation, tracking, and processing
- 🕊️ **RabbitMQ** — Interservice messaging and event-based communication
- **Shared Folder** - share folder for models, views , auth, messing etc(DRY principles)

---

## Architecture Overview


🚀 Getting Started
✅ Prerequisites
- Docker & Docker Compose
- Python 3.10+ (if running locally)
- Keycloak (Via docker)
- RabbitMQ (via Docker)
  ## 🚀 Key Features
- The message broker sends email to admin and to user sms after ordering successfully
- implentations of rabbitMQ client and server for interservice communication between order and product service to check availability of product before ordering
- Authentication with OpenID Connect over keycloak

📁 Project Structure
```sh
market-core-place/
├── auth-service/
├── customer-service/
├── product-service/
├── order-service/
├── shared/
├── deploy.sh
├── kind-config.yaml
├── microservices-k8s.yaml
├── docker-compose.yml
└── README.md
```

## 🔧 Setup & Configuration

### 1️⃣ Clone the Repository
- Create a parent directory for the microservice as market-place-core

```sh
mkdir market-place-core
```
- navigate to market-place-core and clone this repo

```sh
cd market-place-core
git clone git@github.com:sekoph/market-place-core.git
```

⚙️ Environment Configuration

📦 Root .env

🧩 Example auth-service/.env

create .env file at the root folder of auth-service, customer-service, product-service, order-service and copy the files respectively
```sh
# database
DB_NAME=auth
DB_USER=admin
DB_PASSWORD=password
DB_HOST=auth_db
DB_PORT=5432
SECRET_KEY=django-insecure-vojc30+88%k!b7lz%_$+ow$uqq(zlx^r*!powa^2-o=#49ox=u

#keycloak
KEYCLOAK_SERVER_URL=http://keycloak:8080
KEYCLOAK_REALM=master
KEYCLOAK_CLIENT_ID=django-app
KEYCLOAK_CLIENT_SECRET=your-client-secret
KEYCLOAK_ADMIN_USERNAME=admin
KEYCLOAK_ADMIN_PASSWORD=admin

```
🧩 Example customer-service/.env
```sh
DB_NAME=customer
DB_USER=admin
DB_PASSWORD=password
DB_HOST=customer_db
DB_PORT=5432
SECRET_KEY=django-insecure-vojc30+88%k!b7lz%_$+ow$uqq(zlx^r*!powa^2-o=#49ox=u

# celery broker
CELERY_BROKER_URL=amqp://myuser:mypassword@rabbitmq:5672/%2F

# keycloak
KEYCLOAK_SERVER_URL=http://keycloak:8080
KEYCLOAK_REALM=master
KEYCLOAK_CLIENT_ID=django-app
KEYCLOAK_CLIENT_SECRET=your-client-secret
```
🧩 Example order-service/.env
```sh
DB_NAME=order
DB_USER=admin
DB_PASSWORD=password
DB_HOST=order_db
DB_PORT=5432
SECRET_KEY=django-insecure-vojc30+88%k!b7lz%_$+ow$uqq(zlx^r*!powa^2-o=#49ox=u


# sandbox
SANDBOX_USERNAME=sandbox
SANDBOX_API_KEY=atsk_6083170b352878eafec8356b18730e8a8cb763c773b4cca45138102b92088b81544a7e8f

CELERY_BROKER_URL=amqp://myuser:mypassword@rabbitmq:5672/%2F

RABBITMQ_DEFAULT_USER=myuser
RABBITMQ_DEFAULT_PASS=mypassword
RABBITMQ_PORT=5672
RABBITMQ_HOST=rabbitmq
RABBITMQ_MANAGEMENT_PORT=15672

SERVICE_NAME=order-service


EMAIL_HOST_USER=admin@gmail.com
EMAIL_HOST_PASSWORD=admin
ADMIN_EMAIL=admin@gmail.com

KEYCLOAK_SERVER_URL=http://keycloak:8080
KEYCLOAK_REALM=master
KEYCLOAK_CLIENT_ID=django-app
KEYCLOAK_CLIENT_SECRET=your-client-secret
```
🧩 Example product-service/.env
```sh
DB_NAME=product
DB_USER=admin
DB_PASSWORD=password
DB_HOST=product_db
DB_PORT=5432
SECRET_KEY=django-insecure-vojc30+88%k!b7lz%_$+ow$uqq(zlx^r*!powa^2-o=#49ox=u

CELERY_BROKER_URL=amqp://myuser:mypassword@rabbitmq:5672/%2F

KEYCLOAK_SERVER_URL=http://keycloak:8080
KEYCLOAK_REALM=master
KEYCLOAK_CLIENT_ID=django-app
KEYCLOAK_CLIENT_SECRET=your-client-secret
```
🧰 Start All Services
```sh
# run all services at once
# at the root folder of the project
docker-compose us
```

🔐 Setup Keycloak client
```sh
http://localhost:8080
# use admin for password and username
```
- login with admin as username, admin as password
- select client and create client
- enter client type as OpenID Connect
- enter client_id as
```sh
django-app
```
- enter next
- turn on Client authentication leave off Authorization
- check all the other options
- press next
```sh
# root url
http://localhost:8080
# home url
http://localhost:8080
# valid redirect URIs 
http://localhost:8080/api/*
# Valid post logout redirect URI
http://localhost:8080/
# Web origins
http://localhost:8080
```
- Save changes
- In client dashboard navigate to credentials copy client secret paste to env files KEYCLOAK_CLIENT_SECRET
- Navigate to Realm roles create role as user and save
- Navigate to user , Add user
- turn on Email verified
- enter user details and create
- Navigate to user credential enter password and turn off temporary
- Navigate to role mapping and Assign Role you created
- Navigate to Realm setting at the bottom of the screen select Tokens increase token lifespan and save changes

stop and rerun ```docker-compose up``` for client secret to take effect

🔁 Database Migrations
- In a new terminal
- For each service: run
```sh
docker-compose exec order sh 
python manage.py migrate
# to run tests
python manage.py test
# repeat the same for customer,auth and product exactly.
```
📡 API Endpoints (Example)
service                     url
- auth                        http://localhost:8000/api/auth/loginn
The below endpoints are authenticated.
- authenticated routes copy access_token from above url
  
- customer                    http://localhost:8001/api/customers/
```sh
curl -X POST http://localhost:8001/api/customers/ \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
    -d '{
    "phone": "+254 708063310"
}'
```
  
- order                       http://localhost:8002/api/orders/
  ```sh
  curl -X POST http://localhost:8002/api/orders/ \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
    -d '{
      "customer_phone": "+254708063310",
      "quantity": 1,
      "product_id": "0828ce0f-6935-4800-a80d-c96f95a1fbf6"
  }'

  ```
- product                     http://localhost:8003/api/products/
```sh
  curl -X POST http://localhost:8003/api/products/ \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
    -d '{
        "name": "BMW X5",
        "slug": "bmw-x5",
        "description": "Luxury and comfort",
        "category_id": "4a2d2ee3-9b01-458e-9e2c-816acd52afe7",
        "price": 10000,
        "stock_quantity": 10,
        "available": true
      }'
  ```
- product category            http://localhost:8003/api/product_categories/
  ```sh
  curl -X POST http://localhost:8003/api/product_categories/ \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
    -d '{
    "name": "SUV",
    "slug": "suv",
    "description": "porche vehicles",
    "parent_id": "5ddcd636-fc6e-43ab-a421-b17311cdcb48"
    }'
  ```
- product price avg with category   http://localhost:8003/api/categories/{product-slug}/average-price/
  ```sh
  curl -X GET http://localhost:8003/api/categories/{product-slug}/average-price/ \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

## License
[MIT](LICENSE)









