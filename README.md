# 🛒 Market Core Place

A microservices-based Django project for a marketplace platform, consisting of the following services:

- 🔐 **Auth Service** — User management and authentication (via Keycloak)
- 👤 **Customer Service** — Customer profile and data management
- 📦 **Product Service** — Product categories, listings, and pricing
- 📑 **Order Service** — Order creation, tracking, and processing
- 🕊️ **RabbitMQ** — Interservice messaging and event-based communication
- **Shared Folder** - share folder for models, views , auth, messing etc(DRY principles)

---

## 🧱 Architecture Overview

```mermaid
graph TD
  Keycloak[(Keycloak)]
  AuthService[Auth Service]
  CustomerService[Customer Service]
  ProductService[Product Service]
  OrderService[Order Service]
  RabbitMQ((RabbitMQ Broker))
  Postgres[(PostgreSQL DB)]

  Keycloak --> AuthService
  AuthService -->|OIDC| CustomerService
  AuthService -->|OIDC| ProductService
  AuthService -->|OIDC| OrderService

  ProductService --> RabbitMQ
  OrderService --> RabbitMQ
  RabbitMQ --> ProductService
  RabbitMQ --> OrderService

  CustomerService --> Postgres
  ProductService --> Postgres
  OrderService --> Postgres
# market-place-core


🚀 Getting Started
✅ Prerequisites
Docker & Docker Compose
Python 3.10+ (if running locally)
Keycloak (Via docker)
RabbitMQ (via Docker)

📁 Project Structure
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
├── .env
└── README.md

⚙️ Environment Configuration
📦 Root .env
🧩 Example auth-service/.env
create .env file at the root folder of auth-service

cp # database
cp DB_NAME=auth
cp DB_USER=admin
cp DB_PASSWORD=password
cp DB_HOST=auth_db
cp DB_PORT=5432
cp SECRET_KEY=django-insecure-vojc30+88%k!b7lz%_$+ow$uqq(zlx^r*!powa^2-o=#49ox=u

cp #keycloak
cp KEYCLOAK_SERVER_URL=http://keycloak:8080
cp KEYCLOAK_REALM=master
cp KEYCLOAK_CLIENT_ID=django-app
cp KEYCLOAK_CLIENT_SECRET=your-client-secret
cp KEYCLOAK_ADMIN_USERNAME=admin
cp KEYCLOAK_ADMIN_PASSWORD=admin

cp # rabbitMQ


🧩 Example customer-service/.env

cp DB_NAME=customer
cp DB_USER=admin
cp DB_PASSWORD=password
cp DB_HOST=customer_db
cp DB_PORT=5432
cp SECRET_KEY=django-insecure-vojc30+88%k!b7lz%_$+ow$uqq(zlx^r*!powa^2-o=#49ox=u

cp # celery broker
CELERY_BROKER_URL=amqp://myuser:mypassword@rabbitmq:5672/%2F

cp # keycloak
cp KEYCLOAK_SERVER_URL=http://keycloak:8080
cp KEYCLOAK_REALM=master
cp KEYCLOAK_CLIENT_ID=django-app
cp KEYCLOAK_CLIENT_SECRET=your-client-secret

🧩 Example order-service/.env

cp DB_NAME=order
cp DB_USER=admin
cp DB_PASSWORD=password
cp DB_HOST=order_db
cp DB_PORT=5432
cp SECRET_KEY=django-insecure-vojc30+88%k!b7lz%_$+ow$uqq(zlx^r*!powa^2-o=#49ox=u


# sandbox
cp SANDBOX_USERNAME=sandbox
cp SANDBOX_API_KEY=atsk_6083170b352878eafec8356b18730e8a8cb763c773b4cca45138102b92088b81544a7e8f

cp CELERY_BROKER_URL=amqp://myuser:mypassword@rabbitmq:5672/%2F

cp RABBITMQ_DEFAULT_USER=myuser
cp RABBITMQ_DEFAULT_PASS=mypassword
cp RABBITMQ_PORT=5672
cp RABBITMQ_HOST=rabbitmq
cp RABBITMQ_MANAGEMENT_PORT=15672

cp SERVICE_NAME=order-service


cp EMAIL_HOST_USER=admin@gmail.com
cp EMAIL_HOST_PASSWORD=admin
cp ADMIN_EMAIL=admin@gmail.com

cp KEYCLOAK_SERVER_URL=http://keycloak:8080
cp KEYCLOAK_REALM=master
cp KEYCLOAK_CLIENT_ID=django-app
cp KEYCLOAK_CLIENT_SECRET=your-client-secret

🧩 Example product-service/.env

cp DB_NAME=product
cp DB_USER=admin
cp DB_PASSWORD=password
cp DB_HOST=product_db
cp DB_PORT=5432
cp SECRET_KEY=django-insecure-vojc30+88%k!b7lz%_$+ow$uqq(zlx^r*!powa^2-o=#49ox=u

cp CELERY_BROKER_URL=amqp://myuser:mypassword@rabbitmq:5672/%2F

cp KEYCLOAK_SERVER_URL=http://keycloak:8080
cp KEYCLOAK_REALM=master
cp KEYCLOAK_CLIENT_ID=django-app
cp KEYCLOAK_CLIENT_SECRET=your-client-secret




