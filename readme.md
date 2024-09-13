
# E-commerce Platform

This is an advanced E-commerce platform built using Django, featuring user authentication, product management, and a
cart system. The platform uses PostgreSQL for database management, ajax for real-time updates, and has been deployed
on Railway. It offers a clean, responsive design with Bootstrap and includes functionalities like product search, checkout
processes, and dynamic cart updates without reloading the page.

## Features
- **User Authentication**: Secure user login, registration, and profile management.
- **Product Management**: Add, edit, and remove products.
- **Cart System**: Dynamic shopping cart with AJAX for real-time updates with for Cookies & Sessions maintaining user sessions, saving cart data, and enhancing the overall user experience.

- **Search & Filtering**: Find products efficiently.
- **Checkout**: Integrated checkout process and paymentgateway (paypal).

  
## Technologies Used
- python 
- Django
- Django ORM 
- PostgreSQL
- HTML 
- CSS 
- js 
- AJAX (for real-time updates)
- Bootstrap
- Railway (Deployment)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/OmarMuhammmed/E-commerce.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up PostgreSQL and configure the `.env` file.

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Deployment
The platform is deployed on [Railway](https://e-commerce-production-e2d7.up.railway.app/).

