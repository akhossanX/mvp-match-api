# mvp-match-api

## Subject

Design an API for a vending machine, allowing users with a “seller” role to add, update or remove products,
while users with a “buyer” role can deposit coins into the machine and make purchases.
Your vending machine should only accept 5, 10, 20, 50 and 100 cent coins

## Tasks

### REST API should be implemented consuming and producing “application/json”

* Implement product model with amountAvailable, cost, productName and sellerId fields

* Implement user model with username, password, deposit and role fields

* Implement CRUD for users (POST shouldn’t require authentication)

* Implement CRUD for a product model
  * GET can be called by anyone,
  * POST, PUT and DELETE can be called only by the seller user who created the product

* Implement /deposit endpoint so users with a “buyer” role can deposit 5, 10, 20, 50 and 100 cent coins into their vending machine account

* Implement /buy endpoint (accepts productId, amount of products) so users with a “buyer” role can buy products with the money they’ve deposited.
    API should return total they’ve spent, products they’ve purchased and their change if there’s any (in 5, 10, 20, 50 and 100 cent coins)

* Implement /reset endpoint so users with a “buyer” role can reset their deposit.

## Installation

1. **Clone the repository**: `git clone https://github.com/akhossanX/mvp-match-api`

2. **Setup a virtual environment:**
   1. Install virtualenv or any other virtual environment:  `sudo pip3 install virtualenv`
   2. Now create a virtual environment: `python3 -m venv mvp-env` 
   3. Activate your virtual environment: `source mvp-env/bin/activate`
   
3. **Install requirements:** `cd path/to/project/mvp-match-api && pip install -r requirements.txt`
4. **Migrate Database:** `python manage.py makemigrations && python manage.py migrate`
5. **Run Tests:**
   1. Using coverage: `coverage run manage.py test vending-machine && coverage report`
   2. Using django test command: `python manage.py test vending-machine`
    
