# Django Store

Miniapp to sale products

# Requirements

* Linux Server
* Python3

# Installation

Install system
Install using `pip`...

    mkvirtualenv store
    pip install -r requirements.txt

# App online

    https://facturacion.uno/

# Swagger Documentation Link

    https://facturacion.uno/api-doc/


# Running Tests

    python manage.py test

# To try the app

    # Creating new purchase    

    * Go to app online (https://facturacion.uno/)
    * Click on the product
    * Type Quantity and click on Continue
    * The app redirects to TPaga payment
    * After the payment the app reloads the purchase detail

    # Reverting purchase

    * Click on the link (Purchases)
    * Click on link (Details) of purchase to revert
    * Click on Revert Payment 

    * Also you can to find the endpoints to load on postman in the folder called (portman)
