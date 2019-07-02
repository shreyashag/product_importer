# Product Importer
This is a CRUD application for products based using the following tools-
1. Flask for Backend.
2. Flask SSE for Server Side Events.
3. Dramatiq for Workers.
4. Redis as a broker for Dramatiq.
5. Mysql as a Database for Persistence.


The application has an option for bulk upload of products using a CSV.

It also has CRUD for webhooks that are triggered whenever any action is taken on a product.
Currently, the webhook functions only for urls beginning with https://requestbin.

# Deployment

Deployment is really simple. The application has been containerised and has a one command deploy.
Simply navigate to the directory after cloning and run- **docker-compose up**

## Notes
A **docker-envrc** file is used for managing credentials.
The docker-envrc should contain the following variables -
<ul>
<li>DB_USERNAME=user</li>
<li>DB_PASSWORD=password</li>
<li>DB_SCHEMA=db</li>
<li>DB_PORT=3306</li>
<li>DB_HOST=db</li>

<li>REDIS_HOST=redis</li>
<li>REDIS_PORT=6379</li>
<li>REDIS_DB=0 </li>
</ul>
